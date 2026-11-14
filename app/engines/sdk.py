"""El loop lo corre el Agents SDK. Esta capa lo arranca, lo pausa, lo reanuda y lo traduce.

  correr(agente, entrada, contexto_app)      Runner.run + trace + guardrails + límite, en un paquete
  reanudar(agente, pendiente, aprobar, …)    approve / reject sobre el RunState y Runner.run otra vez
  correr_stream(agente, entrada, contexto)   lo mismo, emitiendo eventos conforme ocurren (SSE)

Un solo event loop para todo el SDK, en un hilo propio: el cliente asíncrono de OpenAI queda atado
al loop donde se usó por primera vez; abrir y cerrar uno por petición rompe el siguiente turno.
"""
from __future__ import annotations

import asyncio
import json
import queue
import threading
import time
from typing import Any

from agents import Agent, InputGuardrailTripwireTriggered, MaxTurnsExceeded, OutputGuardrailTripwireTriggered, Runner, trace
from agents.tracing import gen_trace_id

import config
from engines.tracing import PROCESADOR
from guardrails import input as g_in, output as g_out
from tools.registry import registrar

_LOOP = asyncio.new_event_loop()
threading.Thread(target=_LOOP.run_forever, name="agents-sdk-loop", daemon=True).start()


def _en_el_loop(coro):
    return asyncio.run_coroutine_threadsafe(coro, _LOOP).result()


def _totales(entradas: list[dict]) -> dict:
    m = [e for e in entradas if e["tipo"] == "modelo"]
    return {"total_in": sum(e["input_tokens"] for e in m), "total_out": sum(e["output_tokens"] for e in m),
            "total_reason": sum(e["reasoning_tokens"] for e in m)}


def _paquete(entradas: list[dict], t0: float, texto_final: str, pendiente=None) -> dict:
    for i, e in enumerate(e for e in entradas if e["tipo"] == "modelo"):
        e["vuelta"] = i + 1
    return {"trace": entradas, **_totales(entradas), "texto_final": texto_final, "pendiente": pendiente,
            "resultados_tools": [{"nombre": e["nombre"], "args": e["args"], "resultado": e["resultado"]} for e in entradas if e["tipo"] == "tool"],
            "resumenes": [{"vuelta": e["vuelta"], "reasoning_tokens": e["reasoning_tokens"], "pide_tools": e["pide_tools"], "resumen": e.get("resumen_razonamiento", [])}
                          for e in entradas if e["tipo"] == "modelo"],
            "latencia_s": round(time.perf_counter() - t0, 2)}


def _empaquetar(resultado, trace_id: str, t0: float, previo: list[dict] | None = None) -> dict:
    entradas = (previo or []) + PROCESADOR.tomar(trace_id)
    interrupciones = list(getattr(resultado, "interruptions", None) or [])
    for it in interrupciones:   # el SDK abre un span de function para la tool pendiente sin ejecutarla
        for e in reversed(entradas):
            if e["tipo"] == "tool" and e["nombre"] == it.tool_name and e.get("latencia_s", 1) == 0.0:
                entradas.remove(e); break
    if interrupciones:
        items = [{"tool": it.tool_name, "args": json.loads(it.raw_item.arguments or "{}"), "call_id": it.raw_item.call_id} for it in interrupciones]
        for it in items:
            entradas.append({"tipo": "tool", "nombre": it["tool"], "args": it["args"], "decision": "pausada por el SDK: espera aprobación humana",
                             "resultado": {"ejecutado": False, "razon": "needs_approval"}})
        texto = "Antes de ejecutar " + ", ".join(f"{i['tool']}({json.dumps(i['args'], ensure_ascii=False)})" for i in items) + " hace falta la aprobación de una persona."
        return _paquete(entradas, t0, texto, pendiente={"estado": resultado.to_state(), "items": items})
    return _paquete(entradas, t0, str(resultado.final_output or ""))


