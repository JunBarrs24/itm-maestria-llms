"""Tres estrategias de chunking sobre un documento del corpus, con conteos.

Uso:  .venv/bin/python course/week-06/examples/chunking_strategies.py [archivo.md]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rag_lib import cargar_corpus, chunk_fijo, chunk_por_seccion, chunk_recursivo  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

CORPUS = Path(__file__).resolve().parents[2] / "shared" / "datasets" / "corpus"
archivo = sys.argv[1] if len(sys.argv) > 1 else "06-politica-reembolsos-y-cargos.md"
docs = {archivo: cargar_corpus(CORPUS)[archivo]}
modelo = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
contar = lambda t: len(modelo.tokenizer.encode(t, add_special_tokens=False))

estrategias = {
    "por sección (## y ###)": chunk_por_seccion(docs),
    "fijo 200 tokens, overlap 20": chunk_fijo(docs, 200, 20, contar),
    "recursivo hasta 120 tokens": chunk_recursivo(docs, 120, contar),
}
print(f"Documento: {archivo} ({contar(docs[archivo])} tokens)\n")
for nombre, chunks in estrategias.items():
    toks = [contar(c["texto"]) for c in chunks]
    cruzan = sum(1 for c in chunks if len(c.get("secciones", [])) > 1)
    print(f"{nombre:32s} chunks={len(chunks):3d}  tokens min/med/max={min(toks)}/{sum(toks)//len(toks)}/{max(toks)}  cruzan secciones={cruzan}")
    print("   primer chunk:", repr(chunks[0]["texto"][:90]), "... sección:", chunks[0]["seccion"])
    print("   chunk 3:     ", repr(chunks[min(2, len(chunks)-1)]["texto"][:90]), "... sección:", chunks[min(2, len(chunks)-1)]["seccion"])
    print()
print("Qué mirar: el chunk fijo empieza a media frase y puede mezclar 'Plazo' con 'Monto';")
print("el recursivo respeta párrafos; la sección conserva el encabezado, que es la mejor pista para el retrieval.")
