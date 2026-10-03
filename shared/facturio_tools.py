"""Tools de la mesa de soporte de Facturio (canónicas desde la semana 8).

Datos ficticios en memoria, schemas de argumentos con Pydantic, un dispatcher
con validación, timeout y retry, y la política de autorización de la
aplicación para la única tool con side effect (`reembolsar`).

Principio de la semana: el modelo puede pedir una tool; la aplicación decide
si la ejecuta. La autorización vive aquí, en código, y se aplica aunque el
modelo insista.
"""
from __future__ import annotations

import concurrent.futures
import re
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ValidationError

HOY = date(2026, 9, 4)  # fecha fija para que los ejemplos sean reproducibles

# ============================================================================ datos ficticios
USUARIOS: dict[str, dict] = {
    "u001": {"nombre": "Ana Torres", "correo": "ana.torres@example.com", "plan": "Básico",
             "facturas_mes": 41, "proyectos": 10, "reembolso_ultimos_12m": False},
    "u002": {"nombre": "Roberto Sánchez", "correo": "rsanchez@example.com", "plan": "Pro",
             "facturas_mes": 812, "proyectos": 23, "reembolso_ultimos_12m": False},
    "u003": {"nombre": "Escuela Técnica Morelia", "correo": "admin@etm.edu.mx", "plan": "Pro",
             "facturas_mes": 60, "proyectos": 4, "reembolso_ultimos_12m": False, "descuento": "educativo 40 %"},
    "u004": {"nombre": "Grupo Alfa SA de CV", "correo": "ti@grupoalfa.example.com", "plan": "Empresa",
             "facturas_mes": 5230, "proyectos": 118, "reembolso_ultimos_12m": False},
    "u005": {"nombre": "Luis Martínez", "correo": "lmartinez@example.com", "plan": "Básico",
             "facturas_mes": 0, "proyectos": 2, "reembolso_ultimos_12m": True},
}

LIMITES_PLAN = {
    "Básico": {"usuarios": 3, "proyectos": 10, "facturas_mes": 300, "excel": False, "precio": 599},
    "Pro": {"usuarios": 10, "proyectos": 50, "facturas_mes": 2000, "excel": True, "precio": 899},
    "Empresa": {"usuarios": None, "proyectos": None, "facturas_mes": None, "excel": True, "precio": None},
}

# Cargos de suscripción. `facturas_timbradas_periodo` decide reembolso completo o proporcional.
CARGOS: dict[str, dict] = {
    "PAY-00012345": {"usuario": "u001", "monto": 599.00, "fecha": date(2026, 8, 28), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 0, "estado": "cobrado"},
    "PAY-00012346": {"usuario": "u001", "monto": 599.00, "fecha": date(2026, 7, 28), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 37, "estado": "cobrado"},
    "PAY-00012347": {"usuario": "u002", "monto": 899.00, "fecha": date(2026, 8, 30), "concepto": "Pro mensual",
                     "facturas_timbradas_periodo": 12, "estado": "cobrado"},
    "PAY-00012348": {"usuario": "u002", "monto": 899.00, "fecha": date(2026, 8, 30), "concepto": "Pro mensual",
                     "facturas_timbradas_periodo": 0, "estado": "duplicado_detectado", "duplicado_de": "PAY-00012347"},
    "PAY-00012349": {"usuario": "u003", "monto": 539.40, "fecha": date(2026, 8, 25), "concepto": "Pro mensual (educativo)",
                     "facturas_timbradas_periodo": 9, "estado": "cobrado"},
    "PAY-00012350": {"usuario": "u004", "monto": 12500.00, "fecha": date(2026, 8, 28), "concepto": "Empresa mensual",
                     "facturas_timbradas_periodo": 4100, "estado": "cobrado"},
    "PAY-00012351": {"usuario": "u005", "monto": 599.00, "fecha": date(2026, 8, 29), "concepto": "Básico mensual",
                     "facturas_timbradas_periodo": 0, "estado": "cobrado"},
    "PAY-00012352": {"usuario": "u002", "monto": 8990.00, "fecha": date(2026, 9, 1), "concepto": "Pro anual",
                     "facturas_timbradas_periodo": 3, "estado": "cobrado"},
}

