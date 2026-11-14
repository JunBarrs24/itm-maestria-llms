"""Tool con side effect: crea un ticket para una persona del equipo."""
from __future__ import annotations

from data import facturio as db
from tools.registry import RunContextWrapper, _requiere_aprobacion, function_tool, progreso, side_effect


@side_effect
@progreso("Pasando tu caso a una persona del equipo…")
@function_tool(needs_approval=_requiere_aprobacion)
def escalar_a_humano(ctx: RunContextWrapper[dict], motivo: str) -> dict:
    """Pasa el caso a una persona del equipo.

    Úsala cuando la política lo exija (montos altos, folios de otra cuenta, casos sin documentación)
    o cuando falte información que ninguna tool pueda dar. Crea un ticket y lo devuelve.

    Args:
        motivo: Qué necesita la persona para atenderlo, con el folio y el usuario si los hay.
    """
    t = {"ticket": f"HUM-{len(db.TICKETS_HUMANOS) + 1:04d}", "motivo": motivo, "usuario": ctx.context.get("usuario_id")}
    db.TICKETS_HUMANOS.append(t)
    ctx.context.setdefault("ejecutadas", []).append({"tool": "escalar_a_humano", "ticket": t["ticket"]})
    return t
