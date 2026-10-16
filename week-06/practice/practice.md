# Práctica 6. Retrieval bajo medición y contexto con presupuesto

**Semana:** 6 (sesión fusionada con la 7). **Entrega:** antes de la sesión 8. **Tiempo estimado:** 3 horas. **Costo:** cero con el backend local; cerca de 0.02 USD con la llave individual (unas 20 llamadas cortas para la sección de contexto).

## Objetivo

Elegir la configuración de retrieval de la mesa de soporte de Facturio (estrategia de chunking, tamaño, overlap, modelo de embeddings, k y filtros por metadata) a partir de un barrido medido contra el gold set del curso y contra un gold set propio, justificarla con hit@k, MRR y tokens de contexto, y fijar el presupuesto y el orden del contexto que se envía al modelo con una medición propia.

## Qué se evalúa

* Chunking fijo, recursivo y por estructura, y el efecto del contexto jerárquico.
* Modelos de embeddings: idioma, dimensión, longitud máxima y su efecto medido.
* Construcción del contexto: selección sin duplicados, presupuesto de tokens y posición del mejor fragmento, medidos sobre la respuesta.
* Métricas de retrieval con gold set (hit@k, recall@k, MRR) y la granularidad de la evidencia.
* Metadata filtering como decisión de la aplicación.
* Presupuesto de contexto: calidad frente a tokens por consulta.
* Predicciones registradas antes de medir y análisis de las que fallaron.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` de la semana 6.
* Tener a la mano las diez preguntas de la actividad 2 (`exercises/02-gold-set-propio.md`), o escribirlas en el paso 3.
* Abrir `practice-starter.ipynb` en Google Colab y `report-template.md` en un editor de texto. El starter descarga el corpus de Facturio desde el repositorio del curso.

## Instrucciones

1. **Predicciones y barrido.** Antes de ejecutar nada, llena `PREDICCIONES` en la sección 1 del starter: qué esperas de hit@3 al crecer el chunk, qué estrategia gastará más tokens de contexto, y cuántos puntos de hit@5 perderá un modelo en inglés. Ejecuta el barrido completo (sección, sección con contexto, fijo 200/500/1000 con overlap 0 %, 10 % y 25 %; k = 1, 3, 5, 10). Copia la tabla al reporte y marca con una línea cada predicción como acertada o fallida. Una predicción fallida no resta; una ausente sí.
2. **Dos modelos de embeddings.** Sobre las dos mejores configuraciones del barrido, compara el modelo multilingüe del curso con `all-MiniLM-L6-v2` (inglés). Anota hit@5, MRR y tiempo de embedding. Explica en tres líneas por qué el modelo en inglés "funciona algo" y por qué eso engaña.
3. **Gold set propio.** Llena `MI_GOLD` con diez preguntas sobre dos documentos que no se usaron en clase, con archivo y encabezado exacto; al menos dos que crucen secciones y una sin respuesta. La celda de verificación comprueba que cada evidencia exista. Evalúa con sección con contexto y con fijo 200. Para cada pregunta que falle en ambas, escribe un diagnóstico: pregunta ambigua, evidencia también en otra sección, o falla real del retriever.
4. **Un filtro por metadata.** Elige una pregunta del gold set del curso que falle con sección con contexto y encuentra un filtro por `tipo` que la arregle (o demuestra que ninguno la arregla). Responde en el reporte quién decidiría ese filtro en producción y qué pasa si se equivoca.
5. **Contexto con presupuesto.** La sección 5 del starter corre `q29` y `q30` con presupuestos de 150, 300, 600 y 900 tokens y con el mejor fragmento al inicio y al final. Antes de ejecutar, llena `PRED_CONTEXTO` con el presupuesto mínimo que esperas y si crees que la posición cambia la respuesta. Marca en `CORRECTA_5` cuáles respuestas son correctas comparando con la esperada. En el reporte: el presupuesto mínimo con respuestas correctas para ambas preguntas, qué pasa con la posición, y el presupuesto que fijarías para la mesa de soporte con los tokens de entrada por consulta y al mes.
6. **Recomendación.** Llena `RECOMENDACION` con la configuración que propones para Facturio: chunking, tamaño, modelo, k, filtros, presupuesto y orden del contexto. Cada elección con la fila de la tabla que la justifica y con el costo en tokens de contexto por consulta. Cierra con la lista de preguntas que siguen fallando y una línea sobre por qué ningún cambio de chunking las arregla.
7. **Reporte.** Llena `report-template.md` con las tablas que imprime el starter. Guarda el notebook ejecutado con todas las salidas.

## Entregables

* `practica-06-reporte.md`: el `report-template.md` llenado.
* `practica-06-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 8.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Predicciones registradas antes de medir | Faltan o se escribieron después de ver la tabla | Están las tres, con una línea de por qué | Cada predicción se contrasta con la tabla y se explica la que falló con un concepto de la sesión | 15 |
| Barrido correcto e interpretado | Tabla incompleta o sin lectura | Tabla completa con lectura de hit@k por tamaño | Lectura que distingue dilución, truncamiento y granularidad de la métrica, y que incluye el costo de contexto | 25 |
| Comparación de modelos de embeddings | Solo un modelo o sin números | Tabla con hit@5 y MRR de ambos | Explica el efecto del idioma y por qué la caída depende del chunking | 10 |
| Gold set propio | Menos de diez preguntas o evidencias inexistentes | Diez preguntas válidas y medidas | Preguntas con vocabulario de cliente, diagnóstico por falla y una observación sobre el diseño del gold set | 15 |
| Contexto con presupuesto | Tabla sin marcar correctas o sin decisión | Predicción previa, presupuesto mínimo identificado y decisión justificada con tokens | Además explica el efecto de la posición con las respuestas obtenidas y lo lleva a costo mensual | 15 |
| Filtro por metadata | Sin caso o sin resultado | Un caso con antes y después | Discute quién decide el filtro en producción y el costo de equivocarse | 10 |
| Recomendación justificada | Configuración sin tabla | Cada elección apunta a una fila de la tabla | Además pesa calidad contra tokens de contexto y declara la métrica usada | 10 |