REEMBOLSOS: dict[str, dict] = {}      # folio -> reembolso aplicado (para idempotencia)
TICKETS_HUMANOS: list[dict] = []      # escalaciones creadas

# ============================================================================ schemas de argumentos
class ArgsConsultarFactura(BaseModel):
    folio: str = Field(description="Folio de pago, formato PAY- seguido de 8 dígitos")


class ArgsConsultarPlan(BaseModel):
    usuario_id: str = Field(description="Identificador del usuario, por ejemplo u001")


class ArgsBuscarDocumentacion(BaseModel):
    pregunta: str = Field(description="Pregunta en lenguaje natural sobre políticas o funciones de Facturio")
    k: int = Field(default=3, ge=1, le=5)


class ArgsReembolsar(BaseModel):
    folio: str
    monto: float = Field(gt=0)
    motivo: str


class ArgsEscalar(BaseModel):
    motivo: str
    folio: Optional[str] = None


# ============================================================================ tools
def consultar_factura(folio: str) -> dict:
    """Solo lectura. Devuelve el cargo o un error si no existe."""
    if not re.fullmatch(r"PAY-\d{8}", folio):
        return {"error": "folio inválido: el formato es PAY- seguido de 8 dígitos"}
    c = CARGOS.get(folio)
    if not c:
        return {"error": f"no existe el folio {folio}"}
    return {"folio": folio, "usuario": c["usuario"], "monto": c["monto"], "fecha": c["fecha"].isoformat(),
            "concepto": c["concepto"], "facturas_timbradas_periodo": c["facturas_timbradas_periodo"],
            "estado": c["estado"], "dias_desde_el_cargo": (HOY - c["fecha"]).days,
            **({"duplicado_de": c["duplicado_de"],
                "politica": "cargo duplicado: la reversión es automática en 5 días hábiles sin solicitud; "
                            "si no se refleja, abrir ticket con el folio"} if "duplicado_de" in c else {})}


def consultar_plan(usuario_id: str) -> dict:
    """Solo lectura. Plan, límites y uso del mes."""
    u = USUARIOS.get(usuario_id)
    if not u:
        return {"error": f"no existe el usuario {usuario_id}"}
    lim = LIMITES_PLAN[u["plan"]]
    return {"usuario_id": usuario_id, "nombre": u["nombre"], "plan": u["plan"], "limites": lim,
            "uso": {"facturas_mes": u["facturas_mes"], "proyectos": u["proyectos"]},
            "reembolso_ultimos_12m": u["reembolso_ultimos_12m"], **({"descuento": u["descuento"]} if "descuento" in u else {})}


# ---- retrieval sobre el corpus (la primera "herramienta" del curso, ahora pedida por el modelo)
_CORPUS: list[dict] = []
_EMB = None
_MODELO_EMB = None
CORPUS_URL = "https://raw.githubusercontent.com/JunBarrs24/itm-maestria-llms/main/shared/datasets/corpus/"
CORPUS_ARCHIVOS = ["01-manual-facturacion-cfdi.md", "02-manual-usuarios-e-invitaciones.md",
                   "03-manual-reportes-y-exportacion.md", "04-manual-integraciones-y-api.md",
                   "05-preguntas-frecuentes.md", "06-politica-reembolsos-y-cargos.md",
                   "07-politica-cancelacion-y-eliminacion.md", "08-terminos-del-servicio-y-sla.md",
                   "09-catalogo-codigos-de-error.md", "10-notas-de-version.md", "11-guia-de-seguridad.md",
                   "12-comunicado-externo.md"]


def _localizar_corpus() -> Optional[Path]:
    aqui = Path.cwd().resolve()
    for base in [aqui, *aqui.parents]:
        cand = base / "shared" / "datasets" / "corpus"
        if cand.exists():
            return cand
        cand = base / "course" / "shared" / "datasets" / "corpus"
        if cand.exists():
            return cand
    return None


def _leer_corpus() -> list[tuple[str, str]]:
    ruta = _localizar_corpus()
    if ruta:
        return [(a, (ruta / a).read_text(encoding="utf-8")) for a in CORPUS_ARCHIVOS if (ruta / a).exists()]
    import urllib.request
    docs = []
    for a in CORPUS_ARCHIVOS:
        with urllib.request.urlopen(CORPUS_URL + a, timeout=30) as r:
            docs.append((a, r.read().decode("utf-8")))
    return docs


