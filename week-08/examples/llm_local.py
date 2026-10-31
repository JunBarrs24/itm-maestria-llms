"""Copia de course/shared/llm.py y course/shared/usage.py para la semana 8, con una
diferencia: el backend local elige dispositivo (cuda, mps o cpu) para que el
modelo de 1.5B responda en segundos. Los notebooks de la semana embeben este
archivo en una celda para correr en Colab sin clonar el repositorio.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# ----------------------------------------------------------------------------- uso y costo
PRECIOS_USD_POR_MILLON: dict[str, tuple[float, float]] = {
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5": (1.25, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "local": (0.0, 0.0),
}
PRECIO_DEFAULT = (1.0, 4.0)


def costo_estimado(model: str, input_tokens: int, output_tokens: int) -> float:
    p_in, p_out = PRECIOS_USD_POR_MILLON.get(model, PRECIO_DEFAULT)
    return (input_tokens * p_in + output_tokens * p_out) / 1_000_000


@dataclass
class Llamada:
    etiqueta: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latencia_s: float = 0.0
    error: str | None = None

    @property
    def costo_usd(self) -> float:
        return costo_estimado(self.model, self.input_tokens, self.output_tokens)

    @property
    def costo_si_gpt5mini(self) -> float:
        return costo_estimado("gpt-5-mini", self.input_tokens, self.output_tokens)


@dataclass
class UsageLog:
    llamadas: list[Llamada] = field(default_factory=list)

    @contextmanager
    def track(self, etiqueta: str, model: str):
        c = Llamada(etiqueta=etiqueta, model=model)
        t0 = time.perf_counter()
        try:
            yield c
        except Exception as exc:
            c.error = type(exc).__name__
            raise
        finally:
            c.latencia_s = time.perf_counter() - t0
            self.llamadas.append(c)

    def totales(self, etiqueta: str | None = None) -> dict:
        calls = [c for c in self.llamadas if etiqueta is None or c.etiqueta == etiqueta]
        n = len(calls)
        return {
            "llamadas": n,
            "input_tokens": sum(c.input_tokens for c in calls),
            "output_tokens": sum(c.output_tokens for c in calls),
            "latencia_total_s": round(sum(c.latencia_s for c in calls), 2),
            "latencia_media_s": round(sum(c.latencia_s for c in calls) / n, 2) if n else 0.0,
            "costo_usd": round(sum(c.costo_usd for c in calls), 5),
            "costo_si_gpt5mini_usd": round(sum(c.costo_si_gpt5mini for c in calls), 5),
        }

    def tabla(self):
        import pandas as pd
        etiquetas = []
        for c in self.llamadas:
            if c.etiqueta not in etiquetas:
                etiquetas.append(c.etiqueta)
        return pd.DataFrame([{"etiqueta": e, **self.totales(e)} for e in etiquetas])


# ----------------------------------------------------------------------------- cliente
@dataclass
class Respuesta:
    text: str
    input_tokens: int
    output_tokens: int
    latencia_s: float
    model: str
    raw: object = None


def elegir_dispositivo() -> str:
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class LLM:
    """Misma interfaz con dos backends: OpenAI Responses API o un modelo local."""

    def __init__(self, backend: str = "openai", model: str | None = None, **kw):
        self.backend = backend
        if backend == "openai":
            from openai import OpenAI
            self.model = model or "gpt-5-mini"
            self.client = OpenAI()  # lee OPENAI_API_KEY del entorno
        elif backend == "local":
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.model = model or "Qwen/Qwen2.5-1.5B-Instruct"
            self.device = kw.get("device") or elegir_dispositivo()
            self.tok = AutoTokenizer.from_pretrained(self.model)
            dtype = torch.float16 if self.device == "cuda" else torch.float32
            self.net = AutoModelForCausalLM.from_pretrained(self.model, dtype=dtype).to(self.device)
            self.net.eval()
            self.max_new_tokens = kw.get("max_new_tokens", 256)
            # Un modelo local en un proceso atiende una generación a la vez. El candado hace explícito
            # que la parallelization no acelera este backend; con una API remota sí, porque las llamadas se solapan.
            self._lock = threading.Lock()
        else:
            raise ValueError(f"backend desconocido: {backend}")

    def chat(self, user: str, system: str | None = None, temperature: float = 0.0,
             max_output_tokens: int | None = None, **kw) -> Respuesta:
        t0 = time.perf_counter()
        if self.backend == "openai":
            params = dict(model=self.model, input=user)
            if system:
                params["instructions"] = system
            if max_output_tokens:
                params["max_output_tokens"] = max_output_tokens
            # Reasoning models (gpt-5*, o*): gastan max_output_tokens en razonar; con "minimal" la respuesta
            # cabe en presupuestos pequeños. 
            # Ejercicio: probar: 
            # "none"    Sin razonamiento adicional. Menor latencia.
            # "minimal"    Razonamiento mínimo.
            # "low"    Razonamiento ligero.
            # "medium"    Razonamiento moderado.
            # "high"    Razonamiento profundo.
            # "xhigh"    Razonamiento muy profundo.
            # Summary: la cadena de razonamiento viaja cifrada (encrypted_content) y no se puede leer; se puede
            # pedir un resumen generado por el proveedor con reasoning["summary"]:
            # "auto"    El proveedor elige el nivel de detalle.
            # "concise"    Resumen breve.
            # "detailed"    Resumen paso a paso.
            # Ejemplo: params["reasoning"] = {"effort": "medium", "summary": "auto"}
            # Ver https://developers.openai.com/api/reference/resources/responses/methods/create#responses-create-reasoning
            # https://developers.openai.com/api/docs/models/gpt-5-mini (especifico de este modelo)
            # https://developers.openai.com/api/docs/guides/reasoning?api-mode=responses
            if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
                params["reasoning"] = {"effort": "minimal"}
            else:
                params["temperature"] = temperature
            params.update(kw)
            r = self.client.responses.create(**params)
            return Respuesta(r.output_text, r.usage.input_tokens, r.usage.output_tokens,
                             time.perf_counter() - t0, self.model, r)
        import torch
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
        texto = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        ids = self.tok(texto, return_tensors="pt").input_ids.to(self.device)
        with self._lock, torch.no_grad():
            out = self.net.generate(ids, max_new_tokens=max_output_tokens or self.max_new_tokens,
                                    do_sample=temperature > 0, temperature=temperature if temperature > 0 else None,
                                    pad_token_id=self.tok.eos_token_id)
        nuevos = out[0, ids.shape[1]:]
        return Respuesta(self.tok.decode(nuevos, skip_special_tokens=True).strip(),
                         int(ids.shape[1]), int(nuevos.shape[0]), time.perf_counter() - t0, "local")

    def parse(self, user: str, schema, system: str | None = None, max_output_tokens: int = 300,
              intentos: int = 2, temperature: float = 0.0):
        """Salida estructurada validada con un modelo Pydantic.
        Devuelve (instancia o None, Respuesta, número de llamadas)."""
        if self.backend == "openai":
            t0 = time.perf_counter()
            params = dict(model=self.model, input=user, text_format=schema, max_output_tokens=max_output_tokens)
            if system:
                params["instructions"] = system
            if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
                params["reasoning"] = {"effort": "minimal"}   # mismo criterio que en chat()
            r = self.client.responses.parse(**params)
            return r.output_parsed, Respuesta(r.output_text, r.usage.input_tokens, r.usage.output_tokens,
                                              time.perf_counter() - t0, self.model, r), 1
        from pydantic import ValidationError
        esquema = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        instr = ((system or "") + "\n\nResponde únicamente con un objeto JSON válido que cumpla este JSON Schema, "
                 f"sin texto adicional:\n{esquema}").strip()
        prompt, ultimo = user, None
        for i in range(1, intentos + 1):
            r = self.chat(prompt, system=instr, temperature=temperature, max_output_tokens=max_output_tokens)
            ultimo = r
            m = re.search(r"\{.*\}", r.text, re.S)
            try:
                if not m:
                    raise ValueError("la respuesta no contiene un objeto JSON")
                return schema.model_validate_json(m.group(0)), r, i
            except (ValidationError, ValueError) as e:
                prompt = f"{user}\n\nTu respuesta anterior no cumplió el schema: {str(e)[:300]}\nCorrige y responde solo con el JSON."
        return None, ultimo, intentos


def backend_disponible() -> str:
    return "openai" if os.environ.get("OPENAI_API_KEY") else "local"
