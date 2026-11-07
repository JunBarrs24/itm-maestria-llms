"""Motor Agents SDK: el mismo turno de soporte, pero el loop lo corre el runtime de OpenAI.

Cada abstracción del SDK sustituye algo que app.py ya hace a mano:

    Agent            <- instrucciones + lista de tools del especialista (responder, paso 1)
    Runner.run       <- el `for vuelta in range(...)` de _motor_manual
    max_turns        <- max_vueltas: la stop condition por límite
    function_tool    <- tools_para_openai() + ejecutar_tool: la firma se vuelve schema; el cuerpo es la función de negocio
    needs_approval   <- el bloqueo por side_effect, pero pausando la corrida en vez de negarla
    RunContextWrapper<- lo que la aplicación inyecta (usuario de la sesión) sin pasar por el modelo
    input_guardrail  <- una validación antes de gastar la primera llamada
    TracingProcessor <- la lista `trace` que la interfaz pinta

Lo que sigue siendo de la aplicación: el routing, la política de contexto (el SDK recibe la misma
lista de mensajes que el motor manual), la autorización de negocio dentro de cada tool y la
decisión de aprobar o rechazar. El SDK pone el loop, los nombres y los defaults.
"""
from __future__ import annotations

import asyncio
import json
import queue
import re
import threading
import time
import uuid
from datetime import datetime
from typing import Any

from agents import (Agent, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, MaxTurnsExceeded, ModelSettings,
                    RunContextWrapper, Runner, function_tool, input_guardrail, trace)
from agents.tracing import TracingProcessor, add_trace_processor, gen_trace_id
from openai.types.shared import Reasoning

import facturio_tools as ft

MAX_TURNS = 6   # la misma stop condition que max_vueltas en el motor manual (una consulta con tools suele usar 2 a 4)

# Un solo event loop para todo el SDK, en un hilo propio. El cliente asíncrono de OpenAI que el SDK crea
# queda atado al loop donde se usó por primera vez; si cada petición abriera y cerrara un loop con
# asyncio.run, la siguiente (un follow-up, una aprobación) fallaría con "Event loop is closed".
_LOOP = asyncio.new_event_loop()
threading.Thread(target=_LOOP.run_forever, name="agents-sdk-loop", daemon=True).start()


def _en_el_loop(coro):
    """Ejecuta una corrutina en el loop del SDK y espera el resultado (desde código síncrono)."""
    return asyncio.run_coroutine_threadsafe(coro, _LOOP).result()



# ---------------------------------------------------------------- tools: la firma se vuelve schema
# Son funciones de Python normales. El decorador lee la firma (tipos) y el docstring y con eso arma el
# schema que ve el modelo; cuando el modelo la pide, el SDK parsea los argumentos, llama a la función y
# devuelve el resultado. El cuerpo es el mismo código de negocio de shared/facturio_tools.py, aquí a la
# vista, sobre los mismos datos (ft.CARGOS, ft.USUARIOS, el corpus). El motor manual pasa por
# ft.ejecutar_tool (validación Pydantic, timeout, reintentos); aquí esas tres cosas las pone el SDK o no están.
# `ctx.context` es el diccionario que la aplicación pasa a Runner.run: datos que el modelo no controla.

def progreso(texto: str):
    """Lo que el cliente ve mientras la tool corre (streaming). Lo escribe quien conoce al cliente, en la
    tool misma, igual que el docstring describe la tool al modelo. El nombre técnico se queda en el trace."""
    def decorar(tool):
        tool.progreso = texto
        return tool
    return decorar


def _requiere_aprobacion(ctx: RunContextWrapper[dict], params: dict, call_id: str) -> bool:
    """La regla general de la aplicación, en el SDK: con los side effects automáticos apagados,
    toda tool con side effect se detiene y espera a una persona."""
    return not ctx.context.get("side_effects_automaticos", False)


