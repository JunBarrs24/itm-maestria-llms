# policies/

Reglas de negocio de la aplicación, en código y sin modelo de por medio.

| Archivo | Qué decide |
| --- | --- |
| `refunds.py` | `autorizar_reembolso(folio, monto, usuario_sesion)`: dueño del folio, idempotencia, duplicados, plazo, un reembolso por año, monto proporcional, límite que exige persona. |

Semana en que apareció: 8. Es la tercera capa de autorización: la primera es qué tools ve el modelo (`modes/`), la segunda es `needs_approval` (`tools/registry.py`), la tercera es esta.

Qué no va aquí: nada que lea el prompt o la respuesta del modelo; eso es un guardrail (`guardrails/`). Una política se prueba con `pytest tests/test_policies.py` sin llave.
