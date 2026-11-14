# Práctica 9. Contexto mínimo suficiente para el asistente de soporte

**Semana:** 9 (fusionada en la 8; esta práctica no se entrega y queda como ejercicio opcional sin peso). **Entrega:** antes de la sesión 10. **Tiempo estimado:** 3 horas. **Costo:** cero con el servidor local; con la llave de OpenAI, alrededor de 0.10 USD con un modelo pequeño (la conversación completa de 30 turnos con tres estrategias suma cerca de 300,000 tokens de entrada).

## Objetivo

Diseñar y medir la política de contexto del asistente de soporte de Facturio: qué ve el modelo en cada turno, qué se conserva textual, qué se resume y qué se descarta, con evidencia de tokens y de si una restricción crítica sobrevive.

## Qué se evalúa

* Las tres estrategias de contexto (historial completo, sliding window, estado estructurado con resumen) implementadas y medidas sobre la misma conversación.
* La política Keep / Compress / Drop escrita con justificación por entrada.
* Un normalizador determinista de tool output con su medición.
* Un estado estructurado con justificación por campo.
* La distinción entre estado de la aplicación y contexto del modelo.
* Predicciones registradas antes de medir, y contrastadas después.

## Antes de empezar

* Haber ejecutado `notebooks/02-student-experiment.ipynb` en clase o en casa, con los TODOs de las secciones 6 y 7 llenos (son el punto de partida de las secciones 4 y 5 de esta práctica).
* Tener la llave individual cargada en el panel de secretos de Colab como `OPENAI_API_KEY`, o aceptar el servidor local (más lento; la primera celda tarda unos minutos mientras descarga el modelo).
* Abrir `practice-starter.ipynb` en Colab y `report-template.md` en un editor.

## El caso

El asistente de soporte de Facturio atiende a un usuario (u002, plan Pro) durante 30 turnos con las tools de la semana 8. En el turno 2 el usuario fija un presupuesto máximo de 700 pesos al mes. En el turno 30 pide una recomendación de plan. El plan Pro cuesta 899 pesos; el Básico, 599. Una recomendación correcta respeta el presupuesto. El guion completo está en `GUION` dentro del starter.

## Instrucciones

### Sección 1. Predicciones (starter, sección 1)

1. Antes de ejecutar nada, escribe en `PREDICCION` qué estrategia perderá la restricción, cuál gastará más tokens en total y en qué turno la sliding window de 8 mensajes dejará de ver el turno 2. La predicción se conserva aunque falle: la rúbrica evalúa que exista y que la contrastes.

### Sección 2. Las tres estrategias, medidas (sección 2)

2. Ejecuta las tres estrategias con `N_TURNOS = 30`. Si el servidor local tarda demasiado, entrega con `N_TURNOS = 12` y dilo en el reporte; el mecanismo se observa igual.
3. Copia la tabla (`tabla`) al reporte: tokens totales, tokens del último turno, latencia, si la recomendación menciona el presupuesto, si recomienda el plan Pro y si la restricción sobrevive. Adjunta la gráfica de tokens por turno.
4. Cambia `VENTANA_B` (por ejemplo 4 y 16) y repite solo B. Reporta en qué turno cada ventana dejó de ver el turno 2 y qué pasó con la recomendación.
5. Responde en el reporte: ¿coincidieron tus predicciones? Si C conservó la restricción, ¿fue por el resumen del modelo o por el estado que mantiene la aplicación? Revisa el JSON y el resumen impresos.

### Sección 3. Normalizador de tool output (sección 3)

6. Escribe `mi_normalizador`: recibe el JSON crudo de `consultar_plan` (plan, límites, uso, historial de facturas, eventos) y devuelve solo lo necesario para responder cuántas facturas quedan y si conviene cambiar de plan. Calcula en código lo que se pueda calcular en código.
7. Corre la comparación crudo frente a normalizado. Copia al reporte tokens del tool output, tokens de entrada, latencia y si la respuesta trae el número correcto.
8. Responde: si el modelo hubiera acertado con el JSON crudo, ¿seguiría valiendo la pena el filtro? Argumenta con costo por llamada y latencia.

### Sección 4. Política Keep / Compress / Drop (sección 4)

