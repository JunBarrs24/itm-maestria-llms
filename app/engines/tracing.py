"""Los spans del SDK, en el formato del trace que la interfaz pinta.

El SDK emite un span cada vez que cierra una llamada al modelo (`response` con Responses API,
`generation` con Chat Completions), una tool (`function`), un guardrail, un handoff o un agente.
Este procesador los guarda por trace_id como entradas pequeñas; el motor las recoge al terminar.
Se suma al exportador de OpenAI: el mismo trace se ve en el dashboard de Traces.
"""
from __future__ import annotations

import json
from datetime import datetime

from agents.tracing import TracingProcessor, add_trace_processor


def _segundos(span) -> float:
    try:
        return (datetime.fromisoformat(span.ended_at) - datetime.fromisoformat(span.started_at)).total_seconds()
    except Exception:
        return 0.0


class TraceParaLaApp(TracingProcessor):
    def __init__(self):
        self.por_trace: dict[str, list[dict]] = {}

    def on_trace_start(self, t): self.por_trace.setdefault(t.trace_id, [])
    def on_trace_end(self, t): pass
    def on_span_start(self, span): pass
    def force_flush(self): pass
    def shutdown(self): pass

    def on_span_end(self, span):
        d = span.span_data
        entradas = self.por_trace.setdefault(span.trace_id, [])
        if d.type in ("response", "generation"):
            if d.type == "response":
                r = d.response
                if r is None:
                    return
                u = r.usage
                salida = [o.model_dump() for o in r.output]
                rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
                tin, tout = u.input_tokens, u.output_tokens
            else:
                u = d.usage or {}
                salida = list(d.output or [])
                det = u.get("output_tokens_details")
                rt = det.get("reasoning_tokens", 0) if isinstance(det, dict) else 0
                tin, tout = u.get("input_tokens", 0), u.get("output_tokens", 0)
            pide = [o.get("name") for o in salida if o.get("type") == "function_call"] + ["web_search" for o in salida if o.get("type") == "web_search_call"]
            for o in salida:   # las tools hospedadas no tienen span de function: se registran desde la respuesta
                if o.get("type") == "web_search_call":
                    accion = o.get("action") or {}
                    entradas.append({"tipo": "tool", "nombre": "web_search", "args": {"query": accion.get("query"), "tipo": accion.get("type")},
                                     "decision": "ejecutada por OpenAI (hosted)", "resultado": {"status": o.get("status"), "fuentes": [s.get("url") for s in (accion.get("sources") or [])][:5]}})
            resumen = [s.get("text", "") for o in salida if o.get("type") == "reasoning" for s in (o.get("summary") or [])]
            n = 1 + sum(1 for e in entradas if e["tipo"] == "modelo")
            entradas.append({"tipo": "modelo", "vuelta": n, "latencia_s": round(_segundos(span), 2), "input_tokens": tin,
                             "output_tokens": tout, "reasoning_tokens": rt, "status": "sdk", "pide_tools": pide,
                             "resumen_razonamiento": resumen, "agente": self._agente_de(span, entradas)})
        elif d.type == "function":
            if d.output is None:
                return   # tool pendiente de aprobación: el SDK abre el span sin ejecutarla; el motor la registra como pausada
            try: args = json.loads(d.input or "{}")
            except Exception: args = {"raw": d.input}
            res = d.output
            if isinstance(res, str):
                try: res = json.loads(res)
                except Exception: pass
            entradas.append({"tipo": "tool", "nombre": d.name, "args": args, "decision": "ejecutada por el SDK",
                             "latencia_s": round(_segundos(span), 3), "resultado": res})
        elif d.type == "guardrail":
            entradas.append({"tipo": "guardrail", "nombre": d.name, "disparado": bool(d.triggered)})
        elif d.type == "handoff":
            entradas.append({"tipo": "handoff", "de": d.from_agent, "a": d.to_agent})
        elif d.type == "agent":
            entradas.append({"tipo": "agente", "nombre": d.name, "latencia_s": round(_segundos(span), 2), "span_id": span.span_id})

    def _agente_de(self, span, entradas) -> str | None:
        return None

    def tomar(self, trace_id: str) -> list[dict]:
        return self.por_trace.pop(trace_id, [])


PROCESADOR = TraceParaLaApp()
add_trace_processor(PROCESADOR)
