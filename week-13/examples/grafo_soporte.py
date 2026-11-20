"""La mesa de soporte de Facturio como grafo de LangGraph (semana 13).

El flujo lo decide el código; el modelo decide solo dentro de los nodos que lo usan.

    START -> clasificar -> agente_<categoria> -> validar -> END
                              ^                  |
                              +---- reintento ---+  (con límite)
                                                 |
                              (reembolso) -> aprobacion_humana -> ejecutar_reembolso -> END
                              (sin éxito)  -> escalar -> END

Es el sistema de la semana 12 (triage + Facturacion, Acceso, Tecnico, con el agente
general como fallback del routing determinista) escrito como grafo. Dos cambios:
el triage es un nodo sin modelo (las reglas de `ruta_determinista` de la semana 12),
y el reembolso deja de ser una tool del especialista: tiene su propio camino con
aprobación humana y lo ejecuta el grafo.

Nodos deterministas: clasificar, validar, ejecutar_reembolso, escalar.
Nodos con modelo: agente_facturacion, agente_acceso, agente_tecnico, agente_reembolso, agente_general.
Nodo con interrupción: aprobacion_humana (requiere checkpointer).

GRAPH STATE != MODEL CONTEXT: el state guarda categoría, intentos, traza, tokens,
decisión humana y resultado del reembolso. Al modelo solo llegan las instrucciones
de su especialidad, el mensaje del cliente y, si hubo reintento, el motivo.

Backend: con OPENAI_API_KEY usa OpenAI; sin llave usa el servidor local
(`shared/local_server.py`) por Chat Completions. El grafo es el mismo.

Uso:  .venv/bin/python course/week-13/examples/grafo_soporte.py
"""
from __future__ import annotations

import json
import operator
import re
import sys
import time
from pathlib import Path
from typing import Annotated, Any, Callable, Literal, Optional, TypedDict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "shared"))

import facturio_tools as ft  # noqa: E402
from local_server import backend_config  # noqa: E402

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langchain_openai import ChatOpenAI  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402
from langgraph.types import RetryPolicy, interrupt  # noqa: E402

CFG = backend_config()
MAX_INTENTOS = 2          # reintentos semánticos: cuántas veces vuelve al agente si la validación falla
MAX_RONDAS_TOOLS = 2      # dentro de un nodo agente: cuántas vueltas modelo -> tool -> modelo


# ------------------------------------------------------------------ modelo
def modelo(max_tokens: int = 220) -> ChatOpenAI:
    """Un cliente de chat con la misma interfaz en los dos backends."""
    if CFG["local"]:      # servidor local: Chat Completions, modelo pequeño, temperatura fija
        return ChatOpenAI(model=CFG["model"], base_url=CFG["base_url"], api_key=CFG["api_key"] or "local",
                          max_tokens=max_tokens, temperature=0, timeout=180, max_retries=1)
    return ChatOpenAI(model=CFG["model"], max_tokens=max_tokens, timeout=60)   # con llave: OpenAI


LLM = modelo()

# Contador fuera del grafo: cuenta TODAS las llamadas al modelo, incluidas las de intentos
# que el RetryPolicy descartó. El state solo conserva las del intento que terminó.
CONTADOR = {"llamadas": 0, "tokens_in": 0, "tokens_out": 0}


def reiniciar_contador() -> None:
    CONTADOR.update(llamadas=0, tokens_in=0, tokens_out=0)


# ------------------------------------------------------------------ tools (las de shared, envueltas)
# Inyección de fallas para la demo: {nombre_tool: fallas pendientes}. Cada ejecución
# con fallas pendientes lanza ConnectionError y descuenta una.
FALLAS: dict[str, int] = {}


def inyectar_falla(nombre: str, veces: int) -> None:
    FALLAS[nombre] = veces


def _ejecutar(nombre: str, fn: Callable, **kw) -> dict:
    if FALLAS.get(nombre, 0) > 0:
        FALLAS[nombre] -= 1
        raise ConnectionError(f"{nombre}: falla transitoria inyectada")
    return fn(**kw)


@tool
def consultar_factura(folio: str) -> str:
    """Consulta un cargo por folio (formato PAY- seguido de 8 dígitos). Devuelve monto, fecha, estado y días desde el cargo."""
    return json.dumps(_ejecutar("consultar_factura", ft.consultar_factura, folio=folio), ensure_ascii=False)


