"""Procesador de tracing que imprime el árbol de una corrida en consola (canónico desde la semana 11).

El Agents SDK emite spans (agent, turn, generation, function, guardrail,
handoff) a los procesadores registrados. Por defecto los envía al dashboard
de OpenAI; sin llave, o para verlos en clase, se sustituye el exportador por
este procesador. El resultado es el artefacto de la semana:

    RUN Agent workflow
    ├── guardrail solo_soporte  triggered=False
    ├── generation  1.09 s  in=373 out=31
    ├── function consultar_factura({"folio": ...}) -> {...}
    ├── generation  1.48 s  in=512 out=56
    └── agent Soporte  2.57 s

Uso:
    from tracing_consola import activar_tracing_consola
    consola = activar_tracing_consola()       # sustituye el exportador de OpenAI
    ... Runner.run(...)
    consola.imprimir()                        # árbol de la última corrida
    consola.resumen()                         # llamadas, tokens, latencia, tools
"""
from __future__ import annotations

from datetime import datetime

from agents.tracing import TracingProcessor, set_trace_processors, set_tracing_disabled


def _segundos(span) -> float:
    try:
        return (datetime.fromisoformat(span.ended_at) - datetime.fromisoformat(span.started_at)).total_seconds()
    except Exception:
        return 0.0


class TracingConsola(TracingProcessor):
    """Guarda los spans de cada trace y los imprime como árbol."""

    def __init__(self, en_vivo: bool = False):
        self.en_vivo = en_vivo
        self.traces: list[dict] = []
        self._actual: dict | None = None

    # ---- interfaz del SDK
    def on_trace_start(self, trace):
        self._actual = {"nombre": trace.name, "id": trace.trace_id, "spans": []}
        if self.en_vivo:
            print(f"RUN {trace.name}")

    def on_trace_end(self, trace):
        if self._actual is not None:
            self.traces.append(self._actual)
        self._actual = None

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        fila = self._fila(span)
        if self._actual is not None:
            self._actual["spans"].append(fila)
        if self.en_vivo:
            print("  " + fila["texto"])

    def force_flush(self):
        pass

    def shutdown(self):
        pass

    # ---- utilidades
    def _fila(self, span) -> dict:
        d = span.span_data
        tipo = d.type
        usage = {}
        texto = tipo
        if tipo == "generation":
            usage = d.usage or {}
            texto = f"generation  {_segundos(span):5.2f} s  in={usage.get('input_tokens', 0)} out={usage.get('output_tokens', 0)}"
        elif tipo == "function":
            texto = f"function {d.name}({str(d.input)[:50]}) -> {str(d.output)[:50]}"
        elif tipo == "guardrail":
            texto = f"guardrail {d.name}  triggered={d.triggered}"
        elif tipo == "agent":
            texto = f"agent {d.name}  {_segundos(span):5.2f} s"
        elif tipo == "handoff":
            texto = f"handoff {getattr(d, 'from_agent', '?')} -> {getattr(d, 'to_agent', '?')}"
        elif tipo == "turn":
            texto = f"turn  {_segundos(span):5.2f} s"
        else:
            texto = f"{tipo}  {_segundos(span):5.2f} s"
        return {"tipo": tipo, "span_id": span.span_id, "parent_id": span.parent_id,
                "segundos": _segundos(span), "usage": usage, "texto": texto,
                "nombre": getattr(d, "name", None), "error": span.error}

    def ultimo(self) -> dict | None:
        return self.traces[-1] if self.traces else None

    def imprimir(self, trace: dict | None = None) -> None:
        t = trace or self.ultimo()
        if not t:
            print("(sin corridas)")
            return
        print(f"RUN {t['nombre']}")
        # los spans llegan en orden de cierre; se ordenan por jerarquía simple
        por_padre: dict = {}
        for s in t["spans"]:
            por_padre.setdefault(s["parent_id"], []).append(s)

        def rec(padre, nivel):
            hijos = por_padre.get(padre, [])
            for i, s in enumerate(hijos):
                pref = "└── " if i == len(hijos) - 1 else "├── "
                print("    " * nivel + pref + s["texto"] + ("  [ERROR]" if s["error"] else ""))
                rec(s["span_id"], nivel + 1)

        rec(None, 0)

    def resumen(self, trace: dict | None = None) -> dict:
        t = trace or self.ultimo()
        if not t:
            return {}
        gens = [s for s in t["spans"] if s["tipo"] == "generation"]
        funcs = [s for s in t["spans"] if s["tipo"] == "function"]
        ag = [s for s in t["spans"] if s["tipo"] == "agent"]
        return {
            "llamadas_modelo": len(gens),
            "input_tokens": sum(s["usage"].get("input_tokens", 0) for s in gens),
            "output_tokens": sum(s["usage"].get("output_tokens", 0) for s in gens),
            "tool_calls": [s["nombre"] for s in funcs],
            "guardrails_disparados": [s["nombre"] for s in t["spans"] if s["tipo"] == "guardrail" and "triggered=True" in s["texto"]],
            "latencia_s": round(max((s["segundos"] for s in ag), default=0.0), 2),
            "errores": sum(1 for s in t["spans"] if s["error"]),
        }


def activar_tracing_consola(en_vivo: bool = False) -> TracingConsola:
    """Sustituye los procesadores del SDK por la consola. Nada se envía a OpenAI."""
    consola = TracingConsola(en_vivo=en_vivo)
    set_tracing_disabled(False)
    set_trace_processors([consola])
    return consola


if __name__ == "__main__":
    print(__doc__)


# ------------------------------------------------------------------ extensión de la semana 12
import json as _json


class TracingContexto(TracingConsola):
    """El procesador base más la entrada de cada llamada al modelo, para medir qué recibió cada agente."""

    def _fila(self, span) -> dict:
        fila = super()._fila(span)
        if fila["tipo"] == "generation":
            fila["entrada"] = list(span.span_data.input or [])
        return fila


def activar_tracing_contexto() -> TracingContexto:
    consola = TracingContexto()
    set_tracing_disabled(False)
    set_trace_processors([consola])
    return consola


def contexto_que_viajo(trace: dict) -> dict[str, dict]:
    """Por agente: cuántos mensajes y caracteres recibió en su primera llamada al modelo, y qué roles."""
    por_id = {s["span_id"]: s for s in trace["spans"]}
    salida: dict[str, dict] = {}
    for s in trace["spans"]:
        if s["tipo"] != "generation":
            continue
        padre, agente = s["parent_id"], None
        while padre and padre in por_id:
            if por_id[padre]["tipo"] == "agent":
                agente = por_id[padre]["nombre"]
                break
            padre = por_id[padre]["parent_id"]
        if agente in salida:
            continue
        msgs = s.get("entrada", [])
        salida[agente or "?"] = {"mensajes": len(msgs),
                                 "caracteres": sum(len(_json.dumps(m, ensure_ascii=False)) for m in msgs),
                                 "input_tokens": s["usage"].get("input_tokens", 0),
                                 "roles": [m.get("role", m.get("type", "?")) for m in msgs]}
    return salida
