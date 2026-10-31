"""Retrieval semántico, BM25 e híbrido con RRF sobre el corpus de Facturio.

Uso:  .venv/bin/python course/week-07/examples/hybrid_rrf.py ["consulta"]

Sin argumento corre dos consultas de contraste (un código de error y una
pregunta conceptual) y la tabla hit@5 / MRR de los tres retrievers.
"""
import sys

from rag7_core import Hibrido, Lexical, Semantico, cargar_corpus, chunk_por_seccion, evaluar

docs, gold = cargar_corpus()
chunks = chunk_por_seccion(docs)
sem, lex = Semantico(chunks), Lexical(chunks)
hib = Hibrido(sem, lex, candidatos=20)


def top(ret, q, k=3):
    return [(c["archivo"][:2], c["seccion"][:38]) for c in ret(q, k)]


consultas = sys.argv[1:] or ["¿Qué significa E-1003?", "Me sale un mensaje de que mi cuenta está bloqueada, ¿qué hago?"]
for q in consultas:
    print(f"\n{q}")
    for nombre, ret in [("semántico", sem.buscar), ("BM25", lex.buscar), ("híbrido", hib.buscar)]:
        print(f"  {nombre:9s} {top(ret, q)}")

print("\nGold set (25 preguntas con evidencia):")
for nombre, ret in [("semántico", sem.buscar), ("BM25", lex.buscar), ("híbrido", hib.buscar)]:
    r = evaluar(gold, ret, k=5)["resumen"]
    print(f"  {nombre:9s} hit@5={r['hit@5']:.2f}  recall@5={r['recall@5']:.2f}  mrr={r['mrr']:.2f}")
