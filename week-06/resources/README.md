# Recursos de la semana 6

| Recurso | Por qué leerlo |
| --- | --- |
| [SentenceTransformers: documentación](https://www.sbert.net/) | Cómo se cargan modelos, qué significa `max_seq_length` y cómo se comparan modelos en la tabla MTEB. Leer "Pretrained Models" y "Semantic Search". |
| [FAISS: wiki de Facebook Research](https://github.com/facebookresearch/faiss/wiki) | Qué índices existen (plano, IVF, HNSW) y cuándo el índice plano de la clase deja de bastar. Leer "Getting started" y "Guidelines to choose an index". |
| [Chroma: documentación](https://docs.trychroma.com/) | Colecciones, metadata y filtros `where`. Es lo que abstrae la migración de la demo. |
| [pypdf: documentación](https://pypdf.readthedocs.io/) | Extracción de texto de PDF y sus límites con tablas y columnas. |
| Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | El paper de RAG. Leer la sección de retriever para ver que la evaluación del retrieval siempre fue un problema aparte. |
| Reimers y Gurevych (2019), *Sentence-BERT* | De dónde salen los modelos de embeddings de la clase y por qué fueron entrenados con pares de frases cortas. Explica la dilución en chunks largos. |
| `shared/datasets/corpus/README.md` | Estructura del corpus de Facturio, gold set y rasgos deliberados. |
| `shared/retrieval_eval.py` | La versión canónica de hit@k, recall@k y MRR que los notebooks llevan copiada. |
