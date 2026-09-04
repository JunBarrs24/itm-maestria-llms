# ARQUITECTURA DE SOFTWARE PARA SISTEMAS INTELIGENTES

## Subtítulo

**LLM Engineering: Fundamentos, RAG, Agentes y Operación en Producción**

**LGAC:** Ingeniería de Software, Inteligencia Artificial Aplicada, Sistemas Inteligentes, Arquitecturas de Software.

---

# 1. Historial de la asignatura

Diseño y actualización del programa de la asignatura tomando como base un formato institucional de temario y adaptándolo al diseño, implementación y operación de sistemas inteligentes basados en modelos de lenguaje.

La actualización reorganiza el contenido para fortalecer la progresión:

**Fundamentos → Prompt Engineering → RAG → Tool Calling → Context Engineering → Agentes → Sistemas Multi-Agente → Producción.**

---

# 2. Pre-requisitos y correquisitos

Conocimientos generales de programación y comprensión básica de estructuras de datos.

Capacidad de análisis y síntesis.

Habilidad para:

* leer documentación técnica;
* formular problemas;
* experimentar con herramientas computacionales;
* analizar resultados;
* comunicar decisiones de diseño.

No se requiere experiencia previa con:

* LLMs;
* Transformers;
* RAG;
* agentes;
* frameworks de inteligencia artificial.

Se utilizará principalmente Python para las actividades prácticas.

---

# 3. Objetivo de la asignatura

Diseñar, implementar, evaluar y proponer la operación de sistemas inteligentes basados en modelos de lenguaje grandes, integrando fundamentos de generación de lenguaje, arquitectura Transformer, prompt engineering, Retrieval-Augmented Generation, tool calling, context engineering, agentes, razonamiento, evaluación, observabilidad, resiliencia, seguridad y optimización de costos.

El estudiante deberá aprender a seleccionar la arquitectura más simple que satisfaga los requisitos del problema, distinguiendo entre:

* código determinista;
* llamada directa a un LLM;
* RAG;
* workflow con LLM;
* agente;
* sistema multi-agente.

---

# 4. Aportación al perfil del graduado

El egresado podrá:

* analizar problemas donde los LLMs aporten valor;
* identificar problemas donde un LLM no sea la herramienta adecuada;
* comprender los mecanismos fundamentales de los modelos de lenguaje;
* seleccionar modelos y arquitecturas apropiadas;
* construir aplicaciones basadas en LLM;
* diseñar pipelines RAG;
* construir workflows y agentes capaces de utilizar herramientas;
* administrar el contexto, estado y memoria de sistemas agentic;
* evaluar sistemas probabilísticos;
* analizar costo, latencia y calidad;
* instrumentar sistemas mediante trazas, métricas y logs;
* identificar riesgos de seguridad y confiabilidad;
* diseñar mecanismos de resiliencia;
* proponer arquitecturas de producción para sistemas inteligentes.

La asignatura fortalece competencias en:

* ingeniería de software;
* diseño de sistemas;
* inteligencia artificial aplicada;
* evaluación técnica;
* pensamiento crítico;
* toma de decisiones arquitectónicas.

---

# 5. Contenido temático

# UNIDAD I — Fundamentos de LLMs

## Descripción

Esta unidad introduce los fundamentos necesarios para comprender cómo un modelo de lenguaje transforma texto en tokens, representa información, relaciona elementos mediante atención y genera secuencias de manera autoregresiva.

También estudia la transición desde modelos base hasta modelos instruction-tuned y asistentes modernos.

## Objetivos

El estudiante será capaz de:

* explicar qué es y qué no es un LLM;
* distinguir entre un modelo y una aplicación basada en un modelo;
* explicar tokenización y ventanas de contexto;
* describir la predicción del siguiente token;
* comprender logits, probabilidades y estrategias de generación;
* describir conceptualmente la arquitectura Transformer;
* explicar self-attention;
* interpretar intuitivamente Query, Key y Value;
* comprender causal masking y generación autoregresiva;
* distinguir modelos encoder, decoder y encoder-decoder;
* explicar pre-training;
* distinguir modelos base de modelos instruction-tuned;
* describir SFT, instruction tuning, RLHF y preference optimization;
* comparar diferentes familias de modelos.

## Subtemas

### 1.1 Sistemas de software con LLMs

