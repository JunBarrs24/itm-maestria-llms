"""Datos ficticios de Facturio, en memoria: usuarios, planes, cargos, reembolsos y tickets.

Es el "sistema de registro" de la mesa de soporte. Las tools leen y escriben aquí; nada
más lo toca. `reiniciar_estado()` deja todo como al inicio, para repetir experimentos.
"""
from __future__ import annotations

from datetime import date

HOY = date(2026, 9, 4)  # fecha fija para que los ejemplos sean reproducibles

USUARIOS: dict[str, dict] = {
    "u001": {"nombre": "Ana Torres", "correo": "ana.torres@example.com", "plan": "Básico",
             "facturas_mes": 41, "proyectos": 10, "reembolso_ultimos_12m": False},
    "u002": {"nombre": "Roberto Sánchez", "correo": "rsanchez@example.com", "plan": "Pro",
             "facturas_mes": 812, "proyectos": 23, "reembolso_ultimos_12m": False},
    "u003": {"nombre": "Escuela Técnica Morelia", "correo": "admin@etm.edu.mx", "plan": "Pro",
             "facturas_mes": 60, "proyectos": 4, "reembolso_ultimos_12m": False, "descuento": "educativo 40 %"},
    "u004": {"nombre": "Grupo Alfa SA de CV", "correo": "ti@grupoalfa.example.com", "plan": "Empresa",
             "facturas_mes": 5230, "proyectos": 118, "reembolso_ultimos_12m": False},
    "u005": {"nombre": "Luis Martínez", "correo": "lmartinez@example.com", "plan": "Básico",
             "facturas_mes": 0, "proyectos": 2, "reembolso_ultimos_12m": True},
}

LIMITES_PLAN = {
    "Básico": {"usuarios": 3, "proyectos": 10, "facturas_mes": 300, "excel": False, "precio": 599},
    "Pro": {"usuarios": 10, "proyectos": 50, "facturas_mes": 2000, "excel": True, "precio": 899},
    "Empresa": {"usuarios": None, "proyectos": None, "facturas_mes": None, "excel": True, "precio": None},
}

# Cargos de suscripción. `facturas_timbradas_periodo` decide reembolso completo o proporcional.
CARGOS: dict[str, dict] = {
    "PAY-00012345": {"usuario": "u001", "monto": 599.00, "fecha": date(2026, 8, 28), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 0, "estado": "cobrado"},
    "PAY-00012346": {"usuario": "u001", "monto": 599.00, "fecha": date(2026, 7, 28), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 37, "estado": "cobrado"},
    "PAY-00012347": {"usuario": "u002", "monto": 899.00, "fecha": date(2026, 8, 30), "concepto": "Pro mensual",
                     "facturas_timbradas_periodo": 12, "estado": "cobrado"},
    "PAY-00012348": {"usuario": "u002", "monto": 899.00, "fecha": date(2026, 8, 30), "concepto": "Pro mensual",
                     "facturas_timbradas_periodo": 0, "estado": "duplicado_detectado", "duplicado_de": "PAY-00012347"},
    "PAY-00012349": {"usuario": "u003", "monto": 539.40, "fecha": date(2026, 8, 25), "concepto": "Pro mensual (educativo)",
                     "facturas_timbradas_periodo": 9, "estado": "cobrado"},
    "PAY-00012350": {"usuario": "u004", "monto": 12500.00, "fecha": date(2026, 8, 28), "concepto": "Empresa mensual",
                     "facturas_timbradas_periodo": 4100, "estado": "cobrado"},
    "PAY-00012351": {"usuario": "u005", "monto": 599.00, "fecha": date(2026, 8, 29), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 0, "estado": "cobrado"},
    "PAY-00012352": {"usuario": "u002", "monto": 8990.00, "fecha": date(2026, 9, 1), "concepto": "Pro anual",
                     "facturas_timbradas_periodo": 3, "estado": "cobrado"},
}

REEMBOLSOS: dict[str, dict] = {}      # folio -> reembolso aplicado (idempotencia)
TICKETS_HUMANOS: list[dict] = []      # escalaciones creadas


def reiniciar_estado() -> None:
    """Deja los datos como al inicio (útil entre experimentos y en las evals)."""
    REEMBOLSOS.clear()
    TICKETS_HUMANOS.clear()
    for u in USUARIOS.values():
        u["reembolso_ultimos_12m"] = False
    USUARIOS["u005"]["reembolso_ultimos_12m"] = True
