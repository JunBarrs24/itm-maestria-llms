"""Retrieval engineering sobre el corpus de Facturio. Semana 6.

Funciones mínimas y visibles: cargar el corpus, partirlo en chunks con tres
estrategias, embeber, recuperar y medir contra el gold set. Sin framework.
El mismo código va copiado en los notebooks de la semana para que corran en
Colab sin clonar el repositorio.
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

import numpy as np

ARCHIVOS = [
    "01-manual-facturacion-cfdi.md", "02-manual-usuarios-e-invitaciones.md",
    "03-manual-reportes-y-exportacion.md", "04-manual-integraciones-y-api.md",
    "05-preguntas-frecuentes.md", "06-politica-reembolsos-y-cargos.md",
    "07-politica-cancelacion-y-eliminacion.md", "08-terminos-del-servicio-y-sla.md",
    "09-catalogo-codigos-de-error.md", "10-notas-de-version.md",
    "11-guia-de-seguridad.md", "12-comunicado-externo.md",
]
TIPO_DOC = {"01": "manual", "02": "manual", "03": "manual", "04": "manual", "05": "faq",
            "06": "politica", "07": "politica", "08": "terminos", "09": "catalogo",
            "10": "notas", "11": "seguridad", "12": "comunicado"}
RAW = "https://raw.githubusercontent.com/JunBarrs24/itm-maestria-llms/main/shared/datasets/corpus/"


# ------------------------------------------------------------------ carga
def cargar_corpus(local: str | Path | None = None) -> dict[str, str]:
    """Devuelve {archivo: texto}. Usa la carpeta local si existe; si no, descarga del repositorio."""
    docs = {}
    base = Path(local) if local else None
    for nombre in ARCHIVOS:
        if base and (base / nombre).exists():
            docs[nombre] = (base / nombre).read_text(encoding="utf-8")
        else:
            with urllib.request.urlopen(RAW + nombre) as r:
                docs[nombre] = r.read().decode("utf-8")
    return docs


def cargar_gold(local: str | Path | None = None) -> list[dict]:
    base = Path(local) if local else None
    if base and (base / "gold_set.jsonl").exists():
        texto = (base / "gold_set.jsonl").read_text(encoding="utf-8")
    else:
        with urllib.request.urlopen(RAW + "gold_set.jsonl") as r:
            texto = r.read().decode("utf-8")
    return [json.loads(l) for l in texto.splitlines() if l.strip()]


# ------------------------------------------------------------------ estructura
def secciones(texto: str) -> list[dict]:
    """Parte un markdown por encabezados ## y ###. Cada sección conserva su encabezado."""
    out, actual, buf = [], None, []
    for linea in texto.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)", linea)
        if m:
            if actual is not None:
                out.append({"seccion": actual, "texto": "\n".join(buf).strip()})
            actual, buf = m.group(2).strip(), [linea]
        else:
            buf.append(linea)
    if actual is not None:
        out.append({"seccion": actual, "texto": "\n".join(buf).strip()})
    return out


def seccion_en(texto: str, pos: int) -> str | None:
    """Encabezado ## o ### vigente en la posición pos del texto."""
    ultimo = None
    for m in re.finditer(r"^(#{2,3})\s+(.*)$", texto[:pos + 1], re.M):
        ultimo = m.group(2).strip()
    return ultimo


# ------------------------------------------------------------------ chunking
def chunk_por_seccion(docs: dict[str, str]) -> list[dict]:
    chunks = []
    for archivo, texto in docs.items():
        for s in secciones(texto):
            chunks.append({"archivo": archivo, "seccion": s["seccion"], "tipo": TIPO_DOC[archivo[:2]],
                           "texto": s["texto"]})
    return chunks


def chunk_seccion_contexto(docs: dict[str, str], minimo_palabras: int = 8) -> list[dict]:
    """Como chunk_por_seccion, pero cada chunk lleva al inicio su ruta jerárquica
    (título del documento > sección ## > subsección ###) y se omiten los encabezados
    sin cuerpo propio. El texto extra le da al embedding el contexto que el fragmento perdió."""
    out = []
    for archivo, texto in docs.items():
        m = re.search(r"^# (.+)$", texto, re.M)
        titulo = m.group(1).strip() if m else archivo
        padre = None
        for s in secciones(texto):
            nivel2 = s["texto"].startswith("## ")
            cuerpo = "\n".join(s["texto"].splitlines()[1:]).strip()
            if nivel2:
                padre = s["seccion"]
            if len(cuerpo.split()) < minimo_palabras:
                continue
            ruta = f"{titulo} > {padre} > {s['seccion']}" if (not nivel2 and padre) else f"{titulo} > {s['seccion']}"
            out.append({"archivo": archivo, "seccion": s["seccion"], "tipo": TIPO_DOC[archivo[:2]],
                        "texto": ruta + "\n\n" + cuerpo})
    return out