* Qué es un LLM.
* Qué no es un LLM.
* LLM vs aplicación basada en LLM.
* Software determinista y componentes probabilísticos.
* Casos de uso.
* Limitaciones.
* Alucinaciones.
* Riesgos de utilizar LLMs.
* Arquitectura mínima de una aplicación con LLM.

### 1.2 Tokens y generación

* Datos de entrenamiento.
* Preparación de datos.
* Tokenización.
* Tokens vs palabras.
* Token IDs.
* Vocabulary.
* Context window.
* Predicción del siguiente token.
* Logits.
* Softmax.
* Generación autoregresiva.
* Temperature.
* Top-k.
* Top-p.
* Longitud máxima de generación.

### 1.3 Arquitectura Transformer

* Motivación de Attention Is All You Need.
* Embeddings.
* Información posicional.
* Self-attention.
* Query, Key y Value.
* Attention scores.
* Scaled dot-product attention.
* Softmax.
* Weighted values.
* Multi-head attention.
* Causal masking.
* Feed-forward networks.
* Residual connections.
* Normalization.
* Transformer blocks.
* Decoder-only models.
* Generación autoregresiva.

### 1.4 Del modelo base al asistente

* Pre-training.
* Base models.
* Supervised Fine-Tuning.
* Instruction tuning.
* Preference data.
* Reward models.
* RLHF.
* Preference optimization.
* Modelos base vs instruction models.
* Modelos estándar vs modelos orientados al razonamiento.
* Modelos abiertos vs cerrados.
* Modelos pequeños vs grandes.
* Modelos locales vs APIs.

---

# UNIDAD II — Prompt Engineering y Retrieval-Augmented Generation

## Descripción

Esta unidad estudia cómo controlar el comportamiento observable de un modelo mediante instrucciones, contexto, ejemplos y formatos estructurados.

Posteriormente se introduce Retrieval-Augmented Generation como mecanismo para proporcionar al modelo información externa relevante.

El énfasis se coloca en construir RAG desde sus componentes fundamentales antes de utilizar frameworks que abstraigan el proceso.

## Objetivos

El estudiante será capaz de:

* diseñar prompts claros y verificables;
* decidir cuándo utilizar zero-shot, one-shot y few-shot;
* utilizar ejemplos de manera sistemática;
* diseñar restricciones positivas y negativas;
* utilizar formatos estructurados;
* diseñar prompts para clasificación, extracción, resumen, transformación y generación;
* versionar y evaluar prompts;
* explicar la diferencia entre prompting, RAG y fine-tuning;
* construir un pipeline RAG;
* diseñar estrategias de chunking;
* generar embeddings;
* realizar retrieval semántico;
* combinar búsqueda semántica y lexical;
* comprender reranking;
* construir el contexto enviado al modelo;
* evaluar retrieval y generación por separado.

## Subtemas

### 2.1 Prompt Engineering para aplicaciones

Anatomía de un prompt:

* instrucciones;
* contexto;
* datos;
* ejemplos;
* restricciones;
* formato esperado;
* criterios de éxito.

Técnicas:

* zero-shot;
* one-shot;
* few-shot;
* role prompting;
* instruction prompting;
* context prompting;
* structured prompting;
* delimitadores;
* output schemas;
* structured outputs.

Patrones por tarea:

* clasificación;
* extracción;
* resumen;
* transformación;
* generación;
* question answering.

### 2.2 Few-shot e In-Context Learning

* Cuándo utilizar ejemplos.
* Selección de ejemplos.
* Diversidad.
* Edge cases.
* Ejemplos positivos.
* Ejemplos negativos.
* Formato consistente.
* Sesgo introducido por ejemplos.
* Consumo de tokens.
* Zero-shot vs few-shot.

### 2.3 Restricciones y verificabilidad

* Instrucciones positivas.
* Instrucciones negativas.
* Uso de negaciones.
* Restricciones explícitas.
* Output schemas.
* Structured outputs.
* Validación posterior.
* Pydantic y esquemas estructurados.
* Prompt versioning.
* Prompt regression.
* Datasets de evaluación.

### 2.4 Introducción a RAG

* Limitaciones del conocimiento interno del modelo.
* RAG vs prompting.
* RAG vs fine-tuning.
* Arquitectura de RAG.
* Ingesta.
* Retrieval.
* Context construction.
* Generation.
* Grounding.
* Citas.
* Trazabilidad.
* Manejo de ausencia de evidencia.

