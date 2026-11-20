"""Compara modelos de control sobre el mismo caso y el mismo gold set de la semana 12.

Sistemas:
* single_agent, handoffs y routing_determinista de week-12/examples/topologias.py
  (Agents SDK: el modelo decide el flujo; en routing, el código decide la ruta y el
  modelo lo demás);
* grafo: week-13/examples/grafo_soporte.py (LangGraph: el código decide ruta,
  validación, reintento, aprobación y side effect; el modelo decide dentro de sus nodos).

Mismo backend, mismas funciones de negocio, los seis tickets g1 a g6 de la semana 12.
Se mide por ticket: ruta correcta, tool esperada ejecutada, llamadas al modelo,
tokens, latencia. Aparte: líneas de código y las columnas cualitativas (quién decide
el flujo, debugging, reanudación) que van en la tabla de la sesión.

La pregunta que responde la tabla es "¿qué modelo de control encaja con este sistema?"
y no "¿cuál framework es mejor?".

Uso:  .venv/bin/python course/week-13/examples/comparar_control.py [corridas]
Escribe ../slides/resultados.json.
"""
from __future__ import annotations

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "week-12" / "examples"))
sys.path.insert(0, str(HERE.parents[1] / "week-11" / "examples"))
sys.path.insert(0, str(HERE.parents[1] / "shared"))

import facturio_tools as ft  # noqa: E402
import grafo_soporte as gs  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402
from langgraph.types import Command  # noqa: E402

try:
    import topologias as tp  # semana 12
except ImportError:
    tp = None

FOLIO = list(ft.CARGOS)[0]
# El mini gold set de la semana 12 (comparar_topologias.py): ticket, especialista esperado, tool esperada.
GOLD = [
    {"id": "g1", "ticket": f"¿Cuál es el estado de la factura {FOLIO}?", "esperado": "facturacion", "tool": "consultar_factura"},
    {"id": "g2", "ticket": "Consulta el plan del usuario u002 y dime cuántas facturas al mes incluye.", "esperado": "facturacion", "tool": "consultar_plan"},
    {"id": "g3", "ticket": "El cargo PAY-00012348 me aparece duplicado, ¿me lo van a devolver?", "esperado": "facturacion", "tool": "consultar_factura"},
    {"id": "g4", "ticket": "No puedo iniciar sesión: el código 2FA nunca llega.", "esperado": "acceso", "tool": "buscar_documentacion"},
    {"id": "g5", "ticket": "Al exportar a PDF me sale el error E-4001.", "esperado": "tecnico", "tool": "buscar_documentacion"},
    {"id": "g6", "ticket": "Invité a un colega hace una semana y dice que el enlace de invitación ya no sirve.", "esperado": "acceso", "tool": "buscar_documentacion"},
]
SISTEMAS_SDK = ["single_agent", "handoffs", "routing_determinista"]


# ------------------------------------------------------------------ el modelo decide el flujo (semana 12)
def correr_sdk(topologia: str, consola, tarea: dict) -> dict:
    ft.reiniciar_estado()
    f = asyncio.run(tp.ejecutar(topologia, tarea["ticket"], consola))
    atendio = (f.get("atendio") or "").lower()
    ruta_ok = None if topologia == "single_agent" else atendio == tarea["esperado"]
    return {"ruta_ok": ruta_ok, "tool_ok": tarea["tool"] in f["tools"], "calls": f["tools"],
            "llamadas": f["llamadas_modelo"], "tokens_in": f["input_tokens"], "tokens_out": f["output_tokens"],
            "latencia_s": f["latencia_s"], "respuesta": f["respuesta"][:160], "error": f.get("error")}


# ------------------------------------------------------------------ el código decide el flujo (semana 13)
def correr_grafo(app, tarea: dict, corrida: int) -> dict:
    ft.reiniciar_estado()
    gs.reiniciar_contador()
    config = {"configurable": {"thread_id": f"{tarea['id']}-{corrida}"}, "recursion_limit": 25}
    t0 = time.perf_counter()
    s = app.invoke(gs.estado_inicial(tarea["ticket"]), config)
    if "__interrupt__" in s:   # aprobación humana: se aprueba, como haría un operador en la comparación
        s = app.invoke(Command(resume={"aprobado": True, "quien": "operador", "motivo": "prueba"}), config)
    lat = time.perf_counter() - t0
    calls = list(s.get("tool_calls", []))
    if (s.get("reembolso") or {}).get("ejecutado"):
        calls.append("reembolsar")             # lo ejecutó el grafo por decisión del edge: cuenta como tool ejecutada
    if "escalar" in s.get("traza", []):
        calls.append("escalar_a_humano")
    return {"ruta_ok": s.get("categoria") == tarea["esperado"], "tool_ok": tarea["tool"] in calls, "calls": calls,
            "llamadas": gs.CONTADOR["llamadas"], "tokens_in": gs.CONTADOR["tokens_in"], "tokens_out": gs.CONTADOR["tokens_out"],
            "latencia_s": round(lat, 2), "respuesta": s.get("respuesta", "")[:160],
            "traza": s.get("traza"), "intentos": s.get("intentos"), "error": None}


