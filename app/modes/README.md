# modes/

Un agente, varios modos. Cada modo es instrucciones (un `.md`) más una lista de tools visibles.

| Archivo | Qué es |
| --- | --- |
| `modes.py` | `MODOS` (tools y descripción por modo), `instrucciones(modo)`, `tools_del_modo(modo)`, `ruta_determinista(texto)` (el regex de la semana 8). |
| `general.md`, `facturacion.md`, `acceso.md`, `tecnico.md` | El texto de instrucciones de cada modo. Se edita aquí, no en Python. |

Quién cambia de modo es el diseño que se compara en la semana 12: el código (routing), el modelo (`tools/cambiar_modo.py`) u otro agente (`agents/triage.py`). El mecanismo en el SDK: `is_enabled` por tool e `instructions` como función, ambos leen `ctx.context["modo"]`.

Semana en que apareció: 8 (como `ESPECIALISTAS` y routing), 12 (como modos).

Qué no va aquí: procedimientos largos que solo hacen falta a veces; eso es un skill (`skills/`).
