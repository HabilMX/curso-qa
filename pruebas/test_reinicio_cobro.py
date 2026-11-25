"""Bug de la L08 (educación, MEDIDO en 13cdb22): después de `tienda reiniciar`, un cobro que la pasarela seguía
procesando caía en el pedido nuevo con el mismo número, aunque fuera de otra clienta."""
import json
import threading
import time
import urllib.error
import urllib.request

from test_pasos import _api, servidor  # noqa: F401 — servidor es un fixture


def _control(url, metodo, ruta, cuerpo=None):
    peticion = urllib.request.Request(url + ruta, method=metodo, headers={"Content-Type": "application/json"},
                                      data=None if cuerpo is None else json.dumps(cuerpo).encode())
    with urllib.request.urlopen(peticion, timeout=10) as r:
        return json.loads(r.read())


def _pedido_de(url, cliente, contrasena):
    token = _api(url, "POST", "/api/sesiones", {"cliente": cliente, "contrasena": contrasena})["token"]
    _api(url, "PUT", "/api/carrito/productos/playera-azul", {"cantidad": 1}, token)
    return token, _api(url, "POST", "/api/pedidos", {}, token)


def _pagar(url, token, pedido_id, llave, salida):
    try:
        _api(url, "POST", f"/api/pedidos/{pedido_id}/pago", {"tarjeta": "4242424242424242"}, token, llave)
        salida.append(200)
    except urllib.error.HTTPError as e:
        salida.append(e.code)


def test_un_cobro_en_camino_no_cae_en_el_pedido_nuevo_tras_el_reinicio(servidor):  # noqa: F811
    url, _ = servidor
    _control(url, "POST", "/control/reinicio")
    try:
        token_m, pedido_m = _pedido_de(url, "Marta", "marta-practica")
        _control(url, "PUT", "/control/pasarela", {"modo": "tarda", "segundos": 2})
        codigos = []
        hilo = threading.Thread(target=_pagar, args=(url, token_m, pedido_m["id"], "reinicio-1", codigos))
        hilo.start()
        time.sleep(0.5)                              # el cobro de Marta ya va en camino
        _control(url, "POST", "/control/reinicio")
        token_l, pedido_l = _pedido_de(url, "Luis", "luis-practica")
        assert pedido_l["id"] == pedido_m["id"]      # el mismo número: ahí caía el cobro viejo
        hilo.join(10)
        time.sleep(0.5)
        visto = _api(url, "GET", f"/api/pedidos/{pedido_l['id']}", token=token_l)
        assert visto["estado"] == "creado" and visto["movimientos"] == [], visto
        assert codigos == [504], codigos            # a Marta se le dice que no hubo respuesta: no se cobró
    finally:
        _control(url, "POST", "/control/reinicio")
