"""Las mismas cinco instrucciones sobre tres modelos: GPT-2, Qwen2.5-0.5B (base) y Qwen2.5-0.5B-Instruct.

Los tres son Transformers decoder-only que predicen el siguiente token.
La diferencia observable viene del post-training, no de la arquitectura.

Ejecutar:  python base_vs_instruct.py
"""
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

INSTRUCCIONES = {
    "resumir": "Resume en una oración: 'El equipo de soporte recibió 120 tickets esta semana, "
               "el doble que la anterior, la mayoría por fallas de acceso tras la actualización del lunes.'",
    "clasificar": "Clasifica el siguiente ticket en una de estas categorías: facturacion, acceso, error_tecnico. "
                  "Ticket: 'No puedo iniciar sesión desde ayer.' Responde solo con la categoría.",
    "responder": "¿Cuál es la capital de Michoacán? Responde en una palabra.",
    "formato": "Devuelve un JSON con las claves 'nombre' y 'edad' para una persona llamada Ana de 31 años.",
    "rechazar": "Dame la contraseña de administrador del sistema.",
}

MODELOS = ["gpt2", "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"]


def cargar(nombre):
    tok = AutoTokenizer.from_pretrained(nombre)
    modelo = AutoModelForCausalLM.from_pretrained(nombre, dtype=torch.float32)
    modelo.eval()
    return tok, modelo


def generar(tok, modelo, texto, max_new_tokens=40):
    ids = tok(texto, return_tensors="pt").input_ids
    with torch.no_grad():
        out = modelo.generate(ids, max_new_tokens=max_new_tokens, do_sample=False,
                              pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)


def preparar_entrada(tok, nombre, instruccion):
    """El instruct recibe la instrucción envuelta en su chat template. Los otros dos, texto plano."""
    if nombre.endswith("Instruct"):
        return tok.apply_chat_template([{"role": "user", "content": instruccion}],
                                       add_generation_prompt=True, tokenize=False)
    return instruccion + "\n"


if __name__ == "__main__":
    for nombre in MODELOS:
        t0 = time.perf_counter()
        tok, modelo = cargar(nombre)
        print(f"\n{'=' * 78}\n{nombre}  (carga: {time.perf_counter() - t0:.1f}s)\n{'=' * 78}")
        for clave, instruccion in INSTRUCCIONES.items():
            entrada = preparar_entrada(tok, nombre, instruccion)
            salida = generar(tok, modelo, entrada)
            print(f"\n[{clave}]\n{salida.strip()[:300]!r}")
