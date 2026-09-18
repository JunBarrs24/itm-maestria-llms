"""Material opcional de la semana 3: fine-tuning con LoRA sobre Qwen2.5-0.5B.

No forma parte de la sesión ni de la práctica. Sirve para quien necesite afinar
un modelo abierto en su tesis y quiera ver el mecanismo completo en un script
que cabe en Colab gratuito (GPU T4) o corre lento en CPU.

Qué hace:
  1. Construye un dataset pequeño de instrucciones de la mesa de soporte de
     Facturio (clasificación de tickets en el formato de chat de Qwen).
  2. Congela el modelo base y agrega adaptadores LoRA a las matrices de atención.
  3. Entrena unos cientos de pasos con next-token prediction sobre la respuesta.
  4. Compara base, base + LoRA e instruct sobre tickets que no vio en el
     entrenamiento, con la misma métrica de la semana 4 (accuracy de categoría).
  5. Guarda el adaptador (unos MB) por separado del modelo.

Cuándo tiene sentido LoRA (slide 20): comportamiento o formato muy específico,
en volumen alto, con dataset propio de calidad. Rara vez para agregar
conocimiento. Antes de afinar, medir que prompting (semana 4) y RAG (5 a 7)
no bastan.

Uso:
    pip install -q transformers peft datasets accelerate torch
    python lora_opcional.py            # entrena y evalúa
    python lora_opcional.py --pasos 50 # más corto, para probar el flujo
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

BASE = "Qwen/Qwen2.5-0.5B"
INSTRUCT = "Qwen/Qwen2.5-0.5B-Instruct"
CATEGORIAS = ["facturacion", "acceso", "error_tecnico", "solicitud_funcion", "otro"]
SISTEMA = ("Eres el clasificador de tickets de la mesa de soporte de Facturio. "
           "Responde únicamente con una de estas categorías: " + ", ".join(CATEGORIAS) + ".")

# ---------------------------------------------------------------- dataset
# Tickets escritos para el ejercicio, distintos de los 50 de shared/datasets.
# En un caso real el dataset sale de tickets históricos etiquetados por el equipo.
ENTRENAMIENTO = [
    ("Me cobraron la mensualidad dos veces en agosto.", "facturacion"),
    ("Quiero cambiar el RFC que aparece en mis facturas.", "facturacion"),
    ("¿Pueden enviarme la factura de julio con uso de CFDI G03?", "facturacion"),
    ("El cargo de este mes no coincide con mi plan.", "facturacion"),
    ("Necesito cancelar la suscripción antes del siguiente cobro.", "facturacion"),
    ("Quiero pagar por transferencia en vez de tarjeta.", "facturacion"),
    ("Mi contraseña nueva no funciona y no puedo entrar.", "acceso"),
    ("La cuenta quedó bloqueada por intentos fallidos.", "acceso"),
    ("No me llega el código de dos factores por SMS.", "acceso"),
    ("Perdí el correo con el que me registré, ¿cómo recupero la cuenta?", "acceso"),
    ("Mi sesión se cierra sola cada pocos minutos.", "acceso"),
    ("No puedo entrar desde la red de la oficina, desde casa sí.", "acceso"),
    ("Al exportar a PDF las gráficas salen vacías.", "error_tecnico"),
    ("La aplicación se cierra al abrir la pestaña de reportes.", "error_tecnico"),
    ("El botón de guardar no responde en Safari.", "error_tecnico"),
    ("El buscador no encuentra registros con acentos.", "error_tecnico"),
    ("Los totales del dashboard no cuadran con el reporte descargado.", "error_tecnico"),
    ("El correo de invitación a un usuario nuevo nunca llega.", "error_tecnico"),
    ("Estaría bien poder exportar a Excel además de PDF.", "solicitud_funcion"),
    ("¿Podrían agregar modo oscuro?", "solicitud_funcion"),
    ("Me gustaría silenciar notificaciones por horario.", "solicitud_funcion"),
    ("Sugerencia: permitir adjuntos de más de 25 MB.", "solicitud_funcion"),
    ("Sería útil una API para integrar con nuestro ERP.", "solicitud_funcion"),
    ("Propongo sincronizar vencimientos con Google Calendar.", "solicitud_funcion"),
    ("¿Tienen oficina en Guadalajara?", "otro"),
    ("Gracias, el soporte de la semana pasada fue excelente.", "otro"),
    ("¿Cuál es el horario de atención telefónica?", "otro"),
    ("¿Cómo cambio el idioma de la interfaz?", "otro"),
    ("¿Me pueden mandar el contrato de servicio en PDF?", "otro"),
    ("¿Puedo tener dos administradores en la misma cuenta?", "otro"),
]
PRUEBA = [
    ("Aparece un cargo de 899 pesos y mi plan es el básico.", "facturacion"),
    ("La factura de septiembre tiene mal la razón social.", "facturacion"),
    ("Dice que mi contraseña es incorrecta aunque la acabo de cambiar.", "acceso"),
    ("Me pide un código de autenticación que nunca recibo.", "acceso"),
    ("La pantalla de carga se queda en 99 % y no termina.", "error_tecnico"),
    ("El enlace del manual devuelve error 404.", "error_tecnico"),
    ("Quisiera un resumen semanal por correo con la actividad del equipo.", "solicitud_funcion"),
    ("¿Pueden agregar colores a las etiquetas?", "solicitud_funcion"),
    ("¿Tienen descuento para escuelas?", "otro"),
    ("Quiero eliminar mi cuenta y todos mis datos.", "otro"),
]


def mensajes(texto: str, categoria: str | None = None) -> list[dict]:
    m = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": f"Ticket: {texto}"}]
    if categoria is not None:
        m.append({"role": "assistant", "content": categoria})
    return m


def preparar_dataset(tok) -> Dataset:
    """Cada ejemplo se tokeniza con el chat template; la pérdida solo se calcula
    sobre los tokens de la respuesta (los del prompt llevan etiqueta -100)."""
    filas = []
    for texto, cat in ENTRENAMIENTO:
        prompt = tok.apply_chat_template(mensajes(texto), add_generation_prompt=True, tokenize=False)
        completo = prompt + cat + tok.eos_token
        ids_prompt = tok(prompt, add_special_tokens=False).input_ids
        ids = tok(completo, add_special_tokens=False).input_ids
        labels = [-100] * len(ids_prompt) + ids[len(ids_prompt):]
        filas.append({"input_ids": ids, "attention_mask": [1] * len(ids), "labels": labels})
    return Dataset.from_list(filas)


def collate(batch, pad_id: int):
    n = max(len(b["input_ids"]) for b in batch)
    def rellenar(v, valor): return v + [valor] * (n - len(v))
    return {
        "input_ids": torch.tensor([rellenar(b["input_ids"], pad_id) for b in batch]),
        "attention_mask": torch.tensor([rellenar(b["attention_mask"], 0) for b in batch]),
        "labels": torch.tensor([rellenar(b["labels"], -100) for b in batch]),
    }


# ---------------------------------------------------------------- evaluación
@torch.no_grad()
def clasificar(modelo, tok, texto: str, usar_template: bool = True) -> str:
    if usar_template:
        prompt = tok.apply_chat_template(mensajes(texto), add_generation_prompt=True, tokenize=False)
    else:  # el base sin template: texto plano
        prompt = f"{SISTEMA}\nTicket: {texto}\nCategoría:"
    ids = tok(prompt, return_tensors="pt").input_ids.to(modelo.device)
    out = modelo.generate(ids, max_new_tokens=6, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True).strip()


def evaluar(nombre: str, modelo, tok, usar_template: bool = True) -> float:
    aciertos = 0
    for texto, esperado in PRUEBA:
        salida = clasificar(modelo, tok, texto, usar_template)
        ok = salida.lower().startswith(esperado)
        aciertos += ok
        print(f"  [{nombre}] {'ok ' if ok else 'X  '} {esperado:18s} <- {salida[:40]!r}")
    acc = aciertos / len(PRUEBA)
    print(f"  [{nombre}] accuracy {acc:.2f}\n")
    return acc


# ---------------------------------------------------------------- principal
def main(pasos: int, rango: int, salida: str):
    dispositivo = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.float16 if dispositivo == "cuda" else torch.float32
    print(f"dispositivo: {dispositivo}")

    tok = AutoTokenizer.from_pretrained(BASE)
    tok.pad_token = tok.eos_token

    # 1. Línea base: el modelo base con texto plano y con template
    base = AutoModelForCausalLM.from_pretrained(BASE, dtype=dtype).to(dispositivo).eval()
    print("Base, prompt plano:")
    acc_base = evaluar("base", base, tok, usar_template=False)

    # 2. LoRA sobre el base
    cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=rango,                  # rango de las matrices: 8 a 64 es lo usual
        lora_alpha=2 * rango,     # escala del adaptador
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # las matrices de atención
    )
    modelo = get_peft_model(base, cfg)
    modelo.print_trainable_parameters()   # ~0.2 % del total con r=16
    modelo.train()

    ds = preparar_dataset(tok)
    args = TrainingArguments(
        output_dir=salida, max_steps=pasos, per_device_train_batch_size=4,
        learning_rate=2e-4, logging_steps=10, save_strategy="no", report_to=[],
        fp16=(dtype == torch.float16), use_cpu=(dispositivo == "cpu"),
    )
    trainer = Trainer(model=modelo, args=args, train_dataset=ds,
                      data_collator=lambda b: collate(b, tok.pad_token_id))
    t0 = time.time()
    trainer.train()
    print(f"entrenamiento: {time.time() - t0:.0f} s, {pasos} pasos, {len(ENTRENAMIENTO)} ejemplos\n")

    modelo.eval()
    print("Base + LoRA, con template:")
    acc_lora = evaluar("base+lora", modelo, tok)
    modelo.save_pretrained(salida)   # solo el adaptador
    peso = sum(p.stat().st_size for p in Path(salida).rglob("*") if p.is_file()) / 1e6
    print(f"adaptador guardado en {salida}: {peso:.1f} MB (el base pesa ~1,000 MB)\n")

    # 3. El instruct oficial, para comparar
    instruct = AutoModelForCausalLM.from_pretrained(INSTRUCT, dtype=dtype).to(dispositivo).eval()
    print("Instruct oficial, con template:")
    acc_instruct = evaluar("instruct", instruct, tok)

    resumen = {"base_prompt_plano": acc_base, "base_mas_lora": acc_lora, "instruct": acc_instruct,
               "pasos": pasos, "rango": rango, "ejemplos": len(ENTRENAMIENTO)}
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    print("\nLectura: LoRA con 30 ejemplos enseña el formato y las categorías del dominio; no agrega conocimiento. "
          "Si prompting con few-shot (semana 4) da la misma accuracy, LoRA no se justifica.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=int, default=150)
    ap.add_argument("--rango", type=int, default=16)
    ap.add_argument("--salida", default="/tmp/lora_facturio")
    a = ap.parse_args()
    random.seed(0); torch.manual_seed(0)
    main(a.pasos, a.rango, a.salida)
