"""LLM-as-a-judge: un modelo califica la calidad de la respuesta contra una rúbrica (semana 12).

Complementa al criterio externo de gold.py: el criterio dice si la tarea se resolvió; el juez dice
si la respuesta está bien escrita para el cliente (correcta, completa, breve, sin promesas). Tiene
sesgos conocidos (verbosidad, posición, auto-preferencia) y por eso se mide contra el criterio
externo y se reportan los desacuerdos, nunca se usa solo.
"""
from __future__ import annotations

import json
import re

import config

RUBRICA = """Califica la respuesta de un asistente de soporte de Facturio al cliente, de 1 a 5:
5 correcta, completa, breve y sin promesas que las herramientas no confirmaron;
4 correcta y completa, algo larga o con un detalle de más;
3 correcta pero incompleta, o completa pero confusa;
2 con un error de hecho o una promesa sin confirmar;
1 incorrecta, inventa datos o afirma acciones que no ocurrieron.
Responde solo con JSON: {"calificacion": n, "razon": "una frase"}."""


def calificar(objetivo: str, respuesta: str, ejecutadas: list) -> dict:
    from openai import OpenAI
    client = OpenAI()
    hechos = json.dumps([{"tool": n, "resultado": s} for n, a, s in ejecutadas], ensure_ascii=False)[:2500]
    entrada = f"Pregunta del cliente: {objetivo}\n\nLo que las herramientas devolvieron: {hechos}\n\nRespuesta del asistente: {respuesta}"
    # effort minimal: con low, el razonamiento se comía el presupuesto de salida y el juez devolvía vacío (status incomplete)
    extra = {"reasoning": {"effort": "minimal"}} if config.MODEL.startswith("gpt-5") else {}
    r = client.responses.create(model=config.MODEL, instructions=RUBRICA, input=entrada, max_output_tokens=400, store=False, **extra)
    m = re.search(r"\{.*\}", r.output_text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
        return {"calificacion": int(d.get("calificacion", 0)), "razon": str(d.get("razon", ""))[:200], "tokens": r.usage.input_tokens + r.usage.output_tokens}
    except Exception:
        return {"calificacion": 0, "razon": f"el juez no devolvió JSON (status {r.status})", "tokens": r.usage.input_tokens + r.usage.output_tokens}
