# Práctica 10. Del loop manual al Agents SDK, medido

**Semana:** 10 (sesión fusionada con la 11). **Entrega:** antes de la sesión 12. **Tiempo estimado:** 3 horas. **Costo:** cerca de 0.10 USD con la llave individual y `gpt-5-mini` (la evaluación de seis tareas por tres corridas y dos motores cuesta unos 0.05 USD; el resto son pruebas sueltas desde el chat).

## Objetivo

Correr el mismo asistente de soporte con los dos motores de la app (el loop escrito a mano en `app.py` y el `Runner` del OpenAI Agents SDK en `motor_sdk.py`), portar una tool propia al SDK con aprobación humana, escribir un guardrail verificable, provocar la stop condition por límite y decidir por escrito, con la tabla de evaluación, qué se gana y qué se paga con el runtime.

## Qué se evalúa

* Agente = modelo + contexto + estado + herramientas + loop de control, con cada pieza ubicada en `app.py`.
* Stop conditions: respuesta final y límite de vueltas, en el loop manual (`max_vueltas`) y en el SDK (`max_turns`).
* Human-in-the-loop: la diferencia entre bloquear una tool (motor manual) y pausar la corrida para que una persona decida (`needs_approval` y `RunState`).
* `function_tool`: la firma se vuelve schema; el contexto de la aplicación (`RunContextWrapper`) viaja sin pasar por el modelo.
* Guardrails como validación determinista antes de gastar la primera llamada.
* Evaluación de agentes: task success, selección de tools, vueltas, tokens, latencia, costo y variabilidad entre corridas.
* La decisión runtime o loop propio sustentada en la tabla.

## Antes de empezar

* La app corriendo en tu máquina con la versión de la semana 10: `pip install -r requirements.txt` otra vez (agrega `openai-agents`), llave en `.env`, `python app.py`.
* Tu `app.py` y `shared/facturio_tools.py` de la práctica 8, con la tool `reenviar_invitacion` y su `autorizar_reenvio`. Si no la terminaste, la práctica acepta `escalar_a_humano` como tool de trabajo, con una nota en el reporte.
* Leer `motor_sdk.py` completo antes de tocarlo: son menos de 200 líneas y cada bloque dice qué sustituye.

## El caso

El equipo de Facturio quiere decidir si el asistente de primera respuesta sigue sobre el loop propio o se mueve al Agents SDK. Las condiciones son las de siempre: ningún reembolso sin autorización de la aplicación y, con los side effects automáticos apagados, sin una persona; el sistema nunca se queda en un ciclo; y hay que poder medir si resuelve las tareas y cuánto cuesta. La decisión se toma con números de los dos motores sobre las mismas tareas.

## Instrucciones

### Parte 1. Portar la tool (motor_sdk.py)

1. Envuelve `reenviar_invitacion` con `@function_tool(needs_approval=_requiere_aprobacion)` siguiendo el patrón de `reembolsar`: la función del SDK llama a `ft.ejecutar_tool` y el usuario de la sesión llega por `ctx.context`, nunca por un argumento que el modelo pueda inventar. Regístrala en `TOOLS_SDK` y en la ruta que le corresponda en `ESPECIALISTAS`.
2. Prueba el mismo mensaje con los dos motores y la casilla de side effects apagada. Pega los dos traces: en el manual la tool no aparece en `tools_visibles`; en el SDK aparece, el modelo la pide y la corrida se pausa con la tarjeta de aprobación.
3. Aprueba una vez y rechaza una vez. Pega las dos continuaciones del trace y explica en tres líneas qué guardó la aplicación entre la pausa y la decisión (`Sesion.pendiente` y el `RunState`).

### Parte 2. Guardrail (motor_sdk.py)

4. Escribe un segundo guardrail de entrada, determinista y verificable, distinto de `solo_soporte`. Dos opciones: rechazar mensajes con un folio de formato inválido (regex `PAY-\d{8}`), o rechazar mensajes de más de 600 caracteres. Regístralo en el agente.
5. Prueba un mensaje que lo dispara y uno que no. Pega los dos traces y anota los tokens de cada uno: el guardrail que dispara no debe gastar ninguna llamada al modelo.

### Parte 3. Stop condition (app.py y motor_sdk.py)

