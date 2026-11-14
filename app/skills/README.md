# skills/

Procedimientos que el agente carga cuando hacen falta. Una carpeta por skill, con un `SKILL.md`:

```
---
name: reembolsos
description: una línea; siempre visible para el modelo
---
El cuerpo: pasos, reglas, qué no hacer. Visible solo cuando el modelo llama a cargar_skill("reembolsos").
```

| Skill | Cuándo se carga |
| --- | --- |
| `reembolsos/` | el cliente pide un reembolso o dice que le cobraron de más |
| `escalacion/` | antes de escalar a una persona |
| `planes/` | el cliente pregunta si le conviene cambiar de plan |

`loader.py`: `listar()` (nombre y descripción), `cargar(nombre)` (el cuerpo), `indice_para_instrucciones()` (el párrafo que va en las instrucciones). El trace registra qué skill se cargó y cuántos tokens agregó.

Semana en que apareció: 12. Es Keep / Compress / Drop aplicado a las instrucciones: la descripción se conserva siempre, el cuerpo se descarta hasta que se necesita.

Qué no va aquí: instrucciones que aplican a todos los turnos (eso es un modo, `modes/`); código (eso es una tool, `tools/`).
