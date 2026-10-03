"""Métricas mínimas de retrieval para el bloque RAG (semanas 6 y 7).

Un gold set asocia cada pregunta con las evidencias relevantes (archivo y
sección). El retriever devuelve una lista ordenada de chunks; cada chunk sabe
de qué archivo y sección viene. Con eso se calculan:

* hit@k:    1 si alguna evidencia relevante aparece entre los k primeros.
* recall@k: fracción de las evidencias relevantes que aparecen entre los k primeros.
* MRR:      1 / posición de la primera evidencia relevante (0 si no aparece).

Las métricas se promedian sobre las preguntas que sí tienen evidencia; las de
tipo `sin_respuesta` se evalúan aparte (answerability, semana 7).

    from retrieval_eval import cargar_gold, evaluar
    gold = cargar_gold("datasets/corpus/gold_set.jsonl")
    resultados = evaluar(gold, retriever, k=5)   # retriever(pregunta) -> [chunk, ...]
"""
from __future__ import annotations

import json
from pathlib import Path


def cargar_gold(ruta: str | Path) -> list[dict]:
    return [json.loads(l) for l in Path(ruta).read_text(encoding="utf-8").splitlines() if l.strip()]


def clave(archivo: str, seccion: str | None = None) -> str:
    """Identificador de evidencia. Si el chunk no lleva sección, se compara solo por archivo."""
    return f"{archivo}#{seccion}" if seccion else archivo


def es_relevante(chunk: dict, evidencias: list[dict], por_seccion: bool = True) -> bool:
    for ev in evidencias:
        if chunk.get("archivo") != ev.get("archivo"):
            continue
        if not por_seccion or not ev.get("seccion"):
            return True
        if (chunk.get("seccion") or "") == ev["seccion"]:
            return True
    return False


def metricas_pregunta(chunks: list[dict], evidencias: list[dict], k: int, por_seccion: bool = True) -> dict:
    top = chunks[:k]
    hits = [es_relevante(c, evidencias, por_seccion) for c in top]
    hit = float(any(hits))
    encontradas = set()
    for c in top:
        for ev in evidencias:
            if es_relevante(c, [ev], por_seccion):
                encontradas.add(clave(ev["archivo"], ev.get("seccion") if por_seccion else None))
    total = len({clave(ev["archivo"], ev.get("seccion") if por_seccion else None) for ev in evidencias})
    recall = len(encontradas) / total if total else 0.0
    mrr = 0.0
    for i, h in enumerate(hits, start=1):
        if h:
            mrr = 1.0 / i
            break
    return {"hit": hit, "recall": recall, "mrr": mrr}


def evaluar(gold: list[dict], retriever, k: int = 5, por_seccion: bool = True, tipos: set | None = None) -> dict:
    """retriever(pregunta) -> lista de chunks (dicts con 'archivo' y opcionalmente 'seccion')."""
    filas = []
    for g in gold:
        if g.get("tipo") == "sin_respuesta" or not g.get("evidencia"):
            continue
        if tipos and g.get("tipo") not in tipos:
            continue
        chunks = retriever(g["pregunta"])
        m = metricas_pregunta(chunks, g["evidencia"], k, por_seccion)
        m["id"] = g["id"]; m["tipo"] = g.get("tipo")
        filas.append(m)
    n = len(filas)
    resumen = {
        "k": k, "preguntas": n,
        f"hit@{k}": sum(f["hit"] for f in filas) / n if n else 0.0,
        f"recall@{k}": sum(f["recall"] for f in filas) / n if n else 0.0,
        "mrr": sum(f["mrr"] for f in filas) / n if n else 0.0,
    }
    return {"resumen": resumen, "por_pregunta": filas}


if __name__ == "__main__":
    gold = [{"id": 1, "pregunta": "q", "tipo": "factual_exacta", "evidencia": [{"archivo": "a.md", "seccion": "S1"}]}]
    r = evaluar(gold, lambda q: [{"archivo": "b.md", "seccion": "X"}, {"archivo": "a.md", "seccion": "S1"}], k=3)
    assert r["resumen"]["hit@3"] == 1.0 and abs(r["resumen"]["mrr"] - 0.5) < 1e-9, r
    print("retrieval_eval ok", r["resumen"])
