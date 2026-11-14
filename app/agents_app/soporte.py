"""El agente de soporte, en sus dos diseños de un solo agente: routing y modes.

Las dos usan los mismos modos (modes/), las mismas tools (tools/) y los mismos guardrails. Cambia
quién decide el modo:

  routing  el código lo fija antes de llamar al modelo (regex de la semana 8); el agente nace con las
           instrucciones y las tools de ese modo y no puede cambiarlo.
  modes    el agente nace en el modo de la sesión y tiene la tool `cambiar_modo`; `is_enabled` de cada
           tool e `instructions` como función leen el modo del contexto en cada llamada, así que el
           cambio se refleja en la vuelta siguiente sin construir otro agente.

En los dos, `cargar_skill` está disponible y las descripciones de los skills van en las instrucciones.
"""
from __future__ import annotations

import dataclasses

from agents import Agent, RunContextWrapper

import config
from guardrails.input import DE_ENTRADA
from guardrails.output import DE_SALIDA
from modes.modes import MODOS, instrucciones, tools_del_modo
from providers import models
from skills import loader
from tools.registry import registrar

NOMBRE = "Soporte Facturio"


def _tool_habilitada_en_modo(nombre: str):
    """is_enabled que mira el modo del contexto de la aplicación en cada llamada."""
    def habilitada(ctx: RunContextWrapper[dict], agent: Agent) -> bool:
        return nombre in MODOS.get(ctx.context.get("modo", "general"), MODOS["general"])["tools"]
    return habilitada


def _instrucciones_del_modo(ctx: RunContextWrapper[dict], agent: Agent) -> str:
    """instructions como función: el prompt del modo vigente más el índice de skills."""
    modo = ctx.context.get("modo", "general")
    aviso = ("" if ctx.context.get("side_effects_automaticos") else
             " Las acciones (reembolsos, escalaciones) se detienen para que una persona las apruebe; puedes pedirlas, pero no prometas que ya ocurrieron.")
    return (instrucciones(modo) + aviso + loader.indice_para_instrucciones()
            + "\n\nSi el tema no corresponde a tu modo actual, cambia de modo con cambiar_modo antes de responder.")


def agente_routing(modo: str, proveedor: str, effort: str, summary: str) -> Agent:
    """Diseño routing: modo fijo, elegido por el código. Sin cambiar_modo."""
    tools = registrar()
    visibles = [tools[n] for n in tools_del_modo(modo)] + [tools["cargar_skill"]]
    return Agent(name=NOMBRE, instructions=instrucciones(modo) + loader.indice_para_instrucciones(),
                 tools=visibles, model=models.modelo(proveedor),
                 model_settings=models.ajustes(proveedor, effort, summary, con_hosted=any(t.hosted for t in visibles)),
                 input_guardrails=DE_ENTRADA, output_guardrails=DE_SALIDA)


def agente_modes(proveedor: str, effort: str, summary: str) -> Agent:
    """Diseño modes: todas las tools registradas, cada una habilitada según el modo del contexto."""
    tools = registrar()
    dinamicas = [dataclasses.replace(t, is_enabled=_tool_habilitada_en_modo(n)) for n, t in tools.items()
                 if n not in ("cambiar_modo", "cargar_skill") and not t.hosted]
    hospedadas = [t for t in tools.values() if t.hosted]   # sin is_enabled: siempre visibles en este diseño
    return Agent(name=NOMBRE, instructions=_instrucciones_del_modo,
                 tools=dinamicas + hospedadas + [tools["cambiar_modo"], tools["cargar_skill"]],
                 model=models.modelo(proveedor), model_settings=models.ajustes(proveedor, effort, summary, con_hosted=bool(hospedadas)),
                 input_guardrails=DE_ENTRADA, output_guardrails=DE_SALIDA)
