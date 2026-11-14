"""Guardrails de entrada: validaciones deterministas antes de gastar la primera llamada.

Un guardrail que vale es el que se puede probar con un caso que dispara y uno que no (tests/).
Cuando dispara, el SDK lanza InputGuardrailTripwireTriggered y el motor responde sin modelo.
"""
from __future__ import annotations

import json
import re

from agents import GuardrailFunctionOutput, input_guardrail

FUERA_DE_SOPORTE = ("poema", "receta", "clima", "fútbol", "futbol", "chiste", "tarea de matemáticas", "canción")


def _ultimo_mensaje(entrada) -> str:
    if isinstance(entrada, str):
        return entrada
    return next((str(m.get("content", "")) for m in reversed(entrada) if m.get("role") == "user"), json.dumps(entrada, ensure_ascii=False))


def es_fuera_de_soporte(texto: str) -> bool:
    return any(k in texto.lower() for k in FUERA_DE_SOPORTE)


def folio_mal_formado(texto: str) -> bool:
    """Un folio que parece PAY- pero no tiene 8 dígitos: mejor corregirlo que buscarlo."""
    return any(not re.fullmatch(r"PAY-\d{8}", f) for f in re.findall(r"\bPAY-[\w-]*", texto, re.I))


@input_guardrail
async def solo_soporte(ctx, agent, entrada) -> GuardrailFunctionOutput:
    fuera = es_fuera_de_soporte(_ultimo_mensaje(entrada))
    return GuardrailFunctionOutput(output_info={"fuera_de_soporte": fuera}, tripwire_triggered=fuera)


@input_guardrail
async def folio_valido(ctx, agent, entrada) -> GuardrailFunctionOutput:
    malo = folio_mal_formado(_ultimo_mensaje(entrada))
    return GuardrailFunctionOutput(output_info={"folio_mal_formado": malo}, tripwire_triggered=malo)


DE_ENTRADA = [solo_soporte, folio_valido]
RESPUESTAS = {
    "solo_soporte": "Esta mesa atiende soporte de Facturio: cargos, planes, acceso y errores del producto.",
    "folio_valido": "El folio no tiene el formato esperado (PAY- seguido de 8 dígitos). ¿Me lo confirmas?",
}
