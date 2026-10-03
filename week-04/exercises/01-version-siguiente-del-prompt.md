# Actividad 1. La versión siguiente del prompt

**Duración:** 20 minutos. **Modalidad:** individual o en parejas, sobre `notebooks/02-student-experiment.ipynb`, sección TODO 1.

## Instrucciones

1. Parte de `reg_v1` (instrucciones claras más formato JSON). Es la línea base.
2. Cambia **una sola cosa**: una regla nueva, la redefinición de una categoría, un ejemplo. Un cambio por versión permite atribuir el efecto.
3. Corre la evaluación sobre el dataset. Obtén la tabla por caso con `mejoró`, `empeoró`, `igual`.
4. Para cada caso que empeoró, escribe dos líneas: por qué tu cambio lo rompió y si la etiqueta del dataset es defendible.
5. Decide: ¿aceptarías tu versión para producción? Justifica con la tabla por caso y la de costo.

## Entregable

Una celda de texto al final del notebook con:

* el cambio exacto (diff en prosa de una línea);
* el conteo mejoró / empeoró / igual;
* el análisis de los casos que empeoraron;
* la decisión y su justificación.
