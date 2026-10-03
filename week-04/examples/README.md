# examples/ (semana 4)

Un archivo por patrón de prompt por tarea. Cada uno incluye estructura recomendada, prompt de ejemplo, errores comunes y forma de evaluación. En clase se desarrollan a fondo clasificación y extracción; los demás son material de referencia y base de la práctica.

| Archivo | Patrón | Entrada → salida |
| --- | --- | --- |
| `clasificacion.md` | Clasificación | Texto → una etiqueta de un conjunto cerrado |
| `extraccion.md` | Extracción | Texto → estructura con campos |
| `resumen.md` | Resumen | Documento → resumen condicionado por objetivo y audiencia |
| `transformacion.md` | Transformación | Formato A → formato B |
| `generacion.md` | Generación | Restricciones → contenido nuevo |
| `question_answering.md` | Question answering | Pregunta + contexto explícito → respuesta con cita |
| `prompt_regression.py` | Script ejecutable | Tres versiones de un prompt contra 10 tickets, tabla por caso |

`prompt_regression.py` corre con el backend local sin llave, o con OpenAI si `OPENAI_API_KEY` está en el entorno:

```
.venv/bin/python course/week-04/examples/prompt_regression.py
```
