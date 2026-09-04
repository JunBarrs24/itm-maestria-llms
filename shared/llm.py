"""Cliente mínimo con backend intercambiable.

Dos backends con la misma interfaz:

* "openai": OpenAI Responses API. Requiere OPENAI_API_KEY en el entorno.
* "local": un modelo instruction-tuned pequeño de Hugging Face. Sin llave,
  sin costo, con menor calidad. Sirve para Colab sin créditos y para verificar
  notebooks sin gastar.

La interfaz expone lo mínimo que el curso necesita: mensajes de entrada,
texto de salida, tokens consumidos y latencia. Todo lo demás (schemas,
validación, reintentos) se construye encima, a la vista del estudiante.

    from llm import LLM
    llm = LLM(backend="openai", model="gpt-5-mini")
    r = llm.chat(system="Eres un clasificador.", user="Hola")
    print(r.text, r.input_tokens, r.output_tokens, r.latencia_s)
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass


@dataclass
class Respuesta:
    text: str
    input_tokens: int
    output_tokens: int
    latencia_s: float
    model: str
    raw: object = None


class LLM:
    def __init__(self, backend: str = "openai", model: str | None = None, **kw):
        self.backend = backend
        if backend == "openai":
            from openai import OpenAI
            self.model = model or "gpt-5-mini"
            self.client = OpenAI()  # lee OPENAI_API_KEY del entorno
        elif backend == "local":
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.model = model or "Qwen/Qwen2.5-0.5B-Instruct"
            self.tok = AutoTokenizer.from_pretrained(self.model)
            self.net = AutoModelForCausalLM.from_pretrained(
                self.model, dtype=torch.float32
            )
            self.net.eval()
            self.max_new_tokens = kw.get("max_new_tokens", 256)
        else:
            raise ValueError(f"backend desconocido: {backend}")

    def chat(self, user: str, system: str | None = None, temperature: float = 0.0,
             max_output_tokens: int | None = None, **kw) -> Respuesta:
        inicio = time.perf_counter()
        if self.backend == "openai":
            params = dict(model=self.model, input=user)
            if system:
                params["instructions"] = system
            if max_output_tokens:
                params["max_output_tokens"] = max_output_tokens
            # Los reasoning models ignoran temperature; se envía solo si aplica.
            if not self.model.startswith(("gpt-5", "o")):
                params["temperature"] = temperature
            params.update(kw)
            resp = self.client.responses.create(**params)
            return Respuesta(
                text=resp.output_text,
                input_tokens=resp.usage.input_tokens,
                output_tokens=resp.usage.output_tokens,
                latencia_s=time.perf_counter() - inicio,
                model=self.model,
                raw=resp,
            )
        # backend local
        import torch
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": user})
        # transformers 5.x: se tokeniza en dos pasos para obtener un tensor.
        texto = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        ids = self.tok(texto, return_tensors="pt").input_ids
        with torch.no_grad():
            out = self.net.generate(
                ids,
                max_new_tokens=max_output_tokens or self.max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                pad_token_id=self.tok.eos_token_id,
            )
        nuevos = out[0, ids.shape[1]:]
        return Respuesta(
            text=self.tok.decode(nuevos, skip_special_tokens=True).strip(),
            input_tokens=int(ids.shape[1]),
            output_tokens=int(nuevos.shape[0]),
            latencia_s=time.perf_counter() - inicio,
            model="local",
            raw=None,
        )


def backend_disponible() -> str:
    """'openai' si hay llave en el entorno; 'local' en caso contrario."""
    return "openai" if os.environ.get("OPENAI_API_KEY") else "local"