@tool
def consultar_plan(usuario_id: str) -> str:
    """Consulta el plan de un usuario (u001 a u005): límites, uso actual y precio."""
    return json.dumps(_ejecutar("consultar_plan", ft.consultar_plan, usuario_id=usuario_id), ensure_ascii=False)


@tool
def buscar_documentacion(pregunta: str) -> str:
    """Busca en la documentación y políticas de Facturio. Úsala para dudas de políticas, límites, plazos y errores."""
    r = _ejecutar("buscar_documentacion", ft.buscar_documentacion, pregunta=pregunta, k=2)
    return json.dumps(r, ensure_ascii=False)


TOOLS_POR_NOMBRE = {t.name: t for t in (consultar_factura, consultar_plan, buscar_documentacion)}

# Least privilege por especialidad (los PERMISOS de la semana 12): cada agente ve solo las
# tools de su categoría. `reembolsar` y `escalar_a_humano` no son tools del modelo: las ejecuta el grafo.
ESPECIALIDADES: dict[str, dict] = {
    "facturacion": {
        "tools": ["consultar_factura", "consultar_plan"],
        "instrucciones": "Eres el especialista de facturación de Facturio. Usa consultar_factura o consultar_plan "
                         "antes de afirmar algo sobre un cargo o un plan. Responde en español, breve.",
    },
    "acceso": {
        "tools": ["buscar_documentacion"],
        "instrucciones": "Eres el especialista de acceso y seguridad de Facturio. Usa buscar_documentacion antes de "
                         "responder. Responde en español, breve, citando la política encontrada.",
    },
    "tecnico": {
        "tools": ["buscar_documentacion"],
        "instrucciones": "Eres el especialista técnico de Facturio. Usa buscar_documentacion con el código de error "
                         "antes de responder. Responde en español, breve. Si no hay solución documentada, dilo.",
    },
    "reembolso": {
        "tools": ["consultar_factura"],
        "instrucciones": "Eres soporte de reembolsos de Facturio. Consulta el cargo con la tool y resume monto, fecha y "
                         "estado. Di que la solicitud pasará a revisión. No afirmes que el reembolso fue realizado.",
    },
    "general": {
        "tools": ["consultar_factura", "consultar_plan", "buscar_documentacion"],
        "instrucciones": "Eres el asistente de la mesa de soporte de Facturio. Usa las tools antes de afirmar algo: "
                         "facturas y planes con las de consulta, políticas y errores con la documentación. "
                         "Responde en español, breve.",
    },
}
Categoria = Literal["facturacion", "acceso", "tecnico", "reembolso", "general"]


# ------------------------------------------------------------------ state
class EstadoSoporte(TypedDict, total=False):
    # entrada
    mensaje: str
    # decidido por código (clasificar)
    categoria: str
    folio: Optional[str]
    usuario_id: Optional[str]
    monto: Optional[float]
    # producido por el modelo
    respuesta: str
    tool_calls_intento: list[str]                  # las del último intento (se reemplaza)
    tool_calls: Annotated[list[str], operator.add]  # todas las de la corrida (se acumulan)
    ultimo_contexto: list[dict]                    # lo que se envió al modelo, para verlo lado a lado
    # control del grafo: nunca llega al modelo
    intentos: int
    valida: bool
    motivo_invalida: str
    aprobacion: Optional[dict]
    reembolso: Optional[dict]
    traza: Annotated[list[str], operator.add]
    tokens_in: Annotated[int, operator.add]
    tokens_out: Annotated[int, operator.add]


# ------------------------------------------------------------------ nodos deterministas
RE_FOLIO = re.compile(r"PAY-\d{8}")
RE_USUARIO = re.compile(r"\bu\d{3}\b")
RE_MONTO = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:pesos|mxn|\$)", re.I)
# Las palabras clave del routing determinista de la semana 12 (topologias.py), con el reembolso separado.
PALABRAS = {
    "facturacion": ("factura", "cobr", "plan ", "plan.", "precio", "pago", "cargo", "descuento"),
    "acceso": ("contraseña", "sesión", "sesion", "2fa", "bloque", "invitaci", "acceso", "entrar"),
    "tecnico": ("error", "e-", "export", "pdf", "api", "webhook", "integraci", "csv"),
}


