"""Estrategias de decoding sobre la misma distribución de GPT-2.

Muestra, para un mismo prefijo, qué produce greedy, temperature, top-k y top-p,
y cuánto varía la salida entre corridas. Ejecutar con transformers y torch.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.manual_seed(0)
tok = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2", dtype=torch.float32)
model.eval()

prefijo = "The software architect opened the report and"
ids = tok(prefijo, return_tensors="pt").input_ids

configs = {
    "greedy": dict(do_sample=False),
    "temperature=0.2": dict(do_sample=True, temperature=0.2),
    "temperature=1.5": dict(do_sample=True, temperature=1.5),
    "top-k=10": dict(do_sample=True, top_k=10, temperature=1.0),
    "top-p=0.9": dict(do_sample=True, top_p=0.9, top_k=0, temperature=1.0),
}

for nombre, cfg in configs.items():
    print(f"\n=== {nombre} ===")
    salidas = set()
    for corrida in range(3):
        out = model.generate(ids, max_new_tokens=15, pad_token_id=tok.eos_token_id, **cfg)
        texto = tok.decode(out[0, ids.shape[1]:])
        salidas.add(texto)
        print(f"  corrida {corrida + 1}: {texto!r}")
    print(f"  salidas distintas en 3 corridas: {len(salidas)}")
