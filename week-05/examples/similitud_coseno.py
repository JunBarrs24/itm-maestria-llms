"""Cosine similarity a mano, con números pequeños (semana 5).

Muestra por qué normalizar los vectores convierte el producto punto en coseno,
y por qué "parecido" según el embedding no siempre es "la evidencia correcta".

Uso:  .venv/bin/python course/week-05/examples/similitud_coseno.py
"""
import numpy as np


def coseno(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# 1. Con vectores de juguete: la magnitud no importa, la dirección sí.
a = np.array([1.0, 2.0, 0.0])
b = np.array([2.0, 4.0, 0.0])      # misma dirección, el doble de largo
c = np.array([0.0, 0.0, 3.0])      # ortogonal
print("cos(a, b) =", round(coseno(a, b), 3), " (misma dirección: 1.0 aunque b sea más largo)")
print("cos(a, c) =", round(coseno(a, c), 3), " (ortogonales: 0.0)")
an, bn = a / np.linalg.norm(a), b / np.linalg.norm(b)
print("dot(a_norm, b_norm) =", round(float(an @ bn), 3), " (normalizados, el producto punto ya es el coseno)")

# 2. Con un modelo de embeddings real: frases parecidas y frases con las mismas palabras.
from sentence_transformers import SentenceTransformer

m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
frases = [
    "¿Cuántos días tengo para pedir un reembolso?",
    "Plazo para solicitar la devolución de un cargo",
    "El reembolso se solicita dentro de los 14 días naturales posteriores al cargo.",
    "La cabecera X-Facturio-Key autentica cada solicitud a la API v2.",
    "¿Qué cabecera HTTP se usa para autenticarse en la API v2?",
    "El error E-1003 indica cuenta bloqueada por cinco intentos fallidos.",
]
E = m.encode(frases, normalize_embeddings=True)
print("\nMatriz de cosenos (redondeada):")
for i, f in enumerate(frases):
    fila = " ".join(f"{float(E[i] @ E[j]):5.2f}" for j in range(len(frases)))
    print(f"{i}: {fila}   {f[:55]}")
print("\nLectura: 0 y 1 son paráfrasis (alto). 0 y 2 comparten tema (alto). 4 y 3 comparten tema y término exacto.")
print("La fila 5 es un código de error: se parece poco a todo. Los códigos exactos son terreno de la búsqueda lexical (semana 7).")
