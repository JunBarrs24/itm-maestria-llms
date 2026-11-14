"""Modos: un solo agente que cambia de configuración (instrucciones + tools) en tiempo de ejecución.

Es la forma barata de especializar: antes de tener varios agentes, un agente con modos. Cada modo
es un archivo .md con las instrucciones y una lista de tools visibles. Quién cambia de modo es la
decisión de diseño de la semana 12:

  routing   el código, con un regex sobre el mensaje, antes de llamar al modelo (semana 8);
  modes     el modelo, con la tool `cambiar_modo` (como los modes de PostHog);
  handoffs  otro agente, entregando el turno (agents/triage.py).

En el SDK el mecanismo es `is_enabled` por tool e `instructions` como función: ambos leen el modo
del contexto de la aplicación en cada llamada, así que cambiar el modo cambia lo que el modelo ve
en la siguiente vuelta sin construir otro agente.
"""
from __future__ import annotations

import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent

MODOS: dict[str, dict] = {
    "general": {"tools": ["consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar", "escalar_a_humano", "web_search", "leer_pagina"],
                "descripcion": "Cualquier tema; todas las tools."},
    "facturacion": {"tools": ["consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar", "escalar_a_humano"],
                    "descripcion": "Cargos, cobros, reembolsos, planes y precios."},
    "acceso": {"tools": ["buscar_documentacion", "escalar_a_humano"],
               "descripcion": "Contraseñas, bloqueos, inicio de sesión, verificación en dos pasos."},
    "tecnico": {"tools": ["buscar_documentacion", "escalar_a_humano"],
                "descripcion": "Errores del producto, códigos E-xxxx, exportaciones."},
    "web": {"tools": ["web_search", "leer_pagina", "escalar_a_humano"],
            "descripcion": "Preguntas que requieren información de internet: normativa del SAT, noticias, precios de terceros."},
}

BASE = (AQUI / "general.md").read_text(encoding="utf-8").strip()


def instrucciones(modo: str) -> str:
    """Las instrucciones base más las del modo. El texto vive en los .md de esta carpeta."""
    if modo == "general":
        return BASE
    return BASE + " " + (AQUI / f"{modo}.md").read_text(encoding="utf-8").strip()


def tools_del_modo(modo: str) -> list[str]:
    return list(MODOS.get(modo, MODOS["general"])["tools"])


def ruta_determinista(texto: str) -> str:
    """Routing de la semana 8: una regla barata antes del modelo. Devuelve el modo."""
    t = texto.lower()
    if re.search(r"\bpay-\d{8}\b|cobr|cargo|reembols|factur|plan\b|mensualidad", t):
        return "facturacion"
    if re.search(r"contraseñ|password|bloque|iniciar sesi|entrar|2fa|código de verific|sesión", t):
        return "acceso"
    if re.search(r"\be-\d{4}\b|error|falla|se cierra|no funciona|pantalla|exportar|pdf", t):
        return "tecnico"
    if re.search(r"internet|en la web|google|https?://|www\.|\bsat\b|noticia|busca(r)? (en|sobre)", t):
        return "web"
    return "general"
