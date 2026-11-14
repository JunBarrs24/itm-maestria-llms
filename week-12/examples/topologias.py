"""Cinco topologías para la misma mesa de soporte de Facturio.

El agente único de la semana 11 se divide en un triage y tres especialistas
(facturación, acceso, técnico), cada uno con sus instrucciones, sus tools y
sus permisos. Las cinco formas de conectarlos:

    single_agent          un agente con todas las tools (la semana 11)
    handoffs              triage -> especialista; el especialista responde al cliente
    agents_as_tools       un orquestador llama al especialista como tool y responde él
    manager               el orquestador descompone, consulta varios y sintetiza
    routing_determinista  el código elige el especialista (semana 8) y corre un solo agente

Y tres políticas de contexto para el handoff, que responden la pregunta de
cierre de la semana 9 (¿qué debería recibir el agente B del agente A?):

    "completo"   historial completo, incluida la llamada transfer_to_* (default del SDK)
    "sin_tools"  historial sin tool calls ni tool outputs (handoff_filters.remove_all_tools)
    "paquete"    solo un handoff package estructurado: objective, findings, sources,
                 constraints, open_questions

Backend: con OPENAI_API_KEY usa OpenAI y el tracing del dashboard; sin llave usa el
servidor local (`shared/local_server.py`) por Chat Completions y el tracing de consola.

Uso:  .venv/bin/python course/week-12/examples/topologias.py
"""
from __future__ import annotations

import asyncio
import dataclasses
import json
import re
import sys
import time
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "shared"))
sys.path.insert(0, str(HERE.parents[1] / "week-11" / "examples"))

import facturio_tools as ft  # noqa: E402
from local_server import backend_config  # noqa: E402

from agents import (  # noqa: E402
    Agent, HandoffInputData, ModelSettings, OpenAIChatCompletionsModel, RunContextWrapper, Runner,
    function_tool, handoff,
)
from agents.extensions import handoff_filters  # noqa: E402
from tracing_consola import TracingConsola, set_trace_processors, set_tracing_disabled  # noqa: E402

CFG = backend_config()


# ------------------------------------------------------------------ modelo
def modelo():
    """Con llave: Responses API y el nombre del modelo. Sin llave: Chat Completions contra el servidor local."""
    if CFG["local"]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=CFG["base_url"], api_key=CFG["api_key"] or "local", timeout=300)
        return OpenAIChatCompletionsModel(model=CFG["model"], openai_client=client)
    return CFG["model"]


AJUSTES = ModelSettings(max_tokens=160, temperature=0)


# ------------------------------------------------------------------ tools
# Las funciones de negocio viven en shared/facturio_tools.py. FALLAS permite provocar una
# caída controlada en una tool para observar cómo se propaga por cada topología.
FALLAS: dict[str, bool] = {"consultar_factura": False}


@function_tool(failure_error_function=None)   # None: la excepción sube en lugar de volverse texto para el modelo
def consultar_factura(folio: str) -> str:
    """Consulta una factura por folio (formato PAY- seguido de 8 dígitos). Devuelve estado, monto y fecha."""
    if FALLAS["consultar_factura"]:
        raise RuntimeError("servicio de cobros no disponible (timeout)")
    return json.dumps(ft.consultar_factura(folio), ensure_ascii=False)


@function_tool
def consultar_plan(usuario_id: str) -> str:
    """Consulta el plan de un usuario (u001 a u005): límites, uso actual y precio."""
    return json.dumps(ft.consultar_plan(usuario_id), ensure_ascii=False)


@function_tool
def buscar_documentacion(pregunta: str) -> str:
    """Busca en la documentación y políticas de Facturio. Úsala para dudas de políticas, límites y errores."""
    return json.dumps(ft.buscar_documentacion(pregunta, k=2), ensure_ascii=False)


@function_tool(needs_approval=True)
def reembolsar(folio: str, monto: float, motivo: str) -> str:
    """Solicita un reembolso sobre un cargo. Tiene side effect: mueve dinero. Requiere aprobación humana."""
    ok, razon = ft.autorizar_reembolso(folio, monto)
    return json.dumps(ft.reembolsar(folio, monto, motivo) if ok else {"ejecutado": False, "razon": razon}, ensure_ascii=False)


@function_tool
def escalar_a_humano(motivo: str) -> str:
    """Pasa el caso a un agente humano cuando la política lo exige o falta información."""
    return json.dumps(ft.escalar_a_humano(motivo), ensure_ascii=False)


TODAS_LAS_TOOLS = [consultar_factura, consultar_plan, buscar_documentacion, reembolsar, escalar_a_humano]

