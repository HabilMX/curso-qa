"""El `verifica 06` (L06 «Probar una API a mano»): la tienda anota las peticiones a /api desde el último reinicio
—quién, método, ruta, código y hora; nunca cuerpos, encabezados, contraseñas ni tokens— y el verifica busca ahí la
compra de Marta pagada por la API y los cinco errores de la hoja (401, 404, 422, 400, 409), en cualquier orden, y que
E1 haya quedado apagado."""
import json
import urllib.error
import urllib.request

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import _verifica


def _http(url, metodo, ruta, cuerpo=None, token=None, llave=None, crudo=None):
    h = {"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {}),
         **({"Idempotency-Key": llave} if llave else {})}
    datos = crudo if crudo is not None else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    try:
        with urllib.request.urlopen(urllib.request.Request(url + ruta, method=metodo, headers=h, data=datos),
                                    timeout=10) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, None


def _reiniciar(url):
    _http(url, "POST", "/control/reinicio")


def _compra(url, cliente="Marta", contrasena="marta-practica"):
    _, s = _http(url, "POST", "/api/sesiones", {"cliente": cliente, "contrasena": contrasena})
    token = s["token"]
    _http(url, "PUT", "/api/carrito/productos/playera-azul", {"cantidad": 1}, token)
    _, p = _http(url, "POST", "/api/pedidos", token=token)
    codigo, _ = _http(url, "POST", f"/api/pedidos/{p['id']}/pago", {"tarjeta": "4242 4242 4242 4242"}, token, "uno")
    assert codigo == 200
    return token, p["id"]


HOJA = ("401", "404", "422", "400", "409")


def _hoja(url, token, pedido, sin=()):
    hechos = {
        "401": lambda: _http(url, "GET", "/api/pedidos"),
        "404": lambda: _http(url, "GET", "/api/productos/zapatos"),
        "422": lambda: _http(url, "PUT", "/api/carrito/productos/playera-azul", {"cantidad": 0}, token),
        "400": lambda: _http(url, "PUT", "/api/carrito/productos/playera-azul", token=token, crudo=b'{"cantidad":'),
        "409": lambda: _http(url, "POST", f"/api/pedidos/{pedido}/pago", {"tarjeta": "4242 4242 4242 4242"}, token,
                             "dos"),
    }
    for c in reversed(HOJA):                      # en otro orden que la hoja: el orden no importa
        if c not in sin:
            assert str(hechos[c]()[0]) == c


def _v06(servidor, idioma="es"):  # noqa: F811
    url, entorno = servidor
    return _verifica(url, entorno, "/nada", "06", idioma)


def test_verifica_06_verde_con_la_practica_completa(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    codigo, salida = _v06(servidor)
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    assert salida.count("✅") == 8, salida


def test_verifica_06_recien_reiniciada_dice_que_el_registro_se_borro(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    codigo, salida = _v06(servidor)
    assert codigo == 1 and "`tienda reiniciar` borra el registro" in salida, salida


def test_verifica_06_reiniciar_borra_lo_hecho(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    _reiniciar(url)
    codigo, salida = _v06(servidor)
    assert codigo == 1 and "borra el registro" in salida, salida


@pytest.mark.parametrize("falta", HOJA)
def test_verifica_06_dice_cual_error_de_la_hoja_falta(servidor, falta):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido, sin=(falta,))
    codigo, salida = _v06(servidor)
    assert codigo == 1 and f"Falta el {falta}" in salida, salida
    assert salida.count("❌") == 1, salida


def test_verifica_06_la_compra_de_luis_no_cuenta(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url, "Luis", "luis-practica")
    _hoja(url, token, pedido)
    codigo, salida = _v06(servidor)
    assert codigo == 1 and "No encuentro un pago de Marta" in salida, salida


def test_verifica_06_E1_encendido(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    _error(url, "E1", True)
    try:
        codigo, salida = _v06(servidor)
    finally:
        _error(url, "E1", False)
    assert codigo == 1 and "El error E1 sigue encendido" in salida, salida


def test_el_registro_no_guarda_cuerpos_encabezados_ni_credenciales(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    _, registro = _http(url, "GET", "/control/peticiones")
    assert registro and all(set(r) == {"cliente", "metodo", "ruta", "codigo", "hora"} for r in registro)
    texto = json.dumps(registro)
    for secreto in (token, "marta-practica", "4242", "Bearer", "Idempotency", "cantidad"):
        assert secreto not in texto, secreto
    sin = [r for r in registro if r["ruta"] == "/api/pedidos" and r["codigo"] == 401]
    assert sin and sin[0]["cliente"] == "sin sesión"
    assert any(r["cliente"] == "Marta" and r["codigo"] == 409 for r in registro)
    assert not any(r["ruta"].startswith("/control") for r in registro)


@pytest.mark.parametrize("idioma", ["en", "fr", "pt", "bg"])
def test_verifica_06_habla_el_idioma_de_la_tienda(servidor, idioma):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    codigo, salida = _v06(servidor, idioma)
    assert codigo == 0 and salida.count("✅") == 8 and "Provocaste" not in salida and "Idempotency" not in salida, (idioma, salida)


def test_el_healthcheck_no_entra_al_registro_ni_borra_la_practica(servidor):  # noqa: F811
    """La imagen pide /api/salud cada 10 s; si se anotara, en ~14 h la práctica saldría del registro."""
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido)
    for _ in range(5100):
        _http(url, "GET", "/api/salud")
    _, registro = _http(url, "GET", "/control/peticiones")
    assert not any(r["ruta"] == "/api/salud" for r in registro)
    codigo, salida = _v06(servidor)
    assert codigo == 0 and salida.count("✅") == 8, salida


def test_verifica_06_un_404_de_otra_ruta_no_cuenta(servidor):  # noqa: F811
    url, _ = servidor
    _reiniciar(url)
    token, pedido = _compra(url)
    _hoja(url, token, pedido, sin=("404",))
    assert _http(url, "GET", "/api/productos/camisa-que-no-existe")[0] == 404
    codigo, salida = _v06(servidor)
    assert codigo == 1 and "Falta el 404" in salida, salida
