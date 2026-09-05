"""Arquitectura mínima de una aplicación con LLM, en un solo archivo.

Cuatro responsabilidades, una sola probabilística:
  1. construcción del prompt      (determinista)
  2. llamada al modelo            (probabilística)
  3. validación de la salida      (determinista)
  4. registro de cada llamada     (observabilidad)

Ejecutar:  python arquitectura_minima.py
Requiere:  pip install transformers torch   (en Colab ya vienen)
"""
import json
import os
import time
import warnings

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
warnings.filterwarnings("ignore")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

OPCIONES = ["billing", "access", "bug"]
REGISTRO: list[dict] = []

tokenizer = AutoTokenizer.from_pretrained("gpt2")
modelo = AutoModelForCausalLM.from_pretrained("gpt2", dtype=torch.float32).eval()


def generar(prompt: str, max_new_tokens: int = 4) -> str:
    """2. Componente probabilístico. Devuelve solo el texto nuevo."""
    ids = tokenizer(prompt, return_tensors="pt").input_ids
    with torch.no_grad():
        out = modelo.generate(ids, max_new_tokens=max_new_tokens, do_sample=False,
                              pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(out[0, ids.shape[1]:], skip_special_tokens=True)


def construir_prompt(texto: str) -> str:
    """1. Determinista. Dos ejemplos para que GPT-2 siga el formato."""
    return (
        'Ticket: "I need a refund for the duplicate charge."\nCategory: billing\n\n'
        'Ticket: "The login page returns an error."\nCategory: access\n\n'
        f'Ticket: "{texto}"\nCategory:'
    )


def validar(salida: str, opciones: list[str]) -> str | None:
    """3. Determinista. Una opción exacta o nada."""
    encontradas = [o for o in opciones if o in salida.lower()]
    return encontradas[0] if len(encontradas) == 1 else None


def registrar(prompt: str, salida: str, etiqueta: str | None, latencia: float) -> None:
    """4. Observabilidad. Sin la salida cruda no se puede depurar mañana."""
    REGISTRO.append({"prompt": prompt, "salida": salida, "etiqueta": etiqueta,
                     "latencia_s": round(latencia, 3)})


def clasificar(texto: str) -> dict:
    prompt = construir_prompt(texto)
    t = time.perf_counter()
    salida = generar(prompt)
    latencia = time.perf_counter() - t
    etiqueta = validar(salida, OPCIONES)
    registrar(prompt, salida, etiqueta, latencia)
    if etiqueta is None:
        # Política de la aplicación cuando el modelo no cumple el contrato.
        # Aquí: degradar a una categoría por defecto y marcarlo para revisión humana.
        return {"etiqueta": "unknown", "revisar": True, "latencia_s": latencia}
    return {"etiqueta": etiqueta, "revisar": False, "latencia_s": latencia}


if __name__ == "__main__":
    tickets = [
        "I was charged twice for my July subscription.",
        "I cannot log in, it says my password is wrong.",
        "The export to PDF shows blank charts.",
        "Please send me the invoice for June again.",
        "The app crashes when I open the reports tab.",
    ]
    for tk in tickets:
        r = clasificar(tk)
        print(f"{r['etiqueta']:8} revisar={r['revisar']!s:5} {r['latencia_s']:.2f} s  {tk}")
    validas = sum(1 for r in REGISTRO if r["etiqueta"] is not None)
    print(f"\nválidas: {validas}/{len(REGISTRO)}  latencia media: "
          f"{sum(r['latencia_s'] for r in REGISTRO)/len(REGISTRO):.2f} s")
    print("\nregistro (última entrada):")
    print(json.dumps(REGISTRO[-1], ensure_ascii=False, indent=2))
