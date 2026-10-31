"""Tool calling emulado con structured output: una vuelta completa.

    LLM -> solicitud de tool (JSON validado) -> la aplicación ejecuta -> resultado -> LLM -> respuesta

No hay loop: si el modelo pide una tool, se ejecuta una vez y se le devuelve
el resultado para que redacte la respuesta. El loop llega en la semana 10.

Uso:  .venv/bin/python course/week-08/examples/tool_calling_emulado.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import facturio_tools as ft  # noqa: E402
from llm_local import LLM, UsageLog, backend_disponible  # noqa: E402

SISTEMA_DECIDIR = f"""Eres el asistente de la mesa de soporte de Facturio, un SaaS de facturación.
Decide si necesitas una herramienta para responder al cliente. Herramientas disponibles:
{ft.descripcion_tools()}

Reglas:
- Usa consultar_factura cuando el cliente mencione un folio PAY-.
- Usa buscar_documentacion para preguntas sobre políticas, plazos, planes o funciones.
- Usa reembolsar solo si el cliente pide explícitamente un reembolso y da el folio; la aplicación decidirá si procede.
- Usa escalar_a_humano si el caso no se puede resolver con las otras herramientas.
- Si no hace falta ninguna herramienta, responde con tool "ninguna".
Devuelve la herramienta, sus argumentos completos y una razón breve. Ejemplos del formato exacto:
{{"tool": "consultar_factura", "args": {{"folio": "PAY-00012345"}}, "razon": "el cliente dio un folio"}}
{{"tool": "buscar_documentacion", "args": {{"pregunta": "plazo para cancelar una factura", "k": 3}}, "razon": "pregunta de política"}}
{{"tool": "reembolsar", "args": {{"folio": "PAY-00012345", "monto": 599.0, "motivo": "no usó el servicio"}}, "razon": "pidió reembolso con folio y monto"}}
{{"tool": "consultar_plan", "args": {{"usuario_id": "u001"}}, "razon": "pregunta sobre su plan"}}
{{"tool": "escalar_a_humano", "args": {{"motivo": "amenaza legal", "folio": null}}, "razon": "fuera de alcance"}}
{{"tool": "ninguna", "args": {{}}, "razon": "saludo sin solicitud"}}"""

SISTEMA_RESPONDER = """Eres el asistente de la mesa de soporte de Facturio. Responde al cliente en español,
en tres oraciones como máximo, usando únicamente la información del resultado de la herramienta.
Si el resultado contiene 'error' o 'ejecutado: false', explica la razón tal como aparece, sin inventar alternativas."""


def responder_con_tools(llm: LLM, mensaje: str, log: UsageLog, etiqueta: str = "una_vuelta") -> dict:
    traza = {"mensaje": mensaje}
    # 1. el modelo decide (structured output validado con Pydantic)
    with log.track(f"{etiqueta}:decidir", llm.model) as t:
        solicitud, r1, n1 = llm.parse(f"Mensaje del cliente: {mensaje}", ft.SolicitudTool, system=SISTEMA_DECIDIR,
                                      max_output_tokens=160)
        t.input_tokens, t.output_tokens = r1.input_tokens, r1.output_tokens
    if solicitud is None:
        traza.update(solicitud=None, resultado=None, respuesta="No pude interpretar la solicitud.", llamadas=n1)
        return traza
    traza["solicitud"] = solicitud.model_dump()
    # 2. la aplicación valida y ejecuta (o no)
    if solicitud.tool == "ninguna":
        resultado = {"nota": "sin herramienta"}
    else:
        resultado = ft.ejecutar_tool(solicitud.tool, solicitud.args)
    traza["resultado"] = resultado
    # 3. el modelo redacta con el resultado
    contexto = (f"Mensaje del cliente: {mensaje}\n\nHerramienta usada: {solicitud.tool}\n"
                f"Resultado de la herramienta (JSON):\n{json.dumps(resultado, ensure_ascii=False, default=str)[:1500]}")
    with log.track(f"{etiqueta}:responder", llm.model) as t:
        r2 = llm.chat(contexto, system=SISTEMA_RESPONDER, max_output_tokens=140)
        t.input_tokens, t.output_tokens = r2.input_tokens, r2.output_tokens
    traza["respuesta"] = r2.text
    traza["llamadas"] = n1 + 1
    return traza


MENSAJES = [
    "Me cobraron dos veces la mensualidad el 30 de agosto. El folio del segundo cargo es PAY-00012348.",
    "¿Cuántos días tengo para pedir un reembolso después del cargo?",
    "Quiero el reembolso completo de 599 pesos del cargo PAY-00012345: no timbré ninguna factura este mes.",
    "Quiero el reembolso de 599 pesos del cargo PAY-00012346, ya no uso el sistema.",
    "Reembolsen los 12500 pesos del cargo PAY-00012350, cerramos la empresa.",
    "Soy el usuario u001. ¿Puedo exportar mis reportes a Excel?",
]

if __name__ == "__main__":
    backend = backend_disponible()
    llm = LLM(backend=backend, model=None if backend == "openai" else "Qwen/Qwen2.5-1.5B-Instruct")
    log = UsageLog()
    ft.reiniciar_estado()
    for m in MENSAJES:
        tr = responder_con_tools(llm, m, log)
        print("\n>>", m)
        print("   tool:", tr.get("solicitud", {}).get("tool") if tr.get("solicitud") else None, "| args:", tr.get("solicitud", {}).get("args") if tr.get("solicitud") else None)
        print("   resultado:", json.dumps(tr["resultado"], ensure_ascii=False, default=str)[:220])
        print("   respuesta:", tr["respuesta"])
    print()
    print(log.tabla().to_string(index=False))
