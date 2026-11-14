"""Tool con side effect: mueve dinero. Pasa por las tres capas de autorización."""
from __future__ import annotations

import uuid

from data import facturio as db
from policies.refunds import autorizar_reembolso
from tools.registry import RunContextWrapper, _requiere_aprobacion, function_tool, progreso, side_effect


@side_effect
@progreso("Solicitando el reembolso…")
@function_tool(needs_approval=_requiere_aprobacion)
def reembolsar(ctx: RunContextWrapper[dict], folio: str, monto: float, motivo: str) -> dict:
    """Solicita el reembolso de un cargo. Tiene side effect: mueve dinero.

    Llámala solo después de consultar_factura y cuando el cliente la haya pedido de forma explícita.
    La aplicación aplica su política (dueño del folio, plazo, monto, duplicados, límite que exige
    persona) y puede rechazarla: si devuelve ejecutado=false, explica la razón y no lo intentes de nuevo.

    Args:
        folio: Folio del cargo verificado, formato PAY- seguido de 8 dígitos.
        monto: Monto a reembolsar en pesos, mayor que cero y no mayor que el cargo.
        motivo: Razón del cliente en una frase, por ejemplo "cobro duplicado".
    """
    # el usuario de la sesión viene del contexto de la aplicación, nunca de un argumento del modelo
    ok, razon = autorizar_reembolso(folio, monto, ctx.context.get("usuario_id"))
    if not ok:
        return {"ejecutado": False, "razon": razon}
    ref = f"REF-{uuid.uuid4().hex[:8].upper()}"
    db.REEMBOLSOS[folio] = {"referencia": ref, "monto": monto, "motivo": motivo, "fecha": db.HOY.isoformat()}
    db.USUARIOS[db.CARGOS[folio]["usuario"]]["reembolso_ultimos_12m"] = True
    ctx.context.setdefault("ejecutadas", []).append({"tool": "reembolsar", "folio": folio, "referencia": ref})
    return {"ejecutado": True, "referencia": ref, "monto": monto, "abono_en": "5 a 10 días hábiles"}