@progreso("Revisando el cargo…")
@function_tool
def consultar_factura(folio: str) -> dict:
    """Consulta un cargo de suscripción por folio.

    Úsala cuando el cliente mencione un cargo, un cobro, un folio o un reembolso: antes de opinar
    sobre un cargo hay que verlo. No la uses para preguntas de política (para eso está
    buscar_documentacion). Devuelve monto, fecha, concepto, estado, usuario dueño y días desde el cargo.

    Args:
        folio: Folio del cargo, formato PAY- seguido de 8 dígitos, por ejemplo PAY-00012345.
    """
    if not re.fullmatch(r"PAY-\d{8}", folio):
        return {"error": "folio inválido: el formato es PAY- seguido de 8 dígitos"}
    c = ft.CARGOS.get(folio)
    if not c:
        return {"error": f"no existe el folio {folio}"}
    return {"folio": folio, "usuario": c["usuario"], "monto": c["monto"], "fecha": c["fecha"].isoformat(),
            "concepto": c["concepto"], "facturas_timbradas_periodo": c["facturas_timbradas_periodo"],
            "estado": c["estado"], "dias_desde_el_cargo": (ft.HOY - c["fecha"]).days,
            **({"duplicado_de": c["duplicado_de"],
                "politica": "cargo duplicado: la reversión es automática en 5 días hábiles sin solicitud; "
                            "si no se refleja, abrir ticket con el folio"} if "duplicado_de" in c else {})}


@progreso("Consultando tu plan…")
@function_tool
def consultar_plan(usuario_id: str) -> dict:
    """Consulta el plan contratado de un usuario y su uso del mes.

    Úsala cuando la pregunta sea sobre plan, límites, facturas emitidas, proyectos o precio.
    Devuelve plan, límites del plan, uso actual y si ya recibió un reembolso en los últimos 12 meses.

    Args:
        usuario_id: Identificador del usuario, formato u seguido de 3 dígitos, por ejemplo u002.
    """
    u = ft.USUARIOS.get(usuario_id)
    if not u:
        return {"error": f"no existe el usuario {usuario_id}"}
    lim = ft.LIMITES_PLAN[u["plan"]]
    return {"usuario_id": usuario_id, "nombre": u["nombre"], "plan": u["plan"], "limites": lim,
            "uso": {"facturas_mes": u["facturas_mes"], "proyectos": u["proyectos"]},
            "reembolso_ultimos_12m": u["reembolso_ultimos_12m"], **({"descuento": u["descuento"]} if "descuento" in u else {})}


# Alternativa, solo en esta tool y comentada: que el mensaje de progreso lo escriba el modelo. Se agrega un
# argumento que el modelo tiene que llenar y el productor del streaming lo manda al cliente en lugar del texto
# fijo. Cuesta tokens de salida en cada llamada y es texto generado (hay que validarlo antes de mostrarlo);
# vale la pena solo cuando el progreso depende del caso y una frase fija no alcanza.
#
# @function_tool
# def buscar_documentacion(pregunta: str, aviso_para_el_cliente: str) -> dict:
#     """Busca en la documentación y políticas de Facturio.
#
#     Args:
#         pregunta: La duda en lenguaje natural.
#         aviso_para_el_cliente: Una frase corta, en segunda persona, que el cliente verá mientras buscas,
#             por ejemplo "Estoy revisando el plazo de reembolso en la política".
#     """
#     ...   # mismo cuerpo; en el productor: mensaje = json.loads(ev.item.raw_item.arguments).get("aviso_para_el_cliente")
@progreso("Buscando en las políticas de Facturio…")
@function_tool
def buscar_documentacion(pregunta: str) -> dict:
    """Busca en la documentación y políticas de Facturio.

    Úsala para plazos, límites, procedimientos y errores del producto. Consúltala antes de afirmar
    una política (por ejemplo, el plazo para pedir un reembolso); no respondas políticas de memoria.
    Devuelve hasta tres fragmentos con archivo, sección y score.

    Args:
        pregunta: La duda en lenguaje natural, con las palabras clave del cliente, por ejemplo
            "plazo para solicitar reembolso".
    """
    ft.preparar_corpus()                                   # chunks por sección y embeddings, una vez
    v = ft._embed([pregunta])[0]
    scores = [sum(a * b for a, b in zip(e, v)) for e in ft._EMB]
    idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:3]
    return {"fragmentos": [{"archivo": ft._CORPUS[i]["archivo"], "seccion": ft._CORPUS[i]["seccion"],
                            "texto": ft._CORPUS[i]["texto"][:600], "score": round(scores[i], 3)} for i in idx]}


