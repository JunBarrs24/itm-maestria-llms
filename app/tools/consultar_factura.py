"""Tool de solo lectura: un cargo por folio."""
from __future__ import annotations

import re

from data import facturio as db
from tools.registry import function_tool, progreso


@progreso("Revisando el cargo…")
@function_tool
def consultar_factura(folio: str) -> dict:
    """Consulta un cargo de suscripción por folio.

    Úsala cuando el cliente mencione un cargo, un cobro, un folio o un reembolso: antes de opinar
    sobre un cargo hay que verlo. No la uses para preguntas de política (para eso está
    buscar_documentacion). Devuelve monto, fecha, concepto, estado, usuario dueño y días desde el cargo.

    Args:
        folio: Folio del cargo, formato PAY- seguido de 8 dígitos, por ejemplo PAY-00012345.
    """
    if not re.fullmatch(r"PAY-\d{8}", folio):
        return {"error": "folio inválido: el formato es PAY- seguido de 8 dígitos"}
    c = db.CARGOS.get(folio)
    if not c:
        return {"error": f"no existe el folio {folio}"}
    return {"folio": folio, "usuario": c["usuario"], "monto": c["monto"], "fecha": c["fecha"].isoformat(),
            "concepto": c["concepto"], "facturas_timbradas_periodo": c["facturas_timbradas_periodo"],
            "estado": c["estado"], "dias_desde_el_cargo": (db.HOY - c["fecha"]).days,
            **({"duplicado_de": c["duplicado_de"],
                "politica": "cargo duplicado: la reversión es automática en 5 días hábiles sin solicitud; "
                            "si no se refleja, abrir ticket con el folio"} if "duplicado_de" in c else {})}