def _chunks_por_seccion(nombre: str, texto: str) -> list[dict]:
    chunks, seccion, buf = [], None, []
    for line in texto.splitlines():
        m = re.match(r"^(#{2,3})\s+(.*)", line)
        if m:
            if buf and seccion:
                chunks.append({"archivo": nombre, "seccion": seccion, "texto": "\n".join(buf).strip()})
            seccion, buf = m.group(2).strip(), [line]
        else:
            buf.append(line)
    if buf and seccion:
        chunks.append({"archivo": nombre, "seccion": seccion, "texto": "\n".join(buf).strip()})
    return chunks


def preparar_corpus():
    """Indexa el corpus una sola vez (chunking por sección + embeddings)."""
    global _CORPUS, _EMB, _MODELO_EMB
    if _EMB is not None:
        return len(_CORPUS)
    from sentence_transformers import SentenceTransformer
    for nombre, texto in _leer_corpus():
        _CORPUS.extend(_chunks_por_seccion(nombre, texto))
    _MODELO_EMB = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    _EMB = _MODELO_EMB.encode([c["texto"] for c in _CORPUS], normalize_embeddings=True, batch_size=32)
    return len(_CORPUS)


def buscar_documentacion(pregunta: str, k: int = 3) -> dict:
    """Solo lectura. Devuelve los k fragmentos más parecidos, con archivo y sección."""
    import numpy as np
    preparar_corpus()
    v = _MODELO_EMB.encode([pregunta], normalize_embeddings=True)[0]
    idx = np.argsort(-(_EMB @ v))[:k]
    return {"fragmentos": [{"archivo": _CORPUS[i]["archivo"], "seccion": _CORPUS[i]["seccion"],
                            "texto": _CORPUS[i]["texto"][:600], "score": round(float(_EMB[i] @ v), 3)} for i in idx]}


# ---- la tool con side effect y su autorización
PLAZO_REEMBOLSO_DIAS = 14          # política de Facturio
MONTO_MAXIMO_SIN_HUMANO = 1000.0   # política de la aplicación: arriba de esto aprueba una persona


def autorizar_reembolso(folio: str, monto: float) -> tuple[bool, str]:
    """Decisión de la APLICACIÓN. No depende de lo que el modelo haya dicho."""
    c = CARGOS.get(folio)
    if not c:
        return False, f"no existe el folio {folio}"
    if folio in REEMBOLSOS:
        return False, f"el folio {folio} ya fue reembolsado (idempotencia)"
    if c["estado"] == "duplicado_detectado":
        return False, "cargo duplicado: la reversión es automática en 5 días hábiles, no se reembolsa por esta vía"
    dias = (HOY - c["fecha"]).days
    if dias > PLAZO_REEMBOLSO_DIAS:
        return False, f"fuera de plazo: {dias} días desde el cargo, el límite es {PLAZO_REEMBOLSO_DIAS}"
    u = USUARIOS[c["usuario"]]
    if u["reembolso_ultimos_12m"]:
        return False, "la cuenta ya recibió un reembolso en los últimos 12 meses"
    maximo = c["monto"] if c["facturas_timbradas_periodo"] == 0 else round(c["monto"] * (30 - dias) / 30, 2)
    if monto > maximo + 0.01:
        return False, f"monto mayor al permitido: máximo {maximo:.2f} (proporcional si hubo facturas timbradas)"
    if monto > MONTO_MAXIMO_SIN_HUMANO:
        return False, f"requiere aprobación humana: {monto:.2f} supera el límite automático de {MONTO_MAXIMO_SIN_HUMANO:.0f}"
    return True, "autorizado"


def reembolsar(folio: str, monto: float, motivo: str) -> dict:
    """SIDE EFFECT: mueve dinero. Solo se ejecuta si la aplicación autoriza."""
    ok, razon = autorizar_reembolso(folio, monto)
    if not ok:
        return {"ejecutado": False, "razon": razon}
    ref = f"REF-{uuid.uuid4().hex[:8].upper()}"
    REEMBOLSOS[folio] = {"referencia": ref, "monto": monto, "motivo": motivo, "fecha": HOY.isoformat()}
    USUARIOS[CARGOS[folio]["usuario"]]["reembolso_ultimos_12m"] = True
    return {"ejecutado": True, "referencia": ref, "monto": monto, "abono_en": "5 a 10 días hábiles"}


