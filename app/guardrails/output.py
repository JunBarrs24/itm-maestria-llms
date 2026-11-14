"""Guardrails de salida: validar la respuesta antes de entregarla (semana 12).

Son evals que corren en cada turno. Reciben la respuesta final y el contexto de la aplicación,
y disparan cuando la respuesta contradice lo que la aplicación sabe. El caso de la semana 8:
el modelo afirma que un reembolso se ejecutó cuando ninguna tool lo confirmó.
"""
from __future__ import annotations

import re

from agents import GuardrailFunctionOutput, output_guardrail

AFIRMA_REEMBOLSO = re.compile(r"reembolso[^.]{0,60}(ejecut|proces|realiz|aplic|tramit[ae]d|listo)|REF-[0-9A-F]{8}", re.I)


def afirma_reembolso_sin_tool(texto: str, ejecutadas: list[dict]) -> bool:
    """True si la respuesta dice que hubo reembolso y ninguna tool `reembolsar` se ejecutó en el turno."""
    hubo = any(e.get("tool") == "reembolsar" for e in ejecutadas)
    return bool(AFIRMA_REEMBOLSO.search(texto or "")) and not hubo


def contiene_datos_personales(texto: str) -> bool:
    """Correos y RFC del cliente no se repiten en la respuesta."""
    return bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+|\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b", texto or ""))


@output_guardrail
async def sin_afirmar_reembolso(ctx, agent, salida) -> GuardrailFunctionOutput:
    texto = salida if isinstance(salida, str) else str(salida)
    dispara = afirma_reembolso_sin_tool(texto, ctx.context.get("ejecutadas", []))
    return GuardrailFunctionOutput(output_info={"afirma_reembolso_sin_tool": dispara}, tripwire_triggered=dispara)


@output_guardrail
async def sin_datos_personales(ctx, agent, salida) -> GuardrailFunctionOutput:
    texto = salida if isinstance(salida, str) else str(salida)
    dispara = contiene_datos_personales(texto)
    return GuardrailFunctionOutput(output_info={"datos_personales": dispara}, tripwire_triggered=dispara)


DE_SALIDA = [sin_afirmar_reembolso, sin_datos_personales]
RESPUESTAS = {
    "sin_afirmar_reembolso": "No tengo confirmación de que se haya ejecutado un reembolso en esta conversación. Si lo necesitas, lo revisamos con los datos del cargo.",
    "sin_datos_personales": "Tengo la información, pero no repito datos de contacto en el chat. ¿Qué necesitas que haga con ellos?",
}
