"""RAG mínimo sin framework sobre el corpus de Facturio (semana 5).

El pipeline completo en un archivo:

    DOCUMENTO -> PARSE -> CHUNK -> EMBED -> INDEXAR -> RECUPERAR -> CONSTRUIR CONTEXTO -> GENERAR

Uso:  .venv/bin/python course/week-05/examples/rag_minimo.py "¿Cuántos días tengo para pedir un reembolso?"

Sin argumentos corre tres preguntas de muestra. Con OPENAI_API_KEY usa la API;
sin llave usa Qwen2.5-1.5B-Instruct en local (más lento, menos preciso).
"""
from __future__ import annotations

import os
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------- 1. corpus
CORPUS_ARCHIVOS = [
    "01-manual-facturacion-cfdi.md", "02-manual-usuarios-e-invitaciones.md",
    "03-manual-reportes-y-exportacion.md", "04-manual-integraciones-y-api.md",
    "05-preguntas-frecuentes.md", "06-politica-reembolsos-y-cargos.md",
    "07-politica-cancelacion-y-eliminacion.md", "08-terminos-del-servicio-y-sla.md",
    "09-catalogo-codigos-de-error.md", "10-notas-de-version.md",
    "11-guia-de-seguridad.md", "12-comunicado-externo.md",
]
GOLD_ARCHIVO = "gold_set.jsonl"
RAW = "https://raw.githubusercontent.com/JunBarrs24/itm-maestria-llms/main/shared/datasets/corpus/"


def cargar_corpus(cache: str = "corpus") -> dict[str, str]:
    """Devuelve {archivo: texto}. Lee la copia local del repositorio si existe; si no, descarga a ./corpus/."""
    candidatos = [Path("../../shared/datasets/corpus"), Path("shared/datasets/corpus"), Path(cache)]
    if "__file__" in globals():
        candidatos.insert(0, Path(__file__).resolve().parents[2] / "shared" / "datasets" / "corpus")
    base = next((b for b in candidatos if (b / CORPUS_ARCHIVOS[0]).exists()), None)
    if base is None:
        base = Path(cache)
        base.mkdir(exist_ok=True)
        for nombre in CORPUS_ARCHIVOS + [GOLD_ARCHIVO]:
            destino = base / nombre
            if not destino.exists():
                urllib.request.urlretrieve(RAW + nombre, destino)
    return {n: (base / n).read_text(encoding="utf-8") for n in CORPUS_ARCHIVOS}


# ----------------------------------------------------------------- 2. chunking
def chunk_fijo(archivo: str, texto: str, tam: int = 800, overlap: int = 100) -> list[dict]:
    """Ventanas de `tam` caracteres con traslape. Se conserva el último encabezado visto como sección."""
    chunks, seccion, pos = [], "", 0
    while pos < len(texto):
        trozo = texto[pos:pos + tam]
        enc = re.findall(r"^#{2,3}\s+(.*)$", texto[:pos + tam], re.M)
        if enc:
            seccion = enc[-1].strip()
        chunks.append({"archivo": archivo, "seccion": seccion, "texto": trozo})
        pos += tam - overlap
    return chunks


def chunk_por_seccion(archivo: str, texto: str) -> list[dict]:
    """Un chunk por encabezado ## o ###. Respeta la estructura que el autor ya puso."""
    chunks, seccion, buf = [], None, []
    for linea in texto.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)$", linea)
        if m:
            if buf and seccion:
                chunks.append({"archivo": archivo, "seccion": seccion, "texto": "\n".join(buf).strip()})
            seccion, buf = m.group(2).strip(), [linea]
        else:
            buf.append(linea)
    if buf and seccion:
        chunks.append({"archivo": archivo, "seccion": seccion, "texto": "\n".join(buf).strip()})
    return chunks


