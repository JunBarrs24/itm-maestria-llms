"""Tool sin side effect: carga el cuerpo de un skill (semana 12)."""
from __future__ import annotations

from context.session import contar_tokens
from skills import loader
from tools.registry import RunContextWrapper, function_tool, progreso


@progreso("Revisando el procedimiento…")
@function_tool
def cargar_skill(ctx: RunContextWrapper[dict], nombre: str) -> dict:
    """Carga un procedimiento (skill) y devuelve sus instrucciones completas.

    Llámala cuando el caso corresponda a uno de los skills listados en tus instrucciones, antes de
    actuar. Devuelve el procedimiento paso a paso; síguelo. Cada skill se carga una sola vez por turno.

    Args:
        nombre: El nombre del skill tal como aparece en la lista, por ejemplo reembolsos.
    """
    cuerpo = loader.cargar(nombre)
    if cuerpo is None:
        return {"error": f"no existe el skill {nombre}", "disponibles": [s["nombre"] for s in loader.listar()]}
    ctx.context.setdefault("skills_cargados", []).append({"skill": nombre, "tokens_aprox": contar_tokens(cuerpo)})
    return {"skill": nombre, "procedimiento": cuerpo}
