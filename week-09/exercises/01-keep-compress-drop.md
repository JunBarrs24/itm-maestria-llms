# Actividad 1. Keep / Compress / Drop línea por línea (15 minutos)

## Objetivo

Aplicar la política de contexto a una transcripción real de la mesa de soporte y defender cada decisión con el criterio de la sesión: ¿esta información cambia la siguiente decisión del modelo?

## Datos

Los 20 mensajes de `TRANSCRIPCION` en `notebooks/02-student-experiment.ipynb`, sección 6: un usuario de la Escuela Técnica Morelia (u003) con descuento educativo, dos consultas de documentación con tool outputs largos, una restricción institucional ("no pueden cobrarnos nada sin autorización del director") y una petición final de cambio a plan anual.

## Instrucciones para el estudiante

1. Para cada mensaje decide `keep`, `compress` o `drop`, y escribe en dos palabras el motivo.
2. Marca los mensajes que, si se resumen, pierden un dato exacto que la siguiente decisión necesita.
3. Escribe el estado estructurado que quedaría después de aplicar la política (campos `user_id`, `constraints`, `important_facts`, `completed_steps`).
4. Puesta en común: tres estudiantes leen su decisión sobre los mensajes 4, 9 y 15.

## Entregable

El diccionario `DECISIONES` lleno en el notebook, y el estado estructurado de tres líneas. Se conserva para la práctica.