def clasificar(state: EstadoSoporte) -> dict:
    """Clasificador determinista: el triage de la semana 12 sin modelo. Cero tokens, cero variabilidad."""
    m = state["mensaje"]
    bajo = m.lower()
    folio = RE_FOLIO.search(m)
    usuario = RE_USUARIO.search(m)
    monto = RE_MONTO.search(m)
    if "reembols" in bajo:                       # side effect: camino propio con aprobación humana
        cat = "reembolso"
    elif folio:
        cat = "facturacion"
    elif re.search(r"E-\d{4}", m):
        cat = "tecnico"
    else:
        puntos = {n: sum(1 for k in ks if k in bajo) for n, ks in PALABRAS.items()}
        mejor = max(puntos, key=puntos.get)
        cat = mejor if puntos[mejor] > 0 else "general"   # cuando el código no sabe, el agente general
    return {"categoria": cat, "folio": folio.group(0) if folio else None,
            "usuario_id": usuario.group(0) if usuario else None,
            "monto": float(monto.group(1).replace(",", ".")) if monto else None,
            "intentos": 0, "valida": False, "motivo_invalida": "", "aprobacion": None, "reembolso": None,
            "tool_calls_intento": [], "traza": ["clasificar"]}


RE_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
RE_PROMESA = re.compile(r"reembolso (fue|ha sido|se ha|está|esta) (realizado|procesado|aplicado|completado)|"
                        r"hemos reembolsado|se reembols[óo]|ya (fue|está) reembolsad", re.I)


def validar(state: EstadoSoporte) -> dict:
    """Validación determinista de la respuesta del agente. Es el guardrail de salida de la semana 11 como nodo."""
    r = (state.get("respuesta") or "").strip()
    motivo = ""
    if not r:
        motivo = "respuesta vacía"
    elif RE_CORREO.search(r):
        motivo = "la respuesta contiene un correo electrónico"
    elif not state.get("tool_calls_intento"):
        motivo = "respondió sin consultar datos (ninguna tool en este intento)"
    elif RE_PROMESA.search(r) and not state.get("reembolso"):
        motivo = "afirma un reembolso que no se ejecutó"
    return {"valida": motivo == "", "motivo_invalida": motivo, "traza": ["validar"]}


def aprobacion_humana(state: EstadoSoporte) -> dict:
    """Se detiene aquí. El grafo guarda el checkpoint y devuelve el control a la aplicación."""
    decision = interrupt({
        "pregunta": "¿Aprobar el reembolso?",
        "folio": state.get("folio"), "monto": state.get("monto"),
        "resumen_del_agente": (state.get("respuesta") or "")[:300],
    })
    if isinstance(decision, dict):
        return {"aprobacion": decision, "traza": ["aprobacion_humana"]}
    return {"aprobacion": {"aprobado": bool(decision), "quien": "operador"}, "traza": ["aprobacion_humana"]}


def ejecutar_reembolso(state: EstadoSoporte) -> dict:
    """Side effect ejecutado por el grafo después de la aprobación. La regla de negocio sigue en shared."""
    ap = state.get("aprobacion") or {}
    if not ap.get("aprobado"):
        return {"reembolso": {"ejecutado": False, "razon": "rechazado por la persona que aprueba"},
                "respuesta": state["respuesta"] + "\n\n[Sistema] La solicitud de reembolso fue rechazada en revisión.",
                "traza": ["ejecutar_reembolso"]}
    folio, monto = state.get("folio"), state.get("monto")
    if not folio or not monto:
        return {"reembolso": {"ejecutado": False, "razon": "faltan folio o monto en la solicitud"},
                "respuesta": state["respuesta"] + "\n\n[Sistema] Falta el folio o el monto; escribe a soporte con ambos.",
                "traza": ["ejecutar_reembolso"]}
    limite_previo = ft.MONTO_MAXIMO_SIN_HUMANO
    ft.MONTO_MAXIMO_SIN_HUMANO = max(limite_previo, monto)   # la aprobación humana sustituye el límite automático
    try:
        res = ft.reembolsar(folio, monto, ap.get("motivo", "solicitud del cliente"))
    finally:
        ft.MONTO_MAXIMO_SIN_HUMANO = limite_previo
    nota = (f"[Sistema] Reembolso aplicado: {res['referencia']} por {res['monto']:.2f}, abono en {res['abono_en']}."
            if res.get("ejecutado") else f"[Sistema] Reembolso no aplicado: {res.get('razon')}.")
    return {"reembolso": res, "respuesta": state["respuesta"] + "\n\n" + nota, "traza": ["ejecutar_reembolso"]}


