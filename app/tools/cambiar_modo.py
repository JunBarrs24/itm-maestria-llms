"""Tool sin side effect: el agente cambia de modo él mismo (diseño `modes`, semana 12)."""
from __future__ import annotations

from modes.modes import MODOS
from tools.registry import RunContextWrapper, function_tool, progreso


@progreso("Pasando tu caso al especialista…")
@function_tool
def cambiar_modo(ctx: RunContextWrapper[dict], modo: str) -> dict:
    """Cambia al modo especialista adecuado para el tema del cliente.

    Llámala al inicio cuando el tema sea claro: facturacion (cargos, reembolsos, planes), acceso
    (contraseñas, bloqueos, 2FA) o tecnico (errores, exportaciones). En el siguiente paso verás las
    instrucciones y las herramientas de ese modo. No la llames si ya estás en el modo correcto.

    Args:
        modo: Uno de: facturacion, acceso, tecnico, general.
    """
    if modo not in MODOS:
        return {"error": f"modo desconocido: {modo}", "modos": list(MODOS)}
    anterior = ctx.context.get("modo", "general")
    ctx.context["modo"] = modo
    ctx.context.setdefault("cambios_de_modo", []).append({"de": anterior, "a": modo})
    return {"modo": modo, "tools_visibles": MODOS[modo]["tools"], "descripcion": MODOS[modo]["descripcion"]}
