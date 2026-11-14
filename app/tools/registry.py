"""Lo común a todas las tools: el decorador de progreso, la regla de aprobación y el registro.

Una tool es un archivo en esta carpeta con una función decorada con `@function_tool` (Agents SDK).
El decorador lee la firma y el docstring y arma el schema que ve el modelo. Aquí se agregan tres
cosas que el SDK no tiene por sí solo:

  * `@progreso("…")`: lo que el cliente ve mientras la tool corre (streaming).
  * `side_effect=True` como metadato y `_requiere_aprobacion` como regla general: con los side
    effects automáticos apagados, toda tool con side effect se detiene y espera a una persona.
  * `registrar()`: descubre todas las tools de la carpeta importando los módulos; agregar una tool
    es crear un archivo, nada más.
"""
from __future__ import annotations

import dataclasses
import importlib
import pkgutil
from pathlib import Path

from agents import FunctionTool, RunContextWrapper, Tool, function_tool  # noqa: F401  (re-export para las tools)


def progreso(texto: str):
    """Mensaje de progreso para el cliente. Lo escribe quien conoce al cliente, en la tool misma."""
    def decorar(tool):
        tool.progreso = texto
        return tool
    return decorar


def side_effect(tool):
    """Marca una tool que cambia el mundo (mueve dinero, crea tickets, manda correos)."""
    tool.side_effect = True
    return tool


def _requiere_aprobacion(ctx: RunContextWrapper[dict], params: dict, call_id: str) -> bool:
    """Segunda capa de autorización (semana 8 y 10): con los side effects automáticos apagados,
    el SDK pausa la corrida antes de ejecutar y una persona decide (POST /aprobar)."""
    return not ctx.context.get("side_effects_automaticos", False)


TOOLS: dict[str, Tool] = {}


def registrar() -> dict[str, Tool]:
    """Importa cada módulo de tools/ y recoge las tools que define: FunctionTool (nuestras) y
    tools hospedadas del proveedor (por ejemplo WebSearchTool), marcadas con hosted=True."""
    if TOOLS:
        return TOOLS
    paquete = Path(__file__).resolve().parent
    for m in pkgutil.iter_modules([str(paquete)]):
        if m.name in ("registry",):
            continue
        mod = importlib.import_module(f"tools.{m.name}")
        for v in vars(mod).values():
            # una tool del SDK es un dataclass de agents.* con nombre: FunctionTool o una hospedada (WebSearchTool…)
            es_tool = dataclasses.is_dataclass(v) and not isinstance(v, type) and hasattr(v, "name") and type(v).__module__.startswith("agents.")
            if es_tool:
                v.side_effect = getattr(v, "side_effect", False)
                v.progreso = getattr(v, "progreso", "Trabajando en tu solicitud…")
                v.hosted = getattr(v, "hosted", not isinstance(v, FunctionTool))
                TOOLS[v.name] = v
    return TOOLS


def catalogo() -> list[dict]:
    """Para /config y para las slides: nombre, side effect, descripción corta."""
    return [{"nombre": n, "side_effect": t.side_effect, "hosted": t.hosted,
             "descripcion": (getattr(t, "description", "") or ("búsqueda web hospedada por OpenAI" if t.hosted else "")).split("\n")[0]}
            for n, t in registrar().items()]
