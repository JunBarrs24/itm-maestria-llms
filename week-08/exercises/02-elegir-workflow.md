# Actividad 2. Elegir el patrón de workflow (10 minutos)

## Objetivo

Dado un requisito de Facturio, elegir el patrón más simple que lo resuelve (código sin LLM, prompt chaining, routing, parallelization, orchestrator-worker) y justificar por qué no requiere un agente.

## El caso

Cada noche, Facturio quiere procesar los tickets del día con estas reglas:

1. Detectar los tickets que mencionan un folio `PAY-` y hablan de un cargo duplicado.
2. Para cada uno, verificar en la base de cargos si la reversión automática ya se aplicó.
3. Si no se aplicó, crear un ticket para una persona con el folio y un resumen de dos oraciones del reclamo.
4. Responder al cliente con un mensaje que diga qué se hizo.

Variante B (para la segunda mitad del grupo): los tickets del día llegan en cinco idiomas, y hay que clasificarlos en las cinco categorías del dataset y asignar prioridad antes de que el equipo humano entre a las 9:00.

## Instrucciones para el estudiante

1. Decide el patrón y escríbelo en una línea.
2. Dibuja el flujo como cajas y flechas. Marca qué cajas son código determinista y cuáles llaman a un modelo.
3. Justifica en cuatro líneas por qué no hace falta un agente: ¿se conoce el orden de los pasos de antemano? ¿hay alguna decisión que dependa de lo que se descubra en tiempo de ejecución?
4. Escribe qué se mediría para saber que funciona (al menos dos métricas).

## Entregable

La línea del patrón, el dibujo y la justificación. Dos parejas presentan al grupo: una del caso A y una del caso B.
