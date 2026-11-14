# Actividad 2. Dos guardrails verificables para la mesa de soporte

**Tiempo:** 10 minutos. **Modalidad:** individual. **Entregable:** dos guardrails escritos como regla verificable más el caso que los dispara, en el notebook del estudiante.

## Objetivo

Aplicar el principio de la semana 4 (preferir instrucciones cuyo cumplimiento pueda verificarse) a los guardrails del SDK: un guardrail vale si su condición se puede escribir en código y probar con un caso que lo dispare y otro que no.

## Instrucciones para el estudiante

1. Escribe un guardrail de entrada para el asistente de Facturio. Define la condición como una función de la entrada (texto), un caso que la dispara y un caso que no. Ejemplos de dominio: solicitudes fuera de soporte, solicitudes que traen datos bancarios completos, mensajes vacíos o de más de N caracteres.
2. Escribe un guardrail de salida. Define la condición sobre la respuesta final (texto o `RespuestaSoporte`), un caso que la dispara y uno que no. Ejemplos: la respuesta promete un reembolso sin que `reembolsar` se haya ejecutado; la respuesta contiene un correo del cliente; la respuesta afirma un plazo distinto al de la documentación.
3. Para cada uno responde: ¿es determinista o necesita un modelo? Si necesita un modelo, ¿cómo se prueba?
4. Implementa uno de los dos en la celda TODO del notebook del estudiante y dispáralo.