### 2.5 Retrieval Engineering

* Parsing de documentos.
* Limpieza.
* Chunking.
* Chunk size.
* Chunk overlap.
* Metadata.
* Embeddings.
* Vector stores.
* Cosine similarity.
* Top-k retrieval.
* Metadata filtering.

### 2.6 RAG avanzado y evaluación

* Semantic search.
* Lexical search.
* BM25 conceptual.
* Hybrid retrieval.
* Reranking.
* Context construction.
* Orden y selección de evidencia.
* Relevance.
* Faithfulness.
* Correctness.
* Answerability.
* Coverage.
* Evaluación de retrieval.
* Evaluación de generación.
* Diagnóstico de errores.

---

# UNIDAD III — Agentes y Sistemas Agentic

## Descripción

Esta unidad estudia la transición desde llamadas aisladas a modelos hacia workflows, tool calling y agentes.

El estudiante construirá primero los mecanismos fundamentales antes de utilizar frameworks especializados.

Se introduce Context Engineering como disciplina para controlar qué información recibe el modelo durante sistemas multi-paso.

## Objetivos

El estudiante será capaz de:

* distinguir LLM, workflow, sistema agentic y agente;
* diseñar tool calling;
* diseñar workflows deterministas con LLMs;
* identificar cuándo NO utilizar un agente;
* construir un agent loop básico;
* utilizar APIs modernas de agentes;
* diseñar estado y memoria;
* administrar context windows;
* implementar estrategias de compaction;
* diseñar handoffs;
* utilizar guardrails;
* diseñar sistemas multi-agente;
* modelar workflows con grafos;
* establecer límites de iteración y criterios de parada.

## Subtemas

### 3.1 Tool Calling

* Function calling.
* Tool schemas.
* Inputs estructurados.
* Outputs estructurados.
* Validación.
* Ejecución.
* Errores.
* Retries.
* Timeouts.
* Side effects.
* Autorización.
* Idempotencia.

### 3.2 LLM Workflows

* Prompt chaining.
* Routing.
* Parallelization.
* Orchestrator-worker.
* Deterministic workflows.
* LLM-assisted workflows.
* Cuándo utilizar un workflow.
* Cuándo NO utilizar un agente.

### 3.3 Context Engineering

Distinguir:

* model context;
* application state;
* agent state;
* conversation history;
* short-term memory;
* long-term memory;
* external knowledge;
* retrieved context.

Construcción de contexto:

* instrucciones;
* conversación;
* tool definitions;
* tool calls;
* tool outputs;
* RAG;
* memory;
* current state.

Principio:

**No maximizar la cantidad de contexto; proporcionar el contexto mínimo suficiente para tomar correctamente la siguiente decisión.**

### 3.4 Context Compression y Compaction

Razones para comprimir:

* límites del context window;
* costo;
* latencia;
* signal-to-noise ratio;
* información obsoleta;
* tool outputs extensos;
* agentes de larga duración.

Estrategias:

* sliding window;
* summarization;
* compaction;
* structured state;
* tool-output filtering;
* retrieval-based memory;
* hierarchical summaries;
* selective preservation;
* Keep / Compress / Drop.

Riesgos:

* pérdida de información;
* pérdida de restricciones;
* resúmenes incorrectos;
* información obsoleta;
* pérdida de provenance.

### 3.5 De workflow a agente

* Objetivo.
* Estado.
* Contexto.
* Tools.
* Agent loop.
* Observe → Decide → Act.
* Iteraciones.
* Stop conditions.
* Error handling.
* Human-in-the-loop.

### 3.6 APIs y frameworks de agentes

* OpenAI Responses API.
* OpenAI Agents SDK.
* Agent.
* Runner.
* Tools.
* Sessions.
* Guardrails.
* Tracing.

### 3.7 Multi-Agent Systems

* Handoffs.
* Agents-as-tools.
* Manager pattern.
* Specialized agents.
* Routing.
* Context isolation.
* Structured handoff packages.
* Context transfer.
* Riesgos de complejidad innecesaria.

### 3.8 Orquestación explícita

* State machines.
* Graph-based orchestration.
* LangGraph.
* Nodes.
* Edges.
* Conditional edges.
* State.
* Checkpoints.
* Human approval.
* Iteration limits.

