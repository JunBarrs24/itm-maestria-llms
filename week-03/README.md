# Semana 3. Del modelo base al asistente moderno

**Bloque:** Fundamentos. **Unidad del temario:** 1.4 (más datos de entrenamiento del 1.2). **Duración:** 3 horas.

## Pregunta central

> Si GPT-2 ya es un Transformer, ¿por qué no se comporta como ChatGPT?

La semana 2 abrió la caja y mostró el mecanismo. Esta semana muestra que el mecanismo es el mismo en un modelo base y en un asistente, y que la diferencia observable la produce el post-training: qué datos vio el modelo después del pre-training y con qué objetivo. La segunda mitad de la sesión convierte esa comprensión en una decisión de arquitectura: qué tipo de modelo elegir desde los requisitos del proyecto.

## Objetivos

Al terminar la sesión el estudiante puede:

* explicar la progresión datos → pre-training → modelo base → SFT → instruction model → preference optimization → asistente;
* distinguir experimentalmente un modelo base de un modelo instruction-tuned con las mismas instrucciones;
* describir conceptualmente SFT, instruction tuning, datos de preferencia, reward models, RLHF y preference optimization (DPO como ejemplo), sin implementarlos;
* explicar que un chat template convierte mensajes con roles en texto con marcadores, y que el modelo sigue prediciendo el siguiente token;
* clasificar modelos por cuatro ejes (abierto/cerrado, pequeño/grande, local/API, estándar/reasoning) y elegir desde requisitos;
* justificar la decisión de modelo para la mesa de soporte del curso por cada eje, desde requisitos dados.

## Conocimientos previos

* Semana 2: next-token prediction, tokens, logits, softmax, decoding greedy.
* Semana 1: distinción entre modelo y aplicación; alucinación como consecuencia del mecanismo.
* Python básico y ejecución de notebooks en Colab.

No se requiere conocer optimización ni aprendizaje por refuerzo. Todo el post-training se explica a nivel de qué datos entran, qué señal se optimiza y qué comportamiento sale.

## Conceptos fundamentales

| Concepto | Qué debe quedar claro |
| --- | --- |
| Datos de entrenamiento y preparación | Qué texto entra al pre-training, cómo se filtra, deduplica y mezcla. La mezcla decide qué idiomas y qué dominios domina el modelo. |
| Pre-training y modelo base | El único objetivo es predecir el siguiente token sobre texto de la web. El resultado continúa texto; no responde. |
| Supervised Fine-Tuning e instruction tuning | Seguir entrenando con el mismo objetivo sobre pares (instrucción, respuesta). Enseña el formato de interacción. |
| Fine-tuning y LoRA | SFT es un fine-tuning. LoRA lo hace más barato ajustando pocas matrices. Sin implementación en el curso. |
| Chat templates | El chat es texto con tokens especiales que construye la aplicación. Escribirlo a mano da la misma respuesta. |
| Datos de preferencia y reward model | Pares (elegida, rechazada) capturan criterios difíciles de escribir como regla. El reward model aprende a puntuar. |
| RLHF y preference optimization | Optimizar el modelo para producir respuestas mejor puntuadas, con una restricción para no alejarse del SFT. DPO lo hace sin reward model separado. |
| Base vs instruct | Mismo mecanismo, mismos datos de pre-training, mismo conocimiento. Distinto comportamiento. |
| Cuatro ejes de clasificación | Abierto/cerrado, pequeño/grande, local/API, estándar/reasoning. Reasoning solo como categoría; la mecánica es de la semana 14. |
| Elección desde requisitos | El requisito dominante (privacidad, costo, latencia, calidad, control) decide el eje; el resto se acomoda. |

## Agenda de tres horas

