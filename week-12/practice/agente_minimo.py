"""Un agente desde cero con el Agents SDK: dos tools, búsqueda web y una función propia.

Cambia el problema, las instrucciones y la tool propia. Corre con tu OPENAI_API_KEY en el entorno:

    pip install openai-agents python-dotenv
    python agente_minimo.py "¿Cuánto cuesta hoy un Raspberry Pi 5 de 8 GB en México y dónde conviene comprarlo?"
"""
from __future__ import annotations

import asyncio
import sys

from agents import Agent, ModelSettings, Runner, WebSearchTool, function_tool
from dotenv import load_dotenv
from openai.types.shared import Reasoning

load_dotenv()


# ---- tool propia: una función normal con docstring; la firma y el docstring son el schema que ve el modelo
@function_tool
def convertir_a_pesos(monto: float, moneda: str) -> dict:
    """Convierte un monto en USD o EUR a pesos mexicanos con un tipo de cambio fijo de referencia.

    Úsala cuando un precio venga en otra moneda y necesites compararlo en pesos.

    Args:
        monto: La cantidad en la moneda original.
        moneda: USD o EUR.
    """
    tipo = {"USD": 18.5, "EUR": 20.1}.get(moneda.upper())
    if tipo is None:
        return {"error": f"moneda no soportada: {moneda}"}
    return {"pesos": round(monto * tipo, 2), "tipo_de_cambio": tipo, "nota": "tipo de cambio de referencia, no de mercado"}


agente = Agent(
    name="Comparador",
    instructions=("Resuelves el problema del usuario buscando en internet y comparando. Cita la URL de cada dato. "
                  "Convierte a pesos lo que venga en otra moneda. Responde en español, breve, con una recomendación y su razón."),
    tools=[WebSearchTool(search_context_size="low"), convertir_a_pesos],
    model="gpt-5-mini",
    model_settings=ModelSettings(reasoning=Reasoning(effort="low")),   # la búsqueda web exige al menos low
)


async def main(pregunta: str):
    resultado = await Runner.run(agente, pregunta, max_turns=8)       # stop condition por límite
    print("\n== Respuesta\n", resultado.final_output)
    print("\n== Tools que pidió:", [i.raw_item.type if not hasattr(i.raw_item, "name") else i.raw_item.name
                                   for i in resultado.new_items if type(i).__name__ == "ToolCallItem"])
    u = resultado.context_wrapper.usage
    print(f"== Uso: {u.requests} llamadas, {u.input_tokens} tokens de entrada, {u.output_tokens} de salida")
    print("== Trace: https://platform.openai.com/traces")


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or "¿Cuánto cuesta hoy un Raspberry Pi 5 de 8 GB en México y dónde conviene comprarlo?"))
