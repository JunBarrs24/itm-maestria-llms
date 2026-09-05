# Recursos semana 1

## Lecturas

* Radford, A. et al. *Language Models are Unsupervised Multitask Learners* (2019). https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
  El paper de GPT-2. Leer la sección 1 y la 2.1: cómo se plantea el modelado de lenguaje como predicción del siguiente token. Es el modelo que se usa en clase.
* Brown, T. et al. *Language Models are Few-Shot Learners* (2020). https://arxiv.org/abs/2005.14165
  Solo la introducción. Muestra que el mismo mecanismo, a mayor escala, produce comportamientos que hoy se dan por sentados. Se retoma en la semana 4 (few-shot).
* Kalai, A. et al. *Why Language Models Hallucinate* (OpenAI, 2025). https://openai.com/index/why-language-models-hallucinate/
  Explica la alucinación como consecuencia de cómo se entrena y evalúa un modelo, en línea con la postura del curso: se diseña alrededor de ella.

## Documentación

* Hugging Face, guía de generación de texto: https://huggingface.co/docs/transformers/generation_strategies
  Los parámetros `do_sample`, `temperature`, `top_k`, `top_p` y `max_new_tokens` que usa el notebook.
* Ficha del modelo GPT-2 en Hugging Face: https://huggingface.co/gpt2
  Tamaños disponibles, licencia y limitaciones declaradas por los autores.
* Google Colab, primeros pasos: https://colab.research.google.com/
  Para quien no lo haya usado. El notebook de la semana corre en la CPU gratuita.

## Para la semana 2

* Primer de vectores y softmax: `course/shared/primers/01-vectores-y-softmax.md`. Lectura obligatoria de una página antes de la sesión.
* Alammar, J. *The Illustrated GPT-2*: https://jalammar.github.io/illustrated-gpt2/
  Lectura opcional. Diagramas del mismo modelo que se abre por dentro la próxima semana.
