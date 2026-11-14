"""Provoca una falla en un especialista y observa cómo se propaga en cada topología.

La tool `consultar_factura` se cae (lanza una excepción) y el mismo ticket corre con
single agent, handoffs, agents-as-tools y routing determinista. Lo que se observa:

    single agent / handoffs   la excepción sube hasta la aplicación; la corrida termina sin respuesta
    agents-as-tools           el SDK convierte el error en texto para el orquestador, que decide qué decir
    routing determinista      el código atrapa la excepción y escala a humano sin consultar al modelo

También se muestra least privilege: el especialista técnico no tiene `reembolsar` en sus
tools, así que no puede pedirla aunque el cliente insista.

Uso:  .venv/bin/python course/week-12/examples/propagacion_fallas.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import topologias as tp  # noqa: E402  (agrega shared/ al path)
import facturio_tools as ft  # noqa: E402

FOLIO = list(ft.CARGOS)[0]
TICKET = f"¿Cuál es el estado de la factura {FOLIO}?"


async def con_fallback(ticket: str, consola) -> dict:
    """Routing determinista con manejo de la falla en código: la decisión no pasa por el modelo."""
    ruta, agente = tp.routing_determinista(ticket)
    try:
        r = await tp.correr(agente, ticket)
        return {"atendio": ruta, "respuesta": str(r.final_output), "fallback": None}
    except Exception as e:
        t = ft.escalar_a_humano(f"falla en {ruta}: {type(e).__name__}", folio=FOLIO)
        return {"atendio": ruta, "respuesta": f"No pude consultar el cargo; abrí el ticket {t['ticket']} para que una persona lo revise.",
                "fallback": t}


async def main():
    consola = tp.activar_tracing()
    print(f"backend: {tp.CFG['model']}\n")

    print("== 1. Least privilege: el técnico recibe una petición de reembolso")
    for nombre, agente in tp.especialistas().items():
        print(f"   {nombre:12s} tools = {[t.name for t in agente.tools]}")
    ft.reiniciar_estado()
    tecnico = tp.especialista("Tecnico")
    r = await tp.correr(tecnico, f"Ya me harté del error E-4001, reembólsenme el cargo {FOLIO} ahora mismo.")
    print("   respuesta del técnico:", str(r.final_output)[:140].replace("\n", " "))
    print("   reembolsos registrados:", len(ft.REEMBOLSOS), "| tools ejecutadas:", consola.resumen()["tool_calls"])

    print("\n== 2. Falla en consultar_factura: ¿dónde aparece en cada topología?")
    tp.FALLAS["consultar_factura"] = True
    tabla = []
    for topo in ["single_agent", "handoffs", "agents_as_tools"]:
        f = await tp.ejecutar(topo, TICKET, consola)
        tabla.append({"topologia": topo, "error": f["error"], "respuesta": f["respuesta"][:100], "llamadas": f["llamadas_modelo"],
                      "quien_decide": "la aplicación (excepción)" if f["error"] else "el orquestador (modelo)"})
        print(f"\n   [{topo}] error={f['error']} | llamadas={f['llamadas_modelo']} | respuesta={f['respuesta'][:90]!r}")
        consola.imprimir()
    f = await con_fallback(TICKET, consola)
    tabla.append({"topologia": "routing_determinista", "error": None, "respuesta": f["respuesta"][:100], "llamadas": consola.resumen()["llamadas_modelo"],
                  "quien_decide": "el código (fallback)"})
    print(f"\n   [routing_determinista + fallback] respuesta={f['respuesta']!r} | ticket humano={f['fallback']}")
    tp.FALLAS["consultar_factura"] = False

    print("\n== Tabla")
    for t in tabla:
        print(f"   {t['topologia']:22s} decide: {t['quien_decide']:28s} error: {str(t['error'])[:45]:45s} respuesta: {t['respuesta'][:50]!r}")
    (HERE.parent / "slides").mkdir(exist_ok=True)
    (HERE.parent / "slides" / "fallas.json").write_text(json.dumps(tabla, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