def escalar(state: EstadoSoporte) -> dict:
    t = ft.escalar_a_humano(motivo=f"validación fallida {state.get('intentos')} veces: {state.get('motivo_invalida')}",
                            folio=state.get("folio"))
    return {"respuesta": f"Tu caso pasó a una persona del equipo (ticket {t['ticket']}). Te contactamos pronto.",
            "traza": ["escalar"]}


# ------------------------------------------------------------------ nodos con modelo
def contexto_para_modelo(state: EstadoSoporte) -> list:
    """Lo único del state que llega al modelo. Compárese con las llaves del state completo."""
    esp = ESPECIALIDADES[state["categoria"]]
    instr = esp["instrucciones"]
    if state.get("intentos", 0) > 0 and state.get("motivo_invalida"):
        instr += f"\nTu respuesta anterior fue rechazada: {state['motivo_invalida']}. Corrige."
    return [SystemMessage(content=instr), HumanMessage(content=state["mensaje"])]


def _usage(msg: AIMessage) -> tuple[int, int]:
    u = msg.usage_metadata or {}
    return int(u.get("input_tokens", 0)), int(u.get("output_tokens", 0))


def hacer_agente(categoria: str) -> Callable[[EstadoSoporte], dict]:
    """Fábrica: un nodo agente por especialidad, con sus tools y sus instrucciones."""
    esp = ESPECIALIDADES[categoria]
    tools = [TOOLS_POR_NOMBRE[n] for n in esp["tools"]]
    llm_tools = LLM.bind_tools(tools)

    def agente(state: EstadoSoporte) -> dict:
        mensajes = contexto_para_modelo(state)
        t_in = t_out = 0
        calls: list[str] = []
        respuesta = ""
        for ronda in range(MAX_RONDAS_TOOLS + 1):
            ai = (llm_tools if ronda < MAX_RONDAS_TOOLS else LLM).invoke(mensajes)
            a, b = _usage(ai)
            t_in, t_out = t_in + a, t_out + b
            CONTADOR["llamadas"] += 1
            CONTADOR["tokens_in"] += a
            CONTADOR["tokens_out"] += b
            mensajes.append(ai)
            if not ai.tool_calls:
                respuesta = ai.content if isinstance(ai.content, str) else str(ai.content)
                break
            for tc in ai.tool_calls:
                calls.append(tc["name"])
                salida = TOOLS_POR_NOMBRE[tc["name"]].invoke(tc["args"])   # ConnectionError sube al RetryPolicy del nodo
                mensajes.append(ToolMessage(content=salida, tool_call_id=tc["id"]))
        return {"respuesta": respuesta, "tool_calls_intento": calls, "tool_calls": calls,
                "intentos": state.get("intentos", 0) + 1, "tokens_in": t_in, "tokens_out": t_out,
                "ultimo_contexto": [{"role": m.type, "content": (m.content if isinstance(m.content, str) else str(m.content))[:400]}
                                    for m in mensajes],
                "traza": [f"agente_{categoria}"]}

    agente.__name__ = f"agente_{categoria}"
    return agente


# ------------------------------------------------------------------ edges condicionales
def ruta_por_categoria(state: EstadoSoporte) -> str:
    return f"agente_{state['categoria']}"


def ruta_despues_de_validar(state: EstadoSoporte) -> str:
    if state["valida"]:
        return "aprobacion_humana" if state["categoria"] == "reembolso" else END
    if state["intentos"] < MAX_INTENTOS:
        return f"agente_{state['categoria']}"   # ciclo con límite
    return "escalar"