def lineas_de_codigo(path: Path) -> int:
    return sum(1 for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#"))


def resumir(filas: list[dict]) -> dict:
    rutas = [f["ruta_ok"] for f in filas if f["ruta_ok"] is not None]
    return {"corridas": len(filas),
            "ruta_ok": round(sum(rutas) / len(rutas), 2) if rutas else None,
            "tool_ok": round(sum(f["tool_ok"] for f in filas) / len(filas), 2),
            "llamadas_media": round(statistics.mean(f["llamadas"] for f in filas), 2),
            "tokens_media": round(statistics.mean(f["tokens_in"] + f["tokens_out"] for f in filas)),
            "latencia_media_s": round(statistics.mean(f["latencia_s"] for f in filas), 2),
            "variabilidad_tools": round(sum(1 for t in {f["tarea"] for f in filas}
                                            if len({tuple(f["calls"]) for f in filas if f["tarea"] == t}) > 1)
                                        / len({f["tarea"] for f in filas}), 2),
            "errores": sum(1 for f in filas if f.get("error"))}


def main(corridas: int = 3) -> dict:
    filas: list[dict] = []
    app = gs.construir_grafo(checkpointer=InMemorySaver())
    consola = tp.activar_tracing() if (tp is not None and gs.CFG["local"]) else None
    if tp is not None and consola is None:
        print("Con llave: el trace del SDK va al dashboard; se omiten las topologías de la semana 12 en esta corrida.")

    for tarea in GOLD:
        for c in range(1, corridas + 1):
            r = correr_grafo(app, tarea, c)
            filas.append({"tarea": tarea["id"], "sistema": "grafo", "corrida": c, **r})
            print(f"{tarea['id']} grafo               #{c}: ruta={r['ruta_ok']!s:<5} tool={r['tool_ok']!s:<5} calls={r['calls']} "
                  f"llamadas={r['llamadas']} tokens={r['tokens_in']}+{r['tokens_out']} lat={r['latencia_s']} traza={r.get('traza')}")
            if consola is not None:
                for topo in SISTEMAS_SDK:
                    r = correr_sdk(topo, consola, tarea)
                    filas.append({"tarea": tarea["id"], "sistema": topo, "corrida": c, **r})
                    print(f"{tarea['id']} {topo:<20}#{c}: ruta={r['ruta_ok']!s:<5} tool={r['tool_ok']!s:<5} calls={r['calls']} "
                          f"llamadas={r['llamadas']} tokens={r['tokens_in']}+{r['tokens_out']} lat={r['latencia_s']}")

    sistemas = [s for s in SISTEMAS_SDK + ["grafo"] if any(f["sistema"] == s for f in filas)]
    resultado = {
        "backend": gs.CFG["model"], "corridas_por_tarea": corridas, "gold": GOLD, "sistemas": sistemas,
        "resumen": {s: resumir([f for f in filas if f["sistema"] == s]) for s in sistemas},
        "por_tarea": {t["id"]: {s: round(statistics.mean(f["tool_ok"] for f in filas if f["sistema"] == s and f["tarea"] == t["id"]), 2)
                                for s in sistemas} for t in GOLD},
        "tokens_por_tarea": {t["id"]: {s: round(statistics.mean(f["tokens_in"] + f["tokens_out"] for f in filas if f["sistema"] == s and f["tarea"] == t["id"]))
                                       for s in sistemas} for t in GOLD},
        "loc": {"topologias (week-12/examples/topologias.py)": lineas_de_codigo(HERE.parents[1] / "week-12" / "examples" / "topologias.py"),
                "agente único (week-11/examples/agente_sdk.py)": lineas_de_codigo(HERE.parents[1] / "week-11" / "examples" / "agente_sdk.py"),
                "grafo (week-13/examples/grafo_soporte.py)": lineas_de_codigo(HERE / "grafo_soporte.py")},
        "filas": filas,
    }
    destino = HERE.parent / "slides" / "resultados.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in resultado.items() if k not in ("filas", "gold")}, ensure_ascii=False, indent=1))
    return resultado


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
