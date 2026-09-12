# Arquitectura de Software para Sistemas Inteligentes

## LLM Engineering: Fundamentos, RAG, Agentes y Operación en Producción

Material del curso para estudiantes. Se publica semana a semana, después de cada sesión.

## Temario

El programa oficial de la asignatura, con unidades, objetivos, evaluación y bibliografía, está en [TEMARIO.md](TEMARIO.md).

## Cómo usar este repositorio

* Cada carpeta `week-XX` tiene el README de la semana (pregunta central, objetivos, agenda), las slides de la sesión, el notebook de experimentos, la práctica con su plantilla de reporte y su notebook de arranque, ejemplos y lecturas.
* Los notebooks corren en Google Colab. La forma más simple es el enlace "Abrir en Colab" que aparece junto a cada notebook en la tabla de abajo y en el README de cada semana: abre el archivo directamente desde este repositorio. Al guardar, Colab pide hacer una copia en tu Drive; trabaja sobre esa copia. Como alternativa, descarga el `.ipynb` y súbelo con Archivo → Subir notebook. La primera celda instala lo necesario. Las semanas 1 a 3 no requieren llave ni créditos.
* A partir de la semana 4 los notebooks usan la API de OpenAI con la llave individual que entrega el profesor. En Colab, guárdala en el panel de secretos (ícono de llave) con el nombre `OPENAI_API_KEY` y actívala para el notebook; el código la lee del entorno y nunca se escribe dentro del notebook. Si no hay llave, los notebooks caen a un modelo local más lento y menos preciso.
* `shared/` tiene los primers de lectura previa, los datasets del curso y dos helpers (`usage.py` para registrar tokens y costo, `llm.py` como cliente con backend OpenAI o local).

## Prácticas

Cada semana tiene una práctica en `week-XX/practice/`: `practice.md` con instrucciones y rúbrica, `report-template.md` para llenar y `practice-starter.ipynb` como punto de partida. Se entregan antes de la siguiente sesión. La rúbrica premia decisiones justificadas con mediciones; el código que corre es condición necesaria.

## La pregunta del curso

> ¿Cuál es la solución más simple que satisface correctamente el requisito?

Se revisa en este orden: código determinista → LLM → RAG → workflow → agente → sistema multi-agente. Cada peldaño se sube solo cuando el anterior falla contra un requisito concreto y medible.

## Semanas publicadas

| Semana | Sesión | Notebooks en Colab |
| --- | --- | --- |
| [week-01](week-01/README.md) | Semana 1. Sistemas de software con LLMs | [02-student-experiment](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-01/notebooks/02-student-experiment.ipynb) · [practice-starter](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-01/practice/practice-starter.ipynb) |
| [week-02](week-02/README.md) | Semana 2. Dentro de un LLM: tokens, Transformers y generación | [02-student-experiment](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-02/notebooks/02-student-experiment.ipynb) · [practice-starter](https://colab.research.google.com/github/JunBarrs24/itm-maestria-llms/blob/main/week-02/practice/practice-starter.ipynb) |
