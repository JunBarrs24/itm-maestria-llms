# Práctica 11. Del loop manual al runtime de agentes

> **No se entrega.** La sesión 11 se fusionó con la 10 y la práctica 10 (sobre la app) cubre este contenido. Queda como lectura.

**Semana:** 11. **Entrega:** antes de la sesión 12. **Tiempo estimado:** 3 horas. **Costo:** cero con el servidor local; con la llave individual, cerca de 0.05 USD por las 36 corridas de la comparación con un modelo pequeño (la tabla de costo del starter lo calcula).

## Objetivo

Portar el agente de la mesa de soporte de Facturio del loop manual de la semana 10 al OpenAI Agents SDK, agregarle session, guardrails, aprobación humana y salida estructurada, y decidir con una tabla medida qué se gana y qué se pierde al adoptar el runtime.

## Qué se evalúa

* El mapeo entre cada abstracción del SDK y el mecanismo manual que sustituye.
* Guardrails verificables: condición en código, un caso que dispara y uno que no.
* Aprobación humana como decisión de la aplicación, con el reembolso como caso.
* Tracing como artefacto: leer el árbol de una corrida y extraer llamadas, tools, tokens y latencia.
* Comparación manual vs SDK con evidencia: éxito, tools correctas, tokens, latencia, líneas de código, variabilidad.
* La pregunta de la semana: qué problemas resuelve el runtime y a qué costo de control.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` en clase o en casa.
* Tener la práctica 10 entregada: el loop manual y el mini gold set de seis tareas. Si no la tienes, el starter trae una versión reducida del loop y las seis tareas.
* Llave individual cargada en los secretos de Colab como `OPENAI_API_KEY`, o sin llave: el starter arranca el servidor local (tarda unos minutos la primera vez y el modelo es más débil; la práctica se califica igual, porque evalúa decisiones y no accuracy).
* Abrir `practice-starter.ipynb` en Colab y `report-template.md` en un editor.

## Instrucciones

### Parte 1. Portar el agente (secciones 1 y 2 del starter)

1. Ejecuta la sección 1: carga las tools de Facturio, configura el backend y define el agente con `Agent`, `function_tool` y `Runner`. Antes de correrlo, escribe en `PREDICCION_LOC` cuántas líneas crees que ahorra el SDK respecto al loop manual, y en `PREDICCION_TOKENS` si esperas que gaste más, igual o menos tokens por tarea que el loop manual (justifica una línea).
2. Corre la sección 2: el mini gold set de seis tareas, tres veces con el loop manual y tres con el SDK, con las mismas definiciones de tools y las mismas instrucciones. La celda imprime la tabla por corrida y el resumen. Copia el resumen al reporte.
3. Responde en el reporte: ¿en qué tareas difieren los sistemas y por qué? Si difieren en la selección de tools, busca la causa en las definiciones o en el modelo antes de atribuirla al runtime.

### Parte 2. Session, guardrails y aprobación (secciones 3 a 5)

4. Sección 3: crea una `SQLiteSession` y sostén una conversación de cuatro turnos donde el turno 1 fija el usuario y un presupuesto, y el turno 4 lo usa. Anota si el modelo lo recordó y cuántos items guardó la sesión. Responde: ¿qué política de contexto de la semana 9 aplica la sesión por sí sola? (ninguna: guarda y reenvía todo).
5. Sección 4: escribe dos guardrails (los de la actividad 2 sirven): uno de entrada y uno de salida. Cada uno con su condición en código, un caso que dispara el tripwire y uno que no. Ejecuta los cuatro casos y copia la tabla al reporte.
6. Sección 5: activa `needs_approval` en `reembolsar`. Corre la tarea de reembolso dos veces: una aprobando y otra rechazando. Muestra que en la segunda no hubo side effect (el registro de reembolsos no cambia) aunque el modelo lo haya pedido. Escribe la política de aprobación (monto máximo, plazo, quién aprueba) en `POLITICA_APROBACION`.

### Parte 3. Salida estructurada y tracing (secciones 6 y 7)

7. Sección 6: define `RespuestaSoporte` con Pydantic y obtén una respuesta estructurada de una tarea. Con llave, usa `output_type`; sin llave, el starter usa el formateador con tool obligatoria. Explica en dos líneas por qué el mecanismo cambia según el backend y qué contrato se conserva.
8. Sección 7: con el procesador de tracing de consola, imprime el árbol de una corrida con tool call y pégalo en el reporte. Extrae del árbol: llamadas al modelo, tools ejecutadas, tokens de entrada y salida, latencia total. Marca en el árbol dónde ocurrió la aprobación.

### Parte 4. Decisión (reporte)

9. Con la tabla de la parte 1, el mapeo de la actividad 1 y el árbol, escribe un párrafo (máximo 150 palabras) que responda: ¿qué problemas resolvió el runtime para la mesa de soporte y qué decisiones dejó de tomar tu código? Termina con una recomendación: SDK o loop manual para este sistema, y una condición bajo la cual cambiarías la recomendación.
10. Llena `report-template.md` y guarda el notebook ejecutado.

## Entregables

* `practica-11-reporte.md`: el `report-template.md` llenado, con las tablas y el árbol de tracing.
* `practica-11-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 12.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Tabla comparativa manual vs SDK | Falta una de las dos columnas o no hay corridas repetidas. | Seis tareas por tres corridas en ambos sistemas, con éxito, tools, tokens y latencia. | Además explica cada diferencia por tarea y distingue causas de modelo, de definiciones y de runtime. | 30 |
| Guardrails verificables | Condiciones en prosa, sin caso que dispare. | Dos guardrails en código, cada uno con un caso que dispara y uno que no, ejecutados. | Uno de los dos detecta una promesa sin acción (por ejemplo, reembolso afirmado sin tool ejecutada). | 20 |
| Aprobación y session | Falta una de las dos o el rechazo no se comprueba. | Rechazo sin side effect demostrado con el registro; sesión de cuatro turnos con conteo de items. | Además la política de aprobación está escrita con montos, plazos y responsable, y se explica qué compactación haría falta en la sesión. | 20 |
| Tracing | Sin árbol o sin los datos extraídos. | Árbol de una corrida con tool call y los cinco datos extraídos. | Además ubica la aprobación en el árbol y compara el trace con el registro manual de la semana 10. | 15 |
| Decisión sobre el runtime | Opinión sin evidencia. | Párrafo con recomendación apoyada en la tabla y el mapeo. | Además una condición explícita que cambiaría la recomendación, ligada a un dato medido. | 15 |

