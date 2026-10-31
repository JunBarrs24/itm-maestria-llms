# Recursos de la semana 7

## Lecturas

* Robertson, S. y Zaragoza, H. *The Probabilistic Relevance Framework: BM25 and Beyond*. 2009. https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf
  La formulación de BM25 y su origen. Basta la sección que explica tf, idf y la normalización por longitud para entender por qué encuentra `E-1003` a la primera.
* Cormack, G., Clarke, C. y Buettcher, S. *Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods*. SIGIR 2009. https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf
  Dos páginas. La fórmula `1 / (k + rank)` y la evidencia de que fusionar rankings funciona sin calibrar scores.
* Liu, N. et al. *Lost in the Middle: How Language Models Use Long Contexts*. 2023. https://arxiv.org/abs/2307.03172
  El efecto de la posición de la evidencia en el contexto. El experimento de la sección 6 del notebook lo reproduce con ocho fragmentos y un modelo pequeño.
* Lewis, P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. 2020. https://arxiv.org/abs/2005.11401
  Repaso de la semana 5: el punto de partida de todo el bloque.

## Documentación

* SentenceTransformers. *Cross-Encoders*. https://www.sbert.net/examples/applications/cross-encoder/README.html
  Diferencia entre bi-encoder y cross-encoder y por qué el segundo solo se usa para reordenar pocos candidatos.
* `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` en Hugging Face. https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
  El reranker multilingüe que usa el curso; entrenado sobre MS MARCO traducido.
* `rank_bm25`. https://github.com/dorianbrown/rank_bm25
  La implementación de BM25 del notebook. Leer `BM25Okapi.get_scores` (30 líneas) para ver que no hay magia.
* Ragas. *Metrics*. https://docs.ragas.io/en/stable/concepts/metrics/
  Definiciones de faithfulness, answer relevancy y context precision como las usa una librería de evaluación de RAG. El curso las implementa a mano para que se vea qué mide cada una; comparar.

## Del curso

* `shared/datasets/corpus/README.md`: el corpus de Facturio, el gold set y los rasgos deliberados (términos exactos, contradicciones, inyección).
* `shared/retrieval_eval.py`: hit@k, recall@k y MRR.
* Semana 4, `examples/question_answering.md`: el patrón de QA con contexto que la generación de esta semana reutiliza.