# Least privilege: cada especialista ve solo las tools de su dominio. Lo que no está en la
# lista no existe para el modelo; no hace falta prohibirlo en el prompt.
PERMISOS = {
    "Facturacion": [consultar_factura, consultar_plan, reembolsar],
    "Acceso": [buscar_documentacion],
    "Tecnico": [buscar_documentacion, escalar_a_humano],
}

DESCRIPCION = {
    "Facturacion": "Cobros, reembolsos, cargos duplicados, planes y precios.",
    "Acceso": "Contraseñas, inicio de sesión, 2FA, bloqueos, invitaciones.",
    "Tecnico": "Errores E-xxxx, exportación, API, integraciones, fallas del producto.",
}

INSTRUCCIONES = {
    "Soporte": ("Eres el asistente de la mesa de soporte de Facturio. Usa las tools cuando haga falta: consulta facturas "
                "y planes antes de afirmar algo, busca la documentación para políticas y errores, y escala a humano "
                "cuando falte información. Responde en español, breve."),
    "Facturacion": ("Eres el especialista de facturación de Facturio. Usa consultar_factura o consultar_plan antes de "
                    "afirmar algo sobre un cargo o un plan. Responde en español, breve."),
    "Acceso": ("Eres el especialista de acceso y seguridad de Facturio. Usa buscar_documentacion antes de responder. "
               "Responde en español, breve."),
    "Tecnico": ("Eres el especialista técnico de Facturio. Usa buscar_documentacion con el código de error antes de "
                "responder; si no hay solución documentada, escala a humano. Responde en español, breve."),
    "Triage": ("Eres el triage de la mesa de soporte de Facturio. No respondas tú: transfiere cada ticket al "
               "especialista adecuado con la tool transfer_to_*."),
    "Orquestador": ("Eres la mesa de soporte de Facturio. Para resolver el ticket llama a la tool del especialista "
                    "adecuado y devuelve su respuesta al cliente. Responde en español, breve."),
    "Manager": ("Eres el coordinador de la mesa de soporte de Facturio. El ticket puede tener varios temas: llama a la "
                "tool del especialista de cada tema (una llamada por tema) y al final integra las respuestas en un solo "
                "mensaje breve en español."),
}


# ------------------------------------------------------------------ handoff package
class PaqueteHandoff(BaseModel):
    """Lo que el agente B recibe del agente A cuando no se le manda el historial completo."""
    objective: str = Field(description="Qué necesita el cliente, en una oración")
    findings: list[str] = Field(default_factory=list, description="Datos ya conocidos: folios, usuario, códigos, fechas")
    sources: list[str] = Field(default_factory=list, description="De dónde salió cada dato (tool, documento, cliente)")
    constraints: list[str] = Field(default_factory=list, description="Límites que el especialista debe respetar")
    open_questions: list[str] = Field(default_factory=list, description="Lo que falta por averiguar")


PAQUETES: list[dict] = []   # los paquetes que viajaron en la última corrida (para inspección en clase)


async def registrar_paquete(ctx: RunContextWrapper, paquete: PaqueteHandoff) -> None:
    """on_handoff: el código ve el paquete antes que el especialista y puede completarlo."""
    p = paquete.model_dump()
    folios = re.findall(r"PAY-\d{8}", p["objective"] + " ".join(p["findings"]))
    for f in folios:
        if f not in p["findings"]:
            p["findings"].append(f)          # el código completa lo que el modelo omitió
    PAQUETES.append(p)


def filtro_paquete(data: HandoffInputData) -> HandoffInputData:
    """input_filter: el especialista recibe solo el paquete, como único mensaje de usuario."""
    args = "{}"
    for item in data.new_items:
        if type(item).__name__ == "HandoffCallItem":
            args = getattr(item.raw_item, "arguments", "{}") or "{}"
    try:
        paquete = PaqueteHandoff.model_validate_json(args).model_dump()
    except Exception:
        paquete = {"objective": args}
    for f in re.findall(r"PAY-\d{8}", args):
        if f not in paquete.get("findings", []):
            paquete.setdefault("findings", []).append(f)
    mensaje = {"role": "user", "content": "Handoff package:\n" + json.dumps(paquete, ensure_ascii=False, indent=1)}
    return dataclasses.replace(data, input_history=(mensaje,), pre_handoff_items=(), new_items=(), input_items=None)


FILTROS = {"completo": None, "sin_tools": handoff_filters.remove_all_tools, "paquete": filtro_paquete}


# ------------------------------------------------------------------ agentes
def especialista(nombre: str) -> Agent:
    return Agent(name=nombre, handoff_description=DESCRIPCION[nombre], instructions=INSTRUCCIONES[nombre],
                 tools=list(PERMISOS[nombre]), model=modelo(), model_settings=AJUSTES)


def especialistas() -> dict[str, Agent]:
    return {n: especialista(n) for n in PERMISOS}