def escalar_a_humano(motivo: str, folio: Optional[str] = None) -> dict:
    t = {"ticket": f"HUM-{len(TICKETS_HUMANOS) + 1:04d}", "motivo": motivo, "folio": folio}
    TICKETS_HUMANOS.append(t)
    return t


def reiniciar_estado():
    """Deja los datos como al inicio (útil entre experimentos)."""
    REEMBOLSOS.clear()
    TICKETS_HUMANOS.clear()
    for u in USUARIOS.values():
        u["reembolso_ultimos_12m"] = False
    USUARIOS["u005"]["reembolso_ultimos_12m"] = True


# ============================================================================ catálogo y dispatcher
TOOLS: dict[str, dict] = {
    "consultar_factura": {"fn": consultar_factura, "args": ArgsConsultarFactura, "side_effect": False,
                          "descripcion": "Consulta un cargo de suscripción por folio PAY-xxxxxxxx."},
    "consultar_plan": {"fn": consultar_plan, "args": ArgsConsultarPlan, "side_effect": False,
                       "descripcion": "Consulta plan, límites y uso del mes de un usuario."},
    "buscar_documentacion": {"fn": buscar_documentacion, "args": ArgsBuscarDocumentacion, "side_effect": False,
                             "descripcion": "Busca en la documentación y políticas de Facturio."},
    "reembolsar": {"fn": reembolsar, "args": ArgsReembolsar, "side_effect": True,
                   "descripcion": "Reembolsa un cargo. Requiere autorización de la aplicación."},
    "escalar_a_humano": {"fn": escalar_a_humano, "args": ArgsEscalar, "side_effect": True,
                         "descripcion": "Crea un ticket para que una persona atienda el caso."},
}
NOMBRES_TOOLS = tuple(TOOLS.keys())


class SolicitudTool(BaseModel):
    """Lo que el modelo devuelve cuando decide usar una herramienta (emulación con structured output)."""
    tool: Literal["consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar",
                  "escalar_a_humano", "ninguna"]
    args: dict[str, Any] = Field(default_factory=dict)
    razon: str = ""


def descripcion_tools() -> str:
    lineas = []
    for n, t in TOOLS.items():
        props = t["args"].model_json_schema()["properties"]
        campos = ", ".join(f"{k}: {v.get('type') or '|'.join(a.get('type', '?') for a in v.get('anyOf', []))}" for k, v in props.items())
        lineas.append(f"- {n}({campos}): {t['descripcion']}" + (" [side effect]" if t["side_effect"] else ""))
    return "\n".join(lineas)


def tools_para_openai() -> list[dict]:
    """Definiciones en el formato de function calling de Responses API."""
    defs = []
    for n, t in TOOLS.items():
        schema = t["args"].model_json_schema()
        schema["additionalProperties"] = False
        defs.append({"type": "function", "name": n, "description": t["descripcion"], "parameters": schema, "strict": False})
    return defs


class ErrorDeTool(Exception):
    pass


def ejecutar_tool(nombre: str, args: dict, timeout_s: float = 5.0, reintentos: int = 2, backoff_s: float = 0.2,
                  fn_override=None) -> dict:
    """Valida los argumentos, ejecuta con timeout y reintenta errores transitorios con backoff.
    Devuelve siempre un dict serializable, con la clave 'error' si algo falló."""
    if nombre not in TOOLS:
        return {"error": f"tool desconocida: {nombre}"}
    t = TOOLS[nombre]
    try:
        validados = t["args"](**args)
    except ValidationError as e:
        return {"error": "argumentos inválidos", "detalle": str(e)[:300]}
    fn = fn_override or t["fn"]
    ultimo_error = None
    for intento in range(1, reintentos + 2):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(fn, **validados.model_dump())
                return fut.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError:
            ultimo_error = f"timeout tras {timeout_s} s (intento {intento})"
        except ErrorDeTool as e:
            ultimo_error = f"{e} (intento {intento})"
        if intento <= reintentos:
            time.sleep(backoff_s * (2 ** (intento - 1)))
    return {"error": ultimo_error, "intentos": reintentos + 1}
