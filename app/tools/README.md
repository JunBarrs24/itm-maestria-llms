# tools/

Una tool por archivo. Agregar una tool es crear un archivo aquí; `registry.registrar()` la descubre.

| Archivo | Side effect | Qué hace |
| --- | --- | --- |
| `consultar_factura.py` | no | Un cargo por folio. |
| `consultar_plan.py` | no | Plan, límites y uso de un usuario. |
| `buscar_documentacion.py` | no | Búsqueda en el corpus (`data/documentacion.py`). |
| `reembolsar.py` | sí | Pasa por `policies/refunds.py`; con los side effects automáticos apagados, el SDK pausa y una persona decide. |
| `escalar_a_humano.py` | sí | Crea un ticket. |
| `cambiar_modo.py` | no | Semana 12: el agente cambia de modo (instrucciones y tools) él mismo. |
| `cargar_skill.py` | no | Semana 12: carga el cuerpo de un skill de `skills/` cuando hace falta. |
| `buscar_web.py` | no | Semana 12: búsqueda web hospedada por OpenAI (`WebSearchTool`). No corre en nuestra máquina; se cobra por llamada. Trae su propio lector de páginas (`open_page`); comentada está la opción `external_web_access=False` para que lea solo con `leer_pagina`. |
| `leer_pagina.py` | no | Semana 12: descarga una página y devuelve su texto, con sandbox ligero (solo http(s), sin hosts privados, tiempo y tamaño máximos, recorte a 4,000 caracteres). |
| `crear_plan.py` | no | Semana 13: plan mode. Guarda el plan en el contexto; `plan_para_instrucciones` lo muestra con su avance en cada vuelta. |
| `registry.py` | | Decoradores `@progreso` y `@side_effect`, la regla `_requiere_aprobacion`, el registro. |

Anatomía de una tool:

```python
@side_effect                                    # metadato: cambia el mundo
@progreso("Solicitando el reembolso…")          # lo que el cliente ve mientras corre (streaming)
@function_tool(needs_approval=_requiere_aprobacion)   # la firma y el docstring son el schema
def reembolsar(ctx: RunContextWrapper[dict], folio: str, monto: float, motivo: str) -> dict:
    """Primer párrafo: descripción de la tool. Luego cuándo usarla y cuándo no.

    Args:
        folio: cada línea de Args es la descripción de ese parámetro en el JSON schema.
    """
```

`ctx.context` es el diccionario que la aplicación pasa a `Runner.run` (usuario de la sesión, modo, side effects automáticos, tools ejecutadas). El modelo no lo ve ni lo controla.

Semana en que apareció: 8 (tools y dispatcher), 10 (`function_tool`, `needs_approval`), 12 (modos y skills).

Qué no va aquí: política de negocio (`policies/`), datos (`data/`), texto de instrucciones (`modes/`, `skills/`).
