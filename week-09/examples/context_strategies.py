"""Semana 9. Tres estrategias de contexto sobre una conversación guionada de 30 turnos.

El asistente de soporte de Facturio atiende a un usuario durante 30 turnos con
tools. El usuario fija dos restricciones en el turno 2 (presupuesto máximo de
700 pesos al mes y su identificador u002). El turno 30 pide una recomendación
de plan que solo es correcta si la restricción de presupuesto sobrevivió.

Se comparan tres formas de construir el contexto que ve el modelo:

* A. Historial completo: todo lo dicho, siempre.
* B. Sliding window: los últimos N mensajes.
* C. Estado estructurado + resumen: la aplicación conserva un JSON con las
  restricciones y los pasos hechos, resume lo viejo y envía solo eso más los
  últimos mensajes.

Cada llamada registra tokens de entrada y salida (los que reporta la API, con
OpenAI o con el servidor local), latencia y tools ejecutadas.

Este archivo es el mismo código que embeben los notebooks de la semana.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------------------- backend
# Copia reducida de course/shared/local_server.py: OpenAI con llave, servidor local sin ella.
MODELO_LOCAL = "Qwen/Qwen2.5-1.5B-Instruct"
PUERTO = 8765


def _vivo(raiz: str) -> bool:
    try:
        with urllib.request.urlopen(f"{raiz}/health", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_local_server(modelo: str = MODELO_LOCAL, puerto: int = PUERTO, espera_s: int = 900) -> str:
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
        time.sleep(3)
    raise RuntimeError("el servidor local no respondió; revisa " + log.name)


def backend_config() -> dict:
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
        return {"base_url": None, "api_key": os.environ["OPENAI_API_KEY"],
                "model": os.environ.get("OPENAI_MODEL", "gpt-5-mini"), "local": False, "api": "responses"}
    base = os.environ.get("OPENAI_BASE_URL") or ensure_local_server()
    return {"base_url": base, "api_key": os.environ.get("OPENAI_API_KEY", "local"),
            "model": MODELO_LOCAL, "local": True, "api": "chat"}


# ----------------------------------------------------------------------------- tools (shared/facturio_tools.py)
def _cargar_tools():
    """Importa course/shared/facturio_tools.py si está en el repositorio; si no, lo descarga."""
    aqui = Path.cwd().resolve()
    for base in [aqui, *aqui.parents]:
        for cand in (base / "shared", base / "course" / "shared"):
            if (cand / "facturio_tools.py").exists():
                sys.path.insert(0, str(cand))
                import facturio_tools  # noqa
                return facturio_tools
    url = "https://raw.githubusercontent.com/JunBarrs24/itm-maestria-llms/main/shared/facturio_tools.py"
    destino = Path("facturio_tools.py")
    urllib.request.urlretrieve(url, destino)
    sys.path.insert(0, str(destino.parent.resolve()))
    import facturio_tools  # noqa
    return facturio_tools


ft = _cargar_tools()


def tools_chat() -> list[dict]:
    """Definiciones en formato Chat Completions (Responses API usa ft.tools_para_openai())."""
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                              "parameters": t["parameters"]}} for t in ft.tools_para_openai()]


# ----------------------------------------------------------------------------- registro de uso
@dataclass
class Llamada:
    etiqueta: str
    input_tokens: int
    output_tokens: int
    latencia_s: float
    tools: list[str] = field(default_factory=list)


@dataclass
class Registro:
    llamadas: list[Llamada] = field(default_factory=list)

    def totales(self) -> dict:
        n = len(self.llamadas)
        return {"llamadas": n, "input_tokens": sum(c.input_tokens for c in self.llamadas),
                "output_tokens": sum(c.output_tokens for c in self.llamadas),
                "latencia_s": round(sum(c.latencia_s for c in self.llamadas), 1),
                "costo_si_gpt5mini_usd": round(sum(c.input_tokens * 0.25 + c.output_tokens * 2.0 for c in self.llamadas) / 1e6, 5)}


# ----------------------------------------------------------------------------- cliente
SYSTEM = ("Eres el asistente de soporte de Facturio, un servicio de facturación electrónica. Respondes en español, "
          "en dos o tres oraciones. Usa las herramientas cuando necesites datos de cargos, planes o políticas. "
          "Respeta siempre las restricciones que el usuario haya dado en la conversación.")


RE_PRERUTA = [
    (re.compile(r"PAY-\d{8}|\bcargo\b|\bfolio\b|duplicad", re.I), "consultar_factura"),
    (re.compile(r"\bplan\b|l[ií]mite|cu[aá]ntas facturas|cu[aá]ntos usuarios|timbrad", re.I), "consultar_plan"),
    (re.compile(r"pol[ií]tica|reembolso|cancel|versi[oó]n|error E-|c[oó]digo|API|cabecera|sesi[oó]n|dos factores|"
                r"descuento|exportar|excel|invit|horario|transferencia|datos|administrador|incluye|cuesta|precio", re.I), "buscar_documentacion"),
]


def preruta(texto_usuario: str) -> str | None:
    """Regla determinista de la aplicación: qué tool corresponde a la pregunta, si alguna.

    Con OpenAI se deja al modelo elegir (tool_choice auto). Con el modelo local de 1.5B, que
    rara vez elige tools en preguntas en español, la aplicación fuerza la tool que la regla
    indica. Es el routing determinista de la semana 8 aplicado a la selección de tools."""
    for patron, tool in RE_PRERUTA:
        if patron.search(texto_usuario):
            return tool
    return None


class Cliente:
    def __init__(self, cfg: dict | None = None):
        from openai import OpenAI
        self.cfg = cfg or backend_config()
        self.client = OpenAI(base_url=self.cfg["base_url"], api_key=self.cfg["api_key"], timeout=600)
        self.model = self.cfg["model"]

    def completar(self, mensajes: list[dict], tools: bool = True, max_tokens: int = 160,
                  forzar_tool: str | None = None) -> tuple[dict, int, int]:
        """Una llamada. Devuelve (mensaje del asistente en formato chat, tokens_in, tokens_out).
        forzar_tool: nombre de la tool que la aplicación exige en esta llamada (solo se usa con el modelo local)."""
        if self.cfg["api"] == "chat":
            kw = dict(model=self.model, messages=mensajes, max_tokens=max_tokens)
            if tools:
                kw["tools"] = tools_chat()
                if forzar_tool and self.cfg["local"]:
                    kw["tool_choice"] = {"type": "function", "function": {"name": forzar_tool}}
            r = self.client.chat.completions.create(**kw)
            m = r.choices[0].message
            msg = {"role": "assistant", "content": m.content or ""}
            if m.tool_calls:
                msg["tool_calls"] = [{"id": t.id, "type": "function",
                                      "function": {"name": t.function.name, "arguments": t.function.arguments}}
                                     for t in m.tool_calls]
            return msg, r.usage.prompt_tokens, r.usage.completion_tokens
        # Responses API (OpenAI con llave). Sin ejecutar en el entorno de desarrollo.
        entrada = []
        for m in mensajes:
            if m["role"] == "system":
                continue
            if m["role"] == "tool":
                entrada.append({"type": "function_call_output", "call_id": m["tool_call_id"], "output": m["content"]})
            elif m.get("tool_calls"):
                for t in m["tool_calls"]:
                    entrada.append({"type": "function_call", "call_id": t["id"], "name": t["function"]["name"],
                                    "arguments": t["function"]["arguments"]})
            else:
                entrada.append({"role": m["role"], "content": m["content"]})
        kw = dict(model=self.model, input=entrada, instructions=SYSTEM, max_output_tokens=max_tokens)
        if tools:
            kw["tools"] = ft.tools_para_openai()
        # Reasoning models (gpt-5*, o*): gastan max_output_tokens en razonar; con "minimal" la respuesta
        # cabe en presupuestos pequeños. 
        # Ejercicio: probar: 
        # "none"    Sin razonamiento adicional. Menor latencia.
        # "minimal"    Razonamiento mínimo.
        # "low"    Razonamiento ligero.
        # "medium"    Razonamiento moderado.
        # "high"    Razonamiento profundo.
        # "xhigh"    Razonamiento muy profundo.
        # Summary: la cadena de razonamiento viaja cifrada (encrypted_content) y no se puede leer; se puede
        # pedir un resumen generado por el proveedor con reasoning["summary"]:
        # "auto"    El proveedor elige el nivel de detalle.
        # "concise"    Resumen breve.
        # "detailed"    Resumen paso a paso.
        # Ejemplo: params["reasoning"] = {"effort": "medium", "summary": "auto"}
        # Ver https://developers.openai.com/api/reference/resources/responses/methods/create#responses-create-reasoning
        # https://developers.openai.com/api/docs/models/gpt-5-mini (especifico de este modelo)
        # https://developers.openai.com/api/docs/guides/reasoning?api-mode=responses
        if self.model.startswith(("gpt-5", "o1", "o3", "o4")):
            kw["reasoning"] = {"effort": "minimal"}
        r = self.client.responses.create(**kw)
        msg = {"role": "assistant", "content": r.output_text or ""}
        calls = [o for o in r.output if getattr(o, "type", "") == "function_call"]
        if calls:
            msg["tool_calls"] = [{"id": c.call_id, "type": "function",
                                  "function": {"name": c.name, "arguments": c.arguments}} for c in calls]
        return msg, r.usage.input_tokens, r.usage.output_tokens


def _texto_contexto(mensajes: list[dict]) -> str:
    return "\n".join(str(m.get("content") or "") for m in mensajes)


def args_para(tool: str, texto_usuario: str, contexto: list[dict]) -> dict:
    """Argumentos que la aplicación deduce del mensaje y del contexto que la estrategia le dio.

    Si el identificador del usuario ya no está en el contexto (salió de la ventana), la tool
    recibe 'desconocido' y falla: es la misma pérdida que sufre el modelo, hecha visible."""
    visible = _texto_contexto(contexto)
    if tool == "consultar_factura":
        folios = re.findall(r"PAY-\d{8}", texto_usuario) or re.findall(r"PAY-\d{8}", visible)
        return {"folio": folios[-1] if folios else "PAY-00000000"}
    if tool == "consultar_plan":
        ids = re.findall(r"\bu\d{3}\b", visible)
        return {"usuario_id": ids[-1] if ids else "desconocido"}
    return {"pregunta": texto_usuario, "k": 2}


_contador_calls = [0]


def turno(cliente: Cliente, contexto: list[dict], registro: Registro, etiqueta: str,
          max_rondas: int = 2) -> tuple[str, list[dict]]:
    """Un turno del asistente: llama al modelo; si pide tools, las ejecuta y vuelve a llamar.
    Devuelve (texto final, mensajes nuevos que la aplicación debe registrar).

    Con el modelo local, la selección de tools la hace una regla determinista de la aplicación
    (preruta): el modelo de 1.5B rara vez pide tools en preguntas en español. Con OpenAI el
    modelo elige (tool_choice auto). En ambos casos la aplicación ejecuta y el resultado entra
    al contexto igual, que es lo que esta semana mide."""
    nuevos: list[dict] = []
    mensajes = list(contexto)
    ultimo_usuario = next((m["content"] for m in reversed(mensajes) if m["role"] == "user"), "")
    forzar = preruta(ultimo_usuario) if cliente.cfg["local"] else None
    if forzar:
        _contador_calls[0] += 1
        args = args_para(forzar, ultimo_usuario, mensajes)
        tc = {"id": f"call_{_contador_calls[0]:04d}", "type": "function",
              "function": {"name": forzar, "arguments": json.dumps(args, ensure_ascii=False)}}
        msg_tc = {"role": "assistant", "content": "", "tool_calls": [tc]}
        resultado = ft.ejecutar_tool(forzar, args)
        tm = {"role": "tool", "tool_call_id": tc["id"], "name": forzar,
              "content": json.dumps(resultado, ensure_ascii=False, default=str)}
        nuevos += [msg_tc, tm]
        mensajes += [msg_tc, tm]
        t0 = time.perf_counter()
        msg, ti, to = cliente.completar(mensajes, tools=False)
        registro.llamadas.append(Llamada(etiqueta, ti, to, time.perf_counter() - t0, [forzar]))
        nuevos.append(msg)
        return msg["content"], nuevos
    for ronda in range(max_rondas):
        t0 = time.perf_counter()
        msg, ti, to = cliente.completar(mensajes)
        lat = time.perf_counter() - t0
        usadas = []
        nuevos.append(msg)
        mensajes.append(msg)
        if not msg.get("tool_calls"):
            registro.llamadas.append(Llamada(etiqueta, ti, to, lat, usadas))
            return msg["content"], nuevos
        for tc in msg["tool_calls"]:
            nombre = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {}
            resultado = ft.ejecutar_tool(nombre, args)
            usadas.append(nombre)
            tm = {"role": "tool", "tool_call_id": tc["id"], "name": nombre, "content": json.dumps(resultado, ensure_ascii=False, default=str)}
            nuevos.append(tm)
            mensajes.append(tm)
        registro.llamadas.append(Llamada(etiqueta, ti, to, lat, usadas))
    # última llamada sin tools para cerrar el turno
    t0 = time.perf_counter()
    msg, ti, to = cliente.completar(mensajes, tools=False)
    registro.llamadas.append(Llamada(etiqueta, ti, to, time.perf_counter() - t0, []))
    nuevos.append(msg)
    return msg["content"], nuevos


# ----------------------------------------------------------------------------- guion de 30 turnos
PRESUPUESTO = 700
GUION: list[str] = [
    "Hola, tengo dudas sobre mi cuenta de Facturio.",
    f"Antes que nada: mi usuario es u002 y mi presupuesto máximo es {PRESUPUESTO} pesos al mes. No me propongan nada que pase de eso.",
    "¿Qué plan tengo ahora y cuántas facturas he timbrado este mes?",
    "¿Cuál es el límite de facturas de mi plan?",
    "Vi un cargo con folio PAY-00012348. ¿Qué es?",
    "¿Y el PAY-00012347 es el correcto entonces?",
    "¿Cuántos días tarda en revertirse un cargo duplicado?",
    "Perfecto. ¿Puedo exportar mis reportes a Excel con mi plan?",
    "¿Cómo invito a un usuario nuevo a mi cuenta?",
    "¿Cuántos usuarios puedo tener?",
    "Gracias. Otra cosa: ¿qué significa el error E-1042?",
    "¿Y cómo lo resuelvo?",
    "¿La API de Facturio tiene límite de peticiones?",
    "¿Qué cabecera se usa para autenticarse en la API?",
    "Ok. ¿Me recuerdas cuál era el folio del cargo duplicado?",
    "¿Cuánto tiempo dura una sesión antes de cerrarse sola?",
    "¿Y el código de dos factores cuánto dura?",
    "¿Cuál es la política de reembolso si cancelo a mitad de mes?",
    "¿Cuántos días tengo para pedir un reembolso?",
    "¿Puedo pagar con transferencia en vez de tarjeta?",
    "¿Hay descuento para instituciones educativas?",
    "¿Qué incluye el plan Empresa?",
    "¿Cuánto cuesta el plan Pro anual?",
    "¿Qué pasa con mis datos si elimino la cuenta?",
    "¿En qué versión se agregó la exportación a Excel?",
    "¿Puedo tener dos administradores?",
    "¿Cuál es el horario de soporte telefónico?",
    "Me estoy quedando cerca del límite de facturas. ¿Qué opciones tengo?",
    "¿Cuánto cuesta el plan Básico y cuánto el Pro al mes?",
    "Con todo lo que te dije, ¿qué plan me recomiendas contratar el mes que entra? Dame una recomendación concreta.",
]
TURNO_RESTRICCION = 2
TURNO_PRUEBA = 30


def restriccion_sobrevive(respuesta: str) -> dict:
    """Comprueba de forma determinista si la recomendación del turno 30 respeta el presupuesto.

    Dos señales: menciona el presupuesto (700 o la palabra presupuesto) y no recomienda
    el plan Pro (899 pesos) sin advertir que excede el límite."""
    t = respuesta.lower()
    # la señal fuerte es el número: "presupuesto" a secas también aparece cuando el modelo lo pregunta de nuevo
    menciona = str(PRESUPUESTO) in t
    recomienda_pro = bool(re.search(r"recomiend\w*[^.]{0,60}\bpro\b", t)) or ("plan pro" in t and "básico" not in t and "basico" not in t)
    advierte = any(k in t for k in ("excede", "supera", "pasa de", "fuera de tu presupuesto", "más de", "por encima"))
    return {"menciona_presupuesto": menciona, "recomienda_pro": recomienda_pro,
            "sobrevive": menciona and (not recomienda_pro or advierte)}


# ----------------------------------------------------------------------------- estrategias
class HistorialCompleto:
    nombre = "A. historial completo"

    def __init__(self):
        self.mensajes: list[dict] = [{"role": "system", "content": SYSTEM}]

    def contexto(self) -> list[dict]:
        return list(self.mensajes)

    def registrar(self, nuevos: list[dict]) -> None:
        self.mensajes.extend(nuevos)


class SlidingWindow(HistorialCompleto):
    def __init__(self, n_mensajes: int = 8):
        super().__init__()
        self.n = n_mensajes
        self.nombre = f"B. sliding window ({n_mensajes} mensajes)"

    def contexto(self) -> list[dict]:
        cuerpo = self.mensajes[1:]
        # no cortar entre una tool call y su resultado
        corte = max(0, len(cuerpo) - self.n)
        while corte > 0 and cuerpo[corte]["role"] == "tool":
            corte -= 1
        return [self.mensajes[0]] + cuerpo[corte:]


RE_PRESUPUESTO = re.compile(r"(?:presupuesto|máximo|maximo)[^\d]{0,40}(\d{3,5})\s*pesos", re.I)
RE_USUARIO = re.compile(r"\busuario (?:es )?(u\d{3})\b", re.I)


class EstadoEstructurado(HistorialCompleto):
    """La aplicación mantiene un estado JSON y envía al modelo: estado + resumen + últimos N mensajes.

    Keep: restricciones y datos exactos, extraídos con reglas deterministas, se conservan textuales.
    Compress: los mensajes viejos se resumen con el modelo.
    Drop: los tool outputs viejos no entran al resumen completos; solo lo que la regla decide guardar."""

    def __init__(self, cliente: Cliente, n_ventana: int = 6, keep: bool = True):
        super().__init__()
        self.cliente = cliente
        self.n = n_ventana
        self.keep = keep
        self.nombre = f"C. estado estructurado + resumen (ventana {n_ventana}, keep={'sí' if keep else 'no'})"
        self.estado = {"goal": "resolver dudas de soporte del usuario", "user_id": None, "constraints": [],
                       "completed_steps": [], "important_facts": {}}
        self.resumen = ""
        self.resumidos = 0  # cuántos mensajes del historial ya están dentro del resumen

    def registrar(self, nuevos: list[dict]) -> None:
        super().registrar(nuevos)
        for m in nuevos:
            if m["role"] == "user" and self.keep:
                for k in RE_PRESUPUESTO.findall(m["content"]):
                    c = f"presupuesto máximo {k} pesos al mes"
                    if c not in self.estado["constraints"]:
                        self.estado["constraints"].append(c)
                u = RE_USUARIO.search(m["content"])
                if u:
                    self.estado["user_id"] = u.group(1)
            if m["role"] == "tool" and self.keep:
                self.estado["completed_steps"].append(m["name"])
                try:
                    d = json.loads(m["content"])
                    if m["name"] == "consultar_plan" and "plan" in d:
                        self.estado["important_facts"]["plan_actual"] = d["plan"]
                    if m["name"] == "consultar_factura" and "estado" in d:
                        self.estado["important_facts"][d.get("folio", "folio")] = d["estado"]
                except json.JSONDecodeError:
                    pass

    def _compactar(self) -> None:
        cuerpo = self.mensajes[1:]
        viejos = cuerpo[self.resumidos:len(cuerpo) - self.n]
        if len(viejos) < 4:
            return
        texto = "\n".join(f"{m['role']}: {(m.get('content') or '')[:300]}" for m in viejos if m["role"] in ("user", "assistant"))
        instr = ("Resume en cinco líneas la siguiente conversación de soporte. Conserva datos exactos: folios, montos, "
                 "identificadores y restricciones del usuario.")
        msg, ti, to = self.cliente.completar([{"role": "system", "content": instr},
                                              {"role": "user", "content": (self.resumen + "\n" if self.resumen else "") + texto}],
                                             tools=False, max_tokens=180)
        self.resumen = msg["content"].strip()
        self.resumidos = len(cuerpo) - self.n

    def contexto(self) -> list[dict]:
        self._compactar()
        cuerpo = self.mensajes[1:]
        recientes = cuerpo[self.resumidos:]
        while recientes and recientes[0]["role"] == "tool":
            recientes = recientes[1:]
        bloque = SYSTEM + "\n\nEstado de la conversación (mantenido por la aplicación):\n" + json.dumps(self.estado, ensure_ascii=False)
        if self.estado["constraints"]:
            bloque += "\nRestricciones vigentes del usuario, respétalas y menciónalas al recomendar: " + "; ".join(self.estado["constraints"])
        if self.resumen:
            bloque += "\n\nResumen de lo anterior:\n" + self.resumen
        return [{"role": "system", "content": bloque}] + recientes


def correr(estrategia, cliente: Cliente, guion: list[str] = GUION, verbose: bool = False) -> dict:
    """Ejecuta el guion completo con una estrategia. Devuelve filas por turno y el veredicto del último."""
    registro = Registro()
    filas = []
    respuesta = ""
    for i, texto_usuario in enumerate(guion, start=1):
        estrategia.registrar([{"role": "user", "content": texto_usuario}])
        antes = len(registro.llamadas)
        respuesta, nuevos = turno(cliente, estrategia.contexto(), registro, f"t{i:02d}")
        estrategia.registrar(nuevos)
        llamadas = registro.llamadas[antes:]
        filas.append({"turno": i, "input_tokens": sum(c.input_tokens for c in llamadas),
                      "output_tokens": sum(c.output_tokens for c in llamadas),
                      "latencia_s": round(sum(c.latencia_s for c in llamadas), 2),
                      "tools": [t for c in llamadas for t in c.tools], "respuesta": respuesta})
        if verbose:
            print(f"[{i:02d}] {texto_usuario[:60]!r}\n     -> {respuesta[:160]!r}  tools={filas[-1]['tools']}  in={filas[-1]['input_tokens']}")
    veredicto = restriccion_sobrevive(respuesta)
    return {"estrategia": estrategia.nombre, "filas": filas, "respuesta_final": respuesta, "veredicto": veredicto,
            "totales": registro.totales(),
            "estado": getattr(estrategia, "estado", None), "resumen": getattr(estrategia, "resumen", None)}


# ----------------------------------------------------------------------------- tool output grande vs filtro
def tool_output_grande(usuario_id: str = "u002", n_facturas: int = 62) -> dict:
    """Simula la respuesta cruda de un sistema de facturación: el plan más el historial completo del mes."""
    base = ft.consultar_plan(usuario_id)
    base["historial_facturas"] = [
        {"folio": f"F-2026-{i:05d}", "fecha": f"2026-09-{1 + i % 6:02d}", "cliente_rfc": f"XAXX0101{i:06d}",
         "subtotal": round(1200 + (i * 37) % 900, 2), "iva": round((1200 + (i * 37) % 900) * 0.16, 2),
         "moneda": "MXN", "uso_cfdi": "G03" if i % 3 else "P01", "estatus": "timbrada" if i % 17 else "cancelada",
         "uuid": f"{i:08x}-0000-4000-8000-{i:012x}"}
        for i in range(n_facturas)]
    base["eventos"] = [{"tipo": "login", "ip": f"187.190.{i % 255}.{(i * 7) % 255}", "fecha": f"2026-09-0{1 + i % 6}"} for i in range(80)]
    return base


def normalizar_plan(crudo: dict) -> dict:
    """Lo que el modelo necesita para decidir: límites, uso y margen. Lo calcula código, antes de la llamada."""
    lim = crudo["limites"]
    timbradas = sum(1 for f in crudo.get("historial_facturas", []) if f["estatus"] == "timbrada")
    uso = crudo["uso"]["facturas_mes"] if "uso" in crudo else timbradas
    return {"plan": crudo["plan"], "precio_mensual": lim["precio"], "limite_facturas_mes": lim["facturas_mes"],
            "facturas_usadas": uso, "facturas_restantes": (lim["facturas_mes"] - uso) if lim["facturas_mes"] else None,
            "usuarios_max": lim["usuarios"], "excel": lim["excel"], "reembolso_ultimos_12m": crudo["reembolso_ultimos_12m"]}


def contar_tokens(texto: str) -> int:
    """Conteo con el tokenizer de Qwen si está disponible; si no, aproximación por caracteres."""
    try:
        from transformers import AutoTokenizer
        global _TOK
        try:
            _TOK
        except NameError:
            _TOK = AutoTokenizer.from_pretrained(MODELO_LOCAL)
        return len(_TOK(texto).input_ids)
    except Exception:
        return len(texto) // 4


# ----------------------------------------------------------------------------- memoria de largo plazo
class MemoriaLargoPlazo:
    """Hechos guardados como texto y recuperados por similitud. Misma idea que el retrieval de la semana 5."""

    def __init__(self, modelo: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.m = SentenceTransformer(modelo)
        self.hechos: list[str] = []
        self.emb = None

    def guardar(self, hecho: str) -> None:
        import numpy as np
        self.hechos.append(hecho)
        v = self.m.encode([hecho], normalize_embeddings=True)
        self.emb = v if self.emb is None else np.vstack([self.emb, v])

    def recuperar(self, consulta: str, k: int = 2) -> list[tuple[str, float]]:
        import numpy as np
        if self.emb is None:
            return []
        q = self.m.encode([consulta], normalize_embeddings=True)[0]
        s = self.emb @ q
        idx = np.argsort(-s)[:k]
        return [(self.hechos[i], float(s[i])) for i in idx]


# ----------------------------------------------------------------------------- resumen con y sin Keep
def resumir(cliente: Cliente, mensajes: list[dict], keep: list[str] | None = None) -> str:
    texto = "\n".join(f"{m['role']}: {m['content'][:300]}" for m in mensajes if m["role"] in ("user", "assistant"))
    instr = "Resume en tres líneas la siguiente conversación de soporte."
    msg, _, _ = cliente.completar([{"role": "system", "content": instr}, {"role": "user", "content": texto}], tools=False, max_tokens=150)
    resumen = msg["content"].strip()
    if keep:
        resumen = "KEEP (textual): " + " | ".join(keep) + "\n" + resumen
    return resumen


if __name__ == "__main__":
    cliente = Cliente()
    print("backend:", cliente.cfg["api"], cliente.model)
    guion = GUION[:6] + [GUION[-1]]  # versión corta para probar el mecanismo
    for est in (HistorialCompleto(), SlidingWindow(6), EstadoEstructurado(cliente, n_ventana=4)):
        r = correr(est, cliente, guion)
        print(f"\n{r['estrategia']}: tokens in {r['totales']['input_tokens']}, veredicto {r['veredicto']}")
        print("  final:", r["respuesta_final"][:200])
