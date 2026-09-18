# Práctica 3. Elegir el modelo desde los requisitos

**Semana:** 3. **Entrega:** antes de la sesión 4. **Tiempo estimado:** 2.5 horas. **Costo:** cero (modelos abiertos pequeños en Colab gratuito, sin llave).

## Objetivo

Comparar un modelo base y un modelo instruction-tuned de la misma familia sobre cinco instrucciones de la mesa de soporte del curso, explicar las diferencias por el post-training, y documentar qué tipo de modelo conviene para ese caso con una justificación por requisito.

## Qué se evalúa

* Predicción antes de ejecutar y registro separado de formato y corrección para cada modelo.
* Explicación de la diferencia base vs instruct por el post-training, sin atribuirla a tamaño o arquitectura (ambos modelos comparten las dos cosas).
* Chat templates como texto que construye la aplicación.
* Datos de preferencia: criterio explícito y sesgo que introduce.
* Matriz de decisión por cuatro ejes desde tres requisitos dados y un requisito dominante consistente.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` de la semana 3.
* Tener a la mano la tabla de la actividad 2 (`exercises/02-matriz-de-decision.md`).
* Abrir `practice-starter.ipynb` en Colab. Corre en CPU; no requiere GPU ni llave.

## El caso

Una empresa de software recibe un millón de tickets de soporte al mes. Los tickets contienen datos personales de clientes que el contrato prohíbe compartir con terceros sin acuerdo de tratamiento. La clasificación de cada ticket debe mostrarse al agente en menos de un segundo. Los tickets son los del dataset del curso (`shared/datasets/support_tickets.jsonl`).

## Instrucciones

1. **Predice.** El starter trae cinco instrucciones fijas de la mesa de soporte: clasificar un ticket, extraer los datos de contacto a JSON, resumir un ticket largo en una oración, redactar una respuesta con un formato dado y rechazar una petición fuera de política. Antes de ejecutar nada, escribe en la celda `PREDICCIONES` qué crees que hará el modelo base y qué hará el instruct con cada una. Las predicciones se conservan aunque fallen.
2. **Ejecuta y registra.** Corre las cinco instrucciones en `Qwen2.5-0.5B` y en `Qwen2.5-0.5B-Instruct`. Llena la tabla `REGISTRO` con dos columnas por modelo: `formato_ok` (¿la salida tiene la forma pedida?) y `correcto` (¿el contenido es correcto?). Son juicios distintos: una salida puede cumplir el formato y estar mal, o acertar el contenido sin el formato.
3. **Explica.** En el reporte, para cada instrucción donde los dos modelos difieran, explica la diferencia con lo visto en clase: qué aprendió el instruct en SFT y en preference optimization que el base no tiene. Si el instruct falla en algo, di también por qué el post-training no lo resolvió.
4. **Escribe el template a mano.** El starter imprime el texto que produce `apply_chat_template` para la instrucción de clasificación. Escríbelo tú en `TEMPLATE_A_MANO` (con los marcadores `<|im_start|>` y `<|im_end|>`) y comprueba que el modelo produce la misma respuesta con tu texto que con el template automático. Reporta si coincidió y, si no, qué diferencia del texto lo explica.
5. **Construye pares de preferencia.** Para la instrucción de redactar una respuesta, escribe tres pares (respuesta elegida, respuesta rechazada) en `PARES`, con un criterio explícito y común a los tres ("prefiero la respuesta que confirma el problema, da un siguiente paso concreto y no promete plazos"). En el reporte discute qué sesgo introduce ese criterio en un asistente entrenado con miles de pares así.
6. **Llena la matriz de decisión.** Con los tres requisitos del caso (confidencialidad, un millón de tickets al mes, latencia menor a un segundo), decide cada eje en `MATRIZ`: abierto/cerrado, local/API, pequeño/grande, estándar/reasoning. Cada decisión cita el requisito que la justifica. Identifica el requisito dominante y explica por qué los otros dos no lo son. Sin nombres de modelos ni "porque lo usa X empresa".
7. **Escribe el reporte** con `report-template.md`.

## Entregables

* `practica3-reporte.md`: la plantilla `report-template.md` llenada.
* `practica3-starter.ipynb`: el notebook ejecutado de principio a fin, con las predicciones, la tabla de registro, el template a mano, los pares y la matriz.

Ambos archivos en una carpeta `practica3-<apellido>` comprimida, o en el repositorio que indique el profesor.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | ---: |
| Predicción y registro | Faltan predicciones o la tabla mezcla formato con corrección. | Predicciones para las cinco instrucciones y tabla con las dos columnas por modelo. | Además, cada predicción fallida tiene una línea que explica qué se esperaba mal y por qué. | 20 |
| Explicación por post-training | Atribuye la diferencia al tamaño, a la arquitectura o a "el instruct es mejor". | Explica las diferencias con SFT y preference optimization. | Además, explica un caso donde el instruct falla y por qué el post-training no lo cubre (conocimiento del pre-training, sesgo del anotador, sobre-rechazo). | 20 |
| Template a mano | No se escribió o no se comparó. | Reproduce la respuesta del template automático, o documenta la diferencia que lo impidió. | Además, explica qué construye la aplicación y qué implica que un usuario pueda escribir los marcadores dentro de sus datos. | 15 |
| Pares de preferencia | Sin criterio explícito o pares triviales (una respuesta vacía contra una buena). | Tres pares verosímiles con criterio común. | Además, discute con claridad el sesgo que ese criterio introduce (longitud, tono, complacencia) y un caso donde perjudicaría. | 20 |
| Matriz de decisión | Ejes sin requisito, o requisito dominante inconsistente con el resto. | Cada eje cita un requisito dado y el dominante es consistente. | Además, explica por qué los otros dos requisitos no dominan y propone cómo satisfacerlos igualmente (contrato de no retención, clasificación en línea con un modelo pequeño y borrador en segundo plano). | 25 |

Total: 100. Que el notebook ejecute completo es condición para entregar; los puntos salen del análisis.

## Errores frecuentes

* Ejecutar primero y escribir la predicción después. Se nota en el reporte y anula el propósito del paso 1.
* Marcar `correcto = True` porque la salida "suena bien". Corrección se juzga contra el ticket: ¿la categoría es la del dataset?, ¿el JSON trae el correo que aparece en el texto?
* Explicar la diferencia por parámetros: los dos Qwen tienen 494 millones. La explicación está en el entrenamiento posterior.
* Pares de preferencia donde la rechazada es absurda. El reward model aprende de pares donde ambas son plausibles; ahí se ve el criterio.
* Llenar la matriz con "grande, API, cerrado, reasoning" sin citar requisitos. Es elegir por reputación.

## Conexión

La matriz de decisión y el registro formato/corrección se reutilizan en la práctica 4, donde el prompt se mide sobre 50 tickets con las mismas dos columnas, ahora con métrica agregada, tokens y costo.

## Opcional, sin peso: sobre un caso propio

Si tu tesis o tu trabajo tiene un caso de uso con LLM, repite los pasos 1, 2 y 6 con tres instrucciones de ese caso y sus requisitos reales. No se entrega ni se califica; sirve para comprobar si la decisión de modelo cambia cuando cambian los requisitos.