## Errores frecuentes

* **Atribuir al runtime lo que es del modelo.** Con un modelo pequeño, la selección de tools cambia más por la descripción de la tool que por el loop. Si un sistema falla una tarea, revisa primero qué recibió el modelo.
* **Dejar que la sesión decida el contexto.** `SQLiteSession` guarda y reenvía; la política de qué entra al modelo sigue siendo tuya (semana 9).
* **Guardrails en prosa.** "Que no responda cosas fuera de dominio" no es un guardrail; una función con un caso que dispara sí lo es.
* **Confundir aprobación con autorización.** `needs_approval` detiene la corrida; la regla de negocio (monto, plazo) vive en `autorizar_reembolso`, en la aplicación.
* **Olvidar el costo del tracing.** Con la llave, los spans se envían a OpenAI salvo que cambies el procesador; decide qué datos sensibles viajan.

## Conexión

El agente con session, guardrails y tracing es el punto de partida de la práctica 12, donde el mismo problema se divide entre varios agentes con handoffs y agents-as-tools, y la pregunta pasa a ser qué contexto viaja entre ellos.

## Opcional, sin peso: sobre un caso propio

Si tienes un sistema propio con tools (por ejemplo, el de tu tesis), repite la parte 1 con tres tareas de tu dominio y la parte 2 con un guardrail de salida que detecte tu falla más costosa. No se entrega ni se califica.
