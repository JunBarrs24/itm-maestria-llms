"""Reranking con cross-encoder sobre los 20 candidatos del híbrido: qué gana y qué cuesta.

Uso:  .venv/bin/python course/week-07/examples/rerank_demo.py
"""
import time

from rag7_core import Hibrido, Lexical, Reranker, Semantico, cargar_corpus, chunk_por_seccion, evaluar

docs, gold = cargar_corpus()
chunks = chunk_por_seccion(docs)
sem, lex = Semantico(chunks), Lexical(chunks)
hib = Hibrido(sem, lex, candidatos=20)
rr = Reranker(hib, candidatos=20)
g = {x["id"]: x for x in gold}

qid = "q02"
print(g[qid]["pregunta"])
print("  evidencia:", [(e["archivo"][:2], e["seccion"]) for e in g[qid]["evidencia"]])
for nombre, ret in [("híbrido", hib.buscar), ("+ rerank", rr.buscar)]:
    t = time.perf_counter()
    res = ret(g[qid]["pregunta"], 5)
    ms = (time.perf_counter() - t) * 1000
    print(f"  {nombre:9s} {ms:5.0f} ms  {[(c['archivo'][:2], c['seccion'][:30], round(c['score'], 3)) for c in res[:3]]}")

print("\nGold set:")
for nombre, ret in [("híbrido", hib.buscar), ("+ rerank", rr.buscar)]:
    t = time.perf_counter()
    r = evaluar(gold, ret, k=5)["resumen"]
    ms = (time.perf_counter() - t) / 25 * 1000
    print(f"  {nombre:9s} hit@5={r['hit@5']:.2f}  mrr={r['mrr']:.2f}  {ms:.0f} ms por consulta")
