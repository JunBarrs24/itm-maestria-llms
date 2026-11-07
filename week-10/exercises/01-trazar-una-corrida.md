# Actividad 1. Trazar una corrida a mano (15 minutos)

## Objetivo

Predecir, iteración por iteración, qué hará el loop de agente antes de ver el trace real, y comparar. La actividad entrena la habilidad que más se usa al depurar agentes: leer un trace y saber qué debió pasar.

## Instrucciones para el estudiante

1. Trabaja en parejas. Recibes el objetivo, el catálogo de tools con sus descripciones y la política de autorización de `reembolsar` (plazo de 14 días, monto máximo automático de 1,000, cargos duplicados no se reembolsan por esta vía, un reembolso por cuenta cada 12 meses).
2. Objetivo del agente: "El cargo PAY-00012348 me salió doble, devuélvanme el dinero."
3. Para cada iteración escribe, sin ejecutar nada: qué tool pedirá el modelo y con qué argumentos, qué devolverá la aplicación, y si el loop termina. Llena la tabla:

| Iteración | Tool que pide (o respuesta final) | Argumentos | Qué devuelve la aplicación | ¿Termina? |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

4. Ahora corre la celda correspondiente del notebook del estudiante y pega el trace real. Marca en qué iteración divergió tu predicción y por qué.
5. Pregunta final: ¿qué stop condition, además del límite de iteraciones, habría terminado este caso antes?

## Entregable

La tabla con predicción y trace real, y la respuesta a la pregunta final, en el notebook del estudiante (celda de la actividad 1).