---

# UNIDAD IV — Modelos de Pensamiento y Razonamiento

## Descripción

Esta unidad estudia tareas que requieren descomposición, búsqueda, verificación y razonamiento multi-paso.

El énfasis no consiste en utilizar siempre modelos razonadores, sino en decidir cuándo el costo adicional se justifica.

## Objetivos

El estudiante será capaz de:

* distinguir recuperación, razonamiento y acción;
* identificar tareas simples y tareas multi-paso;
* comprender patrones de razonamiento;
* comparar modelos estándar y razonadores;
* diseñar mecanismos de verificación;
* analizar costo y latencia;
* integrar herramientas mediante MCP.

## Subtemas

### 4.1 Patrones de razonamiento y acción

* Decomposition.
* ReAct.
* Reflection.
* Reflexion.
* ReWOO.
* Self-consistency.
* Tree search.
* Planner-executor.
* Verifier-guided workflows.

### 4.2 Modelos orientados al razonamiento

* Modelos estándar vs reasoning models.
* Inference-time compute.
* Self-refinement.
* Verifiers.
* Costos.
* Latencia.
* Overthinking.
* Criterios de uso.

### 4.3 Model Context Protocol

* Propósito de MCP.
* MCP clients.
* MCP servers.
* Tools.
* Resources.
* Prompts.
* Relación con agentes.
* Tool ecosystems.
* Seguridad y autorización.

---

# UNIDAD V — Operación de Sistemas Inteligentes en Producción

## Descripción

Esta unidad integra evaluación, observabilidad, costo, seguridad, resiliencia y mantenimiento.

El objetivo es pasar de una demostración funcional a un sistema capaz de operar de manera controlada.

## Objetivos

El estudiante será capaz de:

* diseñar datasets de evaluación;
* diferenciar evaluación offline y online;
* utilizar revisión humana;
* comprender LLM-as-a-judge;
* instrumentar traces, spans, logs y métricas;
* medir tokens, llamadas, costo y latencia;
* detectar fallas de herramientas;
* diseñar retries, fallbacks y circuit breakers;
* analizar prompt injection;
* analizar data leakage;
* diseñar autorización para tools;
* incorporar human-in-the-loop;
* diseñar una arquitectura final de producción.

## Subtemas

### 5.1 Evaluación

* Evaluation datasets.
* Expected behavior.
* Acceptance criteria.
* Edge cases.
* Offline evaluation.
* Online evaluation.
* Human review.
* LLM-as-a-judge.
* Regression testing.

### 5.2 Observabilidad

* Traces.
* Spans.
* LLM calls.
* Tool calls.
* Handoffs.
* Errors.
* Latency.
* Token usage.
* Prompt version.
* Langfuse.
* Tracing de frameworks.

### 5.3 Cost Engineering

Registrar cuando sea posible:

* input tokens;
* output tokens;
* total tokens;
* número de llamadas;
* tool calls;
* latencia;
* costo estimado.

Analizar:

**quality vs cost vs latency.**

### 5.4 Resiliencia

* Timeouts.
* Retries.
* Exponential backoff.
* Fallbacks.
* Circuit breakers.
* Iteration limits.
* Graceful degradation.
* Human-in-the-loop.

### 5.5 Seguridad

* Prompt injection.
* Data leakage.
* Tool misuse.
* Authorization.
* Least privilege.
* Dangerous side effects.
* Validation.
* Guardrails.
* Auditability.

### 5.6 Arquitectura final

Integración de:

* application;
* model;
* RAG;
* context;
* state;
* tools;
* agents;
* evaluation;
* observability;
* security;
* cost;
* resilience.

---

# 6. Metodología de desarrollo del curso

El curso combinará:

* sesiones conceptuales;
* demostraciones guiadas;
* experimentación;
* programación;
* discusión arquitectónica;
* actividades cortas;
* prácticas semanales autocontenidas sobre el caso común del curso.

El caso común del curso es una mesa de soporte al cliente de un producto de software. Todo el material (datasets, corpus documental, herramientas y arquitectura) se construye sobre ese caso, de modo que las prácticas no dependen de un proyecto externo.

Quien lo desee puede repetir cada práctica sobre un caso propio (por ejemplo, el de su tesis) como ejercicio opcional, sin peso en la evaluación.