def single_agent() -> Agent:
    """La semana 11: un agente, todas las tools."""
    return Agent(name="Soporte", instructions=INSTRUCCIONES["Soporte"], tools=list(TODAS_LAS_TOOLS),
                 model=modelo(), model_settings=AJUSTES)


def handoffs(contexto: str = "completo") -> Agent:
    """Triage que transfiere el control. El especialista responde al cliente; el triage no vuelve a hablar."""
    esp = especialistas()
    if contexto == "paquete":
        hs = [handoff(a, input_type=PaqueteHandoff, on_handoff=registrar_paquete, input_filter=filtro_paquete) for a in esp.values()]
    else:
        hs = [handoff(a, input_filter=FILTROS[contexto]) for a in esp.values()]
    return Agent(name="Triage", instructions=INSTRUCCIONES["Triage"], handoffs=hs, model=modelo(), model_settings=AJUSTES)


def _como_tools(esp: dict[str, Agent]) -> list:
    return [esp["Facturacion"].as_tool("preguntar_facturacion", "Resuelve dudas de cobros, reembolsos, planes y facturas. Pásale el folio o el usuario."),
            esp["Acceso"].as_tool("preguntar_acceso", "Resuelve dudas de contraseñas, sesión, 2FA, bloqueos e invitaciones."),
            esp["Tecnico"].as_tool("preguntar_tecnico", "Resuelve errores E-xxxx, exportación, API e integraciones.")]


def agents_as_tools() -> Agent:
    """El orquestador conserva el control: el especialista devuelve texto y el orquestador responde al cliente."""
    return Agent(name="Orquestador", instructions=INSTRUCCIONES["Orquestador"], tools=_como_tools(especialistas()),
                 model=modelo(), model_settings=AJUSTES)


def manager() -> Agent:
    """Agents-as-tools con descomposición: varios especialistas por ticket y una síntesis al final."""
    return Agent(name="Manager", instructions=INSTRUCCIONES["Manager"], tools=_como_tools(especialistas()),
                 model=modelo(), model_settings=AJUSTES)


PALABRAS = {
    "Facturacion": ("factura", "cobr", "reembols", "plan ", "plan.", "precio", "pago", "cargo", "descuento"),
    "Acceso": ("contraseña", "sesión", "sesion", "2fa", "bloque", "invitaci", "acceso", "entrar"),
    "Tecnico": ("error", "e-", "export", "pdf", "api", "webhook", "integraci", "csv"),
}


def ruta_determinista(ticket: str) -> str | None:
    """El routing de la semana 8 sin modelo: folio o código primero, palabras clave después.
    Devuelve None cuando el código no sabe; entonces responde el agente general."""
    if re.search(r"PAY-\d{8}", ticket):
        return "Facturacion"
    if re.search(r"E-\d{4}", ticket):
        return "Tecnico"
    t = ticket.lower()
    puntos = {n: sum(1 for k in ks if k in t) for n, ks in PALABRAS.items()}
    mejor = max(puntos, key=puntos.get)
    return mejor if puntos[mejor] > 0 else None


def routing_determinista(ticket: str) -> tuple[str, Agent]:
    ruta = ruta_determinista(ticket)
    return (ruta, especialista(ruta)) if ruta else ("Soporte", single_agent())


# ------------------------------------------------------------------ tracing con el contexto que viajó
class TracingContexto(TracingConsola):
    """El procesador de la semana 11 más la entrada de cada llamada al modelo, para medir qué recibió cada agente."""

    def _fila(self, span) -> dict:
        fila = super()._fila(span)
        if fila["tipo"] == "generation":
            fila["entrada"] = list(span.span_data.input or [])
        return fila


def activar_tracing() -> TracingContexto:
    consola = TracingContexto()
    set_tracing_disabled(False)
    set_trace_processors([consola])
    return consola


def contexto_que_viajo(trace: dict) -> dict[str, dict]:
    """Por agente: cuántos mensajes y caracteres recibió en su primera llamada al modelo, y qué roles."""
    por_id = {s["span_id"]: s for s in trace["spans"]}
    salida: dict[str, dict] = {}
    for s in trace["spans"]:
        if s["tipo"] != "generation":
            continue
        padre, agente = s["parent_id"], None
        while padre and padre in por_id:
            if por_id[padre]["tipo"] == "agent":
                agente = por_id[padre]["nombre"]
                break
            padre = por_id[padre]["parent_id"]
        if agente in salida:
            continue                       # solo la primera llamada de cada agente
        msgs = s["entrada"]
        salida[agente or "?"] = {"mensajes": len(msgs), "caracteres": sum(len(json.dumps(m, ensure_ascii=False)) for m in msgs),
                                 "input_tokens": s["usage"].get("input_tokens", 0),
                                 "roles": [m.get("role", m.get("type", "?")) for m in msgs]}
    return salida


