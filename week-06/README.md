# Semana 6. Retrieval Engineering y construcción del contexto

**Bloque:** RAG. **Sesión fusionada:** cubre la semana 6 del plan y la construcción del contexto de la semana 7; el resto de la 7 (búsqueda híbrida, reranking, evaluación de la generación) queda como lectura opcional en `week-07/`. **Unidad del temario:** 2.5. **Densidad:** media.

## Pregunta central

> ¿Qué determina qué información termina viendo el modelo?

La semana 5 dejó un RAG que funciona a veces. Esta semana abre el retriever y lo trata como un componente de ingeniería: cada decisión (cómo se parte el documento, con qué modelo se embebe, cuántos fragmentos se recuperan, qué metadata se guarda) se mide contra un gold set antes de aceptarla.

## Objetivos

Al terminar la sesión el estudiante podrá:

* construir un gold set de preguntas con su evidencia y calcular hit@k, recall@k y MRR sobre un retriever;
* explicar qué pierde un documento al parsearse (PDF, HTML, tablas) y por qué la limpieza cambia los embeddings;
* comparar chunking fijo, recursivo y por estructura, y leer el trade-off entre precisión del fragmento y contexto suficiente en una tabla;
* elegir chunk size, overlap y top-k a partir de mediciones y del presupuesto de tokens de contexto;
* explicar qué aporta un modelo de embeddings (dimensión, idioma, dominio, longitud máxima) y medir el efecto de cambiarlo;
* usar metadata (archivo, sección, tipo de documento) para filtrar candidatos y arreglar consultas que el embedding confunde;
* decir qué abstrae una base vectorial (FAISS, Chroma) respecto a numpy y qué cuesta esa abstracción;
* reconocer que la granularidad de la métrica decide qué configuración "gana", y elegirla con criterio.

## Conocimientos previos

* Semana 5: el pipeline completo (parse → chunk → embed → indexar → recuperar → contexto → generar), cosine similarity y la primera falla de retrieval observada.
* Nociones de precisión y recall (cinco minutos de repaso en la apertura).
* Python con listas de diccionarios y numpy básico.
* Sin llave de API: la sesión completa corre con modelos de embeddings locales en Colab.

## Conceptos fundamentales

* Parsing de documentos reales: markdown, PDF (pypdf), HTML, tablas. Qué estructura se pierde y qué ruido entra.
* Limpieza: qué se normaliza, qué se conserva (encabezados, códigos, montos).
* Chunking: tamaño, overlap, estrategias fijo, recursivo y por estructura. Chunks con contexto jerárquico (título > sección > subsección).
* Metadata: archivo, sección, tipo de documento, fecha, plan. Metadata filtering.
* Modelos de embeddings: dimensión, idioma, dominio, `max_seq_length` y truncamiento, costo.
* Vector stores: numpy, FAISS, Chroma. Similarity coseno, top-k, ruido y costo de contexto.
* Métricas de retrieval con gold set: hit@k, recall@k, MRR. Granularidad de la evidencia (sección frente a archivo).

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 5: el chunk correcto existía y el retrieval no lo trajo. Pregunta central. Regla del día: gold set y métrica antes de cambiar cualquier parámetro. |
| Concepto y mecanismo | 50 | hit@k, recall@k y MRR con un ejemplo de tres preguntas (10). Chunking: tres estrategias, el barrido y el contexto jerárquico (20). La métrica decide al ganador (5). Modelo de embeddings (5). Metadata y filtering (5). Construcción del contexto: cuatro decisiones de la aplicación (5). |
| Receso | 15 | |
| Demo guiada y experimento | 60 | la demo guiada del profesor: gold set y línea base; barrido de chunk size, overlap y k; contexto jerárquico; sensibilidad de la métrica; cambio de modelo; metadata filtering; construcción del contexto: la misma evidencia en tres posiciones y el presupuesto medido. |
| Actividad | 15 | `exercises/01-predecir-chunk-size.md` sobre `notebooks/02-student-experiment.ipynb`. |
| Cierre | 25 | Recomendación de configuración para Facturio con la tabla. Lo que sigue fallando y el árbol de diagnóstico: ¿falla el retrieval o la generación? Conexión con la semana 8: el modelo pide acciones. Práctica. |

Parsing de PDF y vector stores (FAISS, Chroma) salen de la sesión y quedan en el notebook del estudiante como lectura con código. Si la sesión va tarde, la comparación de modelos de embeddings se muestra solo con la tabla. El cierre no se recorta: contiene el árbol de diagnóstico y la conexión con tool calling.

## Resultados de aprendizaje

* Una tabla de barrido (estrategia × tamaño × overlap × k) con hit@k, MRR y tokens de contexto, medida por el estudiante.
* Diez pares pregunta → sección construidos por el estudiante y medidos con dos modelos de embeddings.
* Una recomendación de configuración de retrieval para Facturio justificada con la tabla y con el presupuesto de contexto.
* La explicación, en dos líneas, de por qué una métrica laxa y una estricta dan ganadores distintos.

## Conexión con la semana anterior

La semana 5 construyó el pipeline a mano y mostró un caso donde el chunk correcto existía y no se recuperó. Esta semana convierte esa observación en un número (hit@k) y atribuye cada mejora o empeoramiento a un parámetro concreto.

## Conexión con la semana siguiente (semana 8)

RAG recupera información y la aplicación construye el contexto. El siguiente peldaño aparece cuando el modelo necesita ejecutar acciones o consultar sistemas vivos: la semana 8 introduce tool calling, y el retrieval de hoy se convierte en la tool `buscar_documentacion`. Búsqueda lexical, híbrida y reranking, y la evaluación de la generación con rúbrica y juez, quedan como lectura opcional en `week-07/` y reaparecen en la semana 15.

## Artefacto sobre el caso del curso

Configuración de retrieval recomendada para la mesa de soporte de Facturio: estrategia de chunking, tamaño, overlap, modelo de embeddings, k y filtros por metadata, con la tabla que la justifica y el gold set extendido con diez pares propios. Opcional, sin peso: repetirlo sobre un corpus propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-predecir-chunk-size.md`
* `exercises/02-gold-set-propio.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-06/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-06/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-06-slides.pptx`
