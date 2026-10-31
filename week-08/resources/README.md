# Recursos de la semana 8

Lecturas y documentación, con una línea de por qué cada una.

## Documentación

* [Function calling, OpenAI Responses API](https://platform.openai.com/docs/guides/function-calling): el contrato nativo que la sección 2 del notebook usa: definiciones de tools, items `function_call` y `function_call_output`. Leer la parte de `strict` y de llamadas en paralelo.
* [Structured outputs, OpenAI](https://platform.openai.com/docs/guides/structured-outputs): el mecanismo de la semana 4 que la emulación de tool calling reutiliza.
* [Pydantic, modelos y validación](https://docs.pydantic.dev/latest/concepts/models/): schemas de argumentos y `ValidationError`, la primera línea de defensa del dispatcher. El primer del curso está en `shared/primers/02-pydantic.md`.
* [asyncio, documentación de Python](https://docs.python.org/3/library/asyncio-task.html): `gather` y `to_thread`, lo único que usa el patrón de parallelization. El primer está en `shared/primers/03-asyncio.md`.
* [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html): el `ThreadPoolExecutor` con el que el dispatcher aplica timeouts.

## Lecturas

* Anthropic, *Building effective agents* (2024): la taxonomía de workflows que sigue la semana (prompt chaining, routing, parallelization, orchestrator-workers) y el argumento central del curso: usar el patrón más simple que funcione y agregar complejidad solo cuando mejora resultados medidos. https://www.anthropic.com/research/building-effective-agents
* Schick, T. et al., *Toolformer: Language Models Can Teach Themselves to Use Tools* (2023): el origen de la idea de que un modelo emita llamadas a herramientas dentro del texto. Sirve para ver que tool calling es generación de tokens con un formato, sin magia.
* Yao, S. et al., *ReAct* (2022): se lee completo en la semana 14; esta semana basta el resumen para notar que el loop de ReAct es la versión con control del modelo de lo que aquí se hizo con control del código.

## Del propio curso

* `examples/facturio_tools.py`: las tools, el dispatcher y la política de autorización. Es el archivo que conviene releer antes de la práctica.
* `examples/workflows.py`: los cuatro patrones con medición.
* Semana 4, `examples/`: patrones de prompt por tarea; el chaining de esta semana los encadena.
