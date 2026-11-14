"""Tool de solo lectura: plan, límites y uso del mes de un usuario."""
from __future__ import annotations

from data import facturio as db
from tools.registry import function_tool, progreso


@progreso("Consultando tu plan…")
@function_tool
def consultar_plan(usuario_id: str) -> dict:
    """Consulta el plan contratado de un usuario y su uso del mes.

    Úsala cuando la pregunta sea sobre plan, límites, facturas emitidas, proyectos o precio.
    Devuelve plan, límites del plan, uso actual y si ya recibió un reembolso en los últimos 12 meses.

    Args:
        usuario_id: Identificador del usuario, formato u seguido de 3 dígitos, por ejemplo u002.
    """
    u = db.USUARIOS.get(usuario_id)
    if not u:
        return {"error": f"no existe el usuario {usuario_id}"}
    lim = db.LIMITES_PLAN[u["plan"]]
    return {"usuario_id": usuario_id, "nombre": u["nombre"], "plan": u["plan"], "limites": lim,
            "uso": {"facturas_mes": u["facturas_mes"], "proyectos": u["proyectos"]},
            "reembolso_ultimos_12m": u["reembolso_ultimos_12m"], **({"descuento": u["descuento"]} if "descuento" in u else {})}