# ------------------------------------------------------------------ construcción
def construir_grafo(checkpointer=None, retry_policy: RetryPolicy | None = None):
    """Arma y compila el grafo. Con checkpointer se puede interrumpir y reanudar."""
    if retry_policy is None:
        retry_policy = RetryPolicy(max_attempts=3, initial_interval=0.2, backoff_factor=2.0, retry_on=ConnectionError)
    g = StateGraph(EstadoSoporte)
    g.add_node("clasificar", clasificar)
    for cat in ESPECIALIDADES:
        g.add_node(f"agente_{cat}", hacer_agente(cat), retry_policy=retry_policy)
    g.add_node("validar", validar)
    g.add_node("aprobacion_humana", aprobacion_humana)
    g.add_node("ejecutar_reembolso", ejecutar_reembolso)
    g.add_node("escalar", escalar)

    g.add_edge(START, "clasificar")
    g.add_conditional_edges("clasificar", ruta_por_categoria, [f"agente_{c}" for c in ESPECIALIDADES])
    for cat in ESPECIALIDADES:
        g.add_edge(f"agente_{cat}", "validar")
    g.add_conditional_edges("validar", ruta_despues_de_validar,
                            [f"agente_{c}" for c in ESPECIALIDADES] + ["aprobacion_humana", "escalar", END])
    g.add_edge("aprobacion_humana", "ejecutar_reembolso")
    g.add_edge("ejecutar_reembolso", END)
    g.add_edge("escalar", END)
    return g.compile(checkpointer=checkpointer)


def estado_inicial(mensaje: str) -> dict:
    return {"mensaje": mensaje, "tool_calls": [], "traza": [], "tokens_in": 0, "tokens_out": 0}


def correr(app, mensaje: str, thread_id: str = "demo", recursion_limit: int = 25) -> dict:
    """Invoca el grafo y devuelve el state final (o el parcial, si se interrumpió)."""
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": recursion_limit}
    t0 = time.perf_counter()
    salida = app.invoke(estado_inicial(mensaje), config)
    salida["latencia_s"] = round(time.perf_counter() - t0, 2)
    return salida


def resumen(state: dict) -> dict:
    return {"categoria": state.get("categoria"), "traza": state.get("traza"), "intentos": state.get("intentos"),
            "valida": state.get("valida"), "motivo": state.get("motivo_invalida") or "",
            "tools": state.get("tool_calls"), "tokens": (state.get("tokens_in", 0), state.get("tokens_out", 0)),
            "latencia_s": state.get("latencia_s"), "interrumpido": "__interrupt__" in state}


# ------------------------------------------------------------------ demo
if __name__ == "__main__":
    from langgraph.types import Command

    ft.reiniciar_estado()
    app = construir_grafo(checkpointer=InMemorySaver())
    folio = list(ft.CARGOS)[0]

    print("== 1. Consulta de facturación (clasificar -> agente -> validar)")
    s = correr(app, f"¿Cuál es el estado del cargo {folio}?", thread_id="c1")
    print(s["respuesta"]); print(resumen(s))

    print("\n== 2. Lo que vio el modelo frente a lo que guarda el grafo")
    print("state:", sorted(k for k in s if k != "ultimo_contexto"))
    print("contexto:", [(m["role"], m["content"][:60]) for m in s["ultimo_contexto"]])

    print("\n== 3. Reembolso: se detiene antes del side effect")
    s = correr(app, f"Quiero un reembolso de 300 pesos del cargo {folio}.", thread_id="r1")
    print("interrumpido:", s["__interrupt__"][0].value)
    print("reembolsos antes de aprobar:", dict(ft.REEMBOLSOS))
    s = app.invoke(Command(resume={"aprobado": True, "quien": "supervisora", "motivo": "cargo sin uso"}),
                   {"configurable": {"thread_id": "r1"}})
    print(s["respuesta"]); print("reembolsos:", dict(ft.REEMBOLSOS)); print(resumen(s))

    print("\n== 4. Falla inyectada en una tool: el RetryPolicy del nodo la absorbe")
    reiniciar_contador()
    inyectar_falla("consultar_factura", 2)
    s = correr(app, f"¿Cuánto cobró el cargo {folio}?", thread_id="f1")
    print(resumen(s), "| fallas pendientes:", FALLAS)
    print("el state contó", s["tokens_in"] + s["tokens_out"], "tokens; el contador fuera del grafo contó",
          CONTADOR["tokens_in"] + CONTADOR["tokens_out"], "en", CONTADOR["llamadas"], "llamadas")
