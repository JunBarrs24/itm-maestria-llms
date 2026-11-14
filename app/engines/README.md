# engines/

Quién corre el loop y cómo se traduce lo que pasa adentro.

| Archivo | Qué hace |
| --- | --- |
| `turno.py` | Un turno completo: `preparar` (diseño, modo, contexto), `sdk.correr`, `cerrar` (historial, estado, compresión, costo). `responder` y `decidir_aprobacion` son lo que llaman los endpoints y las evals. |
| `sdk.py` | `Runner.run` en un event loop propio; pausa y reanudación con `RunState`; guardrails y `MaxTurnsExceeded` convertidos en respuestas; `correr_stream` para SSE. |
| `tracing.py` | `TracingProcessor` que convierte los spans del SDK (response, function, guardrail, handoff, agent) en las entradas del panel Trace. |

Semana en que apareció: 10 (sustituyó al loop manual de la semana 8). Semana 13 agrega un segundo motor: el grafo de LangGraph.

Qué no va aquí: decidir quién atiende (`agents_app/`), qué ve el modelo (`context/`).