| Bloque | Minutos | Contenido |
| --- | --- | --- |
| Apertura | 15 | Recuperar la semana 2 con una pregunta: si GPT-2 predice el siguiente token igual que un asistente, ¿qué le falta? Anunciar el experimento: cinco instrucciones, tres modelos. |
| Concepto y mecanismo I | 50 | Datos y pre-training. Modelo base. SFT e instruction tuning. Chat templates. Slides 4 a 22. |
| Receso | 15 | |
| Demo guiada | 40 | Notebook guiado: predicción antes de ejecutar, cinco instrucciones en tres modelos, patrón en el base, template a mano, pares de preferencia. |
| Concepto y mecanismo II | 25 | Preference optimization: reward model, RLHF, DPO, riesgos. Clasificaciones arquitectónicas. Slides 23 a 38. |
| Actividad | 20 | Matriz de decisión por ejes para la mesa de soporte del curso, con tres requisitos dados (`exercises/02-matriz-de-decision.md`). |
| Cierre | 15 | Lo que se llevan, conexión con la semana 4, práctica. |

Si la sesión va tarde: la sección de riesgos del preference optimization (slides 29 y 30) se convierte en lectura y la actividad se recorta a 12 minutos. El cierre no se recorta.

## Resultados de aprendizaje

* Predice correctamente qué hará un modelo base y uno instruct ante una instrucción, y explica la diferencia por el post-training.
* Reconoce en un chat template los tokens especiales y explica quién construye ese texto.
* Explica qué aprende un reward model a partir de un par de preferencias y por qué el sesgo del anotador llega al asistente.
* Entrega la matriz de decisión de la mesa de soporte con una justificación por eje basada en los requisitos dados y un requisito dominante consistente.

## Demo

la demo guiada del profesor. Modelos `gpt2`, `Qwen/Qwen2.5-0.5B` y `Qwen/Qwen2.5-0.5B-Instruct`, todos en CPU. Corre completo en menos de dos minutos en Colab gratuito. Lectura de pares de preferencia por el API de datasets-server de Hugging Face, con respaldo embebido si no hay red.

Resultados que conviene anticipar en las speaker notes: el base repite la instrucción de clasificación; el instruct clasifica pero elige una categoría discutible; el instruct responde una ciudad equivocada como capital de Michoacán. Los tres son material de discusión y forman parte del diseño de la demo.

## Conexión con la semana anterior

Todo el post-training sigue siendo next-token prediction. La semana 2 explicó el mecanismo; esta semana explica qué distribución aprendió el modelo y por qué el instruct produce una respuesta donde el base produce más texto.

## Conexión con la siguiente

Si el asistente responde a instrucciones porque fue entrenado con ejemplos de instrucciones, entonces el prompt es la forma de condicionar esa distribución en tiempo de ejecución, y la aplicación es quien lo construye. La semana 4 trata el prompt como artefacto de ingeniería: anatomía, ejemplos, restricciones, structured outputs, versionado y regresión.

## Artefacto sobre el caso del curso

Matriz de decisión de modelo por los cuatro ejes para la mesa de soporte al cliente del curso, con tres requisitos dados (confidencialidad de datos de clientes, un millón de tickets al mes, latencia menor a un segundo), el requisito dominante y una justificación por eje. Plantilla en `exercises/02-matriz-de-decision.md` y en la última sección de `notebooks/02-student-experiment.ipynb`. La práctica completa está en `practice/practice.md`.

Opcional, sin peso: repetirlo sobre un caso propio.

## Archivos de esta semana

* `README.md`
* `examples/`
* `exercises/01-predecir-antes-de-ejecutar.md`
* `exercises/02-matriz-de-decision.md`
* `notebooks/02-student-experiment.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-03/notebooks/02-student-experiment.ipynb)
* `practice/practice-starter.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-03/practice/practice-starter.ipynb)
* `practice/practice.md`
* `practice/report-template.md`
* `resources/`
* `resources/lora_opcional.ipynb` · [Abrir en Colab](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-03/resources/lora_opcional.ipynb)
* `slides/week-03-slides.pptx`
