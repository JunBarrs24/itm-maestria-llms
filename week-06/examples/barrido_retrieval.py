"""Barrido de chunk size, overlap y k medido con hit@k, recall@k y MRR sobre el gold set.

Uso:  .venv/bin/python course/week-06/examples/barrido_retrieval.py [--json salida.json]
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rag_lib import (Indice, cargar_corpus, cargar_gold, chunk_fijo, chunk_por_seccion,  # noqa: E402
                     chunk_recursivo, chunk_seccion_contexto, evaluar)
from sentence_transformers import SentenceTransformer  # noqa: E402

CORPUS = Path(__file__).resolve().parents[2] / "shared" / "datasets" / "corpus"
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def main(salida: str | None = None):
    docs = cargar_corpus(CORPUS)
    gold = cargar_gold(CORPUS)
    modelo = SentenceTransformer(MODELO)
    contar = lambda t: len(modelo.tokenizer.encode(t, add_special_tokens=False))
    modelo.max_seq_length = 512
    configs = [("seccion", None, None, chunk_por_seccion(docs))]
    for tam in (200, 500, 1000):
        for ov_pct in (0, 10, 25):
            configs.append((f"fijo", tam, ov_pct, chunk_fijo(docs, tam, int(tam * ov_pct / 100), contar)))
    configs.append(("recursivo", 200, None, chunk_recursivo(docs, 200, contar)))
    configs.append(("seccion+ctx", None, None, chunk_seccion_contexto(docs)))
    filas = []
    for nombre, tam, ov, chunks in configs:
        t = time.perf_counter()
        idx = Indice(modelo, chunks)
        fila = {"estrategia": nombre, "tamano": tam, "overlap_pct": ov, "chunks": len(chunks),
                "tokens_medios": round(sum(contar(c["texto"]) for c in chunks) / len(chunks)),
                "embed_s": round(time.perf_counter() - t, 1)}
        for k in (1, 3, 5, 10):
            r = evaluar(gold, lambda q: idx.buscar(q, k=10), k=k)
            fila[f"hit@{k}"] = r[f"hit@{k}"]
            fila[f"recall@{k}"] = r[f"recall@{k}"]
            if k == 5:
                fila["mrr"] = r["mrr"]
                fila["ctx_tokens@5"] = round(sum(sum(contar(c["texto"]) for c in idx.buscar(q["pregunta"], k=5)) for q in gold if q["evidencia"]) / 25)
        filas.append(fila)
        print(f"{nombre:12s} tam={str(tam):5s} ov={str(ov):4s} chunks={fila['chunks']:4d} tok={fila['tokens_medios']:4d} "
              f"hit@1={fila['hit@1']:.2f} hit@3={fila['hit@3']:.2f} hit@5={fila['hit@5']:.2f} hit@10={fila['hit@10']:.2f} "
              f"mrr={fila['mrr']:.2f} ctx@5={fila['ctx_tokens@5']}", flush=True)
    if salida:
        Path(salida).write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    return filas


if __name__ == "__main__":
    main(sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--json" else None)
