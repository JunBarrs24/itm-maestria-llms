"""Agents as tools: un orquestador que llama a los especialistas como si fueran tools (semana 13).

Diferencia con handoffs: el turno no cambia de manos. El orquestador pide `consultar_facturacion(...)`,
el SDK corre al especialista como una sub-corrida, le devuelve el texto como resultado de tool, y el
orquestador sigue: puede llamar a otro, combinar y responder él. Lo que el especialista recibe es solo
lo que el orquestador escribe como argumento (no el historial), así que el contexto que viaja lo
decide el modelo en cada llamada.

Con `parallel_tool_calls=True`, si el orquestador pide dos especialistas en la misma vuelta, el SDK
los corre a la vez.
"""
from __future__ import annotations

from agents import Agent, ModelSettings

from agents_app.triage import especialista
from guardrails.input import DE_ENTRADA
from guardrails.output import DE_SALIDA
from modes.modes import MODOS
from providers import models

ESPECIALISTAS = ("facturacion", "acceso", "tecnico", "web")


def agente_orquestador(proveedor: str, effort: str, summary: str) -> Agent:
    herramientas = [
        especialista(m, proveedor, effort, summary).as_tool(
            tool_name=f"consultar_{m}",
            tool_description=f"Pide al especialista de {m} que atienda una parte del caso. {MODOS[m]['descripcion']} "
                             "Escribe en el argumento todo lo que necesita saber: usuario, folio, qué pide el cliente.",
            max_turns=4)
        for m in ESPECIALISTAS]
    ajustes = models.ajustes(proveedor, effort, summary)
    ajustes = ModelSettings(**{**ajustes.__dict__, "parallel_tool_calls": True})
    return Agent(name="Orquestador", instructions=(
        "Eres el orquestador de la mesa de soporte de Facturio. No tienes herramientas de negocio: tienes especialistas. "
        "Divide el caso del cliente por tema, consulta a cada especialista que haga falta (puedes pedir varios a la vez), "
        "y escribe tú la respuesta final combinando lo que te devolvieron. Responde en español, breve. "
        "Nunca afirmes que un reembolso se ejecutó si el especialista no lo confirmó."),
        tools=herramientas, model=models.modelo(proveedor), model_settings=ajustes,
        input_guardrails=DE_ENTRADA, output_guardrails=DE_SALIDA)
