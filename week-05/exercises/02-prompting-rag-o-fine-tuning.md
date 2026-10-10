# Actividad 2. Prompting, RAG o fine-tuning (10 minutos)

## Objetivo

Decidir, para tres requisitos de la mesa de soporte de Facturio, cuál de las tres técnicas es la solución más simple que satisface el requisito, y justificarlo con criterios.

## Criterios de la sesión

| Pregunta | Si la respuesta es sí, apunta a |
| --- | --- |
| ¿La información cambia con frecuencia o por versión? | RAG |
| ¿La información es privada o no estaba en el entrenamiento? | RAG |
| ¿Hace falta trazabilidad (citar de dónde salió)? | RAG |
| ¿Lo que se quiere cambiar es comportamiento, tono o formato, y no conocimiento? | Prompting; fine-tuning si el volumen justifica el costo |
| ¿Cabe todo el contexto necesario en el prompt y se conoce de antemano? | Prompting |
| ¿Hay miles de ejemplos y el prompt ya no alcanza o cuesta demasiado por llamada? | Fine-tuning |

## Instrucciones para el estudiante

Para cada requisito, elige una técnica y escribe una línea con el criterio que decidió.

* **R1.** Responder preguntas de clientes sobre políticas y límites del plan, que cambian cada versión.
* **R2.** Redactar todas las respuestas de soporte con el tono y la estructura de la casa (saludo, diagnóstico, siguiente paso, despedida).
* **R3.** Clasificar tickets en las cinco categorías del curso con el mínimo de latencia y costo.

## Entregable

Tres decisiones con su criterio, en el notebook del estudiante.
