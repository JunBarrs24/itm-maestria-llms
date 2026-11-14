# Actividad 1. Abstracción del SDK, mecanismo manual y qué se pierde

**Tiempo:** 15 minutos. **Modalidad:** parejas. **Entregable:** la tabla llenada, en el notebook del estudiante o en papel.

## Objetivo

Que ninguna abstracción del Agents SDK quede como magia: cada una se relaciona con el código que el grupo ya escribió a mano en las semanas 4, 8, 9 y 10, y se nombra lo que deja de estar bajo control del desarrollador al adoptarla.

## Instrucciones para el estudiante

1. Completa la tabla. La columna "Mecanismo manual" pide el archivo y la función o estructura de las semanas anteriores que hacía ese trabajo. La columna "Qué se pierde" pide una decisión concreta que antes tomaba tu código y ahora toma el SDK.
2. Marca con un asterisco las filas donde la pérdida de control te parece aceptable para la mesa de soporte de Facturio, y con dos asteriscos donde no.
3. Al terminar, compara con otra pareja: si difieren en los asteriscos, discutan con un caso concreto (por ejemplo, un reembolso).

| Abstracción del SDK | Mecanismo manual (semana y pieza) | Qué se pierde |
| --- | --- | --- |
| `Agent` (instrucciones, tools, model) | | |
| `Runner.run` y `max_turns` | | |
| `function_tool` | | |
| `needs_approval` e interrupciones | | |
| `SQLiteSession` | | |
| `input_guardrail` con tripwire | | |
| `output_guardrail` | | |
| `output_type` | | |
| Tracing (spans y procesadores) | | |
