"""Proveedores: con qué API habla el SDK. El loop, las tools y el trace no cambian.

Dos caminos:
  * OpenAI: el nombre del modelo basta; el SDK usa Responses API con la llave del entorno.
  * Otro proveedor "a mano": muchos exponen un endpoint compatible con Chat Completions, así que se
    construye un cliente de OpenAI apuntando a esa URL y se envuelve en OpenAIChatCompletionsModel.
    Diez líneas, y se ve que el SDK habla Chat Completions con quien sea.

La semana 14 compara esto con LiteLLM (`LitellmModel("anthropic/claude-…")`): dos líneas para cien
proveedores, a cambio de no ver el formato. Las llaves se leen de .env si existen.
"""
from __future__ import annotations

import os

from agents import ModelSettings, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from openai.types.shared import Reasoning

import config

PROVEEDORES = {
    "openai":    {"modelo": config.MODEL, "base_url": None, "llave": "OPENAI_API_KEY"},
    "anthropic": {"modelo": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"), "base_url": "https://api.anthropic.com/v1/", "llave": "ANTHROPIC_API_KEY"},
    "gemini":    {"modelo": os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"), "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "llave": "GEMINI_API_KEY"},
}


def modelo(proveedor: str):
    """Lo que se pasa en `Agent(model=…)`."""
    p = PROVEEDORES.get(proveedor, PROVEEDORES["openai"])
    if p["base_url"] is None:
        return p["modelo"]
    cliente = AsyncOpenAI(base_url=p["base_url"], api_key=os.environ.get(p["llave"], ""))
    return OpenAIChatCompletionsModel(model=p["modelo"], openai_client=cliente)


def effort_efectivo(effort: str, con_hosted: bool) -> str:
    """Las tools hospedadas (web_search) no aceptan effort none ni minimal: el proveedor exige al menos low."""
    return "low" if con_hosted and effort in ("none", "minimal") else effort


def ajustes(proveedor: str, effort: str, summary: str, con_hosted: bool = False) -> ModelSettings:
    """El razonamiento configurable solo existe en los modelos gpt-5 vía Responses API."""
    p = PROVEEDORES.get(proveedor, PROVEEDORES["openai"])
    razona = p["base_url"] is None and p["modelo"].startswith("gpt-5")
    # max_tokens cubre razonamiento más texto: con effort low o más, 600 se agotaban antes de responder
    # (status=incomplete, reason=max_output_tokens) y el SDK lo lanza como ModelBehaviorError.
    return ModelSettings(max_tokens=config.MAX_OUTPUT_TOKENS, reasoning=Reasoning(effort=effort_efectivo(effort, con_hosted), summary=summary or None) if razona else None)


def nombre_modelo(proveedor: str) -> str:
    return PROVEEDORES.get(proveedor, PROVEEDORES["openai"])["modelo"]
