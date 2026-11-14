# Actividad 2. Diseñar el estado estructurado del asistente de soporte (10 minutos)

## Objetivo

Separar el estado de la aplicación del contexto del modelo: decidir qué campos mantiene el código entre turnos y qué fragmento de ese estado se envía al modelo en cada llamada.

## Instrucciones para el estudiante

1. Parte de la plantilla `goal`, `user_id`, `constraints`, `completed_steps`, `pending_steps`, `important_facts`.
2. Para cada campo escribe una línea: qué decisión cambia si ese campo falta.
3. Agrega, si hace falta, un campo propio del asistente de soporte (por ejemplo, `autorizaciones_pendientes` o `folios_en_disputa`) y justifícalo.
4. Marca qué campos se envían al modelo en cada turno y cuáles se quedan solo en la aplicación (por ejemplo, un contador de tokens o un registro de auditoría).

## Entregable

El diccionario `ESTADO` y `JUSTIFICACION` llenos en la sección 7 del notebook del estudiante.