Los pesos suman 100. El código que ejecuta es condición necesaria; la calificación se centra en la justificación con evidencia.

## Errores frecuentes

* **Escribir las predicciones después de ver la tabla.** Se nota porque coinciden exactamente y no tienen "por qué". Escríbelas primero; equivocarse es parte de la práctica.
* **Declarar ganador a fijo 200 sin mirar la métrica ni el costo.** Con la lectura estricta pierde, y gasta el doble de tokens. La recomendación debe decir con qué métrica se decidió.
* **Preguntas del gold set que copian el encabezado.** Inflan hit@k y no miden nada. Escribe la pregunta como la escribiría un cliente que no ha leído el documento.
* **Evidencias con el encabezado mal escrito.** La celda de verificación lo marca; corrígelo antes de evaluar.
* **Cambiar el modelo de embeddings sin ajustar `max_seq_length`.** Cada modelo tiene su límite; el starter lo imprime.
* **Fijar el presupuesto de contexto por la ventana máxima del modelo.** Se fija por medición: el presupuesto mínimo con respuestas correctas, con margen. Más contexto cuesta en cada llamada y puede empeorar la respuesta.

## Conexión

La configuración recomendada, el gold set propio y el presupuesto de contexto se reutilizan en la semana 8: el retrieval se convierte en la tool `buscar_documentacion` y el contexto que construye entra al modelo como un tool output más. Búsqueda lexical, reranking y evaluación de la generación quedan como lectura opcional en `week-07/`.

## Opcional, sin peso: sobre un caso propio

Si tienes un conjunto de documentos propio (el de tu tesis, por ejemplo), puedes repetir los pasos 1, 3 y 5 con él: cambia `cargar_corpus` por una función que lea tu carpeta y escribe un gold set de diez preguntas. Los documentos deben tener encabezados para que el chunking por estructura aplique. No se entrega ni se califica.
