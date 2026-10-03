# Recursos de la semana 4

## Lecturas

* Brown, T. et al. *Language Models are Few-Shot Learners*. 2020. https://arxiv.org/abs/2005.14165
  El origen de "few-shot" como in-context learning. Leer la sección 2 (approach) y mirar las curvas de zero/one/few-shot: la mejora por ejemplos depende del tamaño del modelo y de la tarea, y eso sigue siendo cierto.
* Wei, J. et al. *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. 2022. https://arxiv.org/abs/2201.11903
  Pedir razonamiento explícito antes de la respuesta. Esta semana se menciona como técnica de prompting; su mecánica, su costo en tokens y los reasoning models se estudian en la semana 14.
* Ouyang, L. et al. *Training language models to follow instructions with human feedback*. 2022. https://arxiv.org/abs/2203.02155
  Repaso de la semana 3: por qué un instruction model responde a instrucciones. Explica por qué el prompt condiciona la distribución.

## Documentación

* OpenAI. *Prompt engineering guide*. https://platform.openai.com/docs/guides/prompt-engineering
  Recomendaciones del proveedor sobre instrucciones, delimitadores y ejemplos. Leer con la pregunta "¿cómo verifico esto?" en mente.
* OpenAI. *Structured outputs*. https://platform.openai.com/docs/guides/structured-outputs
  Cómo el SDK aplica un schema en el servidor (`responses.parse` con `text_format`). Comparar con el camino local del notebook: JSON más Pydantic más reintento.
* OpenAI. *Responses API reference*. https://platform.openai.com/docs/api-reference/responses
  Parámetros de `responses.create` que se usan en el curso: `instructions`, `input`, `max_output_tokens`, `temperature` (no aplica a reasoning models) y `usage`.
* Pydantic. *Models* y *Validation errors*. https://docs.pydantic.dev/latest/concepts/models/
  Complemento del primer `course/shared/primers/02-pydantic.md`.

## Material del curso

* `course/shared/primers/02-pydantic.md`: lo mínimo de Pydantic para la sesión.
* `course/shared/datasets/support_tickets.jsonl`: el dataset de la sesión, con sus notas de ambigüedad.
* `course/shared/usage.py` y `course/shared/llm.py`: helpers de costo y cliente con backend intercambiable.
* `examples/`: los seis patrones por tarea y el script de regresión.
