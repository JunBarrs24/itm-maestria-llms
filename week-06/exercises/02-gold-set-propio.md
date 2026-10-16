# Actividad 2. Construir diez pares gold y medirlos (15 minutos)

## Objetivo

Que el estudiante construya evidencia de evaluación con criterio explícito y descubra que su propio gold set también tiene ambigüedades.

## Instrucciones para el estudiante

1. Elige dos documentos del corpus de Facturio que no hayas leído en clase (por ejemplo `07-politica-cancelacion-y-eliminacion.md` y `11-guia-de-seguridad.md`). Léelos por encabezados.
2. Escribe diez preguntas como las haría un cliente en un ticket, en tus palabras, sin copiar frases del documento. Para cada una anota el archivo y el encabezado exacto (`##` o `###`) donde está la respuesta. Incluye al menos dos preguntas cuya respuesta cruce dos secciones y una cuya respuesta no esté en el corpus.
3. Llena `MI_GOLD` en la sección 5 del notebook del estudiante con el formato del gold set del curso.
4. Ejecuta la evaluación con la configuración por sección con contexto y con fijo 200. Anota hit@5 y MRR de cada una.
5. Para cada pregunta que falle en ambas, decide: ¿la pregunta era ambigua, la evidencia estaba en otra sección también, o el retriever falló de verdad?

## Entregable

`MI_GOLD` con diez pares, la tabla de resultados y el diagnóstico por pregunta fallida, en el notebook.
