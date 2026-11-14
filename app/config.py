"""Configuración de la app: todo sale de `.env` (python-dotenv) o de variables de entorno.

Cada estudiante tiene su llave de OpenAI; las de otros proveedores son opcionales y solo
se usan si se elige ese proveedor en la cabecera (semana 12, carpeta providers/).
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

AQUI = Path(__file__).resolve().parent
load_dotenv(AQUI / ".env")

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
REASONING_EFFORT = os.environ.get("REASONING_EFFORT", "minimal")   # none | minimal | low | medium | high | xhigh
REASONING_SUMMARY = os.environ.get("REASONING_SUMMARY", "auto")    # auto | concise | detailed | "" para no pedirlo
COMPRESOR = os.environ.get("COMPRESOR", "llm")                     # determinista | llm  (estrategia C: cómo se resume lo viejo)
UMBRAL_COMPRESION = int(os.environ.get("UMBRAL_COMPRESION", "8"))  # mensajes en el historial a partir de los cuales se comprime
PORT = int(os.environ.get("PORT", "8011"))
MAX_TURNS = int(os.environ.get("MAX_TURNS", "6"))                  # stop condition por límite (semana 10)

EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")
COMPRESORES = ("llm", "determinista")
ESTRATEGIAS = ("completo", "ventana", "estado")

# USD por millón de tokens (entrada, salida). Lo que no está aquí se cobra con el último par.
PRECIOS_USD_POR_MILLON = {
    "gpt-5-mini": (0.25, 2.00), "gpt-5-nano": (0.05, 0.40), "gpt-5": (1.25, 10.00),
    "claude-sonnet-4-5": (3.00, 15.00), "claude-haiku-4-5": (1.00, 5.00),
    "gemini-2.5-flash": (0.30, 2.50), "gemini-2.5-pro": (1.25, 10.00),
}


def costo_usd(model: str, tokens_entrada: int, tokens_salida: int) -> float:
    pi, po = PRECIOS_USD_POR_MILLON.get(model, (1.0, 4.0))
    return (tokens_entrada * pi + tokens_salida * po) / 1e6
