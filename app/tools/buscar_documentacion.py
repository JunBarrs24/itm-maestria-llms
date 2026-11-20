"""Tool de solo lectura: búsqueda en la documentación (el RAG de la semana 5 como tool)."""
from __future__ import annotations

from data import documentacion
from tools.registry import function_tool, progreso

# Alternativa, comentada: que el mensaje de progreso lo escriba el modelo. Se agrega un argumento
# que el modelo tiene que llenar y el productor del streaming lo manda al cliente en lugar del texto
# fijo. Cuesta tokens de salida en cada llamada y es texto generado (hay que validarlo antes de
# mostrarlo); vale la pena solo cuando el progreso depende del caso y una frase fija no alcanza.
#
# @function_tool
# def buscar_documentacion(pregunta: str, aviso_para_el_cliente: str) -> dict:
#     """Busca en la documentación y políticas de Facturio.
#
#     Args:
#         pregunta: La duda en lenguaje natural.
#         aviso_para_el_cliente: Una frase corta, en segunda persona, que el cliente verá mientras buscas,
#             por ejemplo "Estoy revisando el plazo de reembolso en la política".
#     """
#     ...   # mismo cuerpo; en engines/streaming.py: mensaje = json.loads(raw_item.arguments)["aviso_para_el_cliente"]


@progreso("Buscando en las políticas de Facturio…")
@function_tool
def buscar_documentacion(pregunta: str) -> dict:
    """Busca en la documentación y políticas de Facturio.

    Úsala para plazos, límites, procedimientos y errores del producto. Consúltala antes de afirmar
    una política (por ejemplo, el plazo para pedir un reembolso); no respondas políticas de memoria.
    Devuelve hasta tres fragmentos con archivo, sección y score.

    Args:
        pregunta: La duda en lenguaje natural, con las palabras clave del cliente, por ejemplo
            "plazo para solicitar reembolso".
    """

    return {"fragmentos": documentacion.buscar(pregunta, k=3)}