@progreso("Solicitando el reembolso…")
@function_tool(needs_approval=_requiere_aprobacion)
def reembolsar(ctx: RunContextWrapper[dict], folio: str, monto: float, motivo: str) -> dict:
    """Solicita el reembolso de un cargo. Tiene side effect: mueve dinero.

    Llámala solo después de consultar_factura y cuando el cliente la haya pedido de forma explícita.
    La aplicación aplica su política (dueño del folio, plazo, monto, duplicados, límite que exige
    persona) y puede rechazarla: si devuelve ejecutado=false, explica la razón y no lo intentes de nuevo.

    Args:
        folio: Folio del cargo verificado, formato PAY- seguido de 8 dígitos.
        monto: Monto a reembolsar en pesos, mayor que cero y no mayor que el cargo.
        motivo: Razón del cliente en una frase, por ejemplo "cobro duplicado".
    """
    # la política de negocio (dueño, plazo, duplicado, monto, límite) sigue en un solo lugar
    ok, razon = ft.autorizar_reembolso(folio, monto, ctx.context.get("usuario_id"))
    if not ok:
        return {"ejecutado": False, "razon": razon}
    ref = f"REF-{uuid.uuid4().hex[:8].upper()}"
    ft.REEMBOLSOS[folio] = {"referencia": ref, "monto": monto, "motivo": motivo, "fecha": ft.HOY.isoformat()}
    ft.USUARIOS[ft.CARGOS[folio]["usuario"]]["reembolso_ultimos_12m"] = True
    return {"ejecutado": True, "referencia": ref, "monto": monto, "abono_en": "5 a 10 días hábiles"}


@progreso("Pasando tu caso a una persona del equipo…")
@function_tool(needs_approval=_requiere_aprobacion)
def escalar_a_humano(motivo: str) -> dict:
    """Pasa el caso a una persona del equipo.

    Úsala cuando la política lo exija (montos altos, folios de otra cuenta, casos sin documentación)
    o cuando falte información que ninguna tool pueda dar. Crea un ticket y lo devuelve.

    Args:
        motivo: Qué necesita la persona para atenderlo, con el folio y el usuario si los hay.
    """
    t = {"ticket": f"HUM-{len(ft.TICKETS_HUMANOS) + 1:04d}", "motivo": motivo}
    ft.TICKETS_HUMANOS.append(t)
    return t


TOOLS_SDK = {t.name: t for t in (consultar_factura, consultar_plan, buscar_documentacion, reembolsar, escalar_a_humano)}


# ---------------------------------------------------------------- guardrail de entrada
FUERA_DE_SOPORTE = ("poema", "receta", "clima", "fútbol", "futbol", "chiste", "tarea de matemáticas", "canción")


@input_guardrail
async def solo_soporte(ctx, agent, entrada) -> GuardrailFunctionOutput:
    """Determinista y verificable: si la pregunta no es de soporte, la corrida se corta antes del modelo."""
    texto = entrada if isinstance(entrada, str) else json.dumps(entrada, ensure_ascii=False)
    ultimo = texto if isinstance(entrada, str) else next((m.get("content", "") for m in reversed(entrada) if m.get("role") == "user"), "")
    fuera = any(k in str(ultimo).lower() for k in FUERA_DE_SOPORTE)
    return GuardrailFunctionOutput(output_info={"fuera_de_soporte": fuera}, tripwire_triggered=fuera)


# ---------------------------------------------------------------- tracing: los spans del SDK, en el formato del trace de la app
def _segundos(span) -> float:
    try:
        return (datetime.fromisoformat(span.ended_at) - datetime.fromisoformat(span.started_at)).total_seconds()
    except Exception:
        return 0.0


