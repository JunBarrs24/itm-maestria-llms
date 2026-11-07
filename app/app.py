"""Facturio Soporte: la aplicación de chat del curso.

Un solo proceso: FastAPI sirve la página (index.html) y expone POST /chat. El backend
llama a la Responses API de OpenAI con las tools de Facturio, ejecuta lo que el modelo
pide (si la aplicación lo autoriza) y devuelve, además de la respuesta, el trace
completo y el contexto exacto que se envió al modelo.

Lo que se ve en pantalla es lo que el curso estudia:
  * tool calling: el modelo pide, la aplicación valida, decide, ejecuta y devuelve (semana 8);
  * autorización: `reembolsar` solo se ejecuta si la política de la aplicación lo permite (semana 8);
  * routing: una regla determinista elige el especialista antes de llamar al modelo (semana 8);
  * contexto: tres estrategias para construir lo que el modelo ve en cada turno (semana 9);
  * motor: el mismo turno corrido por el loop manual o por el Agents SDK, con aprobación humana (semana 10);
  * trace: llamadas, tools, tokens, latencia y resumen de razonamiento (semanas 11 y 15).

Uso:
    pip install -r requirements.txt
    cp .env.example .env     # la llave individual va ahí
    python app.py            # abre http://localhost:8011
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

AQUI = Path(__file__).resolve().parent
load_dotenv(AQUI / ".env")
sys.path.insert(0, str(AQUI.parent / "shared"))        # dentro del repositorio
sys.path.insert(0, str(AQUI / "shared"))               # copia local para distribución
import facturio_tools as ft                            # noqa: E402

# ---------------------------------------------------------------- configuración
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
REASONING_EFFORT = os.environ.get("REASONING_EFFORT", "minimal")   # none | minimal | low | medium | high | xhigh
REASONING_SUMMARY = os.environ.get("REASONING_SUMMARY", "auto")    # auto | concise | detailed | "" para no pedirlo
COMPRESOR = os.environ.get("COMPRESOR", "llm")                     # determinista | llm  (estrategia C: cómo se resume lo viejo)
UMBRAL_COMPRESION = int(os.environ.get("UMBRAL_COMPRESION", "8"))  # mensajes en el historial a partir de los cuales se comprime
PRECIOS_USD_POR_MILLON = {"gpt-5-mini": (0.25, 2.00), "gpt-5-nano": (0.05, 0.40), "gpt-5": (1.25, 10.00)}

INSTRUCCIONES_BASE = (
    "Eres el asistente de soporte de Facturio, un SaaS mexicano de facturación. Responde en español, "
    "breve y concreto. Cuando necesites datos de un cargo, un plan o la documentación, usa las herramientas. "
    "Nunca afirmes que un reembolso se ejecutó si la herramienta no lo confirmó. Si no puedes resolver, escala a una persona."
)
ESPECIALISTAS = {
    # buscar_documentacion va en todas las rutas: sin ella, el especialista responde políticas de memoria
    # (y se equivoca con fluidez: "30 días" cuando la política dice 14). Se vio en la primera prueba.
    "facturacion": ("Especialista de facturación. Atiende cargos, reembolsos y planes. Para plazos y políticas, consulta la documentación antes de responder.", ["consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar", "escalar_a_humano"]),
    "acceso": ("Especialista de acceso. Atiende contraseñas, bloqueos y 2FA con la documentación.", ["buscar_documentacion", "escalar_a_humano"]),
    "tecnico": ("Especialista técnico. Atiende errores del producto con la documentación.", ["buscar_documentacion", "escalar_a_humano"]),
    "general": (INSTRUCCIONES_BASE, list(ft.TOOLS)),
}


def ruta_determinista(texto: str) -> str:
    """Routing de la semana 8: una regla barata antes del modelo. Devuelve el especialista."""
    t = texto.lower()
    if re.search(r"\bpay-\d{8}\b|cobr|cargo|reembols|factur|plan\b|mensualidad", t):
        return "facturacion"
    if re.search(r"contraseñ|password|bloque|iniciar sesi|entrar|2fa|código de verific|sesión", t):
        return "acceso"
    if re.search(r"\be-\d{4}\b|error|falla|se cierra|no funciona|pantalla|exportar|pdf", t):
        return "tecnico"
    return "general"


# ---------------------------------------------------------------- estado y contexto (semana 9)
class Sesion:
    """APPLICATION STATE: todo lo que la aplicación guarda. MODEL CONTEXT: lo que decide enviar."""

    def __init__(self):
        self.historial: list[dict] = []          # turnos completos, nunca se envían enteros si la estrategia no lo pide
        self.estado = {"usuario_id": None, "folios": [], "constraints": [], "completed_steps": [], "important_facts": {}}
        self.resumen = ""                        # resumen de lo viejo, para la estrategia C
        self.pendiente: dict | None = None       # motor SDK: corrida detenida a la espera de una persona (semana 10)
        self.tokens_acumulados = 0

    def actualizar_estado(self, texto_usuario: str, resultados_tools: list[dict]):
        """KEEP. Reglas deterministas: lo que un regex detecta no se le pide al modelo."""
        for m in re.findall(r"\bu\d{3}\b", texto_usuario):
            self.estado["usuario_id"] = m
        for m in re.findall(r"\bPAY-\d{8}\b", texto_usuario, re.I):
            if m.upper() not in self.estado["folios"]:
                self.estado["folios"].append(m.upper())
        m = re.search(r"(presupuesto|máximo|maximo|no más de)\D{0,15}(\d{2,6})\s*(pesos|mxn|\$)?", texto_usuario, re.I)
        if m:
            c = f"presupuesto máximo {m.group(2)} pesos"
            if c not in self.estado["constraints"]:
                self.estado["constraints"].append(c)
        for r in resultados_tools:
            self.estado["completed_steps"].append(r["nombre"])
            if r["nombre"] == "consultar_plan" and "plan" in r["resultado"]:
                self.estado["important_facts"]["plan"] = r["resultado"]["plan"]
            if r["nombre"] == "consultar_factura" and "monto" in r["resultado"]:
                self.estado["important_facts"][r["args"].get("folio", "?")] = f"{r['resultado'].get('estado')} {r['resultado'].get('monto')}"

    def construir_contexto(self, estrategia: str, ventana: int = 6) -> list[dict]:
        """Devuelve la lista de mensajes (sin el system) que verá el modelo en este turno."""
        if estrategia == "completo":
            return list(self.historial)
        if estrategia == "ventana":
            return list(self.historial[-ventana:])
        # estado estructurado (KEEP) + resumen (COMPRESS) + ventana corta; lo demás no se envía (DROP)
        msgs = []
        bloque = "Estado de la aplicación (fuente de verdad, no lo contradigas):\n" + json.dumps(self.estado, ensure_ascii=False)
        if self.resumen:
            bloque += "\n\nResumen de la conversación previa:\n" + self.resumen
        msgs.append({"role": "user", "content": bloque})
        msgs.append({"role": "assistant", "content": "Entendido. Uso ese estado como referencia."})
        msgs += self.historial[-4:]
        return msgs


# ---- Keep / Compress / Drop (semana 9), nombrados en el código
POLITICA_CONTEXTO = {
    "KEEP": "identificadores (usuario, folios), restricciones (presupuesto), pasos completados y hechos de las tools: textual, en el estado",
    "COMPRESS": "turnos anteriores a la ventana: un resumen (determinista o con LLM) que conserva cifras, folios y decisiones",
    "DROP": "el resto del historial viejo: no se envía al modelo; la aplicación lo guarda",
}

INSTRUCCIONES_COMPRESOR = (
    "Resume la conversación de soporte en no más de seis líneas para que otro asistente pueda continuarla. "
    "Conserva textualmente identificadores (usuario, folios PAY-), montos, plazos, restricciones del cliente "
    "(por ejemplo un presupuesto máximo) y decisiones tomadas. Omite saludos y repeticiones. No inventes nada."
)


def comprimir_con_llm(mensajes: list[dict], effort: str | None = None) -> tuple[str, dict]:
    """COMPRESS con el modelo: una llamada extra que también cuesta. Devuelve (resumen, uso)."""
    client = _cliente()
    transcripcion = "\n".join(f"{m['role']}: {m['content']}" for m in mensajes)
    t0 = time.perf_counter()
    resp = client.responses.create(model=MODEL, instructions=INSTRUCCIONES_COMPRESOR, input=transcripcion,
                                   max_output_tokens=400, store=False, **_reasoning(effort or "minimal"))
    u = resp.usage
    return resp.output_text.strip(), {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                                      "latencia_s": round(time.perf_counter() - t0, 2)}


def comprimir_determinista(mensajes: list[dict]) -> str:
    """COMPRESS sin modelo: una línea por turno del usuario, recortada. Gratis y claramente lossy."""
    return "; ".join(m["content"][:80] for m in mensajes if m["role"] == "user")[:600]


SESIONES: dict[str, Sesion] = {}


def contar_tokens(texto: str) -> int:
    return int(len(texto) / 3.5) + 1


# ---------------------------------------------------------------- el ciclo de tool calling (semana 8)
def _cliente():
    from openai import OpenAI
    return OpenAI()   # lee OPENAI_API_KEY del .env


EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")


def _reasoning(effort: str | None = None):
    if not MODEL.startswith(("gpt-5", "o1", "o3", "o4")):
        return {}
    r: dict[str, Any] = {"effort": effort or REASONING_EFFORT}
    if REASONING_SUMMARY:
        r["summary"] = REASONING_SUMMARY
    return {"reasoning": r}


def _resumenes_de_razonamiento(resp) -> list[str]:
    out = []
    for it in resp.output:
        if getattr(it, "type", "") == "reasoning":
            for s in (it.summary or []):
                out.append(getattr(s, "text", str(s)))
    return out


def _costo(model: str, tin: int, tout: int) -> float:
    pi, po = PRECIOS_USD_POR_MILLON.get(model, (1.0, 4.0))
    return (tin * pi + tout * po) / 1e6


COMPRESORES = ("llm", "determinista")


MOTORES = ("manual", "sdk")


def _preparar(sesion: Sesion, texto: str, estrategia: str, usar_routing: bool, autorizar_reembolsos: bool, motor: str):
    """Pasos 1 y 2 del turno, iguales para los dos motores: routing y contexto son de la aplicación."""
    trace: list[dict] = []
    # 1) routing determinista: decide el especialista antes de gastar una llamada
    ruta = ruta_determinista(texto) if usar_routing else "general"
    instrucciones, permitidas = ESPECIALISTAS[ruta]
    if ruta != "general":
        instrucciones = INSTRUCCIONES_BASE + " " + instrucciones
    # Primera capa de autorización: lo que el modelo no ve, no lo puede pedir ni prometer.
    # Motor manual: con los side effects automáticos apagados, las tools con side_effect salen de la lista.
    # Motor SDK: siguen visibles, pero needs_approval pausa la corrida y una persona decide (otra política válida).
    if not autorizar_reembolsos and motor == "manual":
        permitidas = [n for n in permitidas if not ft.TOOLS[n]["side_effect"]]
        instrucciones += (" En este momento no puedes ejecutar acciones (reembolsos, escalaciones); si el cliente las necesita, "
                          "explícale que una persona del equipo las atenderá y no ofrezcas ejecutarlas tú.")
    trace.append({"tipo": "routing", "ruta": ruta, "tools_visibles": permitidas, "regla": "regex sobre el mensaje" if usar_routing else "desactivado",
                  "side_effects_automaticos": autorizar_reembolsos, "motor": motor})
    # 2) contexto: la aplicación decide qué ve el modelo (en los dos motores)
    sesion.historial.append({"role": "user", "content": texto})
    # KEEP sobre el mensaje actual, antes del loop: si el cliente dice "soy u001" en este mismo turno, la
    # autorización ya tiene el usuario de la sesión (las reglas son deterministas y repetirlas al cerrar no duplica nada).
    sesion.actualizar_estado(texto, [])
    contexto = sesion.construir_contexto(estrategia)
    tokens_ctx = sum(contar_tokens(m["content"]) for m in contexto)
    trace.append({"tipo": "contexto", "estrategia": estrategia, "mensajes": len(contexto), "tokens_aprox": tokens_ctx})
    return ruta, instrucciones, permitidas, contexto, trace


def _motor_manual(sesion: Sesion, instrucciones: str, permitidas: list[str], contexto: list[dict], autorizar_reembolsos: bool,
                  max_vueltas: int, effort: str) -> dict:
    """El loop a mano (semana 8): llamada -> tool calls -> ejecutar -> devolver -> llamada ... hasta que no pida tools."""
    client = _cliente()
    tools = [d for d in ft.tools_para_openai() if d["name"] in permitidas]
    trace: list[dict] = []
    t0_total = time.perf_counter()
    entrada: Any = contexto
    previo = None
    resultados_tools: list[dict] = []
    total_in = total_out = total_reason = 0
    texto_final = ""
    resumenes: list[dict] = []   # uno por vuelta: resumen del razonamiento (si el proveedor lo devolvió)
    for vuelta in range(1, max_vueltas + 1):
        t0 = time.perf_counter()
        resp = client.responses.create(model=MODEL, instructions=instrucciones, input=entrada, tools=tools,
                                       previous_response_id=previo, max_output_tokens=600, store=True, **_reasoning(effort))
        dt = time.perf_counter() - t0
        u = resp.usage
        rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        total_in += u.input_tokens; total_out += u.output_tokens; total_reason += rt
        llamadas = [o for o in resp.output if getattr(o, "type", "") == "function_call"]
        resumenes.append({"vuelta": vuelta, "reasoning_tokens": rt, "pide_tools": [c.name for c in llamadas], "resumen": _resumenes_de_razonamiento(resp)})
        trace.append({"tipo": "modelo", "vuelta": vuelta, "latencia_s": round(dt, 2), "input_tokens": u.input_tokens,
                      "output_tokens": u.output_tokens, "reasoning_tokens": rt, "status": resp.status,
                      "pide_tools": [c.name for c in llamadas]})
        if resp.status == "incomplete":
            trace.append({"tipo": "aviso", "mensaje": f"respuesta incompleta: {getattr(resp.incomplete_details, 'reason', None)}"})
        if not llamadas:            # stop condition 1: el modelo respondió sin pedir tools
            texto_final = resp.output_text
            break
        previo = resp.id
        salidas = []
        for c in llamadas:
            args = json.loads(c.arguments or "{}")
            paso = {"tipo": "tool", "nombre": c.name, "args": args}
            # Regla general de la aplicación, en un solo lugar: toda tool declarada con side_effect
            # se bloquea mientras los side effects automáticos estén apagados. Una tool nueva marcada
            # con side_effect=True queda protegida sin tocar este código. La política específica
            # (plazos, montos, duplicados, dueño del folio) vive dentro de cada función, como autorizar_reembolso.
            tiene_side_effect = ft.TOOLS.get(c.name, {}).get("side_effect", True)   # desconocida: se trata como peligrosa
            if tiene_side_effect and not autorizar_reembolsos:
                resultado = {"ejecutado": False, "razon": f"{c.name} tiene side effect y la aplicación tiene apagados los side effects automáticos; se requiere una persona"}
                paso["decision"] = "bloqueada por la aplicación (side effect)"
            else:
                t1 = time.perf_counter()
                # El usuario de la sesión lo pone la aplicación, nunca el modelo: la autorización lo usa
                # para rechazar folios ajenos. En producción vendría del login; aquí, del estado.
                if c.name == "reembolsar":
                    args = {**args, "_usuario_sesion": sesion.estado.get("usuario_id")}
                resultado = ft.ejecutar_tool(c.name, args)
                paso["decision"] = "ejecutada"
                paso["latencia_s"] = round(time.perf_counter() - t1, 3)
            paso["resultado"] = resultado
            trace.append(paso)
            resultados_tools.append({"nombre": c.name, "args": args, "resultado": resultado})
            salidas.append({"type": "function_call_output", "call_id": c.call_id, "output": json.dumps(resultado, ensure_ascii=False)})
        entrada = salidas
    else:                           # stop condition 2: límite de vueltas; el código toma el control
        texto_final = texto_final or "No pude completar la solicitud en el número máximo de pasos; una persona la revisará."
        trace.append({"tipo": "aviso", "mensaje": f"límite de {max_vueltas} vueltas alcanzado"})
    return {"texto_final": texto_final, "trace": trace, "resultados_tools": resultados_tools, "resumenes": resumenes,
            "total_in": total_in, "total_out": total_out, "total_reason": total_reason,
            "latencia_s": round(time.perf_counter() - t0_total, 2), "pendiente": None}


def _cerrar(sesion: Sesion, texto: str, estrategia: str, effort: str, compresor: str, salida: dict, trace: list[dict]):
    """Paso 4, igual para los dos motores: historial, estado y compresión son de la aplicación."""
    total_in, total_out = salida["total_in"], salida["total_out"]
    sesion.historial.append({"role": "assistant", "content": salida["texto_final"]})
    sesion.actualizar_estado(texto, salida["resultados_tools"])
    # COMPRESS: cuando el historial supera el umbral, lo anterior a la ventana se resume una vez
    # (y se vuelve a resumir cada UMBRAL_COMPRESION mensajes nuevos). Con COMPRESOR=llm es una llamada más.
    if estrategia == "estado" and len(sesion.historial) >= UMBRAL_COMPRESION and (len(sesion.historial) - UMBRAL_COMPRESION) % UMBRAL_COMPRESION == 0:
        viejos = sesion.historial[:-4]
        if compresor == "llm":
            sesion.resumen, uso_c = comprimir_con_llm(viejos, effort)
            total_in += uso_c["input_tokens"]; total_out += uso_c["output_tokens"]
            trace.append({"tipo": "compresion", "compresor": "llm", "mensajes_resumidos": len(viejos), **uso_c, "resumen": sesion.resumen})
        else:
            sesion.resumen = comprimir_determinista(viejos)
            trace.append({"tipo": "compresion", "compresor": "determinista", "mensajes_resumidos": len(viejos),
                          "input_tokens": 0, "output_tokens": 0, "latencia_s": 0.0, "resumen": sesion.resumen})
    sesion.tokens_acumulados += total_in + total_out
    return total_in, total_out


def _respuesta(sesion: Sesion, salida: dict, trace: list[dict], contexto: list[dict], ruta: str, effort: str, compresor: str,
               motor: str, total_in: int, total_out: int) -> dict:
    return {
        "respuesta": salida["texto_final"], "ruta": ruta, "trace": trace, "motor": motor,
        "contexto_enviado": contexto, "estado": sesion.estado, "resumen": sesion.resumen,
        "uso": {"input_tokens": total_in, "output_tokens": total_out, "reasoning_tokens": salida["total_reason"],
                "costo_usd": round(_costo(MODEL, total_in, total_out), 6), "latencia_s": salida["latencia_s"],
                "tokens_sesion": sesion.tokens_acumulados},
        "razonamiento": salida["resumenes"], "modelo": MODEL, "effort": effort, "compresor": compresor,
        "aprobacion_pendiente": salida["pendiente"]["items"] if salida["pendiente"] else None,
    }


def responder(sesion: Sesion, texto: str, estrategia: str, usar_routing: bool, autorizar_reembolsos: bool,
              max_vueltas: int = 6, effort: str | None = None, compresor: str | None = None, motor: str = "manual") -> dict:
    effort = effort if effort in EFFORTS else REASONING_EFFORT
    compresor = compresor if compresor in COMPRESORES else COMPRESOR
    motor = motor if motor in MOTORES else "manual"
    ruta, instrucciones, permitidas, contexto, trace = _preparar(sesion, texto, estrategia, usar_routing, autorizar_reembolsos, motor)
    # 3) el loop: a mano, o el Runner del Agents SDK con las mismas tools y el mismo contexto
    if motor == "sdk":
        import motor_sdk
        agente = motor_sdk.construir_agente(instrucciones, permitidas, MODEL, effort, REASONING_SUMMARY)
        contexto_app = {"usuario_id": sesion.estado.get("usuario_id"), "side_effects_automaticos": autorizar_reembolsos}
        salida = motor_sdk.correr(agente, contexto, contexto_app)
        if salida["pendiente"]:
            # El turno queda abierto: la aplicación guarda el estado del SDK y espera a la persona (POST /aprobar).
            sesion.pendiente = {"agente": agente, "estado_sdk": salida["pendiente"]["estado"], "items": salida["pendiente"]["items"],
                                "trace": trace + salida["trace"], "texto": texto, "estrategia": estrategia, "effort": effort,
                                "compresor": compresor, "contexto": contexto, "ruta": ruta, "contexto_app": contexto_app}
            return _respuesta(sesion, salida, trace + salida["trace"], contexto, ruta, effort, compresor, motor, salida["total_in"], salida["total_out"])
    else:
        salida = _motor_manual(sesion, instrucciones, permitidas, contexto, autorizar_reembolsos, max_vueltas, effort)
    trace += salida["trace"]
    # 4) cerrar el turno: el historial completo lo guarda la aplicación, siempre
    total_in, total_out = _cerrar(sesion, texto, estrategia, effort, compresor, salida, trace)
    return _respuesta(sesion, salida, trace, contexto, ruta, effort, compresor, motor, total_in, total_out)


def decidir_aprobacion(sesion: Sesion, aprobar: bool) -> dict:
    """Human-in-the-loop: una persona decide y el SDK reanuda desde el estado guardado."""
    import motor_sdk
    p = sesion.pendiente
    if not p:
        return {"error": "no hay ninguna aprobación pendiente en esta sesión (si acabas de decidir, la decisión ya se está procesando)"}
    sesion.pendiente = None
    salida = motor_sdk.reanudar(p["agente"], {"estado": p["estado_sdk"], "items": p["items"]}, aprobar, p["contexto_app"], [])
    trace = p["trace"] + salida["trace"]
    # el turno completo (antes y después de la pausa) se numera y se cobra junto
    for i, e in enumerate(e for e in trace if e["tipo"] == "modelo"):
        e["vuelta"] = i + 1
    salida["total_in"] = sum(e["input_tokens"] for e in trace if e["tipo"] == "modelo")
    salida["total_out"] = sum(e["output_tokens"] for e in trace if e["tipo"] == "modelo")
    salida["total_reason"] = sum(e["reasoning_tokens"] for e in trace if e["tipo"] == "modelo")
    salida["resumenes"] = [{"vuelta": e["vuelta"], "reasoning_tokens": e["reasoning_tokens"], "pide_tools": e["pide_tools"], "resumen": e.get("resumen_razonamiento", [])} for e in trace if e["tipo"] == "modelo"]
    if salida["pendiente"]:   # el modelo pidió otra acción con side effect: vuelve a esperar
        sesion.pendiente = {**p, "estado_sdk": salida["pendiente"]["estado"], "items": salida["pendiente"]["items"], "trace": trace}
        return _respuesta(sesion, salida, trace, p["contexto"], p["ruta"], p["effort"], p["compresor"], "sdk", salida["total_in"], salida["total_out"])
    total_in, total_out = _cerrar(sesion, p["texto"], p["estrategia"], p["effort"], p["compresor"], salida, trace)
    return _respuesta(sesion, salida, trace, p["contexto"], p["ruta"], p["effort"], p["compresor"], "sdk", total_in, total_out)


# ---------------------------------------------------------------- HTTP
app = FastAPI(title="Facturio Soporte")


class Mensaje(BaseModel):
    sesion_id: str
    texto: str
    estrategia: Literal["completo", "ventana", "estado"] = "estado"
    routing: bool = True
    autorizar_reembolsos: bool = False   # permitir side effects automáticos (nombre histórico)
    effort: Optional[str] = None     # none | minimal | low | medium | high | xhigh; None usa REASONING_EFFORT
    compresor: Optional[str] = None  # llm | determinista; None usa COMPRESOR
    motor: Literal["manual", "sdk"] = "manual"   # quién corre el loop: app.py o el Agents SDK (semana 10)


@app.get("/", response_class=HTMLResponse)
def index():
    return (AQUI / "index.html").read_text(encoding="utf-8")


@app.get("/config")
def config():
    return {"modelo": MODEL, "effort": REASONING_EFFORT, "efforts": list(EFFORTS), "summary": REASONING_SUMMARY,
            "compresor": COMPRESOR, "compresores": list(COMPRESORES), "motores": list(MOTORES), "umbral_compresion": UMBRAL_COMPRESION, "politica_contexto": POLITICA_CONTEXTO,
            "tools": [{"nombre": n, "side_effect": t["side_effect"], "descripcion": t["descripcion"]} for n, t in ft.TOOLS.items()]}


@app.post("/chat")
def chat(m: Mensaje):
    sesion = SESIONES.setdefault(m.sesion_id, Sesion())
    try:
        return responder(sesion, m.texto, m.estrategia, m.routing, m.autorizar_reembolsos, effort=m.effort, compresor=m.compresor, motor=m.motor)
    except Exception as e:                      # el error llega al panel, nunca se oculta
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {e}"})


@app.post("/chat/stream")
async def chat_stream(m: Mensaje):
    """El mismo turno con el motor SDK, pero como Server-Sent Events: un evento por delta de texto, por tool
    pedida y por tool devuelta, y al final el mismo JSON que devuelve POST /chat. Es el contrato que usaría
    una interfaz que "escribe" la respuesta conforme llega; el estado, el trace y la pausa son los mismos."""
    import motor_sdk
    sesion = SESIONES.setdefault(m.sesion_id, Sesion())
    effort = m.effort if m.effort in EFFORTS else REASONING_EFFORT
    compresor = m.compresor if m.compresor in COMPRESORES else COMPRESOR
    ruta, instrucciones, permitidas, contexto, trace = _preparar(sesion, m.texto, m.estrategia, m.routing, m.autorizar_reembolsos, "sdk")
    agente = motor_sdk.construir_agente(instrucciones, permitidas, MODEL, effort, REASONING_SUMMARY)
    contexto_app = {"usuario_id": sesion.estado.get("usuario_id"), "side_effects_automaticos": m.autorizar_reembolsos}

    async def eventos():
        def sse(d): return f"data: {json.dumps(d, ensure_ascii=False)}\n\n"
        try:
            async for ev in motor_sdk.correr_stream(agente, contexto, contexto_app):
                if ev["tipo"] != "final":
                    yield sse(ev)
                    continue
                salida = ev["paquete"]
                if salida["pendiente"]:
                    sesion.pendiente = {"agente": agente, "estado_sdk": salida["pendiente"]["estado"], "items": salida["pendiente"]["items"],
                                        "trace": trace + salida["trace"], "texto": m.texto, "estrategia": m.estrategia, "effort": effort,
                                        "compresor": compresor, "contexto": contexto, "ruta": ruta, "contexto_app": contexto_app}
                    yield sse({"tipo": "final", **_respuesta(sesion, salida, trace + salida["trace"], contexto, ruta, effort, compresor, "sdk", salida["total_in"], salida["total_out"])})
                    return
                tr = trace + salida["trace"]
                total_in, total_out = _cerrar(sesion, m.texto, m.estrategia, effort, compresor, salida, tr)
                yield sse({"tipo": "final", **_respuesta(sesion, salida, tr, contexto, ruta, effort, compresor, "sdk", total_in, total_out)})
        except Exception as e:
            yield sse({"tipo": "final", "error": f"{type(e).__name__}: {e}"})

    return StreamingResponse(eventos(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/aprobar")
def aprobar(sesion_id: str, decision: bool):
    """La persona aprueba o rechaza la acción pausada por el motor SDK; la corrida se reanuda desde el estado."""
    sesion = SESIONES.get(sesion_id)
    if not sesion:
        return JSONResponse(status_code=404, content={"error": "sesión desconocida"})
    try:
        return decidir_aprobacion(sesion, decision)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {e}"})


@app.post("/reiniciar")
def reiniciar(sesion_id: str):
    SESIONES.pop(sesion_id, None)
    ft.reiniciar_estado()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    print(f"Facturio Soporte en http://localhost:{os.environ.get('PORT', '8011')}  | modelo {MODEL} | effort {REASONING_EFFORT}")
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8011")), log_level="warning")
