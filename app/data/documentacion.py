"""El corpus de documentación de Facturio (data/corpus/*.md) partido por sección y con embeddings.

Es el RAG de la semana 5 reducido a lo que la tool `buscar_documentacion` necesita: chunks por
encabezado, embeddings por API (text-embedding-3-small) calculados una vez por proceso, y una
búsqueda por producto punto. Nada de esto sabe de agentes.
"""
from __future__ import annotations

import re
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
_CORPUS: list[dict] = []
_EMB: list[list[float]] | None = None


def _leer_corpus() -> list[tuple[str, str]]:
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted(CORPUS_DIR.glob("*.md"))
            if not p.name.startswith("00-")]


def _chunks_por_seccion(nombre: str, texto: str) -> list[dict]:
    """Un chunk por encabezado de nivel 2 o 3, con el encabezado incluido (igual que en la semana 5)."""
    chunks, seccion, buf = [], None, []
    for line in texto.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)", line)
        if m:
            if buf and seccion:
                chunks.append({"archivo": nombre, "seccion": seccion, "texto": "\n".join(buf).strip()})
            seccion, buf = m.group(2).strip(), [line]
        else:
            buf.append(line)
    if buf and seccion:
        chunks.append({"archivo": nombre, "seccion": seccion, "texto": "\n".join(buf).strip()})
    return chunks


def _embed(textos: list[str]) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI()
    salida: list[list[float]] = []
    for i in range(0, len(textos), 64):
        r = client.embeddings.create(model="text-embedding-3-small", input=textos[i:i + 64])
        salida.extend(d.embedding for d in r.data)
    return salida


def preparar_corpus() -> int:
    """Parte y vectoriza el corpus una vez por proceso. Devuelve el número de chunks."""
    global _EMB
    if _EMB is None:
        _CORPUS.clear()
        for nombre, texto in _leer_corpus():
            _CORPUS.extend(_chunks_por_seccion(nombre, texto))
        _EMB = _embed([c["texto"] for c in _CORPUS])
    return len(_CORPUS)


def buscar(pregunta: str, k: int = 3) -> list[dict]:
    """Los k fragmentos más parecidos, con archivo, sección y score."""
    preparar_corpus()
    v = _embed([pregunta])[0]
    scores = [sum(a * b for a, b in zip(e, v)) for e in _EMB]
    idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
    return [{"archivo": _CORPUS[i]["archivo"], "seccion": _CORPUS[i]["seccion"],
             "texto": _CORPUS[i]["texto"][:600], "score": round(scores[i], 3)} for i in idx]
