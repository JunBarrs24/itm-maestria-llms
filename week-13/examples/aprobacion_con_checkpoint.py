"""Aprobación humana con interrupción, checkpoints y reanudación (semana 13).

Tres escenas sobre el grafo de `grafo_soporte.py`:

1. Un reembolso se detiene en `aprobacion_humana`. El grafo devuelve `__interrupt__`,
   guarda el checkpoint y la aplicación decide cuándo y con qué reanudar
   (`Command(resume=...)`). El side effect no ocurre hasta entonces.
2. La misma solicitud, rechazada: el registro de reembolsos no cambia.
3. Una falla que supera el RetryPolicy del nodo. Sin checkpointer, la corrida se
   pierde completa. Con checkpointer, el state anterior al nodo sobrevive y
   `invoke(None, config)` reanuda desde ahí una vez corregida la causa.

Uso:  .venv/bin/python course/week-13/examples/aprobacion_con_checkpoint.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import grafo_soporte as gs  # noqa: E402  (pone shared en el path)
import facturio_tools as ft  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402
from langgraph.types import Command  # noqa: E402


def mostrar_estado(app, config, titulo: str) -> None:
    st = app.get_state(config)
    print(f"  [{titulo}] siguiente nodo: {st.next} | traza: {st.values.get('traza')} | "
          f"reembolso: {st.values.get('reembolso')}")


def escena_aprobacion(app, folio: str, aprobar: bool, thread_id: str) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    salida = app.invoke(gs.estado_inicial(f"Solicito el reembolso de 300 pesos del cargo {folio}."), config)
    intr = salida["__interrupt__"][0].value
    print("  interrupción:", {k: intr[k] for k in ("pregunta", "folio", "monto")})
    mostrar_estado(app, config, "detenido")
    print("  reembolsos registrados:", dict(ft.REEMBOLSOS))
    # Aquí la aplicación puede esperar minutos o días: el checkpoint no expira.
    decision = {"aprobado": aprobar, "quien": "supervisora", "motivo": "cargo sin uso en el periodo"}
    salida = app.invoke(Command(resume=decision), config)
    print("  respuesta final:", salida["respuesta"].splitlines()[-1])
    mostrar_estado(app, config, "terminado")
    print("  reembolsos registrados:", dict(ft.REEMBOLSOS))


def escena_falla(folio: str) -> None:
    mensaje = f"¿Cuánto cobró el cargo {folio}?"

    print("  a) sin checkpointer: 5 fallas contra 3 intentos")
    app = gs.construir_grafo()   # sin checkpointer
    gs.inyectar_falla("consultar_factura", 5)
    try:
        app.invoke(gs.estado_inicial(mensaje), {"configurable": {"thread_id": "sin"}})
    except ConnectionError as e:
        print("     excepción:", e, "| fallas que quedaron:", gs.FALLAS["consultar_factura"])
    print("     no hay state que recuperar: la corrida se repite desde START")
    gs.FALLAS.clear()

    print("  b) con checkpointer: la misma falla")
    app = gs.construir_grafo(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "con"}}
    gs.inyectar_falla("consultar_factura", 5)
    try:
        app.invoke(gs.estado_inicial(mensaje), config)
    except ConnectionError as e:
        print("     excepción:", e)
    mostrar_estado(app, config, "tras la falla")
    gs.FALLAS.clear()                       # se corrige la causa
    salida = app.invoke(None, config)       # None: reanuda desde el último checkpoint
    print("     reanudado:", gs.resumen(salida))
    print("     checkpoints del hilo:", [h.next for h in app.get_state_history(config)])


if __name__ == "__main__":
    ft.reiniciar_estado()
    folio = list(ft.CARGOS)[0]
    app = gs.construir_grafo(checkpointer=InMemorySaver())

    print("== 1. Aprobada")
    escena_aprobacion(app, folio, aprobar=True, thread_id="ap-1")
    ft.reiniciar_estado()

    print("\n== 2. Rechazada")
    escena_aprobacion(app, folio, aprobar=False, thread_id="ap-2")

    print("\n== 3. Falla que supera el retry, con y sin checkpoint")
    escena_falla(folio)
