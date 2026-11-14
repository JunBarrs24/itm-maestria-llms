"""Semana 9. Tool output grande frente a un filtro determinista antes del modelo.

Misma pregunta ("¿cuántas facturas me quedan este mes y me conviene cambiar de plan?"),
dos formas de pasar el resultado de `consultar_plan` al modelo:

* crudo: el JSON completo del sistema de facturación (historial del mes incluido);
* normalizado: ocho campos calculados por código.

Se mide tokens de entrada, latencia y si la respuesta contiene el dato correcto.
"""
import json
import time

from context_strategies import Cliente, SYSTEM, contar_tokens, normalizar_plan, tool_output_grande

PREGUNTA = "¿Cuántas facturas me quedan este mes en mi plan y me conviene cambiar de plan? Responde con el número exacto."


def preguntar(cliente: Cliente, payload: dict, etiqueta: str) -> dict:
    texto = json.dumps(payload, ensure_ascii=False)
    mensajes = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": PREGUNTA},
                {"role": "assistant", "content": "", "tool_calls": [{"id": "call_1", "type": "function",
                                                                       "function": {"name": "consultar_plan", "arguments": json.dumps({"usuario_id": "u002"})}}]},
                {"role": "tool", "tool_call_id": "call_1", "name": "consultar_plan", "content": texto}]
    t0 = time.perf_counter()
    msg, ti, to = cliente.completar(mensajes, tools=False, max_tokens=120)
    return {"variante": etiqueta, "tokens_tool_output": contar_tokens(texto), "input_tokens": ti, "output_tokens": to,
            "latencia_s": round(time.perf_counter() - t0, 1), "respuesta": msg["content"]}


if __name__ == "__main__":
    cliente = Cliente()
    crudo = tool_output_grande("u002")
    limpio = normalizar_plan(crudo)
    print("respuesta esperada: restantes =", limpio["facturas_restantes"])
    for payload, et in ((limpio, "normalizado"), (crudo, "crudo")):
        r = preguntar(cliente, payload, et)
        print(f"\n{et}: tool output {r['tokens_tool_output']} tokens | input {r['input_tokens']} | {r['latencia_s']} s")
        print("  ", r["respuesta"][:220].replace("\n", " "))
