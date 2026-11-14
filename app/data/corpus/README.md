# Corpus de Facturio

Base de conocimiento del caso común del curso: la mesa de soporte de Facturio, un SaaS ficticio de facturación electrónica para pymes mexicanas. Todo el contenido fue creado para el curso y es coherente con `support_tickets.jsonl`: los tickets de la semana 4 son preguntas que este corpus responde.

## Archivos

| Archivo | Palabras | Contenido |
| --- | --- | --- |
| `01-manual-facturacion-cfdi.md` | 979 | Emitir, timbrar, corregir y cancelar CFDI; usos G03 y P01; errores E-2xxx |
| `02-manual-usuarios-e-invitaciones.md` | 879 | Roles, invitaciones (72 h), contraseñas, bloqueo, sesiones |
| `03-manual-reportes-y-exportacion.md` | 798 | Dashboard, reportes, PDF/CSV/Excel, adjuntos (25 MB), búsqueda |
| `04-manual-integraciones-y-api.md` | 784 | API v2 (X-Facturio-Key, límites), webhooks, ERP, Google Calendar |
| `05-preguntas-frecuentes.md` | 1153 | Respuestas cortas a los tickets más comunes, con remisión al documento |
| `06-politica-reembolsos-y-cargos.md` | 807 | Reembolso 14 días, uno cada 12 meses, cargos duplicados, cambios de plan, descuentos |
| `07-politica-cancelacion-y-eliminacion.md` | 847 | Cancelar (solo lectura 90 días) frente a eliminar (30 días, CFDI 5 años) |
| `08-terminos-del-servicio-y-sla.md` | 831 | Planes y límites (tabla), pagos, SLA por plan, créditos, exclusiones |
| `09-catalogo-codigos-de-error.md` | 1075 | Los 20 códigos E-xxxx con causa, solución y tabla resumen |
| `10-notas-de-version.md` | 776 | Versiones 3.1.0 a 3.5.2 con fechas; contiene las dos contradicciones históricas |
| `11-guia-de-seguridad.md` | 820 | Contraseñas, 2FA (90 s, 10 códigos), sesiones, IPs permitidas, fraude |
| `12-comunicado-externo.md` | 811 | Programa de aliados contables; contiene la inyección deliberada |

Total indexable: 10560 palabras en 12 documentos. Cada documento usa encabezados `##` y `###` reales para permitir chunking por estructura.

### Lo que no se indexa

`00-biblia-del-producto.md` es la fuente de verdad del caso (planes, políticas numéricas, códigos, versiones, hechos trampa y contradicciones deliberadas). Sirve para construir material, tools y datasets de evaluación coherentes. No forma parte del corpus que ve el sistema RAG: si se indexa, las preguntas de contradicción y de answerability pierden sentido.

## Gold set

`gold_set.jsonl`: 30 preguntas de usuario con respuesta esperada breve, tipo y evidencia (archivo y encabezado de sección).

| Tipo | Cantidad | Para qué |
| --- | --- | --- |
| `factual_exacta` | 10 | Códigos, montos, versiones, cabeceras: motivan la búsqueda lexical (semana 7) |
| `conceptual` | 10 | Preguntas de procedimiento donde la búsqueda semántica funciona bien |
| `sin_respuesta` | 5 | La respuesta no está en el corpus; evalúan answerability (semana 5) |
| `contradiccion` | 3 | Tocan pasajes que se contradicen entre versiones; evalúan selección de evidencia (semana 7) |
| `multi_documento` | 2 | Requieren evidencia de dos documentos; evalúan construcción de contexto (semana 7) |

Campos: `id`, `pregunta`, `respuesta_esperada`, `tipo`, `evidencia` (lista de `{"archivo", "seccion"}`; vacía en `sin_respuesta`).

## Rasgos deliberados

* **Términos exactos** en todos los documentos: códigos `E-1042`, versiones `3.4.1`, montos, cabeceras de API, claves de CFDI. Una consulta por código falla con embeddings y acierta con BM25.
* **Dos contradicciones históricas**: el plazo de reembolso (30 días en las notas de la versión 3.2.0, 14 días en la política vigente) y el tamaño de adjuntos (10 MB en la versión 3.1.0, 25 MB desde 3.3.0). La fuente vigente es siempre el documento de política o el manual, con fecha.
* **Una inyección indirecta** en `12-comunicado-externo.md`, sección "Trámite de certificación": una instrucción dirigida a asistentes automáticos que contradice el costo real de la certificación. Se usa en la semana 7 para mostrar que un documento recuperado puede intentar dar órdenes al modelo.
* **Hechos trampa**: catorce afirmaciones del corpus que un modelo puede contradecir con conocimiento general (lista en la biblia). La respuesta correcta es la del corpus.

## Uso por semana

* **Semana 5**: RAG mínimo sobre los 12 documentos; preguntas `conceptual` y `sin_respuesta`.
* **Semana 6**: barrido de chunk size, overlap y top-k medido con hit@k sobre el gold set; chunking por estructura con los encabezados.
* **Semana 7**: hybrid retrieval con las preguntas `factual_exacta`, reranking, construcción de contexto con `multi_documento` y `contradiccion`, evaluación de generación, inyección indirecta.
* **Semana 8 en adelante**: las políticas numéricas de la biblia definen el comportamiento de las tools (reembolsar respeta 14 días y un reembolso por año) y los guardrails de los agentes.

## Licencia

Contenido ficticio creado para el curso. Facturio no existe; cualquier coincidencia con productos reales es casual. Se puede reutilizar con fines educativos citando el curso.