class TraceParaLaApp(TracingProcessor):
    """Recibe cada span cerrado y guarda, por trace_id, las entradas que la interfaz ya sabe pintar."""

    def __init__(self):
        self.por_trace: dict[str, list[dict]] = {}

    def on_trace_start(self, t): self.por_trace.setdefault(t.trace_id, [])
    def on_trace_end(self, t): pass
    def on_span_start(self, span): pass
    def force_flush(self): pass
    def shutdown(self): pass

    def on_span_end(self, span):
        d = span.span_data
        entradas = self.por_trace.setdefault(span.trace_id, [])
        if d.type in ("response", "generation"):
            # Con Responses API el SDK emite spans "response" (traen el objeto Response completo);
            # con Chat Completions emite "generation" (traen input/output/usage como diccionarios).
            if d.type == "response":
                r = d.response
                if r is None:
                    return
                u = r.usage
                salida = [o.model_dump() for o in r.output]
                rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
                tin, tout = u.input_tokens, u.output_tokens
            else:
                u = d.usage or {}
                salida = list(d.output or [])
                rt = (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0) if isinstance(u.get("output_tokens_details"), dict) else 0
                tin, tout = u.get("input_tokens", 0), u.get("output_tokens", 0)
            pide = [o.get("name") for o in salida if o.get("type") == "function_call"]
            resumen = [s.get("text", "") for o in salida if o.get("type") == "reasoning" for s in (o.get("summary") or [])]
            n = 1 + sum(1 for e in entradas if e["tipo"] == "modelo")
            entradas.append({"tipo": "modelo", "vuelta": n, "latencia_s": round(_segundos(span), 2), "input_tokens": tin,
                             "output_tokens": tout, "reasoning_tokens": rt, "status": "sdk",
                             "pide_tools": pide, "resumen_razonamiento": resumen})
        elif d.type == "function":
            if d.output is None:
                return   # tool pendiente de aprobación: el SDK abre el span y no la ejecuta; se registra abajo como pausada
            try: args = json.loads(d.input or "{}")
            except Exception: args = {"raw": d.input}
            res = d.output
            if isinstance(res, str):
                try: res = json.loads(res)
                except Exception: pass
            entradas.append({"tipo": "tool", "nombre": d.name, "args": args, "decision": "ejecutada por el SDK",
                             "latencia_s": round(_segundos(span), 3), "resultado": res})
        elif d.type == "guardrail":
            entradas.append({"tipo": "guardrail", "nombre": d.name, "disparado": bool(d.triggered)})

    def tomar(self, trace_id: str) -> list[dict]:
        return self.por_trace.pop(trace_id, [])


PROCESADOR = TraceParaLaApp()
add_trace_processor(PROCESADOR)   # se suma al exportador de OpenAI: el mismo trace se ve en el dashboard


# ---------------------------------------------------------------- el motor
def construir_agente(instrucciones: str, permitidas: list[str], model: str, effort: str, summary: str) -> Agent:
    ajustes = ModelSettings(max_tokens=3000, reasoning=Reasoning(effort=effort, summary=summary or None) if model.startswith("gpt-5") else None)
    return Agent(name="Soporte Facturio", instructions=instrucciones, tools=[TOOLS_SDK[n] for n in permitidas if n in TOOLS_SDK],
                 model=model, model_settings=ajustes, input_guardrails=[solo_soporte])


def _totales(entradas: list[dict]) -> dict:
    return {"total_in": sum(e.get("input_tokens", 0) for e in entradas if e["tipo"] == "modelo"),
            "total_out": sum(e.get("output_tokens", 0) for e in entradas if e["tipo"] == "modelo"),
            "total_reason": sum(e.get("reasoning_tokens", 0) for e in entradas if e["tipo"] == "modelo")}


