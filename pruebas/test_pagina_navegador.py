"""La página con un navegador de verdad (Playwright sin ventana): lo que el HTML solo no puede decir. Sin Playwright
con su navegador en la máquina, se salta."""
import json
import urllib.request

import pytest

from test_pasos import servidor  # noqa: F401 — servidor es un fixture
from test_verifica_11 import _hay_navegador

pytestmark = pytest.mark.skipif(not _hay_navegador(), reason="sin Playwright con navegador en esta máquina")


@pytest.fixture()
def pagina():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        yield navegador.new_page(locale="es-MX")
        navegador.close()


def _reiniciar(url):
    urllib.request.urlopen(urllib.request.Request(url + "/control/reinicio", method="POST"), timeout=10).read()


def _textos(url):
    with urllib.request.urlopen(url + "/api/textos", timeout=10) as r:
        return json.loads(r.read())["textos"]


def _entrar(pagina, url):
    from playwright.sync_api import expect
    pagina.goto(url)
    pagina.fill("#cliente", "Marta")
    pagina.fill("#contrasena", "marta-practica")
    pagina.click("#form-entrada button[type=submit]")
    expect(pagina.locator("#catalogo")).to_be_visible()


@pytest.mark.parametrize("como", ["recargando", "sin_recargar"])
def test_tras_reiniciar_la_pagina_no_se_queda_con_una_sesion_muerta(servidor, pagina, como):  # noqa: F811
    """Control positivo: sin sesionVencida en app.js, la página se queda adentro (catálogo visible) con una sesión
    que la tienda ya no reconoce."""
    from playwright.sync_api import expect
    url, _ = servidor
    _entrar(pagina, url)
    _reiniciar(url)
    if como == "recargando":
        pagina.reload()
    else:
        pagina.click("#ver-pedidos")
    expect(pagina.locator("#entrada")).to_be_visible()
    expect(pagina.locator("#catalogo")).to_be_hidden()
    expect(pagina.locator("#mensaje")).to_have_text(_textos(url)["pagina.sesion_vencida"])
    assert pagina.evaluate("sessionStorage.getItem('token')") is None
    _entrar(pagina, url)                                   # y se puede volver a entrar


def test_la_contrasena_equivocada_no_cuenta_como_sesion_vencida(servidor, pagina):  # noqa: F811
    from playwright.sync_api import expect
    url, _ = servidor
    pagina.goto(url)
    pagina.fill("#cliente", "Marta")
    pagina.fill("#contrasena", "otra")
    pagina.click("#form-entrada button[type=submit]")
    expect(pagina.locator("#mensaje")).not_to_be_empty()
    assert pagina.locator("#mensaje").text_content() != _textos(url)["pagina.sesion_vencida"]
