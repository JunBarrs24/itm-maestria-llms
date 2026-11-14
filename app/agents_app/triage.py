"""Varios agentes: un triage que entrega el turno a un especialista (handoffs, semana 12).

Cada especialista es un Agent con las instrucciones y las tools de su modo. El triage no tiene tools
de negocio: solo decide a quién entregar. Lo que se compara con routing y modes es qué contexto viaja
en la entrega:

  completo  el especialista recibe todo el historial más la llamada de handoff, sin el texto que el
            triage haya escrito al transferir (si viaja, el especialista lo repite en vez de actuar);
  minimo    `input_filter` deja solo el estado de la aplicación y el último mensaje del cliente.

El trace registra cada handoff (de → a) y, con el filtro, cuántos mensajes recibió el especialista.
"""
from __future__ import annotations

from agents import Agent, handoff
from agents.handoffs import HandoffInputData

from guardrails.input import DE_ENTRADA
from guardrails.output import DE_SALIDA
from modes.modes import MODOS, instrucciones, tools_del_modo
from providers import models
from skills import loader
from tools.registry import registrar

ESPECIALISTAS = ("facturacion", "acceso", "tecnico", "web")


def sin_texto_del_triage(datos: HandoffInputData) -> HandoffInputData:
    """Historial completo, menos lo que el triage escribió antes de transferir.

    El triage suele emitir un mensaje ("te transfiero con…") junto con la llamada de handoff. Si ese
    texto viaja, el especialista lo lee como la última respuesta y lo repite en vez de actuar.
    Se conservan la llamada de transferencia y su resultado (el SDK los necesita) y se quitan los
    mensajes del asistente generados en el turno del triage."""
    return HandoffInputData(input_history=datos.input_history,
                            pre_handoff_items=tuple(i for i in datos.pre_handoff_items if type(i).__name__ != "MessageOutputItem"),
                            new_items=tuple(i for i in datos.new_items if type(i).__name__ != "MessageOutputItem"),
                            run_context=datos.run_context)


def paquete_minimo(datos: HandoffInputData) -> HandoffInputData:
    """Transferencia mínima: el bloque de estado (si la estrategia lo puso) y el último mensaje del cliente."""
    historial = list(datos.input_history) if not isinstance(datos.input_history, str) else [{"role": "user", "content": datos.input_history}]
    estado = [m for m in historial if m.get("role") == "user" and str(m.get("content", "")).startswith("Estado de la aplicación")][:1]
    ultimo = [m for m in historial if m.get("role") == "user"][-1:]
    return HandoffInputData(input_history=tuple(estado + ultimo), pre_handoff_items=(), new_items=(), run_context=datos.run_context)


def especialista(modo: str, proveedor: str, effort: str, summary: str) -> Agent:
    tools = registrar()
    return Agent(name=f"Especialista {modo}", handoff_description=MODOS[modo]["descripcion"],
                 instructions=instrucciones(modo) + loader.indice_para_instrucciones()
                 + "\n\nEl cliente acaba de ser transferido contigo: atiéndelo tú, ahora, usando tus herramientas. "
                   "No digas que lo transfieres ni que espere; tú eres quien resuelve.",
                 tools=[tools[n] for n in tools_del_modo(modo)] + [tools["cargar_skill"]],
                 model=models.modelo(proveedor),
                 model_settings=models.ajustes(proveedor, effort, summary, con_hosted=any(tools[n].hosted for n in tools_del_modo(modo))),
                 output_guardrails=DE_SALIDA)


def agente_triage(proveedor: str, effort: str, summary: str, contexto_minimo: bool = False) -> Agent:
    filtro = paquete_minimo if contexto_minimo else sin_texto_del_triage
    entregas = [handoff(especialista(m, proveedor, effort, summary), input_filter=filtro) for m in ESPECIALISTAS]
    return Agent(name="Triage", instructions=(
        "Eres el triage de la mesa de soporte de Facturio. No respondes tú: identifica el tema y transfiere al "
        "especialista correcto con la herramienta de transferencia (facturación: cargos, reembolsos, planes; acceso: "
        "contraseñas, bloqueos, 2FA; técnico: errores y exportaciones; web: lo que requiera información de internet). "
        "Si el tema es ambiguo, transfiere a facturación. "
        "No pidas aclaraciones antes de transferir y no escribas ningún mensaje al cliente: solo llama a la herramienta de transferencia."),
        handoffs=entregas, model=models.modelo(proveedor), model_settings=models.ajustes(proveedor, effort, summary),
        input_guardrails=DE_ENTRADA)
