"""El `verifica 10` (L10 «La pasarela que tarda, falla o no contesta», newman): la colección del alumno sale verde con
la tienda limpia y la pasarela en aprueba, rechaza, no contesta y tarda 7 s, y roja con E7 y la pasarela tardando;
sin dirección, Marta, Luis ni contraseñas escritas a mano. pruebas/alumno/10 se arma con la colección que describió
educación (cinco peticiones, seis pruebas). Cada corrida completa tarda ~45 s."""
import json
import shutil
import urllib.request

import pytest

from test_pasos import _error, servidor  # noqa: F401 — servidor es un fixture
from test_verifica import ALUMNO, _errores, _verifica

pytestmark = pytest.mark.skipif(shutil.which("newman") is None, reason="sin newman en esta máquina")
COLECCION = "pasarela.postman_collection.json"


def _practica(tmp_path, cambiar=None):
    d = tmp_path / "practica"
    shutil.copytree(ALUMNO / "10", d)
    if cambiar:
        c = json.loads((d / COLECCION).read_text(encoding="utf-8"))
        cambiar(c)
        (d / COLECCION).write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    return d


def _v10(servidor, d):  # noqa: F811
    url, entorno = servidor
    return _verifica(url, entorno, d, "10")


def _item(c, nombre):
    return next(i for i in c["item"] if i["name"] == nombre)


def _pago_rapido(url):
    """Paga un pedido nuevo: si la pasarela quedó en «aprueba», contesta 200 enseguida."""
    def pedir(metodo, ruta, cuerpo=None, h=None):
        r = urllib.request.Request(url + ruta, method=metodo, data=json.dumps(cuerpo).encode() if cuerpo else None,
                                   headers={"Content-Type": "application/json", **(h or {})})
        with urllib.request.urlopen(r, timeout=10) as x:
            return x.status, json.loads(x.read())
    h = {"Authorization": "Bearer " + pedir("POST", "/api/sesiones",
                                           {"cliente": "Luis", "contrasena": "luis-practica"})[1]["token"]}
    pedir("PUT", "/api/carrito/productos/calcetines", {"cantidad": 1}, h)
    pid = pedir("POST", "/api/pedidos", None, h)[1]["id"]
    return pedir("POST", f"/api/pedidos/{pid}/pago", {"tarjeta": "4242424242424242"}, h)[0]


def test_verifica_10_verde_con_la_coleccion_de_la_leccion(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    codigo, salida = _v10(servidor, _practica(tmp_path))
    assert codigo == 0 and "🎉" in salida and "❌" not in salida, salida
    assert "todo sale del ambiente" in salida and "Luis" not in salida, salida
    assert salida.count("sale en verde (6)") == 4 and "tarda 7 segundos" in salida, salida
    assert "sale en rojo (1): tu colección encuentra el pedido cobrado y sin pagar" in salida, salida
    assert not any(_errores(url).values())
    assert _pago_rapido(url) == 200                    # la pasarela quedó en «aprueba»


def test_verifica_10_falta_el_ambiente(servidor, tmp_path):  # noqa: F811
    d = _practica(tmp_path)
    (d / "local.postman_environment.json").unlink()
    codigo, salida = _v10(servidor, d)
    assert codigo == 1 and "local.postman_environment.json" in salida, salida


def test_verifica_10_marta_escrita_a_mano(servidor, tmp_path):  # noqa: F811
    def a_mano(c):
        _item(c, "La clienta inicia sesión")["request"]["body"]["raw"] = \
            '{"cliente":"Marta","contrasena":"{{contrasena}}"}'
    codigo, salida = _v10(servidor, _practica(tmp_path, a_mano))
    assert codigo == 1 and "trae Marta escrito a mano" in salida, salida


def test_verifica_10_coleccion_que_solo_acepta_el_200(servidor, tmp_path):  # noqa: F811
    def solo_200(c):
        _item(c, "Paga")["event"][-1]["script"]["exec"] = ["pm.test('pagado', () => pm.response.to.have.status(200));"]
    codigo, salida = _v10(servidor, _practica(tmp_path, solo_200))
    assert codigo == 1 and "una pasarela que rechaza salieron 1 de 6 en rojo" in salida, salida


def test_verifica_10_coleccion_que_no_compara_estado_y_dinero(servidor, tmp_path):  # noqa: F811
    def sin_regla(c):
        item = _item(c, "Cómo quedó el pedido")
        item["event"][-1]["script"]["exec"] = [x for x in item["event"][-1]["script"]["exec"] if "si y solo si" not in x]
    codigo, salida = _v10(servidor, _practica(tmp_path, sin_regla))
    assert codigo == 1 and "ninguna prueba compara, después de esperar a la pasarela" in salida, salida


def test_verifica_10_coleccion_que_no_espera_a_la_pasarela(servidor, tmp_path):  # noqa: F811
    def sin_espera(c):
        _item(c, "Cómo quedó el pedido")["event"] = [e for e in _item(c, "Cómo quedó el pedido")["event"]
                                                      if e["listen"] != "prerequest"]
    codigo, salida = _v10(servidor, _practica(tmp_path, sin_espera))
    assert codigo == 1 and "ninguna prueba compara, después de esperar a la pasarela" in salida, salida


def test_verifica_10_respeta_los_errores_del_alumno(servidor, tmp_path):  # noqa: F811
    url, _ = servidor
    _error(url, "E3", True)
    try:
        codigo, salida = _v10(servidor, _practica(tmp_path))
        assert codigo == 0, salida
        assert _errores(url) == {"E1": False, "E2": False, "E3": True, "E4": False, "E5": False, "E6": False,
                                 "E7": False, "E8": False}
    finally:
        _error(url, "E3", False)
