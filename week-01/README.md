# Semana 1. Sistemas de software con LLMs

**Bloque:** Fundamentos. **Unidad del temario:** 1.1. **Duración:** 3 horas.

## Pregunta central

> ¿Qué cambia arquitectónicamente cuando una parte del software deja de ser determinista?

## Objetivos

Al terminar la sesión el estudiante podrá:

* Explicar qué es un LLM (un modelo que asigna probabilidades al siguiente token) y qué no es (una base de datos, un motor de reglas, un buscador, un razonador confiable).
* Distinguir el modelo de la aplicación que lo rodea, y ubicar en un diagrama qué componentes son deterministas y cuál es probabilístico.
* Reconocer la alucinación como consecuencia del mecanismo de generación y proponer validación y grounding como respuesta arquitectónica.
* Enumerar los requisitos no funcionales que aparecen al integrar un LLM: incertidumbre, latencia variable, costo por token, confiabilidad y observabilidad.
* Decidir, para un requisito concreto, si la solución más simple es código determinista, un LLM o si todavía falta información para decidir.
* Bosquejar la arquitectura V0 de la mesa de soporte del curso.

## Conocimientos previos

* Python básico y uso de Google Colab.
* Nociones de arquitectura de software: componentes, contratos, dependencias.
* Ninguna experiencia con LLMs. El temario lo garantiza y la sesión parte de cero.

## Caso común del curso

Todo el material trabaja sobre una mesa de soporte al cliente de un producto de software. Los tickets llegan por correo y por un formulario web. Hoy un equipo humano los lee, los clasifica en categoría y prioridad, y redacta la respuesta. Se quiere automatizar la clasificación y el borrador de respuesta, con un humano que aprueba antes de enviar. El dataset de 50 tickets de `shared/datasets/support_tickets.jsonl` es el material de trabajo desde la semana 4; en el bloque RAG se agrega un corpus documental y en el bloque agentic, herramientas.

Repetir cualquier artefacto sobre un caso propio (por ejemplo, el de la tesis) es opcional y no tiene peso en la calificación.

## Conceptos fundamentales

* LLM: un modelo que, dado un texto, produce una distribución de probabilidad sobre el siguiente token.
* LLM ≠ aplicación de IA. El modelo es un componente; la aplicación es todo lo que lo rodea: construcción del prompt, validación, estado, herramientas, observabilidad.
* Software determinista frente a componentes probabilísticos: misma entrada, distintas salidas; ausencia de contrato fuerte sobre la salida.
* Alucinación: una continuación probable del texto que no corresponde con la realidad. Se diseña alrededor de ella; no se elimina con un prompt.
* Requisitos no funcionales nuevos: incertidumbre, latencia variable, costo por token, confiabilidad, observabilidad.
* Casos de uso donde un LLM aporta valor y casos donde una función determinista es mejor.
* Arquitectura mínima de una aplicación con LLM: entrada → construcción de prompt → modelo → validación → salida, con registro alrededor.
* La escalera de decisión del curso: código determinista → LLM → RAG → workflow → agente → sistema multi-agente.

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Presentación del curso, la pregunta recurrente y la escalera de decisión. Qué se va a medir hoy: varianza y latencia. |
| Concepto y mecanismo | 50 | Qué es y qué no es un LLM. Modelo frente a aplicación. Determinismo y probabilidad. Alucinación. Los requisitos que aparecen. |
| Receso | 15 | |
| Demo guiada | 55 | Notebook con GPT-2: función determinista frente al modelo, temperatura, alucinación, arquitectura mínima en 20 líneas. Los estudiantes predicen antes de ejecutar. |
| Actividad | 30 | Clasificar ocho requisitos (10 min). Bosquejar la arquitectura V0 de la mesa de soporte del curso (20 min). |
| Cierre | 15 | Casos de uso y anti-casos. Conexión con la semana 2. Práctica. |

Si la sesión va tarde, la actividad de los ocho requisitos se reduce a cuatro y el resto pasa a la práctica. El cierre no se recorta.

## Resultados de aprendizaje

* Un diagrama de arquitectura V0 de la mesa de soporte del curso con el componente probabilístico ubicado, su validador y lo que se registra.
* Una clasificación justificada de requisitos en código / LLM / falta información.
* Un notebook ejecutado donde el estudiante observó varianza, latencia y una alucinación, y envolvió la llamada al modelo con validación.

## Conexión con la semana anterior

Ninguna. Esta sesión establece la pregunta recurrente del curso y presenta el caso común: la mesa de soporte.

## Conexión con la semana siguiente

La demo muestra que GPT-2 produce texto plausible sin obedecer instrucciones. La semana 2 abre la caja para explicar de dónde sale ese texto: tokens, atención y decoding. La varianza observada hoy se explica ahí con softmax y sampling.

## Artefacto sobre el caso del curso

Arquitectura V0 de la mesa de soporte: un diagrama de cajas donde se indica dónde entra el componente probabilístico, qué lo valida y qué se registra. Se entrega en la práctica 1 y se retoma en las semanas siguientes.

Opcional, sin peso: repetirlo sobre un caso propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-ocho-requisitos.md`
* `exercises/02-arquitectura-v0.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-01/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-01/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `slides/week-01-slides.pptx`
