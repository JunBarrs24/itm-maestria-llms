# Recursos de la semana 5

* Lewis, P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. 2020. https://arxiv.org/abs/2005.11401. El artículo que nombró la técnica; leer la introducción y la figura 1 para ver que el pipeline de hoy es el mismo, con un retriever entrenable que el curso sustituye por uno fijo.
* Documentación de SentenceTransformers. https://www.sbert.net/. Cómo cargar un modelo de embeddings, normalizar y calcular similitud; la lista de modelos multilingües explica por qué se eligió `paraphrase-multilingual-MiniLM-L12-v2`.
* Documentación de FAISS. https://github.com/facebookresearch/faiss/wiki. `IndexFlatIP` es el índice exacto que usa la sesión; el resto de la wiki muestra qué cambia cuando los vectores son millones.
* Reimers, N. y Gurevych, I. *Sentence-BERT*. 2019. https://arxiv.org/abs/1908.10084. Por qué un encoder entrenado con pares produce vectores comparables por coseno; conecta con la distinción encoder / decoder de la semana 2.
* `shared/datasets/corpus/README.md`. Qué contiene el corpus de Facturio, cómo se usa en cada semana y qué rasgos tiene a propósito.
