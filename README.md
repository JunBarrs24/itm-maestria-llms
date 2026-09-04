# Arquitectura de Software para Sistemas Inteligentes

## LLM Engineering: Fundamentos, RAG, Agentes y Operación en Producción

Material del curso para estudiantes. Se publica semana a semana, después de cada sesión.

## Temario

El programa oficial de la asignatura, con unidades, objetivos, evaluación y bibliografía, está en [TEMARIO.md](TEMARIO.md).

## Cómo usar este repositorio

* Cada carpeta `week-XX` tiene el README de la semana (pregunta central, objetivos, agenda), las slides de la sesión, el notebook de experimentos, la práctica con su plantilla de reporte y su notebook de arranque, ejemplos y lecturas.
* Los notebooks corren en Google Colab: abre Colab, elige "Subir notebook" y carga el archivo `.ipynb`. La primera celda instala lo necesario. Las semanas 1 a 3 no requieren llave ni créditos.
* A partir de la semana 4 los notebooks usan la API de OpenAI con la llave individual que entrega el profesor. En Colab, guárdala en el panel de secretos (ícono de llave) con el nombre `OPENAI_API_KEY` y actívala para el notebook; el código la lee del entorno y nunca se escribe dentro del notebook. Si no hay llave, los notebooks caen a un modelo local más lento y menos preciso.
* `shared/` tiene los primers de lectura previa, los datasets del curso y dos helpers (`usage.py` para registrar tokens y costo, `llm.py` como cliente con backend OpenAI o local).

## Prácticas

Cada semana tiene una práctica en `week-XX/practice/`: `practice.md` con instrucciones y rúbrica, `report-template.md` para llenar y `practice-starter.ipynb` como punto de partida. Se entregan antes de la siguiente sesión. La rúbrica premia decisiones justificadas con mediciones; el código que corre es condición necesaria.

## La pregunta del curso

> ¿Cuál es la solución más simple que satisface correctamente el requisito?

Se revisa en este orden: código determinista → LLM → RAG → workflow → agente → sistema multi-agente. Cada peldaño se sube solo cuando el anterior falla contra un requisito concreto y medible.

## Semanas publicadas

* [week-01](week-01/README.md)
* [week-02](week-02/README.md)
* [week-03](week-03/README.md)
* [week-04](week-04/README.md)
