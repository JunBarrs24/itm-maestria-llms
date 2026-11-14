"""Compara el loop manual de la semana 10 con el Agents SDK sobre el mismo mini gold set.

Seis tareas de la mesa de soporte, cada una con las tools esperadas y un criterio de
éxito verificable. Se corren N veces con cada implementación y se tabula: éxito,
tools correctas, iteraciones o turnos, tokens, latencia y líneas de código.

Uso:  .venv/bin/python course/week-11/examples/comparar_manual_sdk.py [corridas]
Escribe slides/resultados.json.
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
sys.path.insert(0, str(HERE.parents[1] / "week-10" / "examples"))
sys.path.insert(0, str(HERE.parents[1] / "shared"))

import agente_sdk as sdk  # noqa: E402
import facturio_tools as ft  # noqa: E402
from tracing_consola import activar_tracing_consola  # noqa: E402

try:
    import agent_loop as manual  # semana 10
except ImportError:
    manual = None


def definiciones_sdk(ft_mod=None) -> list[dict]:
    """Las mismas definiciones de tools que usa el SDK, en formato Chat Completions.

    Control del experimento: ambos sistemas reciben descripciones e instrucciones
    idénticas, así que la comparación es del mecanismo (loop manual vs runtime) y
    no de la redacción de las tools. Con un modelo pequeño, la descripción de la
    tool cambia más la selección que el runtime: eso también se muestra en clase."""
    return [{"type": "function", "function": {"name": t.name, "description": t.description,
                                              "parameters": t.params_json_schema}} for t in sdk.TOOLS]


if manual:
    manual.tools_chat = definiciones_sdk

FOLIOS = list(ft.CARGOS)
GOLD = [
    {"id": "t1", "tarea": f"¿Cuál es el estado de la factura {FOLIOS[0]}?",
     "tools": ["consultar_factura"], "exito": lambda r, calls: "consultar_factura" in calls},
    {"id": "t2", "tarea": "Consulta el plan del usuario u001 y dime su límite de proyectos y cuántos usa.",
     "tools": ["consultar_plan"], "exito": lambda r, calls: "consultar_plan" in calls},
    {"id": "t3", "tarea": "Busca en la documentación cuántos días tengo para pedir un reembolso y dime el plazo.",
     "tools": ["buscar_documentacion"], "exito": lambda r, calls: "buscar_documentacion" in calls},
    {"id": "t4", "tarea": f"Reembolsa 300 pesos de la factura {FOLIOS[0]} por cargo duplicado.",
     "tools": ["reembolsar"], "exito": lambda r, calls: "reembolsar" in calls},
    {"id": "t5", "tarea": "Quiero eliminar mi cuenta y todos mis datos hoy mismo; si no puedes hacerlo, escala a un humano.",
     "tools": ["escalar_a_humano", "buscar_documentacion"], "exito": lambda r, calls: bool(set(calls) & {"escalar_a_humano", "buscar_documentacion"})},
    {"id": "t6", "tarea": "Busca en la documentación el horario de atención de soporte.",
     "tools": ["buscar_documentacion"], "exito": lambda r, calls: "buscar_documentacion" in calls},
]


def correr_manual(tarea: str) -> dict:
    t0 = time.perf_counter()
    res = manual.correr_agente(tarea, ft=ft, max_iteraciones=6, aprobar=lambda n, a: True, max_tokens=200,
                               instrucciones=sdk.INSTRUCCIONES)
    calls = [c[0] for c in res.tool_calls]
    return {"respuesta": res.respuesta or "", "calls": calls, "pasos": res.iteraciones,
            "tokens_in": res.tokens_in, "tokens_out": res.tokens_out, "latencia": time.perf_counter() - t0,
            "stop": res.motivo_stop}


def correr_sdk(agente, consola, tarea: str) -> dict:
    t0 = time.perf_counter()
    try:
        r = asyncio.run(sdk.correr(agente, tarea, aprobar=lambda n, a: True, max_turns=6))
        respuesta = str(r.final_output or "")
        stop = "respuesta_final"
    except Exception as e:  # MaxTurnsExceeded u otro
        respuesta, stop = "", type(e).__name__
    resumen = consola.resumen() or {}
    return {"respuesta": respuesta, "calls": resumen.get("tool_calls", []), "pasos": resumen.get("llamadas_modelo", 0),
            "tokens_in": resumen.get("input_tokens", 0), "tokens_out": resumen.get("output_tokens", 0),
            "latencia": time.perf_counter() - t0, "stop": stop}


def lineas_de_codigo(path: Path) -> int:
    return sum(1 for l in path.read_text(encoding="utf-8").splitlines() if l.strip() and not l.strip().startswith("#"))


def main(corridas: int = 3):
    consola = activar_tracing_consola()
    agente = sdk.construir_agente(con_guardrails=True)
    filas = []
    for g in GOLD:
        for sistema in (["manual"] if manual else []) + ["sdk"]:
            for k in range(corridas):
                r = correr_manual(g["tarea"]) if sistema == "manual" else correr_sdk(agente, consola, g["tarea"])
                ok = bool(g["exito"](r["respuesta"], r["calls"]))
                tools_ok = set(g["tools"]) & set(r["calls"]) == set(g["tools"]) if g["id"] != "t5" else ok
                filas.append({"tarea": g["id"], "sistema": sistema, "corrida": k + 1, "exito": ok, "tools_ok": bool(tools_ok),
                              "calls": r["calls"], "pasos": r["pasos"], "tokens_in": r["tokens_in"], "tokens_out": r["tokens_out"],
                              "latencia_s": round(r["latencia"], 2), "stop": r["stop"]})
                print(f"{g['id']} {sistema:6s} #{k+1} exito={ok} tools={r['calls']} pasos={r['pasos']} tok={r['tokens_in']}+{r['tokens_out']} {r['latencia']:.1f}s {r['stop']}", flush=True)
    resumen = {}
    for sistema in {f["sistema"] for f in filas}:
        fs = [f for f in filas if f["sistema"] == sistema]
        resumen[sistema] = {
            "corridas": len(fs),
            "exito": round(sum(f["exito"] for f in fs) / len(fs), 2),
            "tools_ok": round(sum(f["tools_ok"] for f in fs) / len(fs), 2),
            "pasos_media": round(statistics.mean(f["pasos"] for f in fs), 2),
            "tokens_media": round(statistics.mean(f["tokens_in"] + f["tokens_out"] for f in fs)),
            "latencia_media_s": round(statistics.mean(f["latencia_s"] for f in fs), 2),
            "variabilidad_tools": round(sum(1 for g in GOLD if len({tuple(f["calls"]) for f in fs if f["tarea"] == g["id"]}) > 1) / len(GOLD), 2),
        }
    loc = {"manual (week-10/examples/agent_loop.py)": lineas_de_codigo(HERE.parents[1] / "week-10" / "examples" / "agent_loop.py") if manual else None,
           "sdk (week-11/examples/agente_sdk.py)": lineas_de_codigo(HERE / "agente_sdk.py")}
    por_tarea = {}
    for g in GOLD:
        por_tarea[g["id"]] = {s: round(sum(f["exito"] for f in filas if f["tarea"] == g["id"] and f["sistema"] == s) / max(1, sum(1 for f in filas if f["tarea"] == g["id"] and f["sistema"] == s)), 2) for s in resumen}
    salida = {"backend": sdk.CFG["model"], "corridas_por_tarea": corridas, "resumen": resumen, "por_tarea": por_tarea, "loc": loc, "filas": filas}
    out = HERE.parent / "slides" / "resultados.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"resumen": resumen, "por_tarea": por_tarea, "loc": loc}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
