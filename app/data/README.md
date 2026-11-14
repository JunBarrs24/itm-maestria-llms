# data/

Los datos de Facturio. Es la única carpeta que las tools leen y escriben.

| Archivo | Qué es |
| --- | --- |
| `facturio.py` | Usuarios, planes, cargos, reembolsos aplicados y tickets, en memoria. `reiniciar_estado()` los deja como al inicio. |
| `documentacion.py` | El corpus de `corpus/` partido por sección, con embeddings por API y una búsqueda por similitud. |
| `corpus/` | Manuales, políticas, preguntas frecuentes y catálogo de errores de Facturio (markdown). |

Semana en que apareció: 5 (corpus y búsqueda) y 8 (datos de la mesa de soporte).

Qué no va aquí: lógica de negocio (vive en `policies/`), tools (en `tools/`), nada que importe del SDK.
