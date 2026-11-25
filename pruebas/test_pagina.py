"""La página de la tienda: lo que el alumno ve en el navegador.

Sin navegador en la Mac: se revisan el HTML y el CSS. El chequeo con navegador (Playwright) va en
pruebas/medir-imagen.sh, adentro de la imagen.
"""
import re
from pathlib import Path

PAGINA = Path(__file__).resolve().parent.parent / "tienda" / "tienda" / "pagina"


def _reglas(css: str):
    """(selector, cuerpo) de cada regla del CSS, sin comentarios."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return [(s.strip(), c) for s, c in re.findall(r"([^{}]+)\{([^{}]*)\}", css)]


def test_lo_oculto_no_se_ve_aunque_su_clase_ponga_display():
    # Bug #3: «.quien { display: flex }» le ganaba al [hidden] del navegador, y el carrito, «Mis pedidos» y
    # «Salir» se veían antes de entrar. El [hidden] de la página tiene que ganarle a cualquier clase.
    reglas = _reglas((PAGINA / "estilo.css").read_text(encoding="utf-8"))
    ocultar = [c for s, c in reglas if "[hidden]" in [x.strip() for x in s.split(",")]]
    assert ocultar, "falta la regla [hidden] en estilo.css"
    assert re.search(r"display\s*:\s*none\s*!important", ocultar[0])


def test_cada_elemento_oculto_al_inicio_tiene_una_clase_o_id_que_existe():
    # Control positivo del de arriba: el HTML sí trae elementos ocultos con clase que pone display.
    html = (PAGINA / "index.html").read_text(encoding="utf-8")
    ocultos = re.findall(r"<(?:div|section)[^>]*\bhidden\b[^>]*>", html)
    assert len(ocultos) >= 4
    assert any('class="quien"' in o for o in ocultos)
