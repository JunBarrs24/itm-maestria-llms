"""Compara las cinco topologías sobre el mismo mini gold set de tickets, con medición.

Seis tickets de la mesa de soporte, cada uno con el especialista que debería
atenderlo y la tool que debería ejecutarse. Cada ticket corre N veces con cada
topología y se tabula: ruta correcta, tool correcta, llamadas al modelo, tokens,
latencia y errores. Después se mide qué contexto recibe el especialista con cada
política de handoff (completo, sin tools, paquete) sobre un ticket largo.

Uso:  .venv/bin/python course/week-12/examples/comparar_topologias.py [corridas]
Escribe slides/resultados.json.
"""
from __future__ import annotations

import asyncio
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import topologias as tp  # noqa: E402  (agrega shared/ al path)
import facturio_tools as ft  # noqa: E402

FOLIO = list(ft.CARGOS)[0]
DUP = "PAY-00012348"

# id, ticket, especialista esperado, tool esperada
GOLD = [
    ("g1", f"¿Cuál es el estado de la factura {FOLIO}?", "Facturacion", "consultar_factura"),
    ("g2", "Consulta el plan del usuario u002 y dime cuántas facturas al mes incluye.", "Facturacion", "consultar_plan"),
    ("g3", f"El cargo {DUP} me aparece duplicado, ¿me lo van a devolver?", "Facturacion", "consultar_factura"),
    ("g4", "No puedo iniciar sesión: el código 2FA nunca llega.", "Acceso", "buscar_documentacion"),
    ("g5", "Al exportar a PDF me sale el error E-4001.", "Tecnico", "buscar_documentacion"),
    ("g6", "Invité a un colega hace una semana y dice que el enlace de invitación ya no sirve.", "Acceso", "buscar_documentacion"),
]


def ruta_ok(fila: dict, esperado: str) -> bool | None:
    """None cuando la topología no tiene ruta (single agent)."""
    if fila["topologia"] == "single_agent":
        return None
    return esperado in str(fila["atendio"]).split("+")


async def main(corridas: int = 2):
    consola = tp.activar_tracing()
    filas = []
    for gid, ticket, esperado, tool in GOLD:
        for topo in tp.TOPOLOGIAS:
            for k in range(corridas):
                ft.reiniciar_estado()
                f = await tp.ejecutar(topo, ticket, consola)
                f.update({"ticket": gid, "corrida": k + 1, "ruta_ok": ruta_ok(f, esperado), "tool_ok": tool in f["tools"],
                          "tokens": f["input_tokens"] + f["output_tokens"]})
                f.pop("paquetes", None)
                filas.append(f)
                print(f"{gid} {topo:20s} #{k+1} atendió={str(f['atendio']):14s} ruta_ok={f['ruta_ok']} tool_ok={f['tool_ok']} "
                      f"calls={f['llamadas_modelo']} tok={f['tokens']} {f['latencia_s']}s err={f['error']}", flush=True)

    resumen = {}
    for topo in tp.TOPOLOGIAS:
        fs = [f for f in filas if f["topologia"] == topo]
        con_ruta = [f for f in fs if f["ruta_ok"] is not None]
        resumen[topo] = {
            "corridas": len(fs),
            "ruta_ok": round(sum(f["ruta_ok"] for f in con_ruta) / len(con_ruta), 2) if con_ruta else None,
            "tool_ok": round(sum(f["tool_ok"] for f in fs) / len(fs), 2),
            "llamadas_media": round(statistics.mean(f["llamadas_modelo"] for f in fs), 2),
            "tokens_media": round(statistics.mean(f["tokens"] for f in fs)),
            "latencia_media_s": round(statistics.mean(f["latencia_s"] for f in fs), 2),
            "errores": sum(1 for f in fs if f["error"]),
            "agentes": {"single_agent": 1, "handoffs": 4, "agents_as_tools": 4, "manager": 4, "routing_determinista": 3}[topo],
        }
    por_ticket = {gid: {topo: round(sum(f["tool_ok"] for f in filas if f["ticket"] == gid and f["topologia"] == topo)
                                    / max(1, sum(1 for f in filas if f["ticket"] == gid and f["topologia"] == topo)), 2)
                        for topo in tp.TOPOLOGIAS} for gid, *_ in GOLD}

    contexto = await medir_contexto(consola)
    salida = {"backend": tp.CFG["model"], "corridas_por_ticket": corridas, "gold": [{"id": g[0], "ticket": g[1], "esperado": g[2], "tool": g[3]} for g in GOLD],
              "resumen": resumen, "por_ticket": por_ticket, "contexto_handoff": contexto, "filas": filas}
    guardar(salida)
    print(json.dumps({"resumen": resumen, "por_ticket": por_ticket}, ensure_ascii=False, indent=1))


async def medir_contexto(consola) -> dict:
    """Qué recibe el especialista con cada política de handoff, sobre un ticket corto y uno largo."""
    contexto = {}
    for nombre, ticket in [("corto", GOLD[0][1]), ("largo", tp.TICKET_LARGO.format(folio=FOLIO))]:
        print(f"\n== contexto que recibe el especialista según la política de handoff (ticket {nombre})")
        contexto[nombre] = {}
        for politica in tp.FILTROS:
            f = await tp.ejecutar("handoffs", ticket, consola, contexto=politica)
            viajo = tp.contexto_que_viajo(consola.ultimo())
            contexto[nombre][politica] = {"atendio": f["atendio"], "llamadas": f["llamadas_modelo"], "tokens": f["input_tokens"] + f["output_tokens"],
                                          "tool_ok": "consultar_factura" in f["tools"], "por_agente": viajo,
                                          "paquete": f["paquetes"][0] if f["paquetes"] else None}
            print(f"   {politica:9s} atendió={f['atendio']:12s} tokens={contexto[nombre][politica]['tokens']} -> {viajo}")
    return contexto


OUT = HERE.parent / "slides" / "resultados.json"


def guardar(salida: dict) -> None:
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")


async def solo_contexto():
    """Repite únicamente la medición de contexto y la guarda sobre el resultados.json existente."""
    consola = tp.activar_tracing()
    salida = json.loads(OUT.read_text(encoding="utf-8"))
    salida["contexto_handoff"] = await medir_contexto(consola)
    guardar(salida)


if __name__ == "__main__":
    if "--solo-contexto" in sys.argv:
        asyncio.run(solo_contexto())
    else:
        asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 2))