def chunk_fijo(docs: dict[str, str], tamano: int, overlap: int, contar) -> list[dict]:
    """Ventanas de `tamano` tokens con `overlap` tokens de traslape, medidas en palabras.
    `contar(texto)` devuelve tokens; se usa para calibrar palabras por token en cada documento.
    Un chunk fijo puede cruzar varias secciones: `seccion` es la vigente al inicio y
    `secciones` la lista de todas las que toca."""
    chunks = []
    for archivo, texto in docs.items():
        palabras = [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", texto)]
        if not palabras:
            continue
        encabezados = [(m.start(), m.group(2).strip()) for m in re.finditer(r"^(#{2,3})\s+(.*)$", texto, re.M)]
        ratio = contar(texto) / len(palabras)              # tokens por palabra en este documento
        paso_p = max(1, int(tamano / ratio))                # palabras por chunk
        over_p = int(overlap / ratio)
        i = 0
        while i < len(palabras):
            ventana = palabras[i:i + paso_p]
            ini, fin = ventana[0][1], ventana[-1][2]
            vigente = None
            tocadas = []
            for pos, h in encabezados:
                if pos <= ini:
                    vigente = h
                elif pos < fin:
                    tocadas.append(h)
            secs = ([vigente] if vigente else []) + tocadas
            chunks.append({"archivo": archivo, "seccion": vigente, "secciones": secs,
                           "tipo": TIPO_DOC[archivo[:2]], "texto": texto[ini:fin]})
            if i + paso_p >= len(palabras):
                break
            i += max(1, paso_p - over_p)
    return chunks


def chunk_recursivo(docs: dict[str, str], tamano: int, contar) -> list[dict]:
    """Parte por secciones; si una sección excede `tamano` tokens, la parte por párrafos;
    si un párrafo excede, por oraciones. Nunca corta a media palabra."""
    def partir(texto: str) -> list[str]:
        if contar(texto) <= tamano:
            return [texto]
        partes = [p for p in re.split(r"\n\s*\n", texto) if p.strip()]
        if len(partes) == 1:
            partes = [p for p in re.split(r"(?<=[.!?])\s+", texto) if p.strip()]
            if len(partes) == 1:
                return [texto]
        out, buf = [], ""
        for p in partes:
            cand = (buf + "\n\n" + p).strip() if buf else p
            if contar(cand) <= tamano:
                buf = cand
            else:
                if buf:
                    out.append(buf)
                buf = p
        if buf:
            out.append(buf)
        return out
    chunks = []
    for archivo, texto in docs.items():
        for s in secciones(texto):
            for t in partir(s["texto"]):
                chunks.append({"archivo": archivo, "seccion": s["seccion"], "tipo": TIPO_DOC[archivo[:2]], "texto": t})
    return chunks


# ------------------------------------------------------------------ índice y retrieval
class Indice:
    """Índice en numpy: embeddings normalizados, similitud coseno por producto punto."""

    def __init__(self, modelo, chunks: list[dict], max_seq_length: int | None = None):
        self.modelo, self.chunks = modelo, chunks
        if max_seq_length:
            modelo.max_seq_length = max_seq_length
        self.E = modelo.encode([c["texto"] for c in chunks], normalize_embeddings=True, batch_size=32,
                               show_progress_bar=False)

    def buscar(self, pregunta: str, k: int = 5, filtro=None) -> list[dict]:
        q = self.modelo.encode([pregunta], normalize_embeddings=True, show_progress_bar=False)[0]
        scores = self.E @ q
        orden = np.argsort(-scores)
        out = []
        for i in orden:
            c = self.chunks[i]
            if filtro and not filtro(c):
                continue
            out.append({**c, "score": float(scores[i])})
            if len(out) == k:
                break
        return out


# ------------------------------------------------------------------ métricas (copia de shared/retrieval_eval.py)
def es_relevante(chunk: dict, evidencias: list[dict], por_seccion: bool = True) -> bool:
    for ev in evidencias:
        if chunk.get("archivo") != ev.get("archivo"):
            continue
        if not por_seccion or not ev.get("seccion"):
            return True
        if (chunk.get("seccion") or "") == ev["seccion"]:
            return True
        if ev["seccion"] in (chunk.get("secciones") or []):   # chunk fijo que cruza secciones
            return True
    return False


def metricas_pregunta(chunks: list[dict], evidencias: list[dict], k: int, por_seccion: bool = True) -> dict:
    top = chunks[:k]
    hits = [es_relevante(c, evidencias, por_seccion) for c in top]
    encontradas = set()
    for c in top:
        for ev in evidencias:
            if es_relevante(c, [ev], por_seccion):
                encontradas.add(ev["archivo"] + "#" + (ev.get("seccion") or "" if por_seccion else ""))
    total = len({ev["archivo"] + "#" + (ev.get("seccion") or "" if por_seccion else "") for ev in evidencias})
    mrr = next((1.0 / i for i, h in enumerate(hits, start=1) if h), 0.0)
    return {"hit": float(any(hits)), "recall": len(encontradas) / total if total else 0.0, "mrr": mrr}


def evaluar(gold: list[dict], retriever, k: int = 5, por_seccion: bool = True, tipos: set | None = None) -> dict:
    filas = []
    for g in gold:
        if not g.get("evidencia"):
            continue
        if tipos and g.get("tipo") not in tipos:
            continue
        m = metricas_pregunta(retriever(g["pregunta"]), g["evidencia"], k, por_seccion)
        filas.append({**m, "id": g["id"], "tipo": g["tipo"]})
    n = len(filas)
    return {"k": k, "preguntas": n,
            f"hit@{k}": round(sum(f["hit"] for f in filas) / n, 3) if n else 0.0,
            f"recall@{k}": round(sum(f["recall"] for f in filas) / n, 3) if n else 0.0,
            "mrr": round(sum(f["mrr"] for f in filas) / n, 3) if n else 0.0,
            "por_pregunta": filas}