Las sesiones seguirán cuando sea conveniente la progresión:

**Problema → Intuición → Mecanismo → Implementación mínima → Experimento → Falla → Solución arquitectónica → Framework → Producción.**

## Principio pedagógico

No introducir una herramienta antes de explicar qué problema resuelve.

Por ejemplo:

* el LLM genera;
* el prompt condiciona;
* el embedding representa;
* el retriever selecciona contexto;
* RAG proporciona conocimiento externo;
* una tool permite recuperar información o realizar acciones;
* un workflow controla una secuencia;
* un agente decide dinámicamente el siguiente paso;
* el estado conserva información de la aplicación;
* context engineering decide qué información verá el modelo;
* las evaluaciones miden comportamiento;
* la observabilidad permite investigar fallas.

## Pregunta recurrente

Durante todo el curso:

> **¿Cuál es la solución más simple que satisface correctamente los requisitos?**

Considerar en orden:

**Código → LLM → RAG → Workflow → Agent → Multi-Agent.**

---

# 7. Sugerencias de evaluación

| Componente                                         | Porcentaje |
| -------------------------------------------------- | ---------: |
| Prácticas semanales sobre el caso común del curso  |        40% |
| Entregables por bloque                             |        30% |
| Prototipo / arquitectura final                     |        20% |
| Participación y análisis crítico                   |        10% |

Las prácticas deberán evaluar decisiones y análisis, no solamente que el código ejecute.

---

# 8. Bibliografía y software de apoyo

## Bibliografía base

1. Vaswani, A. et al. *Attention Is All You Need*. 2017.
2. Brown, T. et al. *Language Models are Few-Shot Learners*. 2020.
3. Ouyang, L. et al. *Training language models to follow instructions with human feedback*. 2022.
4. Lewis, P. et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. 2020.
5. Hu, E. et al. *LoRA: Low-Rank Adaptation of Large Language Models*. 2021.
6. Wei, J. et al. *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. 2022.
7. Yao, S. et al. *ReAct: Synergizing Reasoning and Acting in Language Models*. 2022.
8. Yao, S. et al. *Tree of Thoughts*. 2023.
9. Shinn, N. et al. *Reflexion*. 2023.
10. DeepSeek-AI. *DeepSeek-R1*. 2025.
11. Documentación oficial de OpenAI.
12. Documentación oficial de Google Gemini y ADK.
13. Documentación oficial de LangGraph.
14. Documentación oficial de Model Context Protocol.
15. Documentación oficial de Langfuse.

## Software

### Fundamentos

* Python 3.
* Google Colab.
* Jupyter.
* Hugging Face Transformers.
* PyTorch.
* GPT-2 y modelos abiertos pequeños.

### RAG

* SentenceTransformers.
* FAISS o Chroma.
* Librerías de parsing de documentos.

### APIs

* Gemini API cuando sea conveniente.
* OpenAI API para el bloque de agentes.

### Agentes

* OpenAI Responses API.
* OpenAI Agents SDK.
* LangGraph.
* Google ADK como comparación.
* MCP.

### Operación

* Langfuse.
* Tracing nativo de frameworks.
* Herramientas de logging y métricas.

El curso deberá poder comenzar sin requerir créditos comerciales.

Posteriormente se podrá utilizar un presupuesto controlado de API para experimentar con agentes y modelos de mayor capacidad.

---

# 9. Planeación de 15 semanas

## Semana 1 — Sistemas de software con LLMs

### Pregunta

**¿Qué cambia arquitectónicamente cuando introducimos un componente probabilístico?**

### Conceptos

* Qué es un LLM.
* Qué no es.
* LLM vs aplicación.
* Software determinista vs probabilístico.
* Casos de uso.
* Alucinaciones.
* Arquitectura mínima.
* Fallas.

### Demo

GPT-2 como modelo de lenguaje no instruction-tuned.

### Resultado

Arquitectura V0 de la mesa de soporte del curso.

---

# Semana 2 — Dentro de un LLM: Tokens, Transformers y generación

### Pregunta

**¿Qué ocurre desde que escribimos texto hasta que aparece el siguiente token?**

### Pipeline

texto
→ tokenizer
→ token IDs
→ embeddings
→ positional information
→ self-attention
→ Transformer blocks
→ logits
→ probabilities
→ decoding
→ next token

### Conceptos

