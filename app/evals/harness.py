"""Evaluación de agentes: el gold set, N corridas, los diseños que se pidan, el mismo modelo.

Mide task success, tools esperadas, tools prohibidas ejecutadas, guardrails de salida disparados,
vueltas, tokens, latencia, costo, variabilidad entre corridas y, si se pide, la calificación del juez.
Corre contra engines/turno.py directamente (sin HTTP), con side effects automáticos encendidos para
que la política de negocio sea la que decida.

Uso (desde app/):
    python -m evals.harness --disenos routing,modes,handoffs,handoffs_minimo --corridas 3 --juez
Costo: unas 100 corridas con gpt-5-mini, cerca de 0.10 USD; el juez agrega una llamada por corrida.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))

from context.session import Sesion            # noqa: E402
from data import facturio as db               # noqa: E402
from engines import turno                     # noqa: E402
from evals.gold import GOLD                   # noqa: E402


def correr(tarea: dict, diseno: str, proveedor: str, con_juez: bool) -> dict:
    con_plan = diseno.endswith("+plan")           # "routing+plan": el mismo diseño con la casilla de plan
    diseno = diseno.removesuffix("+plan")
    db.reiniciar_estado()
    s = Sesion()
    s.estado["usuario_id"] = tarea["usuario"]
    s.historial += [{"role": "user", "content": f"Soy el usuario {tarea['usuario']}."}, {"role": "assistant", "content": "Entendido."}]
    t0 = time.perf_counter()
    try:
        r = turno.responder(s, tarea["objetivo"], {"estrategia": "estado", "diseno": diseno, "side_effects": True, "effort": "minimal", "proveedor": proveedor, "con_plan": con_plan})
        if r.get("aprobacion_pendiente"):
            r = turno.decidir_aprobacion(s, True)
    except Exception as e:
        return {"exito": False, "tools_ok": False, "prohibida": False, "guardrail_salida": False, "vueltas": 0, "tokens": 0,
                "latencia_s": round(time.perf_counter() - t0, 2), "costo_usd": 0.0, "tools": [], "juez": None, "error": f"{type(e).__name__}: {e}"}
    ex = [(p["nombre"], p["args"], p["resultado"]) for p in r["trace"] if p["tipo"] == "tool"]
    # el grafo no llama tools del modelo: sus nodos cuentan como tools ejecutadas para el criterio
    for p in r["trace"]:
        if p["tipo"] == "nodo" and p["nombre"] in ("consultar", "reembolsar", "escalar"):
            nombre = {"consultar": "consultar_factura" if "cargo" in p["cambios"] else "consultar_plan", "reembolsar": "reembolsar", "escalar": "escalar_a_humano"}[p["nombre"]]
            ex.append((nombre, {}, p["cambios"].get("resultado_reembolso") or p["cambios"].get("ticket") or p["cambios"]))
            if p["nombre"] == "consultar" and "plan" in p["cambios"] and "cargo" in p["cambios"]:
                ex.append(("consultar_plan", {}, p["cambios"]["plan"]))
    usadas = {n for n, _, _ in ex}
    fila = {"exito": bool(tarea["exito"](r["respuesta"] or "", ex)), "tools_ok": tarea["tools"].issubset(usadas),
            "prohibida": any(n in tarea["prohibidas"] and isinstance(s_, dict) and s_.get("ejecutado") for n, _, s_ in ex),
            "guardrail_salida": any(p["tipo"] == "aviso" and "guardrail de salida" in p["mensaje"] for p in r["trace"]),
            "handoffs": sum(1 for p in r["trace"] if p["tipo"] == "handoff"), "skills": [p["nombre"] for p in r["trace"] if p["tipo"] == "skill"],
            "plan": next(({"pasos": len(p["pasos"]), "hechos": p["hechos"]} for p in r["trace"] if p["tipo"] == "plan"), None),
            "vueltas": sum(1 for p in r["trace"] if p["tipo"] == "modelo"), "tokens": r["uso"]["input_tokens"] + r["uso"]["output_tokens"],
            "latencia_s": r["uso"]["latencia_s"], "costo_usd": r["uso"]["costo_usd"], "tools": [n for n, _, _ in ex], "respuesta": (r["respuesta"] or "")[:300], "juez": None}
    if con_juez:
        from evals.judge import calificar
        fila["juez"] = calificar(tarea["objetivo"], r["respuesta"] or "", ex)
    return fila


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corridas", type=int, default=3)
    ap.add_argument("--disenos", default="routing,modes,handoffs,handoffs_minimo", help="también: orquestador, paralelo, grafo, y <diseño>+plan")
    ap.add_argument("--proveedor", default="openai")
    ap.add_argument("--juez", action="store_true")
    ap.add_argument("--salida", default=str(AQUI / "results" / "eval_resultados.json"))
    a = ap.parse_args()
    disenos = a.disenos.split(",")
    filas = []
    for diseno in disenos:
        for tarea in GOLD:
            corridas = [correr(tarea, diseno, a.proveedor, a.juez) for _ in range(a.corridas)]
            f = {"diseno": diseno, "proveedor": a.proveedor, "tarea": tarea["id"], "objetivo": tarea["objetivo"], "n": a.corridas,
                 "exito": sum(c["exito"] for c in corridas), "tools_ok": sum(c["tools_ok"] for c in corridas), "prohibida": sum(c["prohibida"] for c in corridas),
                 "guardrail_salida": sum(c["guardrail_salida"] for c in corridas), "handoffs": statistics.mean(c.get("handoffs", 0) for c in corridas),
                 "vueltas": statistics.mean(c["vueltas"] for c in corridas), "tokens": statistics.mean(c["tokens"] for c in corridas),
                 "latencia_s": round(statistics.mean(c["latencia_s"] for c in corridas), 2), "costo_usd": round(sum(c["costo_usd"] for c in corridas), 5),
                 "juez": round(statistics.mean(c["juez"]["calificacion"] for c in corridas), 2) if a.juez else None,
                 "tools": [c["tools"] for c in corridas], "skills": [c.get("skills", []) for c in corridas],
                 "respuestas": [c["respuesta"] for c in corridas], "razones_juez": [c["juez"]["razon"] for c in corridas] if a.juez else [],
                 "errores": [c.get("error") for c in corridas if c.get("error")]}
            filas.append(f)
            print(f"[{diseno}] {tarea['id']} éxito {f['exito']}/{a.corridas} tools_ok {f['tools_ok']}/{a.corridas} prohibida {f['prohibida']} guardrail {f['guardrail_salida']} "
                  f"vueltas {f['vueltas']:.1f} tokens {f['tokens']:.0f} lat {f['latencia_s']}s costo ${f['costo_usd']}" + (f" juez {f['juez']}" if a.juez else ""), flush=True)
            if f["errores"]:
                print("   errores:", f["errores"][:2])
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(json.dumps(filas, ensure_ascii=False, indent=1))
    print("\nResumen por diseño:")
    for diseno in disenos:
        fs = [f for f in filas if f["diseno"] == diseno]; n = a.corridas * len(fs)
        print(f"  {diseno:16s} éxito {sum(f['exito'] for f in fs)}/{n}  tools_ok {sum(f['tools_ok'] for f in fs)}/{n}  prohibidas {sum(f['prohibida'] for f in fs)}  "
              f"guardrails {sum(f['guardrail_salida'] for f in fs)}  vueltas {statistics.mean(f['vueltas'] for f in fs):.2f}  tokens {statistics.mean(f['tokens'] for f in fs):.0f}  "
              f"lat {statistics.mean(f['latencia_s'] for f in fs):.2f}s  costo ${sum(f['costo_usd'] for f in fs):.4f}" + (f"  juez {statistics.mean(f['juez'] for f in fs):.2f}" if a.juez else ""))
    print(f"\nGuardado en {a.salida}")


if __name__ == "__main__":
    main()