# ------------------------------------------------------------------ correr y medir
async def correr(agente: Agent, entrada, aprobar: Callable[[str, dict], bool] | None = None, max_turns: int = 6):
    """Runner.run más el ciclo de aprobación de la semana 11 (reembolsar tiene needs_approval)."""
    r = await Runner.run(agente, entrada, max_turns=max_turns)
    while getattr(r, "interruptions", None):
        estado = r.to_state()
        for item in r.interruptions:
            args = json.loads(item.raw_item.arguments or "{}")
            (estado.approve if (aprobar and aprobar(item.tool_name, args)) else estado.reject)(item)
        r = await Runner.run(agente, estado, max_turns=max_turns)
    return r


TOPOLOGIAS = ["single_agent", "handoffs", "agents_as_tools", "manager", "routing_determinista"]


def construir(topologia: str, contexto: str = "sin_tools"):
    if topologia == "single_agent":
        return single_agent()
    if topologia == "handoffs":
        return handoffs(contexto)
    if topologia == "agents_as_tools":
        return agents_as_tools()
    if topologia == "manager":
        return manager()
    raise ValueError(topologia)


async def ejecutar(topologia: str, ticket, consola: TracingContexto, contexto: str = "sin_tools", max_turns: int = 6) -> dict:
    """Corre un ticket con una topología y devuelve una fila medible."""
    PAQUETES.clear()
    t0 = time.perf_counter()
    ruta = None
    if topologia == "routing_determinista":
        ruta, agente = routing_determinista(ticket if isinstance(ticket, str) else ticket[-1]["content"])
    else:
        agente = construir(topologia, contexto)
    try:
        r = await correr(agente, ticket, max_turns=max_turns)
        respuesta, ultimo, error = str(r.final_output or ""), r.last_agent.name, None
    except Exception as e:
        respuesta, ultimo, error = "", "?", f"{type(e).__name__}: {str(e)[:80]}"
    res = consola.resumen() or {}
    tools = res.get("tool_calls", [])
    consultados = [t.replace("preguntar_", "").capitalize() for t in tools if t.startswith("preguntar_")]
    if topologia == "handoffs":
        atendio = ultimo if ultimo != "Triage" else "Triage"
    elif topologia in ("agents_as_tools", "manager"):
        atendio = "+".join(consultados) if consultados else ultimo
    elif topologia == "routing_determinista":
        atendio = ruta
    else:
        atendio = "Soporte"
    return {"topologia": topologia, "atendio": atendio, "llamadas_modelo": res.get("llamadas_modelo", 0),
            "tools": [t for t in tools if not t.startswith("preguntar_")], "tools_de_agente": [t for t in tools if t.startswith("preguntar_")],
            "input_tokens": res.get("input_tokens", 0), "output_tokens": res.get("output_tokens", 0),
            "latencia_s": round(time.perf_counter() - t0, 2), "respuesta": respuesta, "error": error,
            "paquetes": list(PAQUETES)}


# ------------------------------------------------------------------ demo
TICKET_LARGO = ("Hola, buenas tardes. Les escribo porque llevo tres años con Facturio y en general estoy contento, aunque el "
                "mes pasado cambiamos de contador y hubo confusión con los pagos. Mi contador dice que ya se pagó pero yo no "
                "veo nada en el portal. Mi usuario es u001 y el folio del cargo es {folio}. ¿Me pueden decir cuál es el "
                "estado de esa factura? Gracias de antemano, y disculpen la molestia.")


async def demo():
    consola = activar_tracing()
    folio = list(ft.CARGOS)[0]
    ticket = f"¿Cuál es el estado de la factura {folio}?"
    print(f"backend: {CFG['model']} | ticket: {ticket}\n")
    for topo in TOPOLOGIAS:
        fila = await ejecutar(topo, ticket, consola)
        print(f"== {topo}: atendió {fila['atendio']} | {fila['llamadas_modelo']} llamadas | tools {fila['tools']} | "
              f"{fila['input_tokens']}+{fila['output_tokens']} tokens | {fila['latencia_s']} s | error={fila['error']}")
        print("   respuesta:", fila["respuesta"][:120].replace("\n", " "))
        consola.imprimir()
        print()

    print("== handoffs: qué contexto recibió el especialista según la política (ticket largo)")
    for contexto in FILTROS:
        fila = await ejecutar("handoffs", TICKET_LARGO.format(folio=folio), consola, contexto=contexto)
        print(f"   {contexto:9s} atendió {fila['atendio']:12s} -> {contexto_que_viajo(consola.ultimo())}")
        if fila["paquetes"]:
            print("   paquete:", json.dumps(fila["paquetes"][0], ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(demo())
