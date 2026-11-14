"""Las tools se registran solas y su schema sale del docstring."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.registry import registrar


def test_registro_descubre_las_tools():
    t = registrar()
    assert {"consultar_factura", "consultar_plan", "buscar_documentacion", "reembolsar", "escalar_a_humano", "cambiar_modo", "cargar_skill"} <= set(t)


def test_side_effects_marcados():
    t = registrar()
    assert t["reembolsar"].side_effect and t["escalar_a_humano"].side_effect
    assert not t["consultar_factura"].side_effect


def test_docstring_es_schema():
    t = registrar()["reembolsar"]
    props = t.params_json_schema["properties"]
    assert "Folio" in props["folio"]["description"] and "pesos" in props["monto"]["description"]
    assert "ctx" not in props


def test_sandbox_de_leer_pagina():
    from tools.leer_pagina import url_permitida, texto_de_html
    assert not url_permitida("http://localhost:8011/")[0]
    assert not url_permitida("http://127.0.0.1/")[0]
    assert not url_permitida("ftp://example.com/")[0]
    assert texto_de_html("<html><head><title>Hola</title><script>x()</script></head><body><p>Texto <b>visible</b></p></body></html>") == ("Hola", "Texto visible")
