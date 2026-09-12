# datasets/

## support_tickets.jsonl (semana 4)

50 tickets de soporte en español, escritos para el curso. Un registro por línea:

| Campo | Tipo | Descripción |
| --- | --- | --- |
| `id` | int | Identificador 1 a 50. |
| `texto` | str | Texto del ticket tal como lo escribiría el cliente. |
| `categoria` | str | Una de `facturacion`, `acceso`, `error_tecnico`, `solicitud_funcion`, `otro`. |
| `prioridad` | str | Una de `alta`, `media`, `baja`. |
| `pii` | bool | `true` si el texto contiene nombres, correos, teléfonos o RFC. |
| `nota` | str | Opcional. Por qué el caso es difícil o ambiguo. No se envía al modelo. |

Distribución: 12 facturación, 8 acceso, 12 error técnico, 8 solicitud de función, 10 otro. Prioridades: 13 alta, 17 media, 20 baja. Seis tickets con datos personales. Un ticket (id 22) contiene una instrucción de prompt injection.

Las etiquetas de los casos ambiguos son una decisión editorial documentada en `nota`. En clase se discute que el dataset también tiene errores de criterio, y que un desacuerdo entre el modelo y la etiqueta no siempre es culpa del modelo.

## corpus/ (semanas 5 a 8)

Base de conocimiento del caso del curso: 12 documentos markdown de Facturio (manuales, políticas, términos, códigos de error, notas de versión, seguridad, un comunicado con inyección deliberada), un gold set de 30 preguntas con evidencia por sección, y `00-biblia-del-producto.md` como fuente de verdad que no se indexa. Contiene términos exactos para búsqueda lexical, dos contradicciones históricas y catorce hechos trampa para evaluar grounding. Ver `corpus/README.md`.