def _por_excepcion(e: BaseException, trace_id: str, t0: float, previo: list[dict] | None) -> dict:
    """Guardrails y límite: el SDK lanza; la aplicación responde y lo registra."""
    entradas = (previo or []) + PROCESADOR.tomar(trace_id)
    if isinstance(e, InputGuardrailTripwireTriggered):
        nombre = e.guardrail_result.guardrail.get_name()
        entradas.append({"tipo": "aviso", "mensaje": f"guardrail de entrada {nombre} disparado: {e.guardrail_result.output.output_info}; no se llamó al modelo"})
        return _paquete(entradas, t0, g_in.RESPUESTAS.get(nombre, "No puedo atender esa solicitud."))
    if isinstance(e, OutputGuardrailTripwireTriggered):
        nombre = e.guardrail_result.guardrail.get_name()
        bloqueada = str(getattr(e.guardrail_result, "agent_output", "") or "")
        entradas.append({"tipo": "aviso", "mensaje": f"guardrail de salida {nombre} disparado: {e.guardrail_result.output.output_info}; la respuesta del modelo se sustituyó",
                         "respuesta_bloqueada": bloqueada[:600]})
        return _paquete(entradas, t0, g_out.RESPUESTAS.get(nombre, "No puedo entregar esa respuesta."))
    if isinstance(e, MaxTurnsExceeded):
        entradas.append({"tipo": "aviso", "mensaje": f"límite de {config.MAX_TURNS} turnos alcanzado (MaxTurnsExceeded del SDK)"})
        return _paquete(entradas, t0, "No pude completar la solicitud en el número máximo de pasos; una persona la revisará.")
    raise e


def correr(agente: Agent, entrada: Any, contexto_app: dict, previo: list[dict] | None = None) -> dict:
    tid, t0 = gen_trace_id(), time.perf_counter()

    async def corrida():
        with trace("Facturio Soporte", trace_id=tid):
            return await Runner.run(agente, entrada, context=contexto_app, max_turns=config.MAX_TURNS)
    try:
        return _empaquetar(_en_el_loop(corrida()), tid, t0, previo)
    except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, MaxTurnsExceeded) as e:
        return _por_excepcion(e, tid, t0, previo)


def reanudar(agente: Agent, pendiente: dict, aprobar: bool, contexto_app: dict, trace_previo: list[dict]) -> dict:
    """Human-in-the-loop: una persona decidió; approve o reject y el loop continúa desde el estado."""
    estado = pendiente["estado"]
    for it in estado.get_interruptions():
        (estado.approve if aprobar else estado.reject)(it)
    previo = trace_previo + [{"tipo": "aviso", "mensaje": ("aprobado" if aprobar else "rechazado") + " por una persona; el SDK reanuda desde el estado guardado"}]
    return correr(agente, estado, contexto_app, previo=previo)


async def correr_stream(agente: Agent, entrada: Any, contexto_app: dict):
    """Runner.run_streamed: un evento por delta de texto, por tool pedida y por tool devuelta; al final, el paquete."""
    tid, t0 = gen_trace_id(), time.perf_counter()
    cola: queue.Queue = queue.Queue()
    tools = registrar()

    async def productor():
        try:
            with trace("Facturio Soporte", trace_id=tid):
                resultado = Runner.run_streamed(agente, entrada, context=contexto_app, max_turns=config.MAX_TURNS)
                nombres: dict[str, str] = {}
                async for ev in resultado.stream_events():
                    if ev.type == "raw_response_event":
                        if getattr(ev.data, "type", "") == "response.output_text.delta":
                            cola.put({"tipo": "delta", "texto": ev.data.delta})
                    elif ev.type == "run_item_stream_event":
                        if ev.name == "tool_called":
                            n = getattr(ev.item.raw_item, "name", None) or ("web_search" if getattr(ev.item.raw_item, "type", "") == "web_search_call" else "tool")
                            nombres[getattr(ev.item.raw_item, "call_id", "")] = n
                            cola.put({"tipo": "item", "evento": "pide tool", "nombre": n,
                                      "mensaje": getattr(tools.get(n), "progreso", None) or ("Transfiriendo…" if n.startswith("transfer_to") else "Trabajando en tu solicitud…")})
                        elif ev.name == "tool_output":
                            cid = ev.item.raw_item.get("call_id", "") if isinstance(ev.item.raw_item, dict) else getattr(ev.item.raw_item, "call_id", "")
                            cola.put({"tipo": "item", "evento": "tool devolvió", "nombre": nombres.get(cid, "tool")})
                        elif ev.name == "message_output_created":
                            cola.put({"tipo": "item", "evento": "mensaje completo", "mensaje": "Listo."})
                    elif ev.type == "agent_updated_stream_event":
                        cola.put({"tipo": "item", "evento": "agente", "nombre": ev.new_agent.name, "mensaje": f"Te atiende {ev.new_agent.name}…"})
            cola.put({"tipo": "final", "paquete": _empaquetar(resultado, tid, t0)})
        except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, MaxTurnsExceeded) as e:
            cola.put({"tipo": "final", "paquete": _por_excepcion(e, tid, t0, None)})
        except BaseException as e:
            cola.put(e)

    asyncio.run_coroutine_threadsafe(productor(), _LOOP)
    propio = asyncio.get_running_loop()
    while True:
        ev = await propio.run_in_executor(None, cola.get)
        if isinstance(ev, BaseException):
            raise ev
        yield ev
        if ev["tipo"] == "final":
            return
