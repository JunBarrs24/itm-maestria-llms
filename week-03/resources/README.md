# Recursos de la semana 3

Lecturas ordenadas por prioridad. La primera es obligatoria; el resto amplía.

1. **Ouyang et al. (2022). Training language models to follow instructions with human feedback.** https://arxiv.org/abs/2203.02155
   El paper de InstructGPT. Describe exactamente la progresión de la sesión: SFT, reward model, RLHF. Leer las secciones 3 y 5; las figuras 1 y 2 bastan para reconstruir la clase.

2. **Rafailov et al. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model.** https://arxiv.org/abs/2305.18290
   Explica cómo optimizar sobre pares de preferencia sin un reward model separado. Leer la introducción y la figura 1; la derivación matemática es opcional.

3. **Brown et al. (2020). Language Models are Few-Shot Learners.** https://arxiv.org/abs/2005.14165
   Muestra que un modelo base sigue patrones dados en el prompt sin ningún post-training. Es la sección 3 del notebook y el puente hacia la semana 4. Leer la sección 2 y la figura 1.1.

4. **Hu et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models.** https://arxiv.org/abs/2106.09685
   Cómo hacer fine-tuning ajustando pocas matrices. Se menciona en la sesión como la razón por la que el fine-tuning es accesible; no se implementa. Leer el resumen y la figura 1.

5. **Hugging Face. Chat Templates.** https://huggingface.co/docs/transformers/chat_templating
   Documentación de `apply_chat_template`. Explica los marcadores, `add_generation_prompt` y por qué cada familia de modelos tiene su formato.

6. **Qwen2.5 technical report (2024).** https://arxiv.org/abs/2412.15115
   Describe los datos de pre-training, el SFT y el preference optimization de la familia usada en la demo. Leer las secciones de post-training para ver la progresión aplicada a un modelo concreto.

7. **Dataset de preferencias usado en la demo: trl-lib/ultrafeedback_binarized.** https://huggingface.co/datasets/trl-lib/ultrafeedback_binarized
   Pares (elegida, rechazada) con scores de un modelo juez. Sirve para inspeccionar qué criterios terminan dentro de un asistente.
