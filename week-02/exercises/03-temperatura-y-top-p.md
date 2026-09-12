# Ejercicio 3. Modificar temperature y top-p y explicar qué cambió

**Duración:** 15 minutos. **Momento:** bloque de actividad, después de la demo de decoding. **Formato:** individual, en `notebooks/02-student-experiment.ipynb`, sección 4.

## Objetivo

Que el estudiante distinga qué cambia y qué no cambia al mover las perillas de decoding, y elija una estrategia según quién consume la salida.

## Instrucciones para el estudiante

1. En la tabla de configuraciones, predice cuántas salidas distintas habrá en tres corridas para cada una (1, 2 o 3). Ejecuta y compara.
2. Cambia `MIS_TEMPERATURAS` a `[0.1, 0.7, 5.0]` y vuelve a graficar. Describe en una línea la forma de cada distribución.
3. Responde en dos líneas: cuando subes la temperatura, ¿qué cambia en los logits? ¿Y en las probabilidades?
4. Elige y justifica una estrategia de decoding para: (a) clasificar tickets de soporte en cinco categorías; (b) proponer diez nombres para un producto.

## Entregable

La tabla de predicciones con resultados, la descripción de las tres distribuciones y las dos justificaciones.
