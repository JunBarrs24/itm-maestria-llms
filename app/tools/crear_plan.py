"""Plan mode: el modelo escribe los pasos antes de actuar y luego los sigue (semana 13).

La tool guarda el plan en el contexto de la aplicación. `instructions` como función (agents_app/)
lo muestra en cada vuelta con lo hecho y lo pendiente, así el modelo lo "sigue" porque lo ve
actualizado, no porque se le obligue. Es el punto medio entre decidir paso a paso (ReAct) y un flujo
escrito por el código (grafo). Lo que se mide: vueltas, tokens y desvíos del plan con y sin él.
"""
from __future__ import annotations

from tools.registry import RunContextWrapper, function_tool, progreso


@progreso("Armando el plan…")
@function_tool
def crear_plan(ctx: RunContextWrapper[dict], pasos: list[str]) -> dict:
    """Escribe el plan de pasos para resolver la solicitud antes de ejecutar ninguna herramienta.

    Llámala una sola vez, al inicio, cuando la solicitud tenga más de un paso (por ejemplo: consultar el
    cargo, revisar la política, pedir el reembolso). Después ejecuta los pasos en orden; el plan con su
    avance aparecerá en tus instrucciones en cada vuelta.

    Args:
        pasos: Lista corta de pasos concretos, uno por herramienta o decisión, en el orden en que los harás.
    """
    ctx.context["plan"] = [{"paso": p, "hecho": False} for p in pasos[:8]]
    return {"plan": pasos[:8], "nota": "ejecuta los pasos en orden; marcaré como hecho cada tool que llames"}


def plan_para_instrucciones(ctx: RunContextWrapper[dict]) -> str:
    """El bloque que se inserta en las instrucciones en cada vuelta: pasos con ✓ (hecho) o ○ (pendiente)."""
    plan = ctx.context.get("plan")
    if not plan:
        return ""
    llamadas = [h for h in ctx.context.get("tools_llamadas", []) if h != "crear_plan"]
    lineas = []
    for i, p in enumerate(plan, 1):
        # un paso se marca hecho cuando se llamó una tool cuyo nombre (o una de sus palabras) aparece en el paso
        palabras = p["paso"].lower()
        if not p["hecho"] and any(h in palabras or any(w in palabras for w in h.split("_") if len(w) > 4) for h in llamadas):
            p["hecho"] = True
        lineas.append(f"{i}. {'✓' if p['hecho'] else '○'} {p['paso']}")
    return "\n\nTu plan (sigue el orden; ✓ hecho, ○ pendiente):\n" + "\n".join(lineas)
