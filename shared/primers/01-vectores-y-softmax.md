# Primer: la notación mínima para la semana 2

Una página para que la fórmula de atención se pueda leer. Todo lo que se usa en clase está aquí; nada más hace falta.

## Vector

Una lista ordenada de números. En el curso un vector representa un token, una posición o una consulta.

```
a = [1, 0, 2]
b = [2, 1, 0]
```

La dimensión es la cantidad de números. Los embeddings de GPT-2 tienen dimensión 768.

## Producto punto

Multiplicar componente a componente y sumar.

```
a · b = 1*2 + 0*1 + 2*0 = 2
```

Interpretación que usa la semana 2: mide cuánto "apuntan en la misma dirección" dos vectores. Si el producto punto es grande, los vectores se parecen. Si es cero, son ortogonales. Si es negativo, apuntan en sentidos opuestos.

## Matriz y producto matriz por vector

Una matriz es una tabla de números. Multiplicar una matriz por un vector produce otro vector, normalmente de distinta dimensión. En el Transformer, las matrices `W_Q`, `W_K` y `W_V` convierten el embedding de un token en su query, su key y su value.

```
q = x · W_Q      (x: dimensión 768, q: dimensión 64)
```

## Softmax

Convierte una lista de números cualesquiera (logits o scores) en probabilidades: todas entre 0 y 1, y suman 1.

```
softmax(z)_i = exp(z_i) / sum_j exp(z_j)
```

Ejemplo:

```
z = [2.0, 1.0, 0.1]
exp(z) = [7.39, 2.72, 1.11]
suma = 11.22
softmax(z) = [0.66, 0.24, 0.10]
```

Dos propiedades que importan en clase:

* El número más grande recibe la mayor probabilidad, y las diferencias se amplifican por la exponencial.
* Dividir los logits entre un número (la temperatura) antes del softmax cambia qué tan concentrada queda la distribución. Temperatura baja concentra; temperatura alta aplana.

## Escalado por raíz de d_k

En la fórmula `softmax(QKᵀ / √d_k) V`, el producto `QKᵀ` produce scores cuyo tamaño crece con la dimensión `d_k`. Dividir entre `√d_k` los mantiene en un rango donde el softmax todavía distingue sin saturarse. Es un detalle de estabilidad numérica; en clase se menciona y se sigue.

## Lo que NO hace falta

Derivadas, backpropagation, descenso de gradiente. El curso trabaja con modelos ya entrenados. Cómo se entrenan se explica conceptualmente en la semana 3.
