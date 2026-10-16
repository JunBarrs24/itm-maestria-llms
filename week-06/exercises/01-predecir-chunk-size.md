# Actividad 1. Predecir el efecto del chunk size (10 minutos)

## Objetivo

Comprobar que la intuición sobre el tamaño del chunk se equivoca con frecuencia, y que solo la medición contra un gold set decide.

## Instrucciones para el estudiante

1. Abre `notebooks/02-student-experiment.ipynb`, sección 2. Antes de ejecutar el barrido, escribe en `MI_PREDICCION` qué esperas que pase con hit@3 al pasar de chunks fijos de 200 tokens a 500 y a 1000: sube, baja o igual, y por qué.
2. Escribe también cuál de las tres estrategias (fijo 200, por sección, por sección con contexto jerárquico) crees que tendrá mejor hit@5 y cuál consumirá más tokens de contexto por consulta.
3. Ejecuta el barrido. Compara tu predicción con la tabla.
4. En dos líneas, explica el resultado que más te sorprendió usando lo visto en clase: longitud máxima del modelo de embeddings, dilución del embedding en textos largos, o granularidad de la métrica.

## Entregable

Las predicciones y la explicación en las celdas del notebook. Se comparte en voz alta al cerrar la actividad.