# ----------------------------------------------------------------- 3. embeddings e índice
class Indice:
    """Embeddings normalizados + producto punto. La versión numpy es el mecanismo; FAISS es la misma idea a escala."""

    def __init__(self, chunks: list[dict], modelo: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.chunks = chunks
        self.modelo = SentenceTransformer(modelo)
        self.E = self.modelo.encode([c["texto"] for c in chunks], normalize_embeddings=True, batch_size=32)

    def buscar(self, pregunta: str, k: int = 5) -> list[dict]:
        v = self.modelo.encode([pregunta], normalize_embeddings=True)[0]
        scores = self.E @ v                       # coseno, porque ambos están normalizados
        orden = np.argsort(-scores)[:k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in orden]


# ----------------------------------------------------------------- 4. contexto y generación
SYSTEM = (
    "Eres el asistente de soporte de Facturio. Respondes únicamente con la evidencia que se te entrega, "
    "en español y en máximo tres oraciones. Al final de cada afirmación cita la fuente entre corchetes "
    "con el formato [archivo#sección]. Si la evidencia no contiene la respuesta, responde exactamente: "
    "No tengo evidencia en la documentación para responder eso."
)


def construir_contexto(chunks: list[dict]) -> str:
    partes = []
    for i, c in enumerate(chunks, start=1):
        partes.append(f'<evidencia id="{i}" fuente="{c["archivo"]}#{c["seccion"]}">\n{c["texto"]}\n</evidencia>')
    return "\n\n".join(partes)


def construir_prompt(pregunta: str, chunks: list[dict]) -> str:
    return f"{construir_contexto(chunks)}\n\n<pregunta>\n{pregunta}\n</pregunta>"


class LLM:
    """Cliente mínimo: OpenAI Responses API si hay llave; Qwen local si no. Copia de course/shared/llm.py."""

    def __init__(self, model_local: str = "Qwen/Qwen2.5-1.5B-Instruct", model_api: str = "gpt-5-mini"):
        self.backend = "openai" if os.environ.get("OPENAI_API_KEY") else "local"
        if self.backend == "openai":
            from openai import OpenAI
            self.client, self.model = OpenAI(), model_api
        else:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.tok = AutoTokenizer.from_pretrained(model_local)
            self.net = AutoModelForCausalLM.from_pretrained(model_local, dtype=torch.float32).eval()
            self.model = model_local

    def chat(self, user: str, system: str = SYSTEM, max_output_tokens: int = 200) -> dict:
        t = time.perf_counter()
        if self.backend == "openai":
            params = dict(model=self.model, instructions=system, input=user, max_output_tokens=max_output_tokens)
            # Reasoning models (gpt-5*, o*): gastan max_output_tokens en razonar; con "minimal" la respuesta
            # cabe en presupuestos pequeños. Ejercicio: probar "low", "medium", "high" y medir tokens y latencia.
            if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
                params["reasoning"] = {"effort": "minimal"}
            r = self.client.responses.create(**params)
            return {"texto": r.output_text, "in": r.usage.input_tokens, "out": r.usage.output_tokens,
                    "s": time.perf_counter() - t}
        import torch
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        texto = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        ids = self.tok(texto, return_tensors="pt").input_ids
        with torch.no_grad():
            out = self.net.generate(ids, max_new_tokens=max_output_tokens, do_sample=False,
                                    pad_token_id=self.tok.eos_token_id)
        nuevos = out[0, ids.shape[1]:]
        return {"texto": self.tok.decode(nuevos, skip_special_tokens=True).strip(),
                "in": int(ids.shape[1]), "out": int(nuevos.shape[0]), "s": time.perf_counter() - t}


def responder(pregunta: str, indice: Indice, llm: LLM, k: int = 5) -> dict:
    chunks = indice.buscar(pregunta, k)
    r = llm.chat(construir_prompt(pregunta, chunks))
    return {"pregunta": pregunta, "respuesta": r["texto"], "fuentes": [f'{c["archivo"]}#{c["seccion"]}' for c in chunks],
            "tokens_in": r["in"], "tokens_out": r["out"], "latencia_s": r["s"]}


if __name__ == "__main__":
    docs = cargar_corpus()
    chunks = [c for n, t in docs.items() for c in chunk_por_seccion(n, t)]
    print(f"{len(docs)} documentos, {len(chunks)} chunks por sección")
    indice = Indice(chunks)
    llm = LLM()
    print("backend:", llm.backend, llm.model)
    preguntas = sys.argv[1:] or [
        "¿Cuántos días tengo para solicitar el reembolso de un cargo?",
        "¿Facturio tiene oficina en Guadalajara?",
        "¿Qué cabecera HTTP se usa para autenticarse en la API v2?",
    ]
    for q in preguntas:
        r = responder(q, indice, llm)
        print(f"\nPregunta: {q}\nRespuesta: {r['respuesta']}\nFuentes: {r['fuentes'][:3]}\n"
              f"tokens in/out: {r['tokens_in']}/{r['tokens_out']}  latencia: {r['latencia_s']:.1f} s")
