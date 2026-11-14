"""COMPRESS: cómo se resume lo que sale de la ventana en la estrategia C.

Dos compresores para compararlos: con LLM (una llamada más, conserva cifras si se le pide) y
determinista (recorte, gratis, claramente con pérdida). El resultado entra al contexto como texto,
así que un error del compresor lo tomaría el modelo como verdad: por eso el estado va aparte.
"""
from __future__ import annotations

import time

import config

INSTRUCCIONES_COMPRESOR = (
    "Resume la conversación de soporte en no más de seis líneas para que otro asistente pueda continuarla. "
    "Conserva textualmente identificadores (usuario, folios PAY-), montos, plazos, restricciones del cliente "
    "(por ejemplo un presupuesto máximo) y decisiones tomadas. Omite saludos y repeticiones. No inventes nada."
)


def comprimir_con_llm(mensajes: list[dict], effort: str | None = None) -> tuple[str, dict]:
    """Una llamada extra que también cuesta. Devuelve (resumen, uso)."""
    from openai import OpenAI
    client = OpenAI()
    transcripcion = "\n".join(f"{m['role']}: {m['content']}" for m in mensajes)
    t0 = time.perf_counter()
    extra = {"reasoning": {"effort": effort or "minimal"}} if config.MODEL.startswith("gpt-5") else {}
    resp = client.responses.create(model=config.MODEL, instructions=INSTRUCCIONES_COMPRESOR, input=transcripcion,
                                   max_output_tokens=400, store=False, **extra)
    u = resp.usage
    return resp.output_text.strip(), {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                                      "latencia_s": round(time.perf_counter() - t0, 2)}


def comprimir_determinista(mensajes: list[dict]) -> str:
    """Una línea por turno del usuario, recortada. Gratis y con pérdida."""
    return "; ".join(m["content"][:80] for m in mensajes if m["role"] == "user")[:600]