6. Baja `max_vueltas` y `MAX_TURNS` a 2. Pide algo que necesite tres pasos ("Soy u001, dime mi plan, el estado del cargo PAY-00012345 y cuántos días tengo para pedir reembolso"). Registra qué hizo cada motor al llegar al límite: el texto que devolvió, lo que dice el trace (`aviso` de límite o `MaxTurnsExceeded`) y los tokens gastados.
7. Regresa los límites a su valor y escribe en el reporte cuál de los dos comportamientos preferirías en producción y por qué.

### Parte 4. Evaluación medida (eval_motores.py)

8. Corre `python eval_motores.py --corridas 3`. Produce `eval_resultados.json` y la tabla por motor y tarea: task success, tools esperadas presentes, vueltas, tokens, latencia, costo.
9. Agrega una séptima tarea al `GOLD` con tu tool de la parte 1: un mensaje, el usuario de la sesión, las tools esperadas y un criterio de éxito verificable sobre la respuesta y las tools ejecutadas. Vuelve a correr.
10. Antes de ver la tabla, escribe en el reporte tu predicción: cuál motor usará más vueltas y cuál gastará más tokens. Consérvala aunque falle.

### Parte 5. Decisión (reporte)

11. Con la tabla, responde: ¿qué cambió y qué quedó igual entre los dos motores? Separa lo que es del runtime (loop, nombres, pausa, tracing) de lo que sigue siendo de la aplicación (routing, contexto, autorización, decisión humana).
12. Decide para el asistente de primera respuesta: loop propio o Agents SDK. Indica la stop condition, el límite y qué medirías en producción. Llena `report-template.md`.

## Entregables

* `practica-10-reporte.md`: el `report-template.md` llenado, con capturas o texto de los traces.
* `motor_sdk.py` y `eval_motores.py` modificados, más el `eval_resultados.json` de tu corrida.
* El `app.py` solo si cambiaste algo fuera de `ESPECIALISTAS` y `max_vueltas`.

Se entregan en la plataforma del curso antes de la sesión 12.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Tool portada con aprobación | La tool no corre en el SDK o se ejecuta sin pausa con la casilla apagada. | La tool pausa la corrida y las dos continuaciones (aprobar, rechazar) están en el trace. | Además, explica qué guarda la aplicación durante la pausa y por qué el usuario de la sesión viaja por el contexto y no por los argumentos. | 20 |
| Guardrail verificable | No dispara, o dispara con una llamada al modelo de por medio. | Dispara en el caso previsto, pasa en el otro, y la evidencia de tokens está en el reporte. | Además, argumenta qué guardrail del caso conviene determinista y cuál necesitaría un modelo. | 15 |
| Stop condition | No provoca el límite en alguno de los motores. | Los dos límites provocados, con texto, trace y tokens de cada motor. | Además, defiende cuál comportamiento conviene en producción con el costo de cada uno. | 15 |
| Evaluación medida | Corridas incompletas, sin séptima tarea o sin predicción. | Tabla completa de siete tareas por dos motores con predicción registrada. | Además, analiza la variabilidad entre corridas de una misma tarea y la relaciona con la selección de tools. | 25 |
| Decisión | Afirmación sin usar la tabla. | Decisión con criterio, stop condition, límite y evidencia de la tabla. | Además, separa con precisión qué pone el runtime y qué sigue siendo de la aplicación, y qué medir en producción. | 25 |

## Errores frecuentes

* Pasar el usuario de la sesión como argumento de la tool. El modelo lo inventaría; va en `ctx.context`.
* Confundir la pausa del SDK con autorización. `needs_approval` detiene; la política de negocio dentro de la tool sigue decidiendo cuando se reanuda.
* Leer "respuesta final" como éxito. El loop termina también cuando el modelo responde mal; task success se mide contra el criterio de la tarea.
* Correr cada tarea una vez. Con un componente probabilístico, una corrida es una anécdota.
* Comparar motores con distinto effort o distinta estrategia de contexto. La comparación vale si lo único que cambia es el motor.

## Conexión

El agente del SDK de esta práctica es el que la semana 12 divide en varios agentes (handoffs y agents-as-tools) y la semana 13 reconstruye como grafo en LangGraph. La tabla de evaluación se reutiliza para comparar un agente contra varios.

## Opcional, sin peso: sobre un caso propio

Si tienes un caso propio (por ejemplo, el de tu tesis), define tres tools con una de side effect, envuélvelas con `function_tool`, marca la de side effect con `needs_approval` y corre tres tareas con los dos motores. La pregunta es la misma: qué pone el runtime y qué sigue siendo tuyo. No se entrega ni se califica.
