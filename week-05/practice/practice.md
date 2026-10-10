# Práctica 5. Mi primer RAG bajo diagnóstico

**Semana:** 5. **Entrega:** antes de la sesión 6. **Tiempo estimado:** 3 horas. **Costo:** cero con el backend local; con la llave individual y un modelo pequeño, cerca de 0.02 USD (unas 20 llamadas de 700 a 900 tokens de entrada).

## Objetivo

Construir un sistema RAG mínimo sobre el corpus de Facturio, responder trece preguntas del gold set, atribuir cada mala respuesta a su causa (retrieval o generación) con la evidencia recuperada como prueba, comparar cuatro unidades de chunking con la misma métrica, y decidir entre prompting, RAG y fine-tuning para tres requisitos de la mesa de soporte.

## Qué se evalúa

* El pipeline completo como funciones propias: chunking, embeddings, índice, retrieval, contexto, generación.
* La distinción retrieval frente a generación aplicada caso por caso, con las fuentes recuperadas como evidencia.
* Answerability: qué hace el sistema cuando la respuesta no está en el corpus.
* La unidad de chunking como decisión de ingeniería medida, con su costo en tokens.
* Criterios para elegir prompting, RAG o fine-tuning.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` de la semana 5.
* Tener la llave individual cargada como `OPENAI_API_KEY` en Colab (secretos) o usar el backend local. El reporte debe decir qué backend se usó; con el local las respuestas son peores y eso forma parte del análisis.
* Abrir `practice-starter.ipynb` en Colab y `report-template.md` en un editor.
* Tener a la mano la tabla de la actividad 1 (`exercises/01-clasificar-fallas.md`) como referencia de etiquetas.

## Instrucciones

### Parte 1. Pipeline (sección 1 del starter)

1. Ejecuta las celdas del pipeline. Son las mismas de la sesión. Antes de seguir, escribe en el reporte una línea por paso diciendo qué entra y qué sale (por ejemplo: "chunk_por_seccion: texto de un documento → lista de dicts con archivo, sección y texto").

### Parte 2. Trece preguntas (sección 2)

2. Ejecuta la evaluación: diez preguntas con evidencia (`factual_exacta` y `conceptual`) y tres `sin_respuesta`. La celda imprime, por pregunta, si la sección correcta llegó al top-5, la respuesta del sistema y la esperada.

### Parte 3. Diagnóstico (sección 3)

3. Llena `MI_DIAGNOSTICO` para las trece: `correcta` (True/False), `falla` con una de `correcta`, `falla_retrieval`, `falla_generacion`, `sin_respuesta_correcta`, `sin_respuesta_inventada`, y una justificación que mencione al menos una fuente recuperada. Regla: si `evid.top-5` es `NO` y la respuesta está mal, la falla es de retrieval aunque el texto parezca inventado; si es `sí` y está mal, es de generación.
4. En el reporte, cuenta cuántas fallas de cada tipo hubo y responde: ¿cuántas se arreglarían cambiando solo el prompt? ¿Cuántas requieren tocar el retriever?

### Parte 4. Unidad de chunking (sección 4)

5. Ejecuta la comparación de cuatro configuraciones: fijo 400/50, fijo 800/100, fijo 1500/200 y por sección. Antes de ejecutar, escribe en el reporte tu predicción: ¿cuál tendrá mejor `hit@5 sección` y cuál gastará más tokens por pregunta?
6. Copia la tabla y elige una configuración para la mesa de soporte en `MI_CONFIGURACION`, con una justificación que use las dos columnas de hit y la de tokens. Una configuración con el mejor hit y el triple de tokens no gana por defecto.

### Parte 5. Prompting, RAG o fine-tuning (sección 5)

7. Llena `MI_DECISION` para los tres requisitos con la técnica y el criterio que decidió (tabla de la actividad 2). Si un requisito combina dos técnicas, dilo y explica cuál resuelve qué.

### Parte 6. Reporte

8. Llena `report-template.md` con las tablas que imprime el starter y las respuestas. Guarda el notebook ejecutado con todas las salidas.

## Entregables

* `practica-05-reporte.md`: el `report-template.md` llenado.
* `practica-05-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 6.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | ---: |
| Pipeline | No corre, o las descripciones por paso faltan o son incorrectas. | Corre y cada paso tiene su entrada y salida descritas. | Además, identifica qué paso decide cuánto cuesta cada llamada y por qué. | 15 |
| Diagnóstico de las trece | Etiquetas sin justificación, o justificación sin mencionar fuentes, o confunde retrieval con generación cuando la columna de evidencia lo contradice. | Trece etiquetas coherentes con la columna de evidencia y justificadas con fuentes. | Además, señala un caso donde la respuesta fue correcta con la evidencia canónica ausente y explica por qué eso es trazabilidad frágil. | 30 |
| Answerability | Las tres `sin_respuesta` no se analizan o se cuentan como aciertos sin revisar el texto. | Las tres clasificadas como correcta o inventada, con el texto como prueba. | Además, propone una regla determinista (por ejemplo, umbral de score) que evitaría llamar al modelo cuando no hay evidencia, y argumenta su costo. | 15 |
| Unidad de chunking | Sin predicción, o sin tabla, o elección basada en una sola columna. | Predicción registrada, tabla completa y elección justificada con hit y tokens. | Además, explica por qué `hit@5 archivo` y `hit@5 sección` se separan y qué significa para la trazabilidad. | 20 |
| Prompting, RAG o fine-tuning | Decisiones sin criterio o con el criterio equivocado (por ejemplo, RAG para tono). | Tres decisiones con el criterio que decidió. | Además, identifica el requisito que combina técnicas y separa qué resuelve cada una. | 10 |
| Reporte | Incompleto o con afirmaciones sin tabla. | Completo, cada afirmación con su número o su fuente. | Además, cierra con dos líneas sobre qué mediría primero en la semana 6 y por qué. | 10 |

Total: 100. Un diagnóstico que llama "alucinación" a toda respuesta incorrecta, sin mirar la columna de evidencia, no aprueba el criterio de diagnóstico.

## Errores frecuentes

* **Indexar archivos que no son documentos.** El `README.md` del corpus y `gold_set.jsonl` no forman parte de la base de conocimiento. Si aparecen en las fuentes, las preguntas `sin_respuesta` pierden sentido porque el gold set contiene las respuestas.
* **Confundir "el archivo llegó" con "la evidencia llegó".** Un archivo de 1,000 palabras en el top-5 no garantiza que la sección con el dato esté en el contexto. Por eso hay dos columnas de hit.
* **Diagnosticar por el texto de la respuesta.** Una respuesta que suena inventada con `evid.top-5 = NO` es falla de retrieval. El texto engaña; la columna de evidencia decide.
* **Cambiar varias perillas a la vez.** Si cambias k y la unidad de chunking al mismo tiempo, no sabes cuál movió la métrica.
* **Elegir el chunking con más hit sin mirar los tokens.** En la mesa de soporte cada token de contexto se paga en cada llamada, para siempre.

## Conexión

La tabla de chunking de esta práctica es el punto de partida de la práctica 6: ahí se mide con hit@k, recall@k y MRR sobre el gold set completo y se agregan overlap, k, metadata y modelo de embeddings como variables.

## Opcional, sin peso: sobre un caso propio

Sustituye los doce archivos por documentos propios (markdown o texto con encabezados), escribe diez preguntas con su archivo y sección de evidencia, y repite las partes 2 a 4. No se entrega ni se califica; sirve para ver cuánto del diagnóstico depende del corpus y cuánto del pipeline.