* Tokenization.
* Context window.
* Embeddings.
* Self-attention.
* Query, Key, Value.
* Attention scores.
* Softmax.
* Causal masking.
* Multi-head attention.
* Feed-forward.
* Residuals.
* Decoder-only architecture.
* Logits.
* Temperature.
* Top-k.
* Top-p.
* Autoregressive generation.

### Demo

Hugging Face + GPT-2.

Inspeccionar:

* tokens;
* IDs;
* logits;
* top next tokens;
* attention;
* diferentes estrategias de generación.

---

# Semana 3 — De modelo base a asistente moderno

### Pregunta

**Si GPT-2 ya es un Transformer, ¿por qué no se comporta como ChatGPT?**

### Conceptos

* Pre-training.
* Base models.
* SFT.
* Instruction tuning.
* Preference data.
* RLHF.
* Preference optimization.
* Base vs instruction models.
* Open vs closed.
* Small vs large.
* Local vs API.
* Standard vs reasoning models.

### Demo

Comparar el mismo conjunto de instrucciones sobre:

* modelo base;
* modelo instruction-tuned.

---

# Semana 4 — Prompt Engineering para aplicaciones

### Pregunta

**¿Cómo diseñamos instrucciones que produzcan comportamiento verificable?**

### Conceptos

* Anatomy of a prompt.
* Zero-shot.
* One-shot.
* Few-shot.
* In-context learning.
* Example selection.
* Positive constraints.
* Negative constraints.
* Negations.
* Roles.
* Delimiters.
* Structured outputs.
* Output schemas.
* Classification.
* Extraction.
* Summarization.
* Transformation.
* Generation.
* Decomposition.
* Prompt chaining.
* Prompt versioning.
* Prompt regression.
* Evaluation.

### Demo

Dataset de clasificación.

Comparar:

Prompt pobre
→ instrucciones claras
→ schema
→ few-shot
→ structured output.

Medir:

* accuracy;
* format compliance;
* tokens;
* latencia;
* costo cuando aplique.

---

# Semana 5 — RAG Fundamentals: construir el primer RAG

### Pregunta

**¿Qué hacemos cuando el modelo necesita información externa?**

### Conceptos

* Prompt vs RAG vs fine-tuning.
* Grounding.
* Ingestion.
* Chunking básico.
* Embeddings.
* Retrieval.
* Context.
* Generation.
* Citations.
* Answerability.

### Demo

Construir RAG completo sin framework.

---

# Semana 6 — Retrieval Engineering

### Pregunta

**¿Qué determina qué información termina viendo el modelo?**

### Conceptos

* Parsing.
* Cleaning.
* Chunk size.
* Chunk overlap.
* Metadata.
* Embeddings.
* Vector stores.
* Similarity.
* Top-k.
* Metadata filtering.

### Experimento

Cambiar chunk size, overlap y top-k y observar retrieval.

---

# Semana 7 — Advanced RAG: Retrieval, Context y evaluación

### Pregunta

**¿Encontrar documentos parecidos significa encontrar la evidencia correcta?**

### Conceptos

* Semantic retrieval.
* Lexical search.
* BM25.
* Hybrid retrieval.
* Reranking.
* Context construction.
* Evidence selection.
* Retrieval evaluation.
* Generation evaluation.
* Faithfulness.
* Correctness.
* Answerability.
* Citation correctness.

### Mensaje

Separar:

**retrieval failure**

de:

**generation failure.**

---

# Semana 8 — Tool Calling y LLM Workflows

### Pregunta

**¿Qué cambia cuando el modelo puede utilizar herramientas?**

### Conceptos

* Function calling.
* Tool schemas.
* Structured arguments.
* Validation.
* Tool execution.
* Tool errors.
* Prompt chaining.
* Routing.
* Parallelization.
* Orchestrator-worker.
* Deterministic workflows.

### Demo

Construir tool calling primero manualmente.

### Pregunta crítica

**¿Esto ya es un agente?**

No necesariamente.

---

# Semana 9 — Context Engineering, State y Memory

### Pregunta

**¿Qué información necesita realmente el modelo para tomar la siguiente decisión?**

### Conceptos

* Model context.
* Application state.
* Agent state.
* Conversation history.
* Short-term memory.
* Long-term memory.
* RAG knowledge.
* Tool outputs.

### Problemas

