# Práctica 4. Un prompt bajo pruebas

**Semana:** 4. **Entrega:** antes de la sesión 5. **Tiempo estimado:** 3 horas. **Costo:** cerca de 0.10 USD por estudiante con la llave individual y un modelo pequeño (estimación del starter con la tabla de precios de `shared/usage.py`); cero con el backend local.

## Objetivo

Mejorar el prompt de clasificación de tickets del curso con un solo cambio medido por caso, extender el dataset con criterio documentado, diseñar una restricción verificable con su verificador, y decidir qué versión iría a producción considerando calidad, costo y latencia.

## Qué se evalúa

* Prompt regression: un cambio a la vez y tabla por caso (mejoró / empeoró / igual).
* Criterio de etiquetado explícito y análisis de los desacuerdos entre modelo y etiqueta.
* Restricciones verificables y validación en la aplicación, fuera del modelo.
* Structured output con schema Pydantic y format compliance como métrica separada de accuracy.
* Registro de tokens, latencia y costo, y decisión de producción con esas tres variables.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` de la semana 4.
* Tener la llave individual cargada como variable de entorno `OPENAI_API_KEY` en Colab (menú de secretos o `os.environ`). Sin llave, el starter usa el backend local (`Qwen2.5-1.5B-Instruct`), que tarda más y acierta menos; se acepta, pero el reporte debe decir qué backend se usó.
* Leer `shared/primers/02-pydantic.md` si no se hizo en la semana.
* Tener los 20 tickets de la actividad 2 (`exercises/02-extender-el-dataset.md`) o escribirlos en el paso 3.

## Instrucciones

1. **Línea base.** El starter trae `REG_V1`, el prompt de clasificación de la sesión (instrucciones claras más JSON con `categoria` y `prioridad`), y el dataset de 50 tickets. Ejecuta la evaluación de `REG_V1` sobre `N_TICKETS` (50 con llave; 20 con backend local). Anota accuracy de categoría, accuracy de prioridad, format compliance, tokens y latencia.
2. **Un cambio.** Escribe `REG_V4` con **un solo cambio** respecto a `REG_V1` (una regla de desempate, una definición de clase, un ejemplo, una instrucción de prioridad). Escribe en `CAMBIO_V4` qué cambiaste y qué casos esperas que mejore. Ejecuta la evaluación y produce la tabla de regresión por caso. Para cada caso que empeoró, decide si el prompt lo rompió o si la etiqueta es discutible, y argumenta.
3. **Extender el dataset.** Llena `TICKETS_EXTRA` con 20 tickets nuevos (ids 51 a 70) con las reglas de la actividad 2: al menos cuatro ambiguos con `nota` que documente el criterio, al menos dos con datos personales inventados, uno con una instrucción inyectada. Ejecuta el mejor prompt (v1 o v4, según la tabla) sobre los 70 y compara las métricas de los 50 originales contra los 20 nuevos. Si los nuevos salen peor, explica si es por el prompt o por la dificultad de tus casos.
4. **Restricción verificable.** Diseña una restricción sobre la salida del clasificador que pueda comprobarse con código (por ejemplo: la `justificacion` no contiene correos, teléfonos ni RFC; o la prioridad es `alta` solo si el texto menciona caída, pérdida de datos o cobro no reconocido). Escríbela en `RESTRICCION` y su verificador en `verificador()`. Ejecuta sobre los tickets relevantes y reporta el cumplimiento. Explica por qué el verificador vive en la aplicación aunque el prompt pida lo mismo.
5. **Costo y decisión.** El starter acumula tokens, latencia y costo estimado de toda la práctica en `log`. Copia la tabla al reporte. Decide qué versión del prompt iría a producción para la mesa de soporte del curso (un millón de tickets al mes, menos de un segundo) usando las tres variables: calidad, costo por 1,000 tickets y latencia. Una versión con mejor accuracy y el doble de tokens de entrada no gana por defecto.
6. **Escribe el reporte** con `report-template.md`.

## Entregables

* `practica4-reporte.md`: la plantilla llenada, con la tabla de regresión completa (una fila por ticket).
* `practica4-starter.ipynb`: el notebook ejecutado de principio a fin.
* `tickets_extra.jsonl`: los 20 tickets nuevos, exportados por el starter.

Los tres archivos en una carpeta `practica4-<apellido>` comprimida, o en el repositorio que indique el profesor.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | ---: |
| Regresión v1 → v4 | Más de un cambio, o sin tabla por caso, o solo la métrica agregada. | Un cambio justificado y tabla por caso con mejoró / empeoró / igual. | Además, cada caso que empeoró tiene un diagnóstico (el prompt lo rompió, o la etiqueta es discutible) con argumento sobre el texto del ticket. | 30 |
| Dataset extendido | Menos de 20 tickets, sin ambiguos, o ambiguos sin `nota`. | 20 tickets con las reglas y criterio documentado en los ambiguos. | Además, la comparación 50 vs 20 se explica por el prompt o por la dificultad de los casos, con ejemplos. | 20 |
| Restricción verificable | Restricción que no se puede comprobar con código, o sin verificador. | Restricción y verificador que corren y reportan cumplimiento. | Además, explica qué pasaría si la restricción solo viviera en el prompt y muestra un caso donde el verificador atrapó algo. | 20 |
| Costo y decisión | Sin tabla de costo, o decisión basada solo en accuracy. | Tabla de costo completa y decisión que considera calidad, costo por 1,000 tickets y latencia. | Además, calcula el costo mensual al volumen del caso para las dos versiones y explica el trade-off en una oración defendible ante un gerente. | 20 |
| Reporte | Incompleto o sin evidencia (afirmaciones sin tabla). | Completo, cada afirmación con su número. | Además, identifica un ticket del dataset original cuya etiqueta cambiaría y por qué. | 10 |

Total: 100. Un prompt con accuracy alta y sin tabla por caso no aprueba el criterio de regresión.

## Errores frecuentes

* Cambiar tres cosas en v4. Si mejora, no se sabe cuál lo hizo; si empeora, tampoco. Un cambio.
* Comparar solo la métrica agregada. Dos versiones con la misma accuracy pueden acertar casos distintos; la tabla por caso lo muestra.
* Escribir 20 tickets fáciles. Los ambiguos son la parte valiosa: son los que dicen si el prompt tiene criterio.
* Una restricción que no se puede verificar ("responde con cuidado"). Si no hay verificador, no hay restricción.
* Decidir producción por accuracy. Con un millón de tickets al mes, 200 tokens de entrada de más por ticket son 200 millones de tokens al mes.

## Conexión

El dataset extendido y el verificador se reutilizan en la semana 5: la generación de RAG se mide con las mismas dos columnas (formato y corrección) más la evidencia citada, y la restricción de datos personales reaparece cuando el contexto recuperado trae datos de clientes.

## Opcional, sin peso: sobre un caso propio

Si tienes una tarea de clasificación o extracción de tu tesis, repite los pasos 1, 2 y 4 con 20 casos propios y el mismo starter cambiando el dataset y el schema. No se entrega ni se califica; sirve para ver si la tabla de regresión cambia el prompt que habrías elegido.
