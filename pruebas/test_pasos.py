"""El catálogo de pasos contra una tienda de verdad (un uvicorn en un puerto libre).

Corre los escenarios de muestra —las mismas frases de las lecciones 01 y 02— dos veces: con la tienda limpia
tienen que salir verdes, y con E1 encendido el de envío tiene que salir rojo. Es el mismo control que hará el
`verifica` con las pruebas del alumno.
"""

import json
import re
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
ESCENARIOS = Path(__file__).parent / "escenarios"


@pytest.fixture(scope="module")
def servidor(tmp_path_factory):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
    entorno = {**os.environ, "TIENDA_DATOS": str(tmp_path_factory.mktemp("tienda") / "tienda.db"),
               "PYTHONPATH": str(RAIZ / "tienda")}
    proceso = subprocess.Popen([sys.executable, "-m", "uvicorn", "tienda.api:app", "--host", "127.0.0.1",
                                "--port", str(puerto), "--log-level", "warning"], env=entorno)
    url = f"http://127.0.0.1:{puerto}"
    for _ in range(100):
        try:
            urllib.request.urlopen(url + "/api/salud", timeout=1)
            break
        except OSError:
            time.sleep(0.1)
    else:
        proceso.kill()
        pytest.fail("la tienda no arrancó")
    yield url, entorno
    proceso.terminate()
    proceso.wait(10)


def _error(url, e, encendido):
    peticion = urllib.request.Request(f"{url}/control/errores/{e}", method="PUT",
                                      data=json.dumps({"encendido": encendido}).encode(),
                                      headers={"Content-Type": "application/json"})
    urllib.request.urlopen(peticion, timeout=5)


def _behave(url, entorno, *archivos):
    r = subprocess.run([sys.executable, "-m", "behave", "--no-capture", "--format", "plain", "--no-color",
                        *[str(ESCENARIOS / a) for a in archivos]],
                       cwd=ESCENARIOS, env={**entorno, "TIENDA_URL": url}, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_escenarios_de_las_lecciones_salen_verdes_con_la_tienda_limpia(servidor):
    url, entorno = servidor
    codigo, salida = _behave(url, entorno, "cupon.feature", "envio.feature", "piezas_y_meses.feature")
    assert codigo == 0, salida
    assert re.search(r"\b25 scenarios passed, 0 failed, 0 skipped", salida), salida
    assert "undefined" not in salida, salida


def test_con_e1_encendido_el_escenario_de_envio_sale_rojo(servidor):
    url, entorno = servidor
    _error(url, "E1", True)
    try:
        codigo, salida = _behave(url, entorno, "envio.feature")
    finally:
        _error(url, "E1", False)
    assert codigo != 0, salida
    assert "1 failed" in salida and "la tienda mostró un envío de $99.00, no de $0.00" in salida, salida


def test_armar_un_carrito_exacto():
    sys.path.insert(0, str(RAIZ / "tienda"))
    from pasos_tienda import armar

    precios = {"a": 33300, "g": 33299, "e": 1}
    assert armar(precios, 99898) == {"a": 1, "g": 2}
    assert armar({"a": 33300}, 100) is None


# Los montos que las lecciones 01 y 02 y la especificación ponen en un «productos por …», con sus vecinos.
MONTOS_DE_LAS_LECCIONES = ["$480.00", "$499.99", "$500.00", "$500.01", "$600.00", "$998.98", "$998.99", "$999.00",
                           "$999.01", "$1,110.00", "$1,200.00", "$2,999.98", "$2,999.99", "$3,000.00", "$3,000.01",
                           "$49,999.99", "$50,000.00", "$50,000.01", "$50,000.02"]


def test_el_catalogo_arma_cada_monto_de_las_lecciones():
    sys.path.insert(0, str(RAIZ / "tienda"))
    from pasos_tienda import armar, centavos

    from tienda.datos import CATALOGO
    precios = {pid: precio for pid, _, precio, _ in CATALOGO}
    imposibles = [m for m in MONTOS_DE_LAS_LECCIONES if armar(precios, centavos(m)) is None]
    assert not imposibles, f"el catálogo no arma: {imposibles}"


# ---------------------------------------------------------------- el `verifica 00` y el comando `tienda`

def _bin(url, entorno, *args):
    r = subprocess.run([sys.executable, str(RAIZ / "tienda" / "bin" / args[0]), *args[1:]],
                       env={**entorno, "TIENDA_URL": url}, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _api(url, metodo, ruta, cuerpo=None, token="", llave=""):
    cabeza = {"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {}),
              **({"Idempotency-Key": llave} if llave else {})}
    peticion = urllib.request.Request(url + ruta, method=metodo, headers=cabeza,
                                      data=None if cuerpo is None else json.dumps(cuerpo).encode())
    with urllib.request.urlopen(peticion, timeout=10) as r:
        return json.loads(r.read())


def test_verifica_00_rojo_sin_compra_y_verde_con_ella(servidor):
    url, entorno = servidor
    assert _bin(url, entorno, "tienda", "reiniciar")[0] == 0
    codigo, salida = _bin(url, entorno, "verifica", "00")
    assert codigo == 1 and "❌ Marta tiene un pedido pagado" in salida, salida
    assert "✅ La API de la tienda contesta" in salida and "✅ La página de la tienda carga" in salida, salida

    token = _api(url, "POST", "/api/sesiones", {"cliente": "Marta", "contrasena": "marta-practica"})["token"]
    _api(url, "PUT", "/api/carrito/productos/sudadera", {"cantidad": 1}, token)
    pedido = _api(url, "POST", "/api/pedidos", None, token)
    codigo, salida = _bin(url, entorno, "verifica", "00")
    assert codigo == 1 and "ninguno está pagado" in salida, salida

    _api(url, "POST", f"/api/pedidos/{pedido['id']}/pago", {"tarjeta": "4242424242424242"}, token, "v00")
    codigo, salida = _bin(url, entorno, "verifica", "00")
    assert codigo == 0 and "🎉" in salida, salida


def test_verifica_sin_tienda_dice_como_levantarla(servidor):
    _, entorno = servidor
    codigo, salida = _bin("http://127.0.0.1:9", entorno, "verifica", "00")
    assert codigo == 1 and "./practicar" in salida, salida


def test_comando_tienda(servidor):
    url, entorno = servidor
    codigo, salida = _bin(url, entorno, "tienda", "error", "E3", "on")
    assert codigo == 0 and "E3  🔴 encendido" in salida, salida
    codigo, salida = _bin(url, entorno, "tienda", "error", "E3", "off")
    assert codigo == 0 and "E3  ⚪ apagado" in salida, salida
    assert _bin(url, entorno, "tienda", "error", "E9", "on")[0] == 1
    codigo, salida = _bin(url, entorno, "tienda", "reloj", "2030-12-31T23:59:58")
    assert codigo == 0 and "2030-12-31T23:59:5" in salida, salida
    assert _bin(url, entorno, "tienda", "reloj", "real")[0] == 0
    codigo, salida = _bin(url, entorno, "tienda", "pasarela", "tarda", "3")
    assert codigo == 0 and "tarda 3 segundos" in salida, salida
    assert "no contesta" in _bin(url, entorno, "tienda", "pasarela", "no-contesta")[1]
    assert _bin(url, entorno, "tienda", "pasarela", "aprueba")[0] == 0
