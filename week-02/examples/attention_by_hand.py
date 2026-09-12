"""Self-attention calculada a mano con numpy: tres tokens de dimensión dos.

Reproduce el ejercicio en papel de la semana 2. Sin torch, sin modelo.
Ejecutar:  python attention_by_hand.py
"""
import numpy as np

np.set_printoptions(precision=3, suppress=True)

tokens = ["el", "gato", "duerme"]

# Embeddings inventados de dimensión 2 (en GPT-2 la dimensión es 768).
X = np.array([
    [1.0, 0.0],   # el
    [0.0, 1.0],   # gato
    [1.0, 1.0],   # duerme
])

# Matrices aprendidas (aquí elegidas a mano). W_K intercambia las coordenadas
# para que la key de un token sea distinta de su query.
W_Q = np.array([[1.0, 0.0], [0.0, 1.0]])
W_K = np.array([[0.0, 1.0], [1.0, 0.0]])
W_V = np.array([[1.0, 0.0], [0.0, 1.0]])

Q = X @ W_Q   # ¿qué busca cada token?
K = X @ W_K   # ¿qué ofrece cada token?
V = X @ W_V   # ¿qué se combina si resulta relevante?
print("Q =\n", Q, "\nK =\n", K, "\nV =\n", V)

d_k = Q.shape[1]
scores = Q @ K.T / np.sqrt(d_k)
print("\nscores = Q K^T / sqrt(d_k) =\n", scores)

# Máscara causal: un token no puede mirar a los que vienen después.
mask = np.triu(np.ones_like(scores, dtype=bool), k=1)
scores_masked = np.where(mask, -np.inf, scores)
print("\nscores con máscara causal =\n", scores_masked)


def softmax(z):
    z = z - np.max(z, axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


A = softmax(scores_masked)
print("\npesos de atención (softmax por fila) =\n", A)

salida = A @ V
print("\nsalida = A V =\n", salida)

print("\nLectura:")
for i, t in enumerate(tokens):
    pesos = ", ".join(f"{tokens[j]}={A[i, j]:.2f}" for j in range(i + 1))
    print(f"  '{t}' mira a: {pesos}  ->  vector {salida[i]}")
