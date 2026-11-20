"""Paralelo por código: fan-out a varios especialistas a la vez y fan-in con una síntesis (semana 13).

Aquí ni el modelo ni un orquestador deciden a quién llamar: el código manda la misma pregunta a todos
los especialistas con asyncio.gather, espera a todos, y un sintetizador escribe una respuesta. Es el
patrón parallelization de la semana 8 con agentes en lugar de prompts. Latencia: la del más lento.
Costo: todos más la síntesis. Riesgo nuevo: dos especialistas que piden el mismo side effect a la vez
(la política lo contiene por idempotencia, pero es una carrera).

No es un Agent: es una corrutina que corre varios Runner.run. engines/sdk.py la trata aparte.
"""
from __future__ import annotations

import asyncio

from agents import Agent, Runner

from agents_app.triage import especialista
from guardrails.output import DE_SALIDA
from providers import models

ESPECIALISTAS = ("facturacion", "acceso", "tecnico")


def sintetizador(proveedor: str, effort: str, summary: str) -> Agent:
    return Agent(name="Sintetizador", instructions=(
        "Recibes las respuestas de varios especialistas de soporte a la misma pregunta del cliente. Escribe una sola "
        "respuesta en español, breve, que combine lo útil y descarte lo que no aplica al tema. Si solo uno respondió "
        "con sustancia, usa esa. Nunca afirmes que un reembolso se ejecutó si ningún especialista lo confirmó."),
        model=models.modelo(proveedor), model_settings=models.ajustes(proveedor, effort, summary), output_guardrails=DE_SALIDA)


async def correr_en_paralelo(entrada, contexto_app: dict, proveedor: str, effort: str, summary: str, max_turns: int):
    """Fan-out: todos a la vez. Fan-in: síntesis. Devuelve (resultado_final, resultados_parciales)."""
    agentes = [especialista(m, proveedor, effort, summary) for m in ESPECIALISTAS]
    parciales = await asyncio.gather(*(Runner.run(a, entrada, context=contexto_app, max_turns=max_turns) for a in agentes),
                                     return_exceptions=True)
    partes = []
    for a, r in zip(agentes, parciales):
        if isinstance(r, Exception):
            partes.append(f"[{a.name}] no respondió: {type(r).__name__}")   # la falla de uno no tira a los demás
        else:
            partes.append(f"[{a.name}] {r.final_output}")
    pregunta = entrada if isinstance(entrada, str) else next((m["content"] for m in reversed(entrada) if m.get("role") == "user"), "")
    final = await Runner.run(sintetizador(proveedor, effort, summary),
                             f"Pregunta del cliente: {pregunta}\n\nRespuestas de los especialistas:\n" + "\n\n".join(partes),
                             context=contexto_app, max_turns=2)
    return final, parciales
