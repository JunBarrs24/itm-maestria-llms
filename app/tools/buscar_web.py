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

# La búsqueda hospedada trae su propio lector: además de buscar, abre páginas por su cuenta (en el
# trace aparece como web_search con tipo "open_page"). Por eso el modelo casi nunca elige leer_pagina:
# compite con algo que la hospedada ya hace. Para que la división sea visible en clase (OpenAI busca,
# nuestra tool lee, con sandbox), se apaga el acceso a páginas de la hospedada:
#
# buscar_web = WebSearchTool(search_context_size="low", external_web_access=False)
#
# Con eso el flujo queda: web_search encuentra la URL, leer_pagina la abre y recorta, el modelo cita.
# Cuesta una vuelta más y la calidad de lectura es la de nuestro extractor de texto, no la de OpenAI.
buscar_web.progreso = "Buscando en internet…"
buscar_web.side_effect = False
buscar_web.hosted = True
