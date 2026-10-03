"""Servidor local compatible con la API de OpenAI, para trabajar sin llave.

`transformers serve` expone `POST /v1/chat/completions` con el formato de OpenAI,
incluidas las tool calls, sobre un modelo abierto. Con eso, el mismo código que
usa el SDK de OpenAI, el Agents SDK (con `OpenAIChatCompletionsModel`) o LangGraph
(con `ChatOpenAI(base_url=...)`) corre contra un modelo local.

Límites: solo Chat Completions (no Responses API, no built-in tools, no tracing
alojado), un modelo pequeño (calidad menor, tool calls a veces equivocadas),
una petición a la vez, y `tool_choice` se ignora (el modelo decide siempre si
llama una tool; `required` y un nombre de función no lo fuerzan).

    from local_server import ensure_local_server, MODELO_LOCAL
    base_url = ensure_local_server()          # arranca el servidor si no está
    client = OpenAI(base_url=base_url, api_key="local")

En Colab funciona igual: la primera llamada tarda mientras descarga el modelo.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import urllib.request

MODELO_LOCAL = "Qwen/Qwen2.5-1.5B-Instruct"
PUERTO = 8765


def _vivo(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_local_server(modelo: str = MODELO_LOCAL, puerto: int = PUERTO, espera_s: int = 600) -> str:
    """Devuelve la base_url de un servidor local vivo; lo arranca en segundo plano si hace falta."""
    base = f"http://localhost:{puerto}/v1"
    raiz = f"http://localhost:{puerto}"
    if _vivo(raiz):
        return base
    exe = shutil.which("transformers") or os.path.join(os.path.dirname(sys.executable), "transformers")
    log = open(os.path.join(os.environ.get("TMPDIR", "/tmp"), f"transformers-serve-{puerto}.log"), "a")
    subprocess.Popen([exe, "serve", "--port", str(puerto), modelo], stdout=log, stderr=subprocess.STDOUT,
                     start_new_session=True)
    inicio = time.time()
    while time.time() - inicio < espera_s:
        if _vivo(raiz):
            return base
        time.sleep(2)
    raise RuntimeError(f"el servidor local no respondió en {espera_s} s; revisa {log.name}")


def backend_config() -> dict:
    """Configuración según el entorno: llave real de OpenAI o servidor local.

    Devuelve dict con `base_url`, `api_key`, `model`, `local` (bool) y `api`
    ('responses' con OpenAI, 'chat' con el servidor local).
    """
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
        return {"base_url": None, "api_key": os.environ["OPENAI_API_KEY"],
                "model": os.environ.get("OPENAI_MODEL", "gpt-5-mini"), "local": False, "api": "responses"}
    base = os.environ.get("OPENAI_BASE_URL") or ensure_local_server()
    return {"base_url": base, "api_key": os.environ.get("OPENAI_API_KEY", "local"),
            "model": MODELO_LOCAL, "local": True, "api": "chat"}


if __name__ == "__main__":
    cfg = backend_config()
    print(cfg)
