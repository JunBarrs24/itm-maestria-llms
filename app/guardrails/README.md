# guardrails/

Validaciones deterministas alrededor del modelo. Cada una se puede probar sin llave (`tests/test_guardrails.py`).

| Archivo | Cuándo corre | Qué revisa |
| --- | --- | --- |
| `input.py` | antes de la primera llamada | `solo_soporte`: temas fuera de la mesa. `folio_valido`: folios mal formados. Si disparan, no se llama al modelo. |
| `output.py` | sobre la respuesta final | `sin_afirmar_reembolso`: la respuesta dice que hubo reembolso y ninguna tool lo ejecutó. `sin_datos_personales`: correos o RFC en la respuesta. Si disparan, la app sustituye la respuesta y lo registra en el trace. |

Un guardrail de salida es un eval que corre en cada turno (`evals/` cuenta cuántas veces dispara en el gold set).

Semana en que apareció: 10 (entrada), 12 (salida).

Qué no va aquí: reglas de negocio sobre datos (eso es `policies/`); un guardrail mira texto, una política mira registros.