def _empaquetar(resultado, trace_id: str, t0: float, pendiente_previo: list[dict] | None = None) -> dict:
    """Convierte el RunResult (o la interrupción) en lo que responder() espera de un motor."""
    entradas = (pendiente_previo or []) + PROCESADOR.tomar(trace_id)
    for it in list(getattr(resultado, "interruptions", None) or []):
        # el SDK abre un span de function para la tool pendiente sin ejecutarla: se quita del trace
        for e in reversed(entradas):
            if e["tipo"] == "tool" and e["nombre"] == it.tool_name and e.get("latencia_s", 1) == 0.0:
                entradas.remove(e); break
    # los totales salen del trace (y no de context_wrapper.usage) para que una corrida reanudada sume lo anterior
    paquete = {"trace": entradas, **_totales(entradas),
               "resultados_tools": [{"nombre": e["nombre"], "args": e["args"], "resultado": e["resultado"]} for e in entradas if e["tipo"] == "tool"],
               "resumenes": [{"vuelta": e["vuelta"], "reasoning_tokens": e["reasoning_tokens"], "pide_tools": e["pide_tools"], "resumen": e.get("resumen_razonamiento", [])}
                             for e in entradas if e["tipo"] == "modelo"],
               "latencia_s": round(time.perf_counter() - t0, 2), "texto_final": "", "pendiente": None}
    for i, e in enumerate(e for e in entradas if e["tipo"] == "modelo"):
        e["vuelta"] = i + 1      # una corrida reanudada sigue la numeración
    interrupciones = list(getattr(resultado, "interruptions", None) or [])
    if interrupciones:
        # El SDK se detuvo antes de ejecutar: la aplicación decide y reanuda desde el estado.
        items = [{"tool": it.tool_name, "args": json.loads(it.raw_item.arguments or "{}"), "call_id": it.raw_item.call_id} for it in interrupciones]
        for it in items:
            entradas.append({"tipo": "tool", "nombre": it["tool"], "args": it["args"], "decision": "pausada por el SDK: espera aprobación humana", "resultado": {"ejecutado": False, "razon": "needs_approval"}})
        paquete["pendiente"] = {"estado": resultado.to_state(), "items": items}
        paquete["texto_final"] = "Antes de ejecutar " + ", ".join(f"{i['tool']}({json.dumps(i['args'], ensure_ascii=False)})" for i in items) + " hace falta la aprobación de una persona."
    else:
        paquete["texto_final"] = str(resultado.final_output or "")
    return paquete


def correr(agente: Agent, entrada: Any, contexto_app: dict, pendiente_previo: list[dict] | None = None) -> dict:
    """Runner.run con el trace capturado, la stop condition y el guardrail traducidos al formato de la app."""
    tid = gen_trace_id()
    t0 = time.perf_counter()
    async def corrida():
        with trace("Facturio Soporte", trace_id=tid):      # el contexto del trace vive dentro de la corrutina
            return await Runner.run(agente, entrada, context=contexto_app, max_turns=MAX_TURNS)
    try:
        resultado = _en_el_loop(corrida())
        return _empaquetar(resultado, tid, t0, pendiente_previo)
    except InputGuardrailTripwireTriggered as e:
        entradas = (pendiente_previo or []) + PROCESADOR.tomar(tid)
        entradas.append({"tipo": "aviso", "mensaje": f"guardrail de entrada disparado: {e.guardrail_result.output.output_info}; no se llamó al modelo"})
        return {"trace": entradas, "total_in": 0, "total_out": 0, "total_reason": 0, "resultados_tools": [], "resumenes": [],
                "latencia_s": round(time.perf_counter() - t0, 2), "pendiente": None,
                "texto_final": "Esta mesa atiende soporte de Facturio: cargos, planes, acceso y errores del producto."}
    except MaxTurnsExceeded:
        entradas = (pendiente_previo or []) + PROCESADOR.tomar(tid)
        entradas.append({"tipo": "aviso", "mensaje": f"límite de {MAX_TURNS} turnos alcanzado (MaxTurnsExceeded del SDK)"})
        return {"trace": entradas, **_totales(entradas), "resultados_tools": [], "resumenes": [],
                "latencia_s": round(time.perf_counter() - t0, 2), "pendiente": None,
                "texto_final": "No pude completar la solicitud en el número máximo de pasos; una persona la revisará."}


def reanudar(agente: Agent, pendiente: dict, aprobar: bool, contexto_app: dict, trace_previo: list[dict]) -> dict:
    """La decisión es de la aplicación: approve o reject sobre cada interrupción, y el loop continúa desde el estado."""
    estado = pendiente["estado"]
    for it in estado.get_interruptions():
        (estado.approve if aprobar else estado.reject)(it)
    trace_previo = trace_previo + [{"tipo": "aviso", "mensaje": ("aprobado" if aprobar else "rechazado") + " por una persona; el SDK reanuda desde el estado guardado"}]
    return correr(agente, estado, contexto_app, pendiente_previo=trace_previo)


