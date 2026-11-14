# context/

Lo que la aplicación guarda y lo que decide enviar al modelo. Es la misma separación en cualquier diseño (un agente, modos, varios agentes).

| Archivo | Qué hace |
| --- | --- |
| `session.py` | `Sesion`: historial completo, estado estructurado (usuario, modo, folios, restricciones, pasos, hechos), resumen, corrida pendiente. `actualizar_estado` = KEEP con reglas deterministas. `construir_contexto` = estrategias A / B / C. |
| `compression.py` | COMPRESS: resumen con LLM o determinista de lo que sale de la ventana. |

Semana en que apareció: 8 (sesión fusionada con la 9).

Qué no va aquí: nada del SDK. El runtime ofrece `SQLiteSession` para guardar el historial; la app no la usa porque la política de contexto (qué entra y qué no) es de la aplicación.
