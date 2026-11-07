"""Evaluación de agentes (semana 10): seis tareas, N corridas, dos motores, el mismo gpt-5-mini.

Mide lo que la semana define como evaluación de un agente: task success, selección de tools,
número de vueltas, tokens, latencia, costo y variabilidad entre corridas. Corre contra responder()
directamente (sin HTTP), con side effects automáticos encendidos para que los dos motores puedan
ejecutar reembolsar y la política de negocio (dueño, plazo, monto, duplicado) sea la que decida.

Uso:   python eval_motores.py [--corridas 3] [--motores manual,sdk] [--salida eval_resultados.json]
Costo: unas 36 corridas con gpt-5-mini, menos de 5 centavos de dólar.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import app as A                                  # noqa: E402
import facturio_tools as ft                      # noqa: E402

# Cada tarea: usuario de la sesión, objetivo, tools que se esperan, y un criterio de éxito verificable
# sobre la respuesta (r) y las tools ejecutadas (ex: lista de (nombre, args, resultado)).
GOLD = [
    {"id": "t1", "usuario": "u001", "objetivo": "¿Cuánto cobró el cargo PAY-00012345 y de qué fue?",
     "tools": {"consultar_factura"},
     "exito": lambda r, ex: "599" in r and re.search(r"b[áa]sico", r, re.I) is not None},
    {"id": "t2", "usuario": "u002", "objetivo": "¿Cuál es mi plan y cuántas facturas he timbrado este mes?",
     "tools": {"consultar_plan"},
     "exito": lambda r, ex: "Pro" in r and "812" in r},
    {"id": "t3", "usuario": "u001", "objetivo": "¿Cuántos días tengo para pedir un reembolso?",
     "tools": {"buscar_documentacion"},
     "exito": lambda r, ex: "14" in r},
    {"id": "t4", "usuario": "u001", "objetivo": "Reembolsa el cargo PAY-00012345 completo, no usé el servicio.",
     "tools": {"consultar_factura", "reembolsar"},   # dueño, en plazo, bajo el límite: debe ejecutarse
     "exito": lambda r, ex: any(n == "reembolsar" and s.get("ejecutado") and abs(float(a.get("monto", 0)) - 599) < 1 for n, a, s in ex)},
    {"id": "t5", "usuario": "u002", "objetivo": "Reembolsa el cargo PAY-00012345 completo, no usé el servicio.",
     "tools": {"consultar_factura"},                 # folio de otro usuario: no debe ejecutarse
     "exito": lambda r, ex: not any(n == "reembolsar" and s.get("ejecutado") for n, a, s in ex)
                            and re.search(r"otro usuario|otra cuenta|pertenece|no (te )?corresponde|no puedo|persona|escal", r, re.I) is not None},
    {"id": "t6", "usuario": "u002", "objetivo": "El cargo PAY-00012348 me salió doble, devuélvanme el dinero.",
     "tools": {"consultar_factura"},                 # duplicado detectado: la reversión es automática, no se reembolsa por esta vía
     "exito": lambda r, ex: not any(n == "reembolsar" and s.get("ejecutado") for n, a, s in ex)
                            and re.search(r"5 d[íi]as|autom[áa]tic|duplicad|revers", r, re.I) is not None},
]


def correr(tarea: dict, motor: str) -> dict:
    ft.reiniciar_estado()
    s = A.Sesion()
    s.estado["usuario_id"] = tarea["usuario"]
    s.historial.append({"role": "user", "content": f"Soy el usuario {tarea['usuario']}."})
    s.historial.append({"role": "assistant", "content": "Entendido."})
    t0 = time.perf_counter()
    try:
        r = A.responder(s, tarea["objetivo"], "estado", True, True, effort="minimal", motor=motor)
        if r.get("aprobacion_pendiente"):
            r = A.decidir_aprobacion(s, True)
    except Exception as e:
        return {"exito": False, "tools_ok": False, "vueltas": 0, "tokens": 0, "latencia_s": round(time.perf_counter() - t0, 2),
                "costo_usd": 0.0, "tools": [], "error": f"{type(e).__name__}: {e}"}
    ex = [(p["nombre"], p["args"], p["resultado"]) for p in r["trace"] if p["tipo"] == "tool" and isinstance(p.get("resultado"), dict)]
    usadas = {n for n, _, _ in ex}
    return {"exito": bool(tarea["exito"](r["respuesta"] or "", ex)), "tools_ok": tarea["tools"].issubset(usadas),
            "vueltas": sum(1 for p in r["trace"] if p["tipo"] == "modelo"), "tokens": r["uso"]["input_tokens"] + r["uso"]["output_tokens"],
            "latencia_s": r["uso"]["latencia_s"], "costo_usd": r["uso"]["costo_usd"], "tools": [n for n, _, _ in ex], "respuesta": (r["respuesta"] or "")[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corridas", type=int, default=3)
    ap.add_argument("--motores", default="manual,sdk")
    ap.add_argument("--salida", default=str(AQUI / "eval_resultados.json"))
    a = ap.parse_args()
    filas = []
    for motor in a.motores.split(","):
        for tarea in GOLD:
            corridas = [correr(tarea, motor) for _ in range(a.corridas)]
            fila = {"motor": motor, "tarea": tarea["id"], "exito": sum(c["exito"] for c in corridas), "tools_ok": sum(c["tools_ok"] for c in corridas),
                    "vueltas": statistics.mean(c["vueltas"] for c in corridas), "tokens": statistics.mean(c["tokens"] for c in corridas),
                    "latencia_s": round(statistics.mean(c["latencia_s"] for c in corridas), 2), "costo_usd": round(sum(c["costo_usd"] for c in corridas), 5),
                    "tools": [c["tools"] for c in corridas], "n": a.corridas, "errores": [c.get("error") for c in corridas if c.get("error")]}
            filas.append(fila)
            print(f"[{motor}] {tarea['id']} éxito {fila['exito']}/{a.corridas} tools_ok {fila['tools_ok']}/{a.corridas} "
                  f"vueltas {fila['vueltas']:.1f} tokens {fila['tokens']:.0f} lat {fila['latencia_s']}s costo ${fila['costo_usd']}", flush=True)
            if fila["errores"]:
                print("   errores:", fila["errores"])
    Path(a.salida).write_text(json.dumps(filas, ensure_ascii=False, indent=1))
    print("\nResumen por motor:")
    for motor in a.motores.split(","):
        fs = [f for f in filas if f["motor"] == motor]
        n = a.corridas * len(fs)
        print(f"  {motor:7s} éxito {sum(f['exito'] for f in fs)}/{n}  tools_ok {sum(f['tools_ok'] for f in fs)}/{n}  "
              f"vueltas {statistics.mean(f['vueltas'] for f in fs):.2f}  tokens/corrida {statistics.mean(f['tokens'] for f in fs):.0f}  "
              f"lat {statistics.mean(f['latencia_s'] for f in fs):.2f}s  costo total ${sum(f['costo_usd'] for f in fs):.4f}")
    print(f"\nGuardado en {a.salida}")


if __name__ == "__main__":
    main()