# ---------------------------------------------------------------- streaming (SSE)
async def correr_stream(agente: Agent, entrada: Any, contexto_app: dict):
    """La misma corrida, pero emitiendo eventos conforme ocurren, en vez de un paquete al final.

    Runner.run_streamed devuelve un RunResultStreaming; stream_events() entrega tres tipos de evento:
      raw_response_event      deltas del proveedor (cada fragmento de texto del mensaje final)
      run_item_stream_event   un item completo: tool pedida, tool output, mensaje terminado
      agent_updated_stream_event  cambio de agente (handoffs, semana 12)
    Este generador los traduce a diccionarios pequeños y, al terminar, emite el mismo paquete que
    correr() para que la interfaz pinte los paneles igual que sin streaming.
    """
    tid = gen_trace_id()
    t0 = time.perf_counter()
    cola: queue.Queue = queue.Queue()          # puente entre el loop del SDK y el loop del servidor

    async def productor():
        try:
            with trace("Facturio Soporte", trace_id=tid):
                resultado = Runner.run_streamed(agente, entrada, context=contexto_app, max_turns=MAX_TURNS)
                nombres: dict[str, str] = {}          # call_id -> nombre de la tool, para nombrar el output
                async for ev in resultado.stream_events():
                    if ev.type == "raw_response_event":
                        if getattr(ev.data, "type", "") == "response.output_text.delta":
                            cola.put({"tipo": "delta", "texto": ev.data.delta})
                    elif ev.type == "run_item_stream_event":
                        if ev.name == "tool_called":
                            nombres[getattr(ev.item.raw_item, "call_id", "")] = ev.item.raw_item.name
                            cola.put({"tipo": "item", "evento": "pide tool", "nombre": ev.item.raw_item.name,
                                      "mensaje": getattr(TOOLS_SDK.get(ev.item.raw_item.name), "progreso", None) or "Trabajando en tu solicitud…"})
                        elif ev.name == "tool_output":
                            cid = ev.item.raw_item.get("call_id", "") if isinstance(ev.item.raw_item, dict) else getattr(ev.item.raw_item, "call_id", "")
                            cola.put({"tipo": "item", "evento": "tool devolvió", "nombre": nombres.get(cid, "tool")})
                        elif ev.name == "message_output_created":
                            cola.put({"tipo": "item", "evento": "mensaje completo", "mensaje": "Listo."})
                    elif ev.type == "agent_updated_stream_event":
                        cola.put({"tipo": "item", "evento": "agente", "nombre": ev.new_agent.name})
            cola.put({"tipo": "final", "paquete": _empaquetar(resultado, tid, t0)})
        except BaseException as e:            # la excepción cruza al consumidor por la cola
            cola.put(e)

    asyncio.run_coroutine_threadsafe(productor(), _LOOP)
    propio = asyncio.get_running_loop()
    try:
        while True:
            ev = await propio.run_in_executor(None, cola.get)
            if isinstance(ev, BaseException):
                raise ev
            yield ev
            if ev["tipo"] == "final":
                return
    except InputGuardrailTripwireTriggered as e:
        entradas = PROCESADOR.tomar(tid)
        entradas.append({"tipo": "aviso", "mensaje": f"guardrail de entrada disparado: {e.guardrail_result.output.output_info}; no se llamó al modelo"})
        yield {"tipo": "final", "paquete": {"trace": entradas, "total_in": 0, "total_out": 0, "total_reason": 0, "resultados_tools": [], "resumenes": [],
                                            "latencia_s": round(time.perf_counter() - t0, 2), "pendiente": None,
                                            "texto_final": "Esta mesa atiende soporte de Facturio: cargos, planes, acceso y errores del producto."}}
    except MaxTurnsExceeded:
        entradas = PROCESADOR.tomar(tid)
        entradas.append({"tipo": "aviso", "mensaje": f"límite de {MAX_TURNS} turnos alcanzado (MaxTurnsExceeded del SDK)"})
        yield {"tipo": "final", "paquete": {"trace": entradas, **_totales(entradas), "resultados_tools": [], "resumenes": [],
                                            "latencia_s": round(time.perf_counter() - t0, 2), "pendiente": None,
                                            "texto_final": "No pude completar la solicitud en el número máximo de pasos; una persona la revisará."}}
