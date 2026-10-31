"""Cuatro patrones de workflow con LLM sobre tickets de Facturio, con medición.

    prompt chaining      extraer -> clasificar -> redactar -> validar (orden fijo)
    routing              clasificar la ruta -> prompt especializado
    parallelization      el mismo trabajo sobre N tickets a la vez
    orchestrator-worker  un LLM parte la tarea; workers resuelven; un paso sintetiza

En todos, el orden de los pasos lo decide el código. Ninguno es un agente.

Uso:  .venv/bin/python course/week-08/examples/workflows.py
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent))
import facturio_tools as ft  # noqa: E402
from llm_local import LLM, UsageLog, backend_disponible  # noqa: E402

TICKETS = [
    "Me cobraron dos veces la mensualidad de julio. Necesito el reembolso del cargo duplicado.",
    "No puedo iniciar sesión, dice que mi contraseña es incorrecta aunque la acabo de cambiar.",
    "Cuando exporto el reporte a PDF las gráficas salen en blanco.",
    "La autenticación de dos factores me pide un código que nunca llega por SMS.",
    "¿Tienen descuento para instituciones educativas?",
]

# ---------------------------------------------------------------- routing
class Ruta(BaseModel):
    ruta: Literal["facturacion", "acceso", "otro"]


RUTAS = {
    "facturacion": "Eres el especialista de cobros de Facturio. Responde en dos oraciones. "
                   "Políticas: reembolso dentro de 14 días naturales, uno por cuenta cada 12 meses; un cargo duplicado "
                   "se revierte solo en 5 días hábiles; descuento educativo de 40 % solo en el plan Pro.",
    "acceso": "Eres el especialista de acceso y seguridad de Facturio. Responde en dos oraciones. "
              "Políticas: bloqueo tras 5 intentos fallidos que se libera a los 15 minutos; el código 2FA vale 90 segundos; "
              "la sesión expira a los 30 minutos de inactividad.",
    "otro": "Eres el asistente general de Facturio. Responde en dos oraciones y, si es una falla técnica, "
            "pide el navegador y la versión. Safari anterior a 17 exporta PDF sin gráficas (E-4001).",
}
SISTEMA_RUTA = ("Clasifica el ticket de soporte en una ruta: facturacion (cobros, reembolsos, planes, descuentos), "
                "acceso (contraseñas, sesión, 2FA, bloqueos), otro (todo lo demás).")


def preruta_determinista(ticket: str) -> Optional[str]:
    """Reglas antes del modelo: si el ticket trae un folio PAY- o un código E-1xxx, la ruta ya se sabe."""
    if re.search(r"PAY-\d{8}", ticket):
        return "facturacion"
    if re.search(r"E-1\d{3}", ticket):
        return "acceso"
    return None


def routing(llm: LLM, ticket: str, log: UsageLog, etiqueta: str = "routing") -> dict:
    ruta = preruta_determinista(ticket)
    llamadas = 0
    if ruta is None:
        with log.track(f"{etiqueta}:clasificar", llm.model) as t:
            r, resp, n = llm.parse(f"Ticket: {ticket}", Ruta, system=SISTEMA_RUTA, max_output_tokens=40)
            t.input_tokens, t.output_tokens = resp.input_tokens, resp.output_tokens
        ruta = r.ruta if r else "otro"
        llamadas += n
    with log.track(f"{etiqueta}:responder", llm.model) as t:
        resp = llm.chat(f"Ticket: {ticket}", system=RUTAS[ruta], max_output_tokens=90)
        t.input_tokens, t.output_tokens = resp.input_tokens, resp.output_tokens
    llamadas += 1
    return {"ticket": ticket, "ruta": ruta, "respuesta": resp.text, "llamadas": llamadas}


# ---------------------------------------------------------------- prompt chaining
class Extraccion(BaseModel):
    folio: Optional[str] = Field(default=None, description="Folio PAY- si aparece")
    codigo_error: Optional[str] = Field(default=None, description="Código E-xxxx si aparece")
    problema: str = Field(description="El problema en una frase")


class Clasificacion(BaseModel):
    categoria: Literal["facturacion", "acceso", "error_tecnico", "solicitud_funcion", "otro"]
    prioridad: Literal["alta", "media", "baja"]


def validar_respuesta(texto: str) -> tuple[bool, str]:
    """Paso determinista al final de la cadena."""
    if re.search(r"[\w.]+@[\w.]+\.\w+|\b\d{2}\s?\d{4}\s?\d{4}\b", texto):
        return False, "contiene correo o teléfono"
    if len(re.findall(r"[.!?](\s|$)", texto)) > 3:
        return False, "más de tres oraciones"
    return True, "ok"


def chaining(llm: LLM, ticket: str, log: UsageLog) -> dict:
    with log.track("chaining:extraer", llm.model) as t:
        ext, r1, _ = llm.parse(f"Ticket: {ticket}", Extraccion, system="Extrae los datos del ticket.", max_output_tokens=80)
        t.input_tokens, t.output_tokens = r1.input_tokens, r1.output_tokens
    with log.track("chaining:clasificar", llm.model) as t:
        cla, r2, _ = llm.parse(f"Problema: {ext.problema if ext else ticket}", Clasificacion,
                               system="Clasifica el ticket de soporte de un SaaS de facturación.", max_output_tokens=40)
        t.input_tokens, t.output_tokens = r2.input_tokens, r2.output_tokens
    with log.track("chaining:redactar", llm.model) as t:
        r3 = llm.chat(f"Ticket: {ticket}\nCategoría: {cla.categoria if cla else 'otro'}. Prioridad: {cla.prioridad if cla else 'media'}.",
                      system="Redacta una respuesta al cliente en máximo tres oraciones, sin datos personales.", max_output_tokens=90)
        t.input_tokens, t.output_tokens = r3.input_tokens, r3.output_tokens
    ok, razon = validar_respuesta(r3.text)
    return {"extraccion": ext.model_dump() if ext else None, "clasificacion": cla.model_dump() if cla else None,
            "respuesta": r3.text, "valida": ok, "razon": razon, "llamadas": 3}


# ---------------------------------------------------------------- parallelization
async def routing_paralelo(llm: LLM, tickets: list[str], log: UsageLog) -> list[dict]:
    """Con una API remota las llamadas se solapan; con un modelo local en un solo proceso, no."""
    return await asyncio.gather(*(asyncio.to_thread(routing, llm, t, log, "paralelo") for t in tickets))


def correr_paralelo(llm: LLM, tickets: list[str], log: UsageLog) -> list[dict]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():          # dentro de un notebook
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.get_event_loop().run_until_complete(routing_paralelo(llm, tickets, log))
    return asyncio.run(routing_paralelo(llm, tickets, log))


# ---------------------------------------------------------------- orchestrator-worker
class Plan(BaseModel):
    subtareas: list[str] = Field(description="Entre 1 y 3 problemas independientes contenidos en el ticket")


def orchestrator_worker(llm: LLM, ticket: str, log: UsageLog) -> dict:
    with log.track("orquestador:planear", llm.model) as t:
        plan, r, _ = llm.parse(f"Ticket: {ticket}", Plan, system="Separa el ticket en problemas independientes, uno por frase corta.",
                               max_output_tokens=120)
        t.input_tokens, t.output_tokens = r.input_tokens, r.output_tokens
    subtareas = (plan.subtareas if plan else [ticket])[:3]
    parciales = [routing(llm, s, log, "worker") for s in subtareas]
    with log.track("orquestador:sintetizar", llm.model) as t:
        texto = "\n".join(f"- {p['ruta']}: {p['respuesta']}" for p in parciales)
        r2 = llm.chat(f"Ticket original: {ticket}\n\nRespuestas parciales:\n{texto}",
                      system="Integra las respuestas parciales en un solo mensaje al cliente de máximo cuatro oraciones.", max_output_tokens=140)
        t.input_tokens, t.output_tokens = r2.input_tokens, r2.output_tokens
    return {"subtareas": subtareas, "parciales": parciales, "respuesta": r2.text, "llamadas": 2 + sum(p["llamadas"] for p in parciales)}


# ---------------------------------------------------------------- medición
def medir(nombre: str, fn, log: UsageLog, etiquetas: tuple[str, ...], corridas: int = 2) -> dict:
    salidas, t0 = [], time.perf_counter()
    for _ in range(corridas):
        salidas.append(json.dumps(fn(), ensure_ascii=False, sort_keys=True, default=str))
    dt = (time.perf_counter() - t0) / corridas
    calls = [c for c in log.llamadas if c.etiqueta.startswith(etiquetas)]
    return {"patron": nombre, "llamadas_por_corrida": len(calls) / corridas,
            "tokens_por_corrida": (sum(c.input_tokens + c.output_tokens for c in calls)) / corridas,
            "latencia_s": round(dt, 2), "salidas_identicas": len(set(salidas)) == 1}


if __name__ == "__main__":
    backend = backend_disponible()
    llm = LLM(backend=backend, model=None if backend == "openai" else "Qwen/Qwen2.5-1.5B-Instruct")
    log = UsageLog()
    ft.reiniciar_estado()

    print("== routing (5 tickets)")
    for t in TICKETS:
        r = routing(llm, t, log)
        print(f"  [{r['ruta']:11s}] {t[:60]}...\n      -> {r['respuesta'][:140]}")

    print("\n== prompt chaining (1 ticket)")
    print("  ", json.dumps(chaining(llm, TICKETS[0], log), ensure_ascii=False)[:400])

    print("\n== parallelization (5 tickets): secuencial vs asyncio.gather")
    t0 = time.perf_counter(); [routing(llm, t, log, "secuencial") for t in TICKETS]; seq = time.perf_counter() - t0
    t0 = time.perf_counter(); correr_paralelo(llm, TICKETS, log); par = time.perf_counter() - t0
    print(f"  secuencial {seq:.1f} s | paralelo {par:.1f} s | backend {backend}")

    print("\n== orchestrator-worker (1 ticket compuesto)")
    compuesto = "Me cobraron doble este mes, folio PAY-00012348, y además desde ayer no me llega el código de dos factores."
    ow = orchestrator_worker(llm, compuesto, log)
    print("  subtareas:", ow["subtareas"]); print("  respuesta:", ow["respuesta"][:300])

    print("\n== tabla de medición (2 corridas por patrón)")
    filas = [
        medir("chaining", lambda: chaining(llm, TICKETS[0], log), log, ("chaining",)),
        medir("routing", lambda: routing(llm, TICKETS[1], log, "medir_routing"), log, ("medir_routing",)),
        medir("orchestrator-worker", lambda: orchestrator_worker(llm, compuesto, log), log, ("orquestador", "worker")),
    ]
    import pandas as pd
    print(pd.DataFrame(filas).to_string(index=False))
    print("\n", log.tabla().to_string(index=False))
