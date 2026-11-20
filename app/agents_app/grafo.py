"""El flujo escrito por el código: un grafo de nodos y aristas, en Python puro (semana 13).

Es el otro extremo de la escalera: el modelo no decide el siguiente paso, lo decide el grafo. Cada nodo
es una función que recibe el estado y devuelve cambios; las aristas dicen qué nodo sigue, a veces con
una condición sobre el estado. El modelo aparece dentro de algunos nodos (clasificar, redactar), nunca
eligiendo la ruta. Sin framework: un diccionario de nodos, un diccionario de aristas y un while con
límite. LangGraph hace esto mismo con reducers, checkpoints e interrupt; aquí se ve el mecanismo.

El grafo de la mesa de soporte:

    clasificar ──► consultar ──► decidir ──┬─► aprobar (pausa) ──► reembolsar ──► redactar ──► FIN
                                            ├─► redactar ──► FIN
                                            └─► escalar ──► redactar ──► FIN
"""
from __future__ import annotations

import json
import re
from typing import Callable

from agents import Agent, Runner

from data import facturio as db
from modes.modes import ruta_determinista
from policies.refunds import autorizar_reembolso
from providers import models

LIMITE_PASOS = 8


# ---- nodos: funciones estado -> cambios. Las que usan el modelo lo dicen en el nombre.
def clasificar(estado: dict) -> dict:
    """Código puro: el regex de la semana 8 decide el tema."""
    return {"tema": ruta_determinista(estado["pregunta"])}


def consultar(estado: dict) -> dict:
    """Código puro: si hay folio, se consulta el cargo; si hay usuario, el plan. Sin preguntarle al modelo."""
    cambios = {}
    folio = next(iter(re.findall(r"\bPAY-\d{8}\b", estado["pregunta"], re.I)), None)
    if folio:
        c = db.CARGOS.get(folio.upper())
        cambios["cargo"] = {"folio": folio.upper(), **c, "fecha": c["fecha"].isoformat()} if c else {"error": "no existe"}
    if estado.get("usuario_id"):
        u = db.USUARIOS.get(estado["usuario_id"])
        cambios["plan"] = {"plan": u["plan"], "facturas_mes": u["facturas_mes"]} if u else None
    return cambios


def decidir(estado: dict) -> dict:
    """Código puro: la política decide si procede reembolso, si se escala, o si solo se responde."""
    quiere_reembolso = bool(re.search(r"reembols|devolu|devuelv", estado["pregunta"], re.I))
    cargo = estado.get("cargo") or {}
    if not quiere_reembolso or "monto" not in cargo:
        return {"decision": "responder"}
    # el monto lo calcula el código con la misma regla de la política: completo sin facturas, la mitad si las hubo
    monto = cargo["monto"] if cargo.get("facturas_timbradas_periodo", 0) == 0 else round(cargo["monto"] * 0.5, 2)
    ok, razon = autorizar_reembolso(cargo["folio"], monto, estado.get("usuario_id"))
    if ok:
        return {"decision": "aprobar", "monto": monto}
    if "aprobación humana" in razon:
        return {"decision": "escalar", "razon": razon}
    return {"decision": "responder", "razon": razon}


def aprobar(estado: dict) -> dict:
    """Human-in-the-loop como nodo: si no hay decisión de una persona, el grafo se detiene aquí."""
    if estado.get("aprobado") is None:
        return {"pausa": {"tool": "reembolsar", "args": {"folio": estado["cargo"]["folio"], "monto": estado["monto"], "motivo": "solicitud del cliente"}}}
    return {}


def reembolsar(estado: dict) -> dict:
    if not estado.get("aprobado"):
        return {"resultado_reembolso": {"ejecutado": False, "razon": "rechazado por una persona"}}
    import uuid
    ref = f"REF-{uuid.uuid4().hex[:8].upper()}"
    db.REEMBOLSOS[estado["cargo"]["folio"]] = {"referencia": ref, "monto": estado["monto"], "motivo": "grafo", "fecha": db.HOY.isoformat()}
    return {"resultado_reembolso": {"ejecutado": True, "referencia": ref, "monto": estado["monto"]}}


def escalar(estado: dict) -> dict:
    t = {"ticket": f"HUM-{len(db.TICKETS_HUMANOS) + 1:04d}", "motivo": estado.get("razon", ""), "usuario": estado.get("usuario_id")}
    db.TICKETS_HUMANOS.append(t)
    return {"ticket": t}


async def redactar_con_modelo(estado: dict, proveedor: str, effort: str, summary: str) -> dict:
    """El único nodo con modelo: recibe los hechos que el grafo reunió y escribe la respuesta. Sin tools."""
    hechos = {k: estado.get(k) for k in ("tema", "cargo", "plan", "decision", "razon", "resultado_reembolso", "ticket") if estado.get(k) is not None}
    redactor = Agent(name="Redactor", instructions=(
        "Eres el asistente de soporte de Facturio. Recibes la pregunta del cliente y los hechos que la aplicación ya verificó. "
        "Responde en español, breve, usando solo esos hechos. Nunca afirmes que un reembolso se ejecutó si resultado_reembolso no lo dice."),
        model=models.modelo(proveedor), model_settings=models.ajustes(proveedor, effort, summary))
    r = await Runner.run(redactor, f"Pregunta: {estado['pregunta']}\n\nHechos verificados: {json.dumps(hechos, ensure_ascii=False, default=str)}", max_turns=1)
    return {"respuesta": r.final_output, "uso": r.context_wrapper.usage}


# ---- aristas: de cada nodo, a cuál sigue. Una función cuando depende del estado.
ARISTAS: dict[str, str | Callable[[dict], str]] = {
    "clasificar": "consultar",
    "consultar": "decidir",
    "decidir": lambda e: {"aprobar": "aprobar", "escalar": "escalar"}.get(e["decision"], "redactar"),
    "aprobar": lambda e: "FIN" if e.get("pausa") else "reembolsar",
    "reembolsar": "redactar",
    "escalar": "redactar",
    "redactar": "FIN",
}
NODOS = {"clasificar": clasificar, "consultar": consultar, "decidir": decidir, "aprobar": aprobar, "reembolsar": reembolsar, "escalar": escalar}


async def correr_grafo(estado: dict, proveedor: str, effort: str, summary: str, desde: str = "clasificar") -> tuple[dict, list[dict]]:
    """El loop del grafo: nodo actual, aplicar, elegir arista, repetir, con límite. Devuelve (estado, pasos)."""
    pasos: list[dict] = []
    nodo = desde
    for _ in range(LIMITE_PASOS):
        if nodo == "FIN":
            break
        cambios = await redactar_con_modelo(estado, proveedor, effort, summary) if nodo == "redactar" else NODOS[nodo](estado)
        estado.update(cambios)
        pasos.append({"nodo": nodo, "cambios": {k: v for k, v in cambios.items() if k != "uso"}})
        siguiente = ARISTAS[nodo]
        nodo = siguiente(estado) if callable(siguiente) else siguiente
        if estado.get("pausa") and nodo == "FIN":
            estado["reanudar_en"] = "aprobar"
    else:
        pasos.append({"nodo": "límite", "cambios": {"aviso": f"límite de {LIMITE_PASOS} pasos"}})
    return estado, pasos
