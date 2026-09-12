# Ejercicio 2. Self-attention en papel: tres tokens, dimensión dos

**Duración:** 10 minutos de cálculo más 5 de puesta en común. **Momento:** sección 3, justo después de mostrar la fórmula. **Formato:** parejas, con papel y calculadora (o la celda del notebook para verificar al final).

## Objetivo

Que la fórmula `softmax(Q·Kᵀ/√dk)·V` deje de ser abstracta. Todo lo que se necesita es producto punto, exponencial y suma.

## Datos

Tokens: `el`, `gato`, `duerme`. Embeddings de dimensión dos:

```
x_el     = [1, 0]
x_gato   = [0, 1]
x_duerme = [1, 1]
```

Matrices (en un modelo real se aprenden; aquí se eligen para que los números salgan limpios):

```
W_Q = [[1, 0], [0, 1]]      (identidad)
W_K = [[0, 1], [1, 0]]      (intercambia coordenadas)
W_V = [[1, 0], [0, 1]]      (identidad)
```

## Pasos

1. Calcular q, k, v de cada token (`x · W`).
2. Calcular los scores `q_i · k_j` para todos los pares y dividir entre `√2 ≈ 1.414`.
3. Aplicar la máscara causal: un token no puede mirar a los que vienen después. Marcar esas celdas como −∞.
4. Softmax por fila.
5. Salida de cada token: suma ponderada de los v.

## Entregable

La tabla de pesos y las tres salidas. Verificación con `examples/attention_by_hand.py` o la celda 3.1 del notebook.
