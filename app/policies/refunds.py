"""Política de reembolsos de Facturio, en código.

Es la tercera capa de autorización (semana 8): el modelo puede pedir `reembolsar`, la aplicación
decide. Vive aparte de la tool para que se pueda leer, probar y cambiar sin tocar el schema que ve
el modelo. El usuario de la sesión lo inyecta la aplicación; el modelo nunca lo controla.
"""
from __future__ import annotations

from typing import Optional

from data import facturio as db

PLAZO_REEMBOLSO_DIAS = 14          # política de Facturio
MONTO_MAXIMO_SIN_HUMANO = 1000.0   # política de la aplicación: arriba de esto aprueba una persona


def autorizar_reembolso(folio: str, monto: float, usuario_sesion: Optional[str] = None) -> tuple[bool, str]:
    """Devuelve (autorizado, razón). Cada rechazo tiene una razón que el modelo puede explicar."""
    c = db.CARGOS.get(folio)
    if not c:
        return False, f"no existe el folio {folio}"
    if usuario_sesion is None:
        return False, "no hay usuario identificado en la sesión; un reembolso exige saber de quién es el cargo"
    if c["usuario"] != usuario_sesion:
        return False, f"el folio {folio} pertenece a otro usuario; no se reembolsa desde esta sesión"
    if folio in db.REEMBOLSOS:
        return False, f"el folio {folio} ya fue reembolsado (idempotencia)"
    if c["estado"] == "duplicado_detectado":
        return False, "cargo duplicado: la reversión es automática en 5 días hábiles, no se reembolsa por esta vía"
    dias = (db.HOY - c["fecha"]).days
    if dias > PLAZO_REEMBOLSO_DIAS:
        return False, f"fuera de plazo: {dias} días desde el cargo, el límite es {PLAZO_REEMBOLSO_DIAS}"
    u = db.USUARIOS[c["usuario"]]
    if u["reembolso_ultimos_12m"]:
        return False, "la cuenta ya recibió un reembolso en los últimos 12 meses"
    maximo = c["monto"] if c["facturas_timbradas_periodo"] == 0 else round(c["monto"] * 0.5, 2)
    if monto > maximo + 0.01:
        return False, f"monto mayor al permitido: máximo {maximo:.2f} (proporcional si hubo facturas timbradas)"
    if monto > MONTO_MAXIMO_SIN_HUMANO:
        return False, f"requiere aprobación humana: {monto:.2f} supera el límite automático de {MONTO_MAXIMO_SIN_HUMANO:.0f}"
    return True, "autorizado"
