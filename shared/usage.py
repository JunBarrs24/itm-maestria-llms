"""Registro de uso y costo de llamadas a modelos.

Se usa desde la primera llamada a una API comercial (semana 4). Cada llamada
registra input tokens, output tokens, latencia y costo estimado. El costo se
calcula con una tabla de precios editable: los precios cambian, el mecanismo no.

Uso mínimo:

    from usage import UsageLog
    log = UsageLog()
    with log.track("clasificar", model="gpt-5-mini") as t:
        resp = client.responses.create(...)
        t.record(resp.usage.input_tokens, resp.usage.output_tokens)
    log.summary()
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# Precio en USD por millón de tokens (input, output). Editar según la tabla
# vigente del proveedor. Los nombres son ilustrativos; el helper acepta
# cualquier modelo y usa PRECIO_DEFAULT si no lo conoce.
PRECIOS_USD_POR_MILLON: dict[str, tuple[float, float]] = {
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5": (1.25, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
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
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def costo_usd(self) -> float:
        return costo_estimado(self.model, self.input_tokens, self.output_tokens)


@dataclass
class UsageLog:
    llamadas: list[Llamada] = field(default_factory=list)

    @contextmanager
    def track(self, etiqueta: str, model: str):
        llamada = Llamada(etiqueta=etiqueta, model=model)
        inicio = time.perf_counter()
        try:
            yield llamada
        except Exception as exc:  # se registra la falla y se propaga
            llamada.error = type(exc).__name__
            raise
        finally:
            llamada.latencia_s = time.perf_counter() - inicio
            self.llamadas.append(llamada)

    def por_etiqueta(self, etiqueta: str) -> list[Llamada]:
        return [c for c in self.llamadas if c.etiqueta == etiqueta]

    def totales(self, etiqueta: str | None = None) -> dict:
        calls = self.llamadas if etiqueta is None else self.por_etiqueta(etiqueta)
        n = len(calls)
        return {
            "llamadas": n,
            "errores": sum(1 for c in calls if c.error),
            "input_tokens": sum(c.input_tokens for c in calls),
            "output_tokens": sum(c.output_tokens for c in calls),
            "total_tokens": sum(c.total_tokens for c in calls),
            "latencia_media_s": (sum(c.latencia_s for c in calls) / n) if n else 0.0,
            "costo_usd": sum(c.costo_usd for c in calls),
        }

    def summary(self, etiqueta: str | None = None) -> str:
        t = self.totales(etiqueta)
        titulo = etiqueta or "todas las llamadas"
        lineas = [
            f"Resumen de uso ({titulo})",
            f"  llamadas:        {t['llamadas']}  (errores: {t['errores']})",
            f"  input tokens:    {t['input_tokens']}",
            f"  output tokens:   {t['output_tokens']}",
            f"  total tokens:    {t['total_tokens']}",
            f"  latencia media:  {t['latencia_media_s']:.2f} s",
            f"  costo estimado:  ${t['costo_usd']:.5f} USD",
        ]
        texto = "\n".join(lineas)
        print(texto)
        return texto

    def tabla(self):
        """Devuelve un DataFrame si pandas está disponible; si no, lista de dicts."""
        filas = [
            {
                "etiqueta": c.etiqueta,
                "model": c.model,
                "input": c.input_tokens,
                "output": c.output_tokens,
                "latencia_s": round(c.latencia_s, 3),
                "costo_usd": round(c.costo_usd, 6),
                "error": c.error,
            }
            for c in self.llamadas
        ]
        try:
            import pandas as pd
            return pd.DataFrame(filas)
        except ImportError:
            return filas