9. Escribe la política del asistente como tres listas en `POLITICA`, con una justificación por entrada. Parte de la actividad 1 de clase. Incluye al menos: identificador del usuario, restricciones, folios y montos, plan actual, conversación vieja, consultas de documentación ya respondidas, tool outputs viejos, historial de facturas.
10. Marca en el reporte qué entradas nunca deben resumirse de forma ambigua y por qué.

### Sección 5. Estado estructurado (sección 5)

11. Llena `ESTADO` y `JUSTIFICACION`: por cada campo, qué decisión cambia si falta. Agrega al menos un campo propio del asistente de soporte.
12. Indica qué campos se envían al modelo en cada turno y cuáles se quedan solo en la aplicación.

### Sección 6. Reporte

13. Llena `report-template.md` con las tablas que imprime la celda final del starter y las respuestas. Guarda el notebook ejecutado con todas las salidas.

## Entregables

* `practica-09-reporte.md`: el `report-template.md` llenado, con la gráfica `practica9_tokens_por_turno.png` incrustada o adjunta.
* `practica-09-starter.ipynb`: el starter ejecutado de principio a fin, con los TODO llenos y las salidas visibles.

Se entregan en la plataforma del curso antes de la sesión 10.

## Rúbrica

| Criterio | Insuficiente | Aceptable | Sobresaliente | Peso |
| --- | --- | --- | --- | --- |
| Predicciones y contraste | No hay predicciones, o se escribieron después de ver los resultados. | Predicciones registradas y contrastadas con una frase. | Contraste que explica por qué falló o acertó cada predicción con los números de la tabla. | 10 |
| Medición de las tres estrategias | Falta alguna estrategia o la tabla no tiene tokens y supervivencia. | Tabla completa y gráfica; N_TURNOS declarado. | Además, el barrido de ventanas de B con el turno en que cada una olvida, y la explicación de por qué C conservó (o no) la restricción. | 25 |
| Normalizador de tool output | Devuelve el JSON casi completo o pierde el dato necesario. | Devuelve lo necesario, calcula el restante en código, mide tokens y corrección. | Además, argumenta el caso en que el modelo acierta con el crudo y por qué el filtro sigue valiendo la pena. | 20 |
| Política Keep / Compress / Drop | Listas sin justificación o con "keep todo". | Tres listas con una justificación por entrada. | Justificaciones que citan qué decisión cambia, y la lista de lo que nunca se resume de forma ambigua. | 20 |
| Estado estructurado | Campos sin justificar. | Cada campo con qué decisión cambia si falta. | Campo propio justificado y separación explícita entre lo que ve el modelo y lo que se queda en la aplicación. | 15 |
| Reporte y notebook | Notebook sin ejecutar o reporte incompleto. | Ambos entregados y consistentes. | Reporte que se sostiene solo, sin abrir el notebook. | 10 |

Los pesos suman 100.

## Errores frecuentes

* **Medir con guiones distintos.** Las tres estrategias deben correr sobre el mismo `GUION_SESION`; si cambias `N_TURNOS` entre corridas, la tabla deja de ser comparable.
* **Confundir "menciona el presupuesto" con "lo respeta".** El veredicto tiene dos señales; una recomendación puede decir "700" y aun así recomendar el plan Pro sin advertencia. Léelo completo.
* **Normalizar quitando el dato.** Un normalizador que devuelve solo el plan y el precio obliga al modelo a adivinar las facturas restantes. Calcula el restante en código y pásalo.
* **Keep de todo lo que dijo el usuario.** Cuesta tokens en cada turno hasta el final. Pregúntate qué decisión cambia.
* **Estado que duplica el historial.** Si el estado guarda los mensajes completos, es el historial con otro nombre. Guarda hechos; la conversación se resume aparte.

## Conexión

El estado estructurado y la política de contexto de esta práctica son el estado que consume el loop de agente de la semana 10. La práctica 10 arranca con tu `ESTADO` como punto de partida.

## Opcional, sin peso: sobre un caso propio

Si tienes una conversación real de soporte, atención o consulta de tu propio dominio, sustituye `GUION` por 20 a 30 turnos con una restricción dicha al inicio y una decisión al final que dependa de ella, y repite las secciones 2 y 4. No se entrega ni se califica.
