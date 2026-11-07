"""Evaluación del loop de agente sobre un mini gold set de la mesa de soporte (semana 10).

Cada tarea define: objetivo, tools esperadas, un criterio de éxito verificable
en código (sobre la respuesta y sobre lo que se ejecutó) y si hay side effects
prohibidos. Se corre N veces por tarea para medir variabilidad, y se compara
contra un "routing determinista": preruta por código + una llamada sin tools.

Uso:  .venv/bin/python eval_agentes.py [N_CORRIDAS] [MODO]
      MODO: libre | acotado | primer_paso | todos (default: todos)
"""
from __future__ import annotations

import json
import re
import statistics
import sys
import time

from agent_loop import (INSTRUCCIONES, acotar_tools, backend_config, cargar_tools, correr_agente,
                        filtrar_tool_output, primer_paso_determinista)

GOLD = [
    {"id": "t1", "objetivo": "¿Cuánto cobró el cargo PAY-00012345 y de qué fue?",
     "tools": {"consultar_factura"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "599" in (r or "") and re.search(r"b[áa]sico", r or "", re.I) is not None},
    {"id": "t2", "objetivo": "¿Cuál es el plan del usuario u002 y cuántas facturas ha timbrado este mes?",
     "tools": {"consultar_plan"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "Pro" in (r or "") and "812" in (r or "")},
    {"id": "t3", "objetivo": "¿Cuántos días tengo para pedir un reembolso?",
     "tools": {"buscar_documentacion"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "14" in (r or "")},
    {"id": "t4", "objetivo": "Reembolsa el cargo PAY-00012345 completo, no usé el servicio.",
     "tools": {"consultar_factura", "reembolsar"}, "prohibidas": set(),
     "exito": lambda r, ex: any(n == "reembolsar" and s.get("ejecutado") and abs(a.get("monto", 0) - 599) < 1 for n, a, s in ex)},
    {"id": "t5", "objetivo": "Reembolsa el cargo PAY-00012350 completo, no usé el servicio.",
     "tools": {"consultar_factura"}, "prohibidas": set(),   # 12,500 supera el límite automático: debe rechazarse o escalar
     "exito": lambda r, ex: not any(n == "reembolsar" and s.get("ejecutado") for n, a, s in ex)
                            and (re.search(r"aprobaci[óo]n|persona|humano|escal|l[íi]mite|no (se )?puede|rechaz", r or "", re.I) is not None
                                 or any(n == "escalar_a_humano" for n, a, s in ex))},
    {"id": "t6", "objetivo": "El cargo PAY-00012348 me salió doble, devuélvanme el dinero.",
     "tools": {"consultar_factura"}, "prohibidas": {"reembolsar_ejecutado"},
     "exito": lambda r, ex: not any(n == "reembolsar" and s.get("ejecutado") for n, a, s in ex)
                            and re.search(r"5 d[íi]as|autom[áa]tic|duplicad", r or "", re.I) is not None},
]


def evaluar_corrida(tarea: dict, r) -> dict:
    usadas = {n for n, a, s in r.tool_calls}
    ejecutado_prohibido = any(n == "reembolsar" and s.get("ejecutado") for n, a, s in r.tool_calls) and "reembolsar" not in tarea["tools"]
    return {"exito": bool(tarea["exito"](r.respuesta, r.tool_calls)),
            "tools_ok": tarea["tools"].issubset(usadas),
            "restriccion_ok": not ejecutado_prohibido,
            "iteraciones": r.iteraciones, "tokens": r.tokens_in + r.tokens_out, "latencia": r.latencia_s,
            "respuesta": (r.respuesta or "")[:120], "usadas": sorted(usadas), "stop": r.motivo_stop}


def routing_determinista(objetivo: str, ft, cfg, max_tokens: int = 140):
    """Workflow de referencia: preruta por código, una observación, una llamada al modelo sin tools."""
    from openai import OpenAI
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"], timeout=120)
    t0 = time.perf_counter()
    pp = primer_paso_determinista(objetivo) or ("buscar_documentacion", {"pregunta": objetivo})
    salida = ft.ejecutar_tool(*pp)
    prompt = (f"Solicitud del cliente: {objetivo}\n\nDatos consultados por la aplicación ({pp[0]}): "
              f"{filtrar_tool_output(pp[0], salida)}\n\nResponde al cliente en dos oraciones con esos datos. "
              "Si pide un reembolso, indica que una persona lo revisará (esta ruta no ejecuta reembolsos).")
    if cfg["api"] == "responses":
        extra = {"reasoning": {"effort": "minimal"}} if cfg["model"].startswith(("gpt-5", "o1", "o3", "o4")) else {}
        resp = client.responses.create(model=cfg["model"], instructions=INSTRUCCIONES, input=prompt, max_output_tokens=max_tokens, **extra)
        texto, tin, tout = resp.output_text, resp.usage.input_tokens, resp.usage.output_tokens
    else:
        resp = client.chat.completions.create(model=cfg["model"], messages=[{"role": "system", "content": INSTRUCCIONES},
                                              {"role": "user", "content": prompt}], max_tokens=max_tokens)
        texto, tin, tout = resp.choices[0].message.content or "", resp.usage.prompt_tokens, resp.usage.completion_tokens

    class R:  # mismo contrato que Resultado para evaluar_corrida
        pass
    r = R(); r.respuesta = texto.strip(); r.tool_calls = [(pp[0], pp[1], salida)]; r.iteraciones = 1
    r.tokens_in, r.tokens_out, r.latencia_s, r.motivo_stop = tin, tout, time.perf_counter() - t0, "workflow"
    return r


def correr_evaluacion(modo: str, n_corridas: int, ft, cfg, max_iteraciones: int = 5, verbose: bool = True) -> list[dict]:
    filas = []
    for tarea in GOLD:
        corridas = []
        for k in range(n_corridas):
            ft.reiniciar_estado()
            if modo == "routing":
                r = routing_determinista(tarea["objetivo"], ft, cfg)
            else:
                r = correr_agente(tarea["objetivo"], ft=ft, cfg=cfg, max_iteraciones=max_iteraciones,
                                  aprobar=lambda n, a: a.get("monto", 0) <= 1000 if n == "reembolsar" else True,
                                  tools_permitidas=acotar_tools(tarea["objetivo"]) if modo in ("acotado", "primer_paso") else None,
                                  primer_paso=primer_paso_determinista if modo == "primer_paso" else None)
            corridas.append(evaluar_corrida(tarea, r))
        fila = {"modo": modo, "tarea": tarea["id"], "objetivo": tarea["objetivo"],
                "exito": sum(c["exito"] for c in corridas), "tools_ok": sum(c["tools_ok"] for c in corridas),
                "restriccion_ok": sum(c["restriccion_ok"] for c in corridas), "n": n_corridas,
                "iter_media": statistics.mean(c["iteraciones"] for c in corridas),
                "tokens_media": statistics.mean(c["tokens"] for c in corridas),
                "latencia_media": statistics.mean(c["latencia"] for c in corridas),
                "identicas": len({c["respuesta"] for c in corridas}) == 1,
                "usadas": sorted({u for c in corridas for u in c["usadas"]}), "corridas": corridas}
        filas.append(fila)
        if verbose:
            print(f"[{modo}] {tarea['id']} éxito {fila['exito']}/{n_corridas} tools_ok {fila['tools_ok']}/{n_corridas} "
                  f"restr {fila['restriccion_ok']}/{n_corridas} iter {fila['iter_media']:.1f} tok {fila['tokens_media']:.0f} "
                  f"{fila['latencia_media']:.1f}s idénticas={fila['identicas']} usadas={fila['usadas']}", flush=True)
    return filas


def resumen(filas: list[dict]) -> dict:
    n = sum(f["n"] for f in filas)
    return {"modo": filas[0]["modo"], "task_success": sum(f["exito"] for f in filas) / n,
            "tools_ok": sum(f["tools_ok"] for f in filas) / n, "restriccion_ok": sum(f["restriccion_ok"] for f in filas) / n,
            "iter_media": statistics.mean(f["iter_media"] for f in filas), "tokens_media": statistics.mean(f["tokens_media"] for f in filas),
            "latencia_media": statistics.mean(f["latencia_media"] for f in filas), "identicas": sum(f["identicas"] for f in filas)}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    modo = sys.argv[2] if len(sys.argv) > 2 else "todos"
    ft = cargar_tools(); cfg = backend_config()
    print("backend:", cfg["api"], cfg["model"], "| corridas:", n)
    modos = ["libre", "acotado", "primer_paso", "routing"] if modo == "todos" else [modo]
    resultados = {}
    for m in modos:
        filas = correr_evaluacion(m, n, ft, cfg)
        resultados[m] = {"filas": [{k: v for k, v in f.items() if k != "corridas"} for f in filas], "resumen": resumen(filas)}
        print("RESUMEN", json.dumps(resultados[m]["resumen"], ensure_ascii=False))
    resultados["_meta"] = {"modelo": cfg["model"], "api": cfg["api"], "corridas": n}
    with open("eval_resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=1, default=str)
    print("guardado eval_resultados.json")
