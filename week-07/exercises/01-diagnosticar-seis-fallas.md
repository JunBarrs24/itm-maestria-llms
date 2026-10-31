# Actividad 1. Diagnosticar seis fallas (20 minutos)

## Objetivo

Aplicar el árbol de diagnóstico de la sesión a seis respuestas malas del sistema RAG de Facturio: ubicar en qué peldaño está la falla (corpus, retrieval, contexto, generación) y proponer la intervención más barata que la corrige.

## Instrucciones para el estudiante

Trabaja en parejas. Para cada caso tienes la pregunta, la respuesta esperada, lo que trajo el retriever, lo que entró al contexto y la respuesta del sistema (celda de la sección 5 de `02-student-experiment.ipynb`, o la tabla impresa que reparte el profesor). Llena la tabla:

| Caso | ¿Evidencia en el corpus? | ¿Entre los candidatos? (posición) | ¿En el contexto? (posición) | Peldaño de la falla | Intervención más barata |
| --- | --- | --- | --- | --- | --- |
| A. `q23` ¿Cuántos empleados tiene Facturio? | | | | | |
| B. `q05` cabecera de la API con k=3 | | | | | |
| C. `q26` reembolso 30 vs 14 días | | | | | |
| D. `q30` con el mejor chunk al final | | | | | |
| E. `q13` corregir uso de CFDI | | | | | |
| F. `q29` con presupuesto de 150 tokens | | | | | |

Reglas:

* El peldaño se decide en orden. Si la evidencia no está en el corpus, la falla es de cobertura aunque el modelo haya inventado algo.
* "Más barata" se refiere a costo de implementación y de operación: cambiar un parámetro es más barato que cambiar de modelo; un filtro determinista es más barato que un reranker; un reranker es más barato que reentrenar nada.
* Si un caso sale bien con tu backend, escribe "sin falla" y explica por qué esa configuración lo evita.

## Entregable

La tabla llena y una línea por caso. Se discute en plenaria con dos parejas por caso.
