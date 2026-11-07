"""Loop de agente mínimo para la mesa de soporte de Facturio (semana 10).

AGENTE = MODELO + CONTEXTO + ESTADO + HERRAMIENTAS + LOOP DE CONTROL

    observar -> decidir -> actuar -> observar

Dos ramas con la misma interfaz:

* `chat`: Chat Completions con tool calls. Sirve con OpenAI y con el servidor
  local (`transformers serve`), que es como se verificó este archivo.
* `responses`: Responses API con `previous_response_id`. Escrita contra el
  SDK openai 3.x, sin ejecutar en el entorno de desarrollo (sin llave).

Uso:

    from agent_loop import correr_agente, cargar_tools
    ft = cargar_tools()
    r = correr_agente("¿Cuánto cobró el cargo PAY-00012345?", max_iteraciones=6)
    print(r.respuesta, r.iteraciones, r.tool_calls)

La semana 11 sustituye este archivo por el Agents SDK; cada abstracción del
SDK corresponde a una pieza de aquí.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# ----------------------------------------------------------------------------- backend
MODELO_LOCAL = "Qwen/Qwen2.5-3B-Instruct"   # el de 1.5B no sostiene un loop con cinco tools
PUERTO_LOCAL = 8766


def _vivo(raiz: str) -> bool:
    try:
        with urllib.request.urlopen(f"{raiz}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_local_server(modelo: str = MODELO_LOCAL, puerto: int = PUERTO_LOCAL, espera_s: int = 600) -> str:
    """Arranca `transformers serve` si no está vivo y devuelve la base_url (copia de shared/local_server.py)."""
    import shutil
    import subprocess
    raiz = f"http://localhost:{puerto}"
    if _vivo(raiz):
        return raiz + "/v1"
    exe = shutil.which("transformers") or os.path.join(os.path.dirname(sys.executable), "transformers")
    log = open(os.path.join(os.environ.get("TMPDIR", "/tmp"), f"transformers-serve-{puerto}.log"), "a")
    subprocess.Popen([exe, "serve", "--port", str(puerto), modelo], stdout=log, stderr=subprocess.STDOUT,
                     start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < espera_s:
        if _vivo(raiz):
            return raiz + "/v1"
        time.sleep(2)
    raise RuntimeError("el servidor local no respondió")


def backend_config() -> dict:
    """Llave real -> OpenAI con Responses API. Sin llave -> servidor local con Chat Completions."""
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
        return {"base_url": None, "api_key": os.environ["OPENAI_API_KEY"],
                "model": os.environ.get("OPENAI_MODEL", "gpt-5-mini"), "local": False, "api": "responses"}
    base = os.environ.get("OPENAI_BASE_URL") or ensure_local_server()
    return {"base_url": base, "api_key": os.environ.get("OPENAI_API_KEY", "local"),
            "model": os.environ.get("OPENAI_MODEL", MODELO_LOCAL), "local": True, "api": "chat"}


# ----------------------------------------------------------------------------- tools
TOOLS_URL = "https://raw.githubusercontent.com/JunBarrs24/itm-maestria-llms/main/shared/facturio_tools.py"


def cargar_tools():
    """Importa shared/facturio_tools.py (local) o lo descarga (Colab)."""
    aqui = Path.cwd().resolve()
    for base in [Path(__file__).resolve().parent, aqui, *aqui.parents]:
        for cand in (base / "shared", base / "course" / "shared", base.parents[1] / "shared" if len(base.parents) > 1 else base):
            if (cand / "facturio_tools.py").exists():
                sys.path.insert(0, str(cand))
                import facturio_tools  # noqa
                return facturio_tools
    destino = Path("facturio_tools.py")
    if not destino.exists():
        with urllib.request.urlopen(TOOLS_URL, timeout=30) as r:
            destino.write_bytes(r.read())
    sys.path.insert(0, str(destino.parent.resolve()))
    import facturio_tools  # noqa
    return facturio_tools


def tools_chat(ft) -> list[dict]:
    """Del formato de Responses API al de Chat Completions."""
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                              "parameters": t["parameters"]}} for t in ft.tools_para_openai()]


# ----------------------------------------------------------------------------- estado y trace
INSTRUCCIONES = (
    "Asistente de la mesa de soporte de Facturio. Responde con los datos de las herramientas; nunca pidas al usuario "
    "datos que ya escribió (folio PAY-xxxxxxxx, usuario uNNN). Para un reembolso: consulta el cargo y luego llama a "
    "reembolsar con el monto del cargo y el motivo del usuario. Si la aplicación rechaza una acción, explica la razón "
    "o escala a una persona. Responde en español, en dos o tres oraciones, y termina cuando tengas la respuesta."
)


def primer_paso_determinista(objetivo: str):
    """Observación inicial decidida por código a partir de señales del texto. Devuelve (tool, args) o None.
    Es control que regresa al código: un modelo pequeño decide mejor cuando ya tiene la primera observación."""
    import re
    if m := re.search(r"PAY-\d{8}", objetivo):
        return "consultar_factura", {"folio": m.group(0)}
    if m := re.search(r"\bu\d{3}\b", objetivo):
        return "consultar_plan", {"usuario_id": m.group(0)}
    if re.search(r"pol[ií]tica|d[ií]as|plazo|error|E-\d{4}|c[oó]mo|qu[eé]|puedo|l[ií]mite|plan ", objetivo, re.I):
        return "buscar_documentacion", {"pregunta": objetivo}
    return None


def acotar_tools(objetivo: str) -> set:
    """Conjunto de tools pertinentes según señales deterministas del texto (context engineering de tools)."""
    import re
    t = set()
    if re.search(r"PAY-\d{8}", objetivo):
        t |= {"consultar_factura"}
    if re.search(r"\bu\d{3}\b", objetivo):
        t |= {"consultar_plan"}
    if re.search(r"reembols|devu[eé]lv|dinero|cobr", objetivo, re.I):
        t |= {"consultar_factura", "reembolsar", "escalar_a_humano"}
    if re.search(r"error|E-\d{4}|pol[ií]tica|d[ií]as|c[oó]mo|qu[eé] significa|plazo|puedo|l[ií]mite", objetivo, re.I):
        t |= {"buscar_documentacion"}
    return t or {"consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar", "escalar_a_humano"}


def estado_inicial(objetivo: str) -> dict:
    """Estado estructurado de la aplicación (semana 9). No es el contexto del modelo."""
    return {"objetivo": objetivo, "completed_steps": [], "pending_steps": [],
            "constraints": ["ningún side effect sin autorización de la aplicación"], "important_facts": {}}


def filtrar_tool_output(nombre: str, salida: dict, max_chars: int = 900) -> str:
    """Filtro determinista antes de que el resultado entre al contexto (semana 9)."""
    if nombre == "buscar_documentacion" and "fragmentos" in salida:
        salida = {"fragmentos": [{"archivo": f["archivo"], "seccion": f["seccion"], "texto": f["texto"][:300]}
                                 for f in salida["fragmentos"][:2]]}
    texto = json.dumps(salida, ensure_ascii=False)
    return texto[:max_chars]


@dataclass
class Paso:
    iteracion: int
    tipo: str                 # modelo | tool | aprobacion | stop
    detalle: str
    tokens_in: int = 0
    tokens_out: int = 0
    latencia_s: float = 0.0


@dataclass
class Resultado:
    respuesta: Optional[str]
    motivo_stop: str
    iteraciones: int
    pasos: list[Paso] = field(default_factory=list)
    tool_calls: list[tuple[str, dict, dict]] = field(default_factory=list)   # (nombre, args, resultado)
    tokens_in: int = 0
    tokens_out: int = 0
    latencia_s: float = 0.0
    estado: dict = field(default_factory=dict)

    def trace(self) -> str:
        lineas = []
        for p in self.pasos:
            extra = f"  ({p.tokens_in}+{p.tokens_out} tok, {p.latencia_s:.1f}s)" if p.tipo == "modelo" else ""
            lineas.append(f"[{p.iteracion}] {p.tipo:10s} {p.detalle}{extra}")
        return "\n".join(lineas)


# ----------------------------------------------------------------------------- el loop
def correr_agente(objetivo: str, ft=None, cfg: dict | None = None, max_iteraciones: int = 6,
                  aprobar: Optional[Callable[[str, dict], bool]] = None, instrucciones: str = INSTRUCCIONES,
                  max_tokens: int = 160, ejecutar: Optional[Callable] = None, tools_permitidas: Optional[set] = None,
                  estado: dict | None = None, timeout_s: float = 120.0,
                  primer_paso: Optional[Callable[[str], Optional[tuple]]] = None) -> Resultado:
    """Observar -> decidir -> actuar, hasta respuesta final o límite de iteraciones.

    aprobar(nombre, args) -> bool: se consulta antes de ejecutar una tool con side effect.
    ejecutar(nombre, args) -> dict: por defecto el dispatcher de facturio_tools (valida, timeout, retry).
    tools_permitidas: subconjunto de tools que el modelo ve (acotar por contexto).
    primer_paso(objetivo) -> (tool, args) | None: observación inicial decidida por código antes de la primera
        decisión del modelo. Cuenta como iteración 0 en el trace.
    """
    ft = ft or cargar_tools()
    cfg = cfg or backend_config()
    ejecutar = ejecutar or ft.ejecutar_tool
    estado = estado if estado is not None else estado_inicial(objetivo)
    from openai import OpenAI
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"], timeout=timeout_s)
    defs = [d for d in tools_chat(ft) if tools_permitidas is None or d["function"]["name"] in tools_permitidas]
    res = Resultado(respuesta=None, motivo_stop="", iteraciones=0, estado=estado)
    t_inicio = time.perf_counter()

    if cfg["api"] == "responses":
        return _loop_responses(client, cfg, objetivo, ft, defs, max_iteraciones, aprobar, instrucciones,
                               max_tokens, ejecutar, estado, res, t_inicio, primer_paso)

    mensajes = [{"role": "system", "content": instrucciones}, {"role": "user", "content": objetivo}]
    if primer_paso is not None and (pp := primer_paso(objetivo)):
        nombre0, args0 = pp
        salida0 = ejecutar(nombre0, args0)
        res.tool_calls.append((nombre0, args0, salida0))
        estado["completed_steps"].append(f"{nombre0}({args0}) [código]")
        if nombre0 == "consultar_factura" and "monto" in salida0:
            estado["important_facts"][args0.get("folio", "?")] = {"monto": salida0["monto"], "estado": salida0["estado"]}
        res.pasos.append(Paso(0, "tool", f"[código] {nombre0} {args0} -> {json.dumps(salida0, ensure_ascii=False)[:110]}"))
        mensajes.append({"role": "assistant", "content": "", "tool_calls": [{"id": "call_0", "type": "function",
                         "function": {"name": nombre0, "arguments": json.dumps(args0, ensure_ascii=False)}}]})
        mensajes.append({"role": "tool", "tool_call_id": "call_0", "content": filtrar_tool_output(nombre0, salida0)})
    for it in range(1, max_iteraciones + 1):
        res.iteraciones = it
        t0 = time.perf_counter()
        resp = client.chat.completions.create(model=cfg["model"], messages=mensajes, tools=defs,
                                              tool_choice="auto", max_tokens=max_tokens)
        dt = time.perf_counter() - t0
        msg = resp.choices[0].message
        u = resp.usage
        res.tokens_in += u.prompt_tokens; res.tokens_out += u.completion_tokens
        if not msg.tool_calls:                                   # DECIDIR: respuesta final
            res.pasos.append(Paso(it, "modelo", "respuesta final", u.prompt_tokens, u.completion_tokens, dt))
            res.respuesta = (msg.content or "").strip()
            res.motivo_stop = "respuesta_final"
            break
        nombres = [tc.function.name for tc in msg.tool_calls]
        res.pasos.append(Paso(it, "modelo", f"pide {nombres}", u.prompt_tokens, u.completion_tokens, dt))
        mensajes.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [{"id": tc.id, "type": "function",
                                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                        for tc in msg.tool_calls]})
        for tc in msg.tool_calls:                                # ACTUAR
            nombre = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_raw": tc.function.arguments}
            side_effect = ft.TOOLS.get(nombre, {}).get("side_effect", False)
            if side_effect and aprobar is not None:
                ok = aprobar(nombre, args)
                res.pasos.append(Paso(it, "aprobacion", f"{nombre} {args} -> {'aprobado' if ok else 'rechazado'}"))
                if not ok:
                    salida = {"ejecutado": False, "razon": "rechazado por la persona que supervisa"}
                    res.tool_calls.append((nombre, args, salida))
                    mensajes.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(salida, ensure_ascii=False)})
                    continue
            salida = ejecutar(nombre, args)
            res.tool_calls.append((nombre, args, salida))
            estado["completed_steps"].append(f"{nombre}({', '.join(f'{k}={v}' for k, v in args.items())})")
            if nombre == "consultar_factura" and "monto" in salida:
                estado["important_facts"][args.get("folio", "?")] = {"monto": salida["monto"], "estado": salida["estado"]}
            res.pasos.append(Paso(it, "tool", f"{nombre} {args} -> {json.dumps(salida, ensure_ascii=False)[:110]}"))
            mensajes.append({"role": "tool", "tool_call_id": tc.id, "content": filtrar_tool_output(nombre, salida)})  # OBSERVAR
    else:
        res.motivo_stop = "max_iteraciones"
        res.pasos.append(Paso(max_iteraciones, "stop", f"límite de {max_iteraciones} iteraciones alcanzado"))
    res.latencia_s = time.perf_counter() - t_inicio
    return res


def _loop_responses(client, cfg, objetivo, ft, defs, max_iteraciones, aprobar, instrucciones, max_tokens,
                    ejecutar, estado, res, t_inicio, primer_paso=None):
    """Misma máquina de estados con Responses API. La API guarda la conversación: cada vuelta envía
    solo los outputs de las tools y `previous_response_id`. Sin ejecutar en desarrollo (sin llave)."""
    tools = [t for t in ft.tools_para_openai() if any(t["name"] == d["function"]["name"] for d in defs)]
    entrada = objetivo
    previo = None
    if primer_paso is not None and (pp := primer_paso(objetivo)):
        # Responses API no acepta un tool output sin tool call previa: la observación inicial va como texto.
        nombre0, args0 = pp
        salida0 = ejecutar(nombre0, args0)
        res.tool_calls.append((nombre0, args0, salida0))
        estado["completed_steps"].append(f"{nombre0}({args0}) [código]")
        if nombre0 == "consultar_factura" and "monto" in salida0:
            estado["important_facts"][args0.get("folio", "?")] = {"monto": salida0["monto"], "estado": salida0["estado"]}
        res.pasos.append(Paso(0, "tool", f"[código] {nombre0} {args0} -> {json.dumps(salida0, ensure_ascii=False)[:110]}"))
        entrada = f"{objetivo}\n\n[Datos ya consultados por la aplicación con {nombre0}: {filtrar_tool_output(nombre0, salida0)}]"
    for it in range(1, max_iteraciones + 1):
        res.iteraciones = it
        t0 = time.perf_counter()
        # Reasoning models (gpt-5*, o*): esfuerzo mínimo para que cada vuelta del loop sea barata.
        # Ejercicio: subir a "low" o "medium" y medir iteraciones, tokens y task success.
        extra = {"reasoning": {"effort": "minimal"}} if cfg["model"].startswith(("gpt-5", "o1", "o3", "o4")) else {}
        resp = client.responses.create(model=cfg["model"], instructions=instrucciones, input=entrada, tools=tools,
                                       previous_response_id=previo, max_output_tokens=max_tokens, **extra)
        dt = time.perf_counter() - t0
        previo = resp.id
        res.tokens_in += resp.usage.input_tokens; res.tokens_out += resp.usage.output_tokens
        llamadas = [o for o in resp.output if getattr(o, "type", "") == "function_call"]
        if not llamadas:
            res.pasos.append(Paso(it, "modelo", "respuesta final", resp.usage.input_tokens, resp.usage.output_tokens, dt))
            res.respuesta = resp.output_text.strip()
            res.motivo_stop = "respuesta_final"
            break
        res.pasos.append(Paso(it, "modelo", f"pide {[c.name for c in llamadas]}", resp.usage.input_tokens, resp.usage.output_tokens, dt))
        entrada = []
        for c in llamadas:
            args = json.loads(c.arguments or "{}")
            if ft.TOOLS.get(c.name, {}).get("side_effect") and aprobar is not None and not aprobar(c.name, args):
                salida = {"ejecutado": False, "razon": "rechazado por la persona que supervisa"}
                res.pasos.append(Paso(it, "aprobacion", f"{c.name} {args} -> rechazado"))
            else:
                salida = ejecutar(c.name, args)
                estado["completed_steps"].append(f"{c.name}({args})")
                if c.name == "consultar_factura" and "monto" in salida:
                    estado["important_facts"][args.get("folio", "?")] = {"monto": salida["monto"], "estado": salida["estado"]}
                res.pasos.append(Paso(it, "tool", f"{c.name} {args} -> {json.dumps(salida, ensure_ascii=False)[:110]}"))
            res.tool_calls.append((c.name, args, salida))
            entrada.append({"type": "function_call_output", "call_id": c.call_id, "output": filtrar_tool_output(c.name, salida)})
    else:
        res.motivo_stop = "max_iteraciones"
        res.pasos.append(Paso(max_iteraciones, "stop", f"límite de {max_iteraciones} iteraciones alcanzado"))
    res.latencia_s = time.perf_counter() - t_inicio
    return res


# ----------------------------------------------------------------------------- idempotencia
_REGISTRO_IDEMPOTENCIA: dict[str, dict] = {}


def con_clave_de_idempotencia(nombre: str, args: dict, ejecutar: Callable, clave: Optional[str] = None) -> dict:
    """Si la misma clave ya se ejecutó, devuelve el resultado guardado sin repetir el side effect."""
    clave = clave or f"{nombre}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
    if clave in _REGISTRO_IDEMPOTENCIA:
        return {**_REGISTRO_IDEMPOTENCIA[clave], "repetido": True}
    salida = ejecutar(nombre, args)
    _REGISTRO_IDEMPOTENCIA[clave] = salida
    return salida


if __name__ == "__main__":
    ft = cargar_tools()
    cfg = backend_config()
    print("backend:", cfg["api"], cfg["model"])
    for objetivo in ["¿Cuánto cobró el cargo PAY-00012345 y de qué fue?",
                     "Reembolsa el cargo PAY-00012350 completo, no usé el servicio."]:
        ft.reiniciar_estado()
        r = correr_agente(objetivo, ft=ft, cfg=cfg, max_iteraciones=5, aprobar=lambda n, a: True,
                          tools_permitidas=acotar_tools(objetivo), primer_paso=primer_paso_determinista)
        print("\nOBJETIVO:", objetivo)
        print(r.trace())
        print("RESPUESTA:", r.respuesta, "| stop:", r.motivo_stop, "| tokens:", r.tokens_in, r.tokens_out, f"| {r.latencia_s:.1f}s")
        print("estado:", r.estado["completed_steps"], r.estado["important_facts"])
