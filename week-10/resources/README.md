# Recursos de la semana 10

* Yao, S. et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. https://arxiv.org/abs/2210.03629. El loop que se construyó hoy (pensar, actuar, observar) es este patrón; la semana 14 lo formaliza junto con los demás patrones de razonamiento.
* OpenAI. *Responses API: conversation state*. https://platform.openai.com/docs/guides/conversation-state. Cómo `previous_response_id` guarda la conversación del lado de la API y qué implica para el control del loop.
* OpenAI. *Function calling*. https://platform.openai.com/docs/guides/function-calling. Definiciones `function`, items `function_call` y `function_call_output`, que la rama `responses` del loop usa.
* Anthropic (2024). *Building effective agents*. https://www.anthropic.com/research/building-effective-agents. La sección de agentes: cuándo el loop se justifica frente a un workflow, y por qué conviene empezar simple.
* Hugging Face. *transformers serve*. https://huggingface.co/docs/transformers/main/serving. El servidor compatible con la API de OpenAI que los notebooks usan sin llave.
* `shared/facturio_tools.py` y `shared/local_server.py` del curso: las tools con autorización y el helper de backend que el loop reutiliza.
