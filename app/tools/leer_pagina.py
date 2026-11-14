"""Tool propia: descarga una página y devuelve su texto, con un sandbox ligero.

Es lo que una búsqueda hospedada no da: control de qué se abre y qué entra al contexto. El sandbox
son cuatro reglas en código: solo http(s); nunca hosts privados ni localhost (SSRF); tiempo y tamaño
máximos; y el texto se recorta antes de entrar al contexto (tool output compression, semana 8).
"""
from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlparse

import httpx

from tools.registry import function_tool, progreso

MAX_BYTES = 2_000_000
MAX_CARACTERES = 4000
TIMEOUT_S = 10.0


def url_permitida(url: str) -> tuple[bool, str]:
    """Reglas del sandbox, como función pura para probarlas sin red."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False, "solo se abren URLs http o https"
    host = u.hostname.lower()
    if host in ("localhost",) or host.endswith(".local") or host.endswith(".internal"):
        return False, "no se abren hosts locales"
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
    except (socket.gaierror, ValueError):
        return False, f"no se pudo resolver {host}"
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
        return False, "no se abren direcciones privadas"
    return True, "ok"


def texto_de_html(html: str) -> tuple[str, str]:
    """Título y texto visible, sin scripts, estilos ni etiquetas. Suficiente para leer; no es un parser."""
    titulo = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    cuerpo = re.sub(r"<(head|script|style|noscript|svg)[^>]*>.*?</\1>", " ", html, flags=re.I | re.S)
    cuerpo = re.sub(r"<[^>]+>", " ", cuerpo)
    cuerpo = re.sub(r"&nbsp;|&#160;", " ", cuerpo)
    cuerpo = re.sub(r"\s+", " ", cuerpo).strip()
    return (titulo.group(1).strip() if titulo else ""), cuerpo


@progreso("Leyendo la página…")
@function_tool
def leer_pagina(url: str) -> dict:
    """Descarga una página web y devuelve su título y su texto visible.

    Úsala después de buscar_web cuando necesites el contenido completo de una fuente (una política,
    un artículo, una tabla de precios) y no solo el resumen de la búsqueda. Devuelve como máximo
    4,000 caracteres; si la página es más larga, dilo y cita lo que sí leíste.

    Args:
        url: La dirección completa, con http o https, por ejemplo https://www.sat.gob.mx/.
    """
    ok, razon = url_permitida(url)
    if not ok:
        return {"error": razon}
    try:
        with httpx.Client(timeout=TIMEOUT_S, follow_redirects=True, headers={"User-Agent": "FacturioSoporte/1.0 (curso)"}) as c:
            r = c.get(url)
    except httpx.HTTPError as e:
        return {"error": f"no se pudo abrir la página: {type(e).__name__}"}
    if r.status_code >= 400:
        return {"error": f"la página respondió {r.status_code}"}
    if "html" not in r.headers.get("content-type", "") and "text" not in r.headers.get("content-type", ""):
        return {"error": f"contenido no textual: {r.headers.get('content-type', '?')}"}
    titulo, texto = texto_de_html(r.content[:MAX_BYTES].decode(r.encoding or "utf-8", errors="replace"))
    return {"url": str(r.url), "titulo": titulo, "caracteres_totales": len(texto),
            "texto": texto[:MAX_CARACTERES], "recortado": len(texto) > MAX_CARACTERES}
