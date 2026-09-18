"""Un chat es texto con marcadores especiales. El modelo sigue prediciendo el siguiente token.

Este script muestra el template renderizado de Qwen2.5-Instruct, lo tokeniza y demuestra que
enviar ese texto plano con generate() produce la misma respuesta que usar el template.

Ejecutar:  python chat_template_inspect.py
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

NOMBRE = "Qwen/Qwen2.5-0.5B-Instruct"

tok = AutoTokenizer.from_pretrained(NOMBRE)
modelo = AutoModelForCausalLM.from_pretrained(NOMBRE, dtype=torch.float32)
modelo.eval()

mensajes = [
    {"role": "system", "content": "Eres un asistente breve. Respondes en una oración."},
    {"role": "user", "content": "¿Qué es un token?"},
]

# 1. El template convierte la lista de mensajes en un solo string con marcadores.
texto = tok.apply_chat_template(mensajes, add_generation_prompt=True, tokenize=False)
print("TEMPLATE RENDERIZADO\n" + "-" * 40)
print(texto)

# 2. Los marcadores son tokens especiales del vocabulario, con ID propio.
ids = tok(texto, return_tensors="pt").input_ids
print("\nPRIMEROS 12 TOKENS\n" + "-" * 40)
for i in ids[0, :12].tolist():
    print(f"{i:>7}  {tok.decode([i])!r}")
print(f"... total: {ids.shape[1]} tokens")

# 3. El modelo genera a partir de ese texto plano. No hay ninguna otra ruta de entrada.
with torch.no_grad():
    out = modelo.generate(ids, max_new_tokens=60, do_sample=False, pad_token_id=tok.eos_token_id)
print("\nRESPUESTA\n" + "-" * 40)
print(tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True))

# 4. Escribir el template a mano produce lo mismo. El "chat" es una convención de formato.
a_mano = ("<|im_start|>system\nEres un asistente breve. Respondes en una oración.<|im_end|>\n"
          "<|im_start|>user\n¿Qué es un token?<|im_end|>\n"
          "<|im_start|>assistant\n")
ids2 = tok(a_mano, return_tensors="pt").input_ids
with torch.no_grad():
    out2 = modelo.generate(ids2, max_new_tokens=60, do_sample=False, pad_token_id=tok.eos_token_id)
print("\nMISMA RESPUESTA CON EL TEMPLATE ESCRITO A MANO:",
      torch.equal(out[0, ids.shape[1]:], out2[0, ids2.shape[1]:]))