* Context limits.
* Cost.
* Latency.
* Noise.
* Stale information.

### Estrategias

* Sliding window.
* Summarization.
* Compaction.
* Structured state.
* Tool-output filtering.
* Retrieval-based memory.
* Hierarchical summaries.
* Keep / Compress / Drop.

### Demo

Comparar:

A. Full history.

B. Sliding window.

C. Structured state + summary.

Medir tokens y comprobar si se pierde una restricción crítica.

---

# Semana 10 — De workflow a agente: Responses API

### Pregunta

**¿Qué convierte un workflow en un agente?**

### Conceptos

* Objective.
* Context.
* State.
* Tools.
* Observe.
* Decide.
* Act.
* Agent loop.
* Stop condition.
* Iteration limits.
* Error handling.

### Progresión

Python manual agent loop
→ Responses API.

### Objetivo

El estudiante debe entender el mecanismo antes del framework.

---

# Semana 11 — OpenAI Agents SDK

### Pregunta

**¿Qué problemas nos resuelve un runtime de agentes?**

### Conceptos

* Agent.
* Runner.
* Tools.
* Sessions.
* Guardrails.
* Structured outputs.
* Tracing.
* Human-in-the-loop.

### Comparación

Manual agent loop
vs
Agents SDK.

### Evaluar

* código;
* control;
* abstracción;
* debugging;
* costo;
* observabilidad.

---

# Semana 12 — Multi-Agent Systems

### Pregunta

**¿Cuándo tiene sentido dividir un problema entre varios agentes?**

### Conceptos

* Specialized agents.
* Handoffs.
* Agents-as-tools.
* Manager pattern.
* Routing.
* Context isolation.
* Handoff packages.
* Guardrails.
* Permissions.

### Comparación

Single agent
vs
multi-agent.

### Mensaje

Más agentes ≠ mejor arquitectura.

---

# Semana 13 — LangGraph y control explícito

### Pregunta

**¿Qué hacemos cuando no queremos que el modelo controle todo el flujo?**

### Conceptos

* State graph.
* Nodes.
* Edges.
* Conditional edges.
* Deterministic control.
* Agent nodes.
* Checkpoints.
* Human approval.
* Retry loops.
* Stop conditions.
* State vs model context.

### Comparación

Agents SDK
vs
graph/state-machine orchestration.

---

# Semana 14 — Reasoning, MCP y patrones agentic

### Pregunta

**¿Cuándo necesitamos más razonamiento, más información o más herramientas?**

### Conceptos

* ReAct.
* Planner-executor.
* Reflection.
* Reflexion.
* ReWOO.
* Self-consistency.
* Tree search.
* Verifiers.
* Reasoning models.
* Inference-time compute.
* Cost/latency.
* MCP.
* MCP servers.
* MCP clients.
* Tools y resources.

### Decisión arquitectónica

Simple prompt
vs
RAG
vs
workflow
vs
reasoning model
vs
agent.

---

# Semana 15 — Producción de sistemas inteligentes

### Pregunta

**¿Qué falta entre un prototipo que funciona y un sistema que podemos operar?**

### Conceptos

## Evals

* datasets;
* regression;
* human review;
* LLM-as-a-judge.

## Observability

* traces;
* spans;
* logs;
* tool calls;
* handoffs;
* latency;
* Langfuse.

## Cost Engineering

* input tokens;
* output tokens;
* calls;
* cost;
* latency.

## Resilience

* retries;
* timeouts;
* fallbacks;
* circuit breakers;
* iteration limits.

## Security

* prompt injection;
* data leakage;
* tool authorization;
* least privilege;
* dangerous actions;
* human approval.

## Cierre

Diseñar la arquitectura final:

User
→ Application
→ Context Builder
→ RAG / State / Memory
→ Agent / Workflow
→ Tools
→ Guardrails
→ Evaluation
→ Observability
→ Production.

---

# 10. Principios transversales del curso

Toda técnica deberá responder:

1. ¿Qué problema resuelve?
2. ¿Cómo funciona?
3. ¿Cuándo debemos utilizarla?
4. ¿Cuándo NO debemos utilizarla?
5. ¿Cómo sabemos si funciona?
6. ¿Cuánto cuesta?
7. ¿Qué puede fallar?

Toda arquitectura deberá considerar:

**Quality + Reliability + Latency + Cost + Security + Maintainability.**
