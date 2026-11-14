# agents_app/

Quién atiende el turno. Tres diseños sobre los mismos modos, tools y guardrails; lo que cambia es quién decide el especialista y qué contexto viaja.

| Diseño | Archivo | Quién elige el modo | Qué contexto viaja |
| --- | --- | --- | --- |
| `routing` | `soporte.py` → `agente_routing` | el código (regex de `modes/modes.py`) antes de llamar al modelo | nada: un solo agente |
| `modes` | `soporte.py` → `agente_modes` | el modelo, con `tools/cambiar_modo.py` | nada: cambian instrucciones y tools dentro del mismo agente |
| `handoffs` | `triage.py` → `agente_triage` | otro agente (Triage), entregando el turno | todo el historial, o el paquete mínimo con `input_filter` |

Mecanismos del SDK que se usan: `instructions` como función, `is_enabled` por tool, `handoff(agente, input_filter=…)`, `handoff_description`.

Semana en que apareció: 12. La semana 13 agrega el diseño `grafo` (LangGraph) en `engines/`.

Qué no va aquí: el loop (`engines/`), el texto de instrucciones (`modes/`, `skills/`), las tools (`tools/`).
