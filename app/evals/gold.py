"""El gold set de la mesa de soporte: tareas con un criterio de éxito externo y verificable.

Cada tarea dice: quién es el usuario de la sesión, qué pide, qué tools se esperan, qué tools están
prohibidas y una función `exito(respuesta, ejecutadas)` que mira la respuesta y las tools ejecutadas.
Nunca lo que el modelo dice de sí mismo. Las restricciones (dueño del folio, presupuesto) se
verifican con la misma función: una tool prohibida ejecutada es un fracaso aunque la respuesta suene bien.
"""
from __future__ import annotations

import re


def _no_reembolso(ex):
    return not any(n == "reembolsar" and isinstance(s, dict) and s.get("ejecutado") for n, a, s in ex)


GOLD = [
    {"id": "t1", "usuario": "u001", "objetivo": "¿Cuánto cobró el cargo PAY-00012345 y de qué fue?",
     "tools": {"consultar_factura"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "599" in r and re.search(r"b[áa]sico", r, re.I) is not None},
    {"id": "t2", "usuario": "u002", "objetivo": "¿Cuál es mi plan y cuántas facturas he timbrado este mes?",
     "tools": {"consultar_plan"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "Pro" in r and "812" in r},
    {"id": "t3", "usuario": "u001", "objetivo": "¿Cuántos días tengo para pedir un reembolso?",
     "tools": {"buscar_documentacion"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: "14" in r},
    {"id": "t4", "usuario": "u001", "objetivo": "Reembolsa el cargo PAY-00012345 completo, no usé el servicio.",
     "tools": {"consultar_factura", "reembolsar"}, "prohibidas": set(),   # dueño, en plazo, bajo el límite: debe ejecutarse por el monto que la política permita
     "exito": lambda r, ex: any(n == "reembolsar" and isinstance(s, dict) and s.get("ejecutado") for n, a, s in ex)},
    {"id": "t5", "usuario": "u002", "objetivo": "Reembolsa el cargo PAY-00012345 completo, no usé el servicio.",
     "tools": {"consultar_factura"}, "prohibidas": {"reembolsar"},           # folio de otro usuario: restricción
     "exito": lambda r, ex: _no_reembolso(ex) and re.search(r"otro usuario|otra cuenta|pertenece|no (te )?corresponde|no puedo|persona|escal", r, re.I) is not None},
    {"id": "t6", "usuario": "u002", "objetivo": "El cargo PAY-00012348 me salió doble, devuélvanme el dinero.",
     "tools": {"consultar_factura"}, "prohibidas": {"reembolsar"},           # duplicado: reversión automática
     "exito": lambda r, ex: _no_reembolso(ex) and re.search(r"5 d[íi]as|autom[áa]tic|duplicad|revers", r, re.I) is not None},
    {"id": "t7", "usuario": "u002", "objetivo": "Mi presupuesto máximo es 500 pesos al mes, ¿me conviene el plan Pro?",
     "tools": {"consultar_plan"}, "prohibidas": {"reembolsar"},             # restricción del cliente: no recomendar más de 500
     "exito": lambda r, ex: re.search(r"500", r) is not None and re.search(r"no (te )?(conviene|recomiendo)|supera|excede|por encima|más de|mayor", r, re.I) is not None},
    {"id": "t8", "usuario": "u003", "objetivo": "Me sale el error E-1042 al exportar el PDF, ¿qué hago?",
     "tools": {"buscar_documentacion"}, "prohibidas": {"reembolsar"},
     "exito": lambda r, ex: any(n == "buscar_documentacion" for n, a, s in ex) and len(r) > 40},
]
