"""Tool hospedada: búsqueda web de OpenAI. La forma más fácil de darle internet a un agente.

No es una función nuestra: es una tool que ejecuta el proveedor (WebSearchTool). El modelo decide
la consulta, OpenAI busca, lee las páginas y devuelve un resumen con citas. Nada corre en nuestra
máquina, así que no hay sandbox que cuidar; a cambio no vemos qué páginas abrió más allá de las
citas, y cada llamada se cobra aparte de los tokens (ver precios de la herramienta web search).

Se registra como las demás, pero el registro la marca `hosted=True`: no tiene schema propio ni
needs_approval, y no se puede habilitar por modo en tiempo de ejecución.
"""
from __future__ import annotations

from agents import WebSearchTool

buscar_web = WebSearchTool(search_context_size="low")   # low: menos tokens de contexto por búsqueda
buscar_web.progreso = "Buscando en internet…"
buscar_web.side_effect = False
buscar_web.hosted = True
