"""Agente de la mesa de soporte de Facturio con el OpenAI Agents SDK.

Cada abstracción del SDK sustituye un mecanismo que el curso ya construyó a mano:

    Runner.run        <- el loop observar / decidir / actuar de la semana 10
    function_tool     <- los schemas y el dispatcher de la semana 8
    SQLiteSession     <- el historial de conversación de la semana 9
    guardrails        <- la validación de entrada y salida de la semana 4
    output_type       <- los structured outputs con Pydantic de la semana 4
    needs_approval    <- el callable `aprobar` del loop de la semana 10
    tracing           <- el registro de llamadas de la semana 1

Backend: con OPENAI_API_KEY usa OpenAI y el tracing del dashboard; sin llave usa
el servidor local (`shared/local_server.py`) por Chat Completions y el tracing
de consola. La lógica del agente es la misma en ambos casos.

Uso:  .venv/bin/python course/week-11/examples/agente_sdk.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "shared"))
sys.path.insert(0, str(HERE))

import facturio_tools as ft  # noqa: E402
from local_server import backend_config  # noqa: E402

from agents import (  # noqa: E402
    Agent, AgentOutputSchema, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, ModelSettings,
    OpenAIChatCompletionsModel, OutputGuardrailTripwireTriggered, Runner, SQLiteSession, function_tool,
    input_guardrail, output_guardrail, set_tracing_disabled,
)
from tracing_consola import activar_tracing_consola  # noqa: E402

CFG = backend_config()


# ------------------------------------------------------------------ modelo
def modelo():
    """El SDK usa Responses API por defecto. El servidor local solo habla Chat Completions."""
    if CFG["local"]:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(base_url=CFG["base_url"], api_key=CFG["api_key"] or "local")
        return OpenAIChatCompletionsModel(model=CFG["model"], openai_client=client)
    return CFG["model"]  # nombre del modelo; el SDK crea el cliente con la llave del entorno


AJUSTES = ModelSettings(max_tokens=200, temperature=0)


# ------------------------------------------------------------------ tools
# Las funciones de negocio viven en shared/facturio_tools.py. Aquí solo se envuelven:
# el docstring se vuelve descripción y la firma se vuelve schema.

@function_tool
def consultar_factura(folio: str) -> str:
    """Consulta una factura por folio (formato PAY- seguido de 8 dígitos). Devuelve estado, monto y fecha."""
    return json.dumps(ft.consultar_factura(folio), ensure_ascii=False)


@function_tool
def consultar_plan(usuario_id: str) -> str:
    """Consulta el plan de un usuario (u001 a u005): límites, uso actual y precio."""
    return json.dumps(ft.consultar_plan(usuario_id), ensure_ascii=False)


@function_tool
def buscar_documentacion(pregunta: str) -> str:
    """Busca en la documentación y políticas de Facturio. Úsala para dudas de políticas, límites y errores."""
    return json.dumps(ft.buscar_documentacion(pregunta, k=2), ensure_ascii=False)


@function_tool(needs_approval=True)
def reembolsar(folio: str, monto: float, motivo: str) -> str:
    """Solicita un reembolso sobre un cargo. Tiene side effect: mueve dinero. Requiere aprobación humana."""
    ok, razon = ft.autorizar_reembolso(folio, monto)  # la autorización de la aplicación sigue aquí
    if not ok:
        return json.dumps({"ejecutado": False, "razon": razon}, ensure_ascii=False)
    return json.dumps(ft.reembolsar(folio, monto, motivo), ensure_ascii=False)


@function_tool
def escalar_a_humano(motivo: str) -> str:
    """Pasa el caso a un agente humano cuando la política lo exige o falta información."""
    return json.dumps(ft.escalar_a_humano(motivo), ensure_ascii=False)


TOOLS = [consultar_factura, consultar_plan, buscar_documentacion, reembolsar, escalar_a_humano]


# ------------------------------------------------------------------ guardrails
FUERA_DE_DOMINIO = ("poema", "receta", "clima", "fútbol", "futbol", "chiste", "tarea de matemáticas")


@input_guardrail
async def solo_soporte(ctx, agent, entrada):
    """Guardrail de entrada: determinista y verificable. Rechaza lo que no es soporte."""
    texto = entrada if isinstance(entrada, str) else json.dumps(entrada, ensure_ascii=False)
    fuera = any(k in texto.lower() for k in FUERA_DE_DOMINIO)
    return GuardrailFunctionOutput(output_info={"fuera_de_dominio": fuera}, tripwire_triggered=fuera)


PII = ("@", "rfc ", "teléfono", "telefono")


@output_guardrail
async def sin_datos_personales(ctx, agent, salida):
    """Guardrail de salida: la respuesta no repite correos ni RFC del cliente."""
    texto = salida if isinstance(salida, str) else json.dumps(salida.model_dump() if hasattr(salida, "model_dump") else salida, ensure_ascii=False)
    fuga = "@" in texto or "example.com" in texto
    return GuardrailFunctionOutput(output_info={"fuga": fuga}, tripwire_triggered=fuga)


# ------------------------------------------------------------------ structured output
class RespuestaSoporte(BaseModel):
    resumen: str = Field(description="Una oración con lo que se hizo o se respondió")
    requiere_humano: bool
    tools_usadas: list[str] = Field(default_factory=list)


@function_tool
def entregar_respuesta(resumen: str, requiere_humano: bool, tools_usadas: list[str]) -> str:
    """Entrega la respuesta final al usuario con la forma acordada. Llámala una sola vez, al terminar."""
    return json.dumps({"resumen": resumen, "requiere_humano": requiere_humano, "tools_usadas": tools_usadas}, ensure_ascii=False)


def esquema_salida():
    """Con OpenAI el schema se aplica en el servidor (structured outputs estrictos) y `output_type`
    basta. El servidor local ignora `response_format`, así que la salida estructurada se pide como
    una tool final (`entregar_respuesta`) y la corrida se detiene al llamarla: el mismo contrato,
    aplicado por el schema de la tool en lugar de por el modo estricto del proveedor."""
    return RespuestaSoporte


INSTRUCCIONES = (
    "Eres el asistente de la mesa de soporte de Facturio. Usa las tools cuando haga falta: "
    "consulta facturas y planes antes de afirmar algo, busca la documentación para políticas, "
    "y escala a humano cuando falte información o la política lo exija. Responde en español, breve."
)


def construir_agente(con_guardrails: bool = True, salida_estructurada: bool = False, tools=None) -> Agent:
    return Agent(
        name="Soporte Facturio",
        instructions=INSTRUCCIONES,
        tools=list(tools if tools is not None else TOOLS),
        model=modelo(),
        model_settings=AJUSTES,
        input_guardrails=[solo_soporte] if con_guardrails else [],
        output_guardrails=[sin_datos_personales] if con_guardrails else [],
        output_type=esquema_salida() if (salida_estructurada and not CFG["local"]) else None,
    )


def formateador() -> Agent:
    """Segundo agente, solo para el servidor local: convierte una respuesta libre en RespuestaSoporte.

    Con OpenAI no hace falta: `output_type` aplica el schema en el servidor. El servidor local
    ignora `response_format`, así que el contrato se aplica con una tool obligatoria
    (`tool_choice` fijo) y la corrida se detiene al llamarla (`StopAtTools`)."""
    from agents import StopAtTools
    return Agent(
        name="Formateador",
        instructions="Recibes la respuesta de un asistente de soporte y las tools que usó. Llama a entregar_respuesta una vez.",
        tools=[entregar_respuesta],
        model=modelo(),
        model_settings=ModelSettings(max_tokens=150, temperature=0, tool_choice="entregar_respuesta"),
        tool_use_behavior=StopAtTools(stop_at_tool_names=["entregar_respuesta"]),
    )


async def correr_estructurado(agente: Agent, entrada, **kw):
    """Corrida con salida RespuestaSoporte en ambos backends."""
    r = await correr(agente, entrada, **kw)
    if not CFG["local"]:
        return r, salida_estructurada(r)
    usadas = [i.raw_item.name for i in r.new_items if type(i).__name__ == "ToolCallItem"]
    texto = f"Respuesta del asistente: {r.final_output}\nTools usadas: {usadas}\nrequiere_humano es true solo si se escaló a humano."
    f = await Runner.run(formateador(), texto, max_turns=2)
    return r, salida_estructurada(f)


def salida_estructurada(resultado) -> RespuestaSoporte | None:
    """Convierte el final_output en RespuestaSoporte en ambos backends."""
    fo = resultado.final_output
    if isinstance(fo, RespuestaSoporte):
        return fo
    try:
        return RespuestaSoporte.model_validate_json(fo if isinstance(fo, str) else json.dumps(fo))
    except Exception:
        return None


# ------------------------------------------------------------------ correr con aprobación
async def correr(agente: Agent, entrada, aprobar: Callable[[str, dict], bool] | None = None,
                 session=None, max_turns: int = 6):
    """Runner.run más el ciclo de aprobación humana.

    Cuando una tool con needs_approval es solicitada, el SDK detiene la corrida y devuelve
    `interruptions`. La aplicación decide (aquí, el callable `aprobar`) y reanuda desde el estado.
    """
    resultado = await Runner.run(agente, entrada, session=session, max_turns=max_turns)
    while getattr(resultado, "interruptions", None):
        estado = resultado.to_state()
        for item in resultado.interruptions:
            args = json.loads(item.raw_item.arguments or "{}")
            decision = bool(aprobar(item.tool_name, args)) if aprobar else False
            (estado.approve if decision else estado.reject)(item)
        resultado = await Runner.run(agente, estado, session=session, max_turns=max_turns)
    return resultado


def correr_sync(agente: Agent, entrada, **kw):
    return asyncio.run(correr(agente, entrada, **kw))


# ------------------------------------------------------------------ demo
if __name__ == "__main__":
    consola = activar_tracing_consola() if CFG["local"] else None
    if not CFG["local"]:
        print("Con llave: el trace se ve en el dashboard de OpenAI (Traces).")
    agente = construir_agente()
    folio = list(ft.CARGOS)[0]

    print("\n== 1. Consulta simple")
    r = correr_sync(agente, f"¿Cuál es el estado de la factura {folio}?")
    print("Respuesta:", r.final_output)
    if consola:
        consola.imprimir(); print(consola.resumen())

    print("\n== 2. Guardrail de entrada")
    try:
        correr_sync(agente, "Escríbeme un poema sobre el clima de Morelia")
    except InputGuardrailTripwireTriggered as e:
        print("Rechazado por guardrail:", e.guardrail_result.output.output_info)

    print("\n== 3. Reembolso con aprobación humana (la aplicación decide)")
    decisiones = {"reembolsar": False}
    r = correr_sync(agente, f"Reembolsa 300 pesos de la factura {folio} por cargo duplicado.",
                    aprobar=lambda tool, args: decisiones.get(tool, False))
    print("Respuesta (rechazado):", r.final_output)
    if consola:
        consola.imprimir()

    print("\n== 4. Session: el historial lo administra el runtime")
    db = Path(tempfile.gettempdir()) / "facturio-w11.db"
    s = SQLiteSession("u002", db)
    correr_sync(agente, "Mi usuario es u002 y mi presupuesto máximo es 500 pesos.", session=s)
    r = correr_sync(agente, "¿Cuál era mi presupuesto máximo?", session=s)
    print("Respuesta:", r.final_output, "| items en sesión:", len(asyncio.run(s.get_items())))
    db.unlink(missing_ok=True)

    print("\n== 5. Salida estructurada")
    r, est = asyncio.run(correr_estructurado(construir_agente(con_guardrails=False, salida_estructurada=True,
                                                              tools=[buscar_documentacion, escalar_a_humano]),
                                             "Quiero cancelar mi cuenta y que borren mis datos."))
    print("Libre:", str(r.final_output)[:120]); print("Estructurada:", est)
