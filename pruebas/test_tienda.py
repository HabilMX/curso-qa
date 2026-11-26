"""Las reglas de la tienda (R1…R11) y los errores sembrados (E1…E8).

Cada error tiene su par de pruebas: con el error APAGADO la tienda cumple la regla, y con el error ENCENDIDO la
rompe de la forma exacta que dice la especificación. Si un error dejara de sembrarse, su prueba «encendido» se
pondría roja: así se sabe que el curso sigue teniendo algo que encontrar.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from conftest import error, llenar, sesion

from tienda import dinero, reglas, textos


# ---------------------------------------------------------------- dinero y reglas puras

def test_montos_ida_y_vuelta():
    assert dinero.a_texto(99900) == "$999.00"
    assert dinero.a_texto(5000001) == "$50,000.01"
    assert dinero.de_texto("$1,234.56") == 123456
    assert dinero.de_texto("999") == 99900
    with pytest.raises(ValueError):
        dinero.de_texto("mil pesos")


@pytest.mark.parametrize("mercancia, envio", [(99898, 9900), (99899, 9900), (99900, 0), (99901, 0)])
def test_r5_envio_en_la_orilla(mercancia, envio):
    assert reglas.costo_envio(mercancia) == envio


def test_e1_corre_la_orilla_solo_en_999():
    assert reglas.costo_envio(99900, e1_encendido=True) == 9900
    assert reglas.costo_envio(99901, e1_encendido=True) == 0
    assert reglas.costo_envio(99899, e1_encendido=True) == 9900


@pytest.mark.parametrize("valor, mensaje", [
    (-1, "el mínimo es 1 pieza"), (0, "el mínimo es 1 pieza"), (11, "el máximo es 10 piezas"),
    (12, "el máximo es 10 piezas"), (2.5, "la cantidad tiene que ser entera"), ("2.5", "la cantidad tiene que ser entera"),
    ("dos", "la cantidad tiene que ser un número"), ("", "la cantidad es obligatoria"),
    ("  ", "la cantidad es obligatoria"), (None, "la cantidad es obligatoria"),
    (True, "la cantidad tiene que ser un número"),
])
def test_r6_cantidades_que_se_rechazan(valor, mensaje):
    with pytest.raises(reglas.ReglaRota) as exc:
        reglas.validar_cantidad(valor)
    assert exc.value.mensaje == mensaje


@pytest.mark.parametrize("valor", [1, 2, 9, 10, "4", 3.0])
def test_r6_cantidades_que_se_aceptan(valor):
    assert reglas.validar_cantidad(valor) == int(float(valor))


@pytest.mark.parametrize("total, aparece", [(299998, False), (299999, False), (300000, True), (300001, True),
                                            (4999999, True), (5000000, True), (5000001, False), (5000002, False)])
def test_r7_meses_en_sus_orillas(total, aparece):
    assert reglas.meses_disponibles(total) is aparece


# ---------------------------------------------------------------- catálogo y sesión

def test_salud_productos_y_pagina(tienda):
    assert tienda.get("/api/salud").json()["estado"] == "arriba"
    precios = {p["id"]: p["precio"]["texto"] for p in tienda.get("/api/productos").json()}
    assert precios["playera-azul"] == "$333.00" and precios["playera-gris"] == "$332.99"
    assert precios["estampa"] == "$0.01" and precios["mochila"] == "$2,999.99" and precios["gorra"] == "$111.00"
    assert tienda.get("/").status_code == 200


def test_sin_sesion_no_hay_carrito(tienda):
    assert tienda.get("/api/carrito").status_code == 401
    assert tienda.post("/api/sesiones", json={"cliente": "Marta", "contrasena": "otra"}).status_code == 401


# ---------------------------------------------------------------- carrito: R1, R2, R5, R6, R7

def test_r1_diez_por_ciento_sin_contar_envio(tienda):
    h = sesion(tienda)
    llenar(tienda, h, calcetines=10)                                    # $1,200.00
    c = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).json()
    assert c["descuento"]["texto"] == "$120.00" and c["cupon"]["aplicado"] is True


def test_r2_minimo_de_500(tienda):
    h = sesion(tienda)
    llenar(tienda, h, playera_azul=1, calcetines=1, estampa=1)          # 333 + 120 + 0.01 = $453.01
    r = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    assert r.status_code == 422 and r.json()["mensaje"] == "el cupón es para compras de $500.00 o más"
    assert tienda.get("/api/carrito", headers=h).json()["subtotal"]["texto"] == "$453.01"


def test_r5_envio_despues_del_cupon(tienda):
    """Decisión de la PO: $999.00 con BIENVENIDA10 queda en $899.10 y paga $99.00 de envío."""
    h = sesion(tienda)
    llenar(tienda, h, playera_azul=3)
    assert tienda.get("/api/carrito", headers=h).json()["envio"]["texto"] == "$0.00"
    c = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).json()
    assert (c["descuento"]["texto"], c["envio"]["texto"], c["total"]["texto"]) == ("$99.90", "$99.00", "$998.10")


def test_r5_carrito_de_la_l03_queda_justo_en_la_orilla(tienda):
    h = sesion(tienda)
    llenar(tienda, h, playera_azul=3, gorra=1)                          # $1,110.00
    c = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).json()
    assert (c["descuento"]["texto"], c["envio"]["texto"], c["total"]["texto"]) == ("$111.00", "$0.00", "$999.00")


def test_r6_rechazo_deja_la_cantidad_que_tenia(tienda):
    h = sesion(tienda)
    llenar(tienda, h, playera_azul=3)
    r = tienda.put("/api/carrito/productos/playera-azul", json={"cantidad": "dos"}, headers=h)
    assert r.status_code == 422 and r.json()["mensaje"] == "la cantidad tiene que ser un número"
    assert tienda.get("/api/carrito", headers=h).json()["productos"][0]["cantidad"] == 3


def test_r7_mochila_y_un_centavo(tienda):
    h = sesion(tienda)
    llenar(tienda, h, mochila=1)
    assert tienda.get("/api/carrito/formas-de-pago", headers=h).json()["meses_sin_intereses"] is False
    llenar(tienda, h, estampa=1)
    assert tienda.get("/api/carrito/formas-de-pago", headers=h).json()["meses_sin_intereses"] is True


# ---------------------------------------------------------------- cupón: R3 y R4

def comprar(tienda, h, llave=None, **piezas):
    llenar(tienda, h, **piezas)
    pedido = tienda.post("/api/pedidos", headers=h).json()
    extra = {"Idempotency-Key": llave} if llave else {}
    return pedido, tienda.post(f"/api/pedidos/{pedido['id']}/pago", json={"tarjeta": "4242424242424242"},
                               headers={**h, **extra})


def test_r3_segunda_vez_ya_uso(tienda):
    h = sesion(tienda)
    llenar(tienda, h, calcetines=5)
    tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    _, pago = comprar(tienda, h)
    assert pago.status_code == 200
    llenar(tienda, h, calcetines=5)
    r = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    assert r.status_code == 422 and r.json()["mensaje"] == "ya usó este cupón"


def test_r4_vence_el_31_de_diciembre_al_ultimo_milisegundo(tienda):
    h = sesion(tienda)
    llenar(tienda, h, calcetines=5)
    anio = tienda.get("/api/salud").json()["hora_de_la_tienda"][:4]
    tienda.put("/control/reloj", json={"ahora": f"{anio}-12-31T23:59:58"})
    assert tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).status_code == 200
    tienda.put("/control/reloj", json={"ahora": f"{int(anio) + 1}-01-01T00:00:00"})
    r = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    assert r.status_code == 422 and r.json()["mensaje"] == "el cupón ya venció"


# ---------------------------------------------------------------- pedidos: R8, R9, R10

def test_r8_avanzar_no_paga_un_pedido_sin_cobrarlo(tienda):
    # «tienda pedido N avanzar» es el almacén o la paquetería: no cobra. Un pedido «creado» solo pasa a «pagado»
    # con un pago aprobado; si no, cancelarlo después «reembolsaría» algo que nunca se cobró.
    h = sesion(tienda)
    llenar(tienda, h, sudadera=1)
    pedido = tienda.post("/api/pedidos", headers=h).json()
    r = tienda.post(f"/control/pedidos/{pedido['id']}/avance")
    assert r.status_code == 409 and r.json()["mensaje"] == "este pedido no está pagado: el almacén solo mueve pedidos pagados"
    assert tienda.get(f"/api/pedidos/{pedido['id']}", headers=h).json()["estado"] == "creado"
    # Control positivo: ya pagado, sí avanza.
    assert tienda.post(f"/api/pedidos/{pedido['id']}/pago", json={"tarjeta": "4242424242424242"},
                       headers=h).status_code == 200
    assert tienda.post(f"/control/pedidos/{pedido['id']}/avance").json()["estado"] == "en almacén"


def test_r8_r9_cancelar_antes_de_salir_reembolsa(tienda):
    h = sesion(tienda)
    pedido, pago = comprar(tienda, h, sudadera=1)
    assert pago.status_code == 200
    assert tienda.post(f"/control/pedidos/{pedido['id']}/avance").json()["estado"] == "en almacén"
    c = tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=h).json()
    assert c["estado"] == "cancelado" and c["reembolso"]["texto"] == "$748.00" and c["cobrado"]["centavos"] == 0


def test_r12_cancelar_no_devuelve_el_cupon_y_lo_dice(tienda):
    h = sesion(tienda)
    llenar(tienda, h, calcetines=5)
    tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    pedido, pago = comprar(tienda, h)
    assert pago.status_code == 200
    c = tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=h).json()
    assert c["estado"] == "cancelado"
    assert c["aviso"] == "Tu cupón BIENVENIDA10 ya se usó en este pedido y no se devuelve al cancelarlo"
    llenar(tienda, h, calcetines=5)
    r = tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    assert r.status_code == 422 and r.json()["mensaje"] == "ya usó este cupón"


def test_r12_sin_cupon_no_hay_aviso(tienda):
    h = sesion(tienda)
    pedido, _ = comprar(tienda, h, sudadera=1)
    assert "aviso" not in tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=h).json()


def test_r10_pedido_ajeno_no_existe(tienda):
    marta, luis = sesion(tienda, "Marta"), sesion(tienda, "Luis")
    pedido, _ = comprar(tienda, marta, sudadera=1)
    assert tienda.get(f"/api/pedidos/{pedido['id']}", headers=luis).status_code == 404
    assert tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=luis).status_code == 404


def test_e5_luis_ve_el_pedido_de_marta_solo_al_consultarlo(tienda):
    marta, luis = sesion(tienda, "Marta"), sesion(tienda, "Luis")
    pedido, _ = comprar(tienda, marta, sudadera=1)
    error(tienda, "E5")
    visto = tienda.get(f"/api/pedidos/{pedido['id']}", headers=luis)
    assert visto.status_code == 200 and visto.json()["id"] == pedido["id"], visto.text
    # Solo la consulta: cancelar sigue revisando el dueño, y un pedido que no existe sigue sin existir
    assert tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=luis).status_code == 404
    assert tienda.get("/api/pedidos/999", headers=luis).status_code == 404
    assert tienda.get(f"/api/pedidos/{pedido['id']}", headers=marta).status_code == 200


def test_e5_apagado_el_pedido_ajeno_no_existe(tienda):
    marta, luis = sesion(tienda, "Marta"), sesion(tienda, "Luis")
    pedido, _ = comprar(tienda, marta, sudadera=1)
    error(tienda, "E5")
    error(tienda, "E5", False)
    r = tienda.get(f"/api/pedidos/{pedido['id']}", headers=luis)
    assert r.status_code == 404 and r.json()["mensaje"] == textos.t("error.pedido_no_existe", "es"), r.text


def test_pasarela_que_rechaza_libera_el_cupon(tienda):
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "rechaza"})
    llenar(tienda, h, calcetines=5)
    tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h)
    _, pago = comprar(tienda, h)
    assert pago.status_code == 402
    llenar(tienda, h, calcetines=5)
    assert tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).status_code == 200


# ---------------------------------------------------------------- R11 y los errores sembrados

def test_r11_misma_llave_un_solo_cobro(tienda):
    h = sesion(tienda)
    pedido, pago = comprar(tienda, h, llave="llave-1", sudadera=1)
    otra = tienda.post(f"/api/pedidos/{pedido['id']}/pago", json={"tarjeta": "4242424242424242"},
                       headers={**h, "Idempotency-Key": "llave-1"})
    assert pago.status_code == otra.status_code == 200
    assert len(tienda.get(f"/api/pedidos/{pedido['id']}", headers=h).json()["movimientos"]) == 1


def test_e1_carrito_de_999_paga_envio(tienda):
    h = sesion(tienda)
    llenar(tienda, h, playera_azul=3)
    assert tienda.get("/api/carrito", headers=h).json()["envio"]["texto"] == "$0.00"
    error(tienda, "E1")
    assert tienda.get("/api/carrito", headers=h).json()["envio"]["texto"] == "$99.00"


def _dos_pedidos_con_cupon(tienda, h):
    pedidos = []
    for _ in range(2):
        llenar(tienda, h, calcetines=5)
        assert tienda.post("/api/carrito/cupon", json={"codigo": "BIENVENIDA10"}, headers=h).status_code == 200
        pedidos.append(tienda.post("/api/pedidos", headers=h).json()["id"])
    return pedidos


def _pagar_a_la_vez(tienda, h, pedidos):
    barrera = threading.Barrier(len(pedidos))

    def pagar(pid):
        barrera.wait()
        return tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"}, headers=h).status_code

    with ThreadPoolExecutor(len(pedidos)) as hilos:
        return sorted(hilos.map(pagar, pedidos))


def test_e2_apagado_dos_pagos_a_la_vez_usan_el_cupon_una_vez(tienda):
    h = sesion(tienda)
    assert _pagar_a_la_vez(tienda, h, _dos_pedidos_con_cupon(tienda, h)) == [200, 422]


def _pagar_uno_tras_otro(tienda, h, pedidos):
    return [tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"}, headers=h).status_code
            for pid in pedidos]


def test_e2_encendido_dos_pagos_a_la_vez_usan_el_cupon_dos_veces(tienda):
    h = sesion(tienda)
    error(tienda, "E2")
    assert _pagar_a_la_vez(tienda, h, _dos_pedidos_con_cupon(tienda, h)) == [200, 200]


@pytest.mark.parametrize("encendido", [False, True])
def test_e2_uno_tras_otro_el_segundo_uso_del_cupon_se_rechaza(tienda, encendido):
    """E2 solo se nota al mismo tiempo: uno tras otro, la tienda rechaza el segundo uso esté o no encendido."""
    h = sesion(tienda)
    error(tienda, "E2", encendido)
    pedidos = _dos_pedidos_con_cupon(tienda, h)
    assert _pagar_uno_tras_otro(tienda, h, pedidos) == [200, 422]
    segundo = tienda.post(f"/api/pedidos/{pedidos[1]}/pago", json={"tarjeta": "4242424242424242"}, headers=h)
    assert segundo.status_code == 422 and segundo.json()["mensaje"] == "ya usó este cupón"
    assert [tienda.get(f"/api/pedidos/{p}", headers=h).json()["estado"] for p in pedidos] == ["pagado", "creado"]


def test_e2_encendido_el_reintento_del_mismo_pago_no_choca_con_su_cupon(tienda):
    h = sesion(tienda)
    error(tienda, "E2")
    pedido = _dos_pedidos_con_cupon(tienda, h)[0]
    cabeza = {**h, "Idempotency-Key": "e2-reintento"}
    primero = tienda.post(f"/api/pedidos/{pedido}/pago", json={"tarjeta": "4242424242424242"}, headers=cabeza)
    otra_vez = tienda.post(f"/api/pedidos/{pedido}/pago", json={"tarjeta": "4242424242424242"}, headers=cabeza)
    assert (primero.status_code, otra_vez.status_code) == (200, 200)


@pytest.mark.parametrize("hora, dia", [("2026-11-21T12:00:00", "2026-11-21"), ("2026-11-30T17:59:00", "2026-11-30"),
                                       ("2026-11-30T18:00:00", "2026-12-01"), ("2026-12-31T23:30:00", "2027-01-01")])
def test_e6_la_fecha_del_pedido_en_utc(tienda, hora, dia):
    h = sesion(tienda)
    tienda.put("/control/reloj", json={"ahora": hora})
    pedido, _ = comprar(tienda, h, calcetines=1)
    assert pedido["creado"].startswith(hora[:16]) and pedido["creado"].endswith("-06:00"), pedido["creado"]
    error(tienda, "E6")
    pedido, _ = comprar(tienda, h, calcetines=1)
    assert pedido["creado"][:10] == dia and "+" not in pedido["creado"][10:] and "-06" not in pedido["creado"][10:]


@pytest.mark.parametrize("encendido, esperado", [(False, 409), (True, 200)])
def test_e3_cancelar_lo_entregado(tienda, encendido, esperado):
    h = sesion(tienda)
    pedido, _ = comprar(tienda, h, sudadera=1)
    for _ in range(4):                                                 # pagado → … → entregado
        tienda.post(f"/control/pedidos/{pedido['id']}/avance")
    error(tienda, "E3", encendido)
    r = tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=h)
    assert r.status_code == esperado
    if encendido:
        assert r.json()["reembolso"]["texto"] == "$748.00"


@pytest.mark.parametrize("encendido, cargos", [(False, 1), (True, 2)])
def test_e4_reintento_despues_de_que_la_pasarela_tardo(tienda, encendido, cargos):
    h = sesion(tienda)
    error(tienda, "E4", encendido)
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": 1.5})   # la tienda espera 1 s
    llenar(tienda, h, sudadera=1)
    pedido = tienda.post("/api/pedidos", headers=h).json()
    url, cabeza = f"/api/pedidos/{pedido['id']}/pago", {**h, "Idempotency-Key": "reintento-1"}
    primero = tienda.post(url, json={"tarjeta": "4242424242424242"}, headers=cabeza)
    assert primero.status_code == 504
    tienda.put("/control/pasarela", json={"modo": "aprueba"})
    time.sleep(1.0)                                                    # el primer cobro termina de llegar
    segundo = tienda.post(url, json={"tarjeta": "4242424242424242"}, headers=cabeza)
    assert segundo.status_code == 200
    movimientos = tienda.get(f"/api/pedidos/{pedido['id']}", headers=h).json()["movimientos"]
    assert len(movimientos) == cargos


def test_control_no_contesta_desde_afuera(tienda):
    from fastapi.testclient import TestClient

    from tienda import api
    with TestClient(api.app, client=("172.17.0.1", 5000)) as afuera:
        assert afuera.get("/control/errores").status_code == 404


# ---------------------------------------------------------------- forma de las respuestas (L06)

def test_un_401_dice_como_autenticarse(tienda):
    # RFC 9110 §15.5.2: un 401 MUST traer WWW-Authenticate. Tres formas de llegar a un 401.
    sin = tienda.get("/api/carrito")
    inventado = tienda.get("/api/carrito", headers={"Authorization": "Bearer inventado"})
    mala = tienda.post("/api/sesiones", json={"cliente": "Marta", "contrasena": "otra"})
    for r in (sin, inventado, mala):
        assert r.status_code == 401 and r.headers.get("www-authenticate") == "Bearer", (r.status_code, r.headers)
    # Control positivo: lo que no es 401 no lo trae.
    assert "www-authenticate" not in tienda.get("/api/productos").headers


def test_ruta_que_no_existe_y_metodo_no_permitido_hablan_como_la_tienda(tienda):
    for idioma, ruta, metodo in (("es", "/api/no-existe", "GET"), ("en", "/api/no-existe", "GET"),
                                 ("es", "/api/productos", "DELETE"), ("fr", "/api/productos", "DELETE")):
        r = tienda.request(metodo, ruta, headers={"Accept-Language": idioma})
        clave = "error.ruta_no_existe" if r.status_code == 404 else "error.metodo_no_permitido"
        assert r.status_code in (404, 405) and "detail" not in r.json(), r.json()
        assert r.json()["mensaje"] == textos.t(clave, idioma), r.json()
        assert r.headers["content-language"] == idioma


def test_sin_content_type_es_400_y_no_tumba_la_tienda(tienda):
    # curl -d sin -H 'Content-Type: application/json' daba 500 en texto plano (el detalle traía bytes).
    for cuerpo in ('{"cliente":"Marta","contrasena":"marta-practica"}', "cliente=Marta"):
        r = tienda.post("/api/sesiones", content=cuerpo,
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert r.status_code == 400 and r.json()["mensaje"] == textos.t("error.peticion", "es"), r.text


def test_la_tarjeta_sale_enmascarada_en_el_pedido(tienda):
    h = sesion(tienda)
    pedido, pago = comprar(tienda, h, sudadera=1)
    assert pago.status_code == 200, pago.text
    r = tienda.get(f"/api/pedidos/{pedido['id']}", headers=h)
    assert [m["tarjeta"] for m in r.json()["movimientos"]] == ["•••• 4242"], r.text
    assert "4242424242424242" not in r.text and "4242 4242 4242 4242" not in r.text
    assert "4242424242424242" not in tienda.get("/control/pedidos").text


# ---------------------------------------------------------------- L10: el cargo que llega tarde, y E7

def _pedido_y_pago_tardio(tienda, h, llaves=("tarde-1",), segundos=1.5):
    """Un pedido y sus pagos con la pasarela tardando más de lo que la tienda espera (1 s): cada uno da 504."""
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": segundos})
    llenar(tienda, h, sudadera=1)
    pedido = tienda.post("/api/pedidos", headers=h).json()
    for llave in llaves:
        r = tienda.post(f"/api/pedidos/{pedido['id']}/pago", json={"tarjeta": "4242424242424242"},
                        headers={**h, "Idempotency-Key": llave})
        assert r.status_code == 504, r.text
    return pedido


def _ver(tienda, h, pedido):
    v = tienda.get(f"/api/pedidos/{pedido['id']}", headers=h).json()
    return v["estado"], v["cobrado"]["centavos"], [m["tipo"] for m in v["movimientos"]]


def test_el_cargo_que_llega_tarde_deja_el_pedido_pagado(tienda):
    h = sesion(tienda)
    pedido = _pedido_y_pago_tardio(tienda, h)
    time.sleep(1.5)
    assert _ver(tienda, h, pedido) == ("pagado", pedido["total"]["centavos"], ["cargo"])


def test_e7_el_cargo_que_llega_tarde_no_se_concilia(tienda):
    h = sesion(tienda)
    error(tienda, "E7")
    pedido = _pedido_y_pago_tardio(tienda, h)
    time.sleep(1.5)
    assert _ver(tienda, h, pedido) == ("creado", pedido["total"]["centavos"], ["cargo"])


@pytest.mark.parametrize("e7", [False, True])
def test_el_segundo_cargo_con_otra_llave_se_devuelve_solo(tienda, e7):
    """Control positivo: con E7 (sin conciliar) quedan dos cargos netos y el pedido sin pagar."""
    h = sesion(tienda)
    error(tienda, "E7", e7)
    pedido = _pedido_y_pago_tardio(tienda, h, llaves=("tarde-1", "tarde-2"))
    time.sleep(1.5)
    total = pedido["total"]["centavos"]
    if e7:
        assert _ver(tienda, h, pedido) == ("creado", 2 * total, ["cargo", "cargo"])
    else:
        assert _ver(tienda, h, pedido) == ("pagado", total, ["cargo", "cargo", "reembolso"])


def test_el_cargo_que_llega_a_un_pedido_cancelado_se_devuelve(tienda):
    h = sesion(tienda)
    pedido = _pedido_y_pago_tardio(tienda, h)
    assert tienda.post(f"/api/pedidos/{pedido['id']}/cancelacion", headers=h).status_code == 200
    time.sleep(1.5)
    assert _ver(tienda, h, pedido) == ("cancelado", 0, ["cargo", "reembolso"])


def test_reintento_con_la_misma_llave_despues_de_conciliar(tienda):
    h = sesion(tienda)
    pedido = _pedido_y_pago_tardio(tienda, h)
    time.sleep(1.5)
    r = tienda.post(f"/api/pedidos/{pedido['id']}/pago", json={"tarjeta": "4242424242424242"},
                    headers={**h, "Idempotency-Key": "tarde-1"})
    assert r.status_code == 200 and r.json()["pedido"]["estado"] == "pagado"
    assert _ver(tienda, h, pedido)[2] == ["cargo"]


def test_cuarenta_cobros_sin_respuesta_no_cuelgan_el_siguiente(tienda):
    """La pasarela tiene 32 tareas; una espera de «no contesta» (10 min) no puede ocupar una."""
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "no contesta"})
    pedidos = []
    for _ in range(41):
        llenar(tienda, h, calcetines=1)
        pedidos.append(tienda.post("/api/pedidos", headers=h).json()["id"])

    def pagar(pid):
        return tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"},
                           headers={**h, "Idempotency-Key": f"nc-{pid}"}).status_code
    with ThreadPoolExecutor(10) as hilos:
        assert set(hilos.map(pagar, pedidos[:40])) == {504}
    tienda.put("/control/pasarela", json={"modo": "aprueba"})
    assert pagar(pedidos[40]) == 200


def test_el_reinicio_suelta_las_esperas_de_la_pasarela(tienda):
    from tienda import pasarela
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "no contesta"})
    llenar(tienda, h, calcetines=1)
    pid = tienda.post("/api/pedidos", headers=h).json()["id"]
    assert tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"}, headers=h).status_code == 504
    assert len(pasarela._agenda) == 1
    tienda.post("/control/reinicio")
    for _ in range(20):
        if not pasarela._agenda and not pasarela._en_curso:
            break
        time.sleep(0.1)
    assert not pasarela._agenda and not pasarela._en_curso


# ---------------------------------------------------------------- el reloj de la pasarela no puede morir

def _envenenar_reloj():
    """Mete en la agenda una entrada rota que vence ya: al despacharla, el reloj tropieza (IndexError)."""
    import heapq

    from tienda import pasarela
    with pasarela._reloj_cond:
        heapq.heappush(pasarela._agenda, (0.0, -1, -1))
        pasarela._reloj_cond.notify()
    time.sleep(0.3)


def _pagar(tienda, h, llave, producto="calcetines"):
    llenar(tienda, h, **{producto: 1})
    pid = tienda.post("/api/pedidos", headers=h).json()["id"]
    return tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"},
                       headers={**h, "Idempotency-Key": llave}).status_code


def test_el_reloj_sobrevive_a_un_tropiezo_y_la_pasarela_que_tarda_sigue_contestando(tienda):
    """Control positivo: sin la protección, el reloj muere y este pago (tarda 0.3 s, la tienda espera 1 s) da 504."""
    h = sesion(tienda)
    _envenenar_reloj()
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": 0.3})
    assert _pagar(tienda, h, "tropiezo-1") == 200


def test_despues_del_tropiezo_no_contesta_y_luego_aprueba(tienda):
    """Lo que pidió la PO: tras el tropiezo, un pago sin respuesta y luego uno aprobado siguen dando 504 y 200; y
    el reinicio todavía suelta la espera del primero (eso sí necesita al reloj)."""
    from tienda import pasarela
    h = sesion(tienda)
    _envenenar_reloj()
    tienda.put("/control/pasarela", json={"modo": "no contesta"})
    assert _pagar(tienda, h, "tropiezo-nc") == 504
    tienda.put("/control/pasarela", json={"modo": "aprueba"})
    assert _pagar(tienda, h, "tropiezo-ok") == 200
    tienda.post("/control/reinicio")
    for _ in range(20):
        if not pasarela._agenda and not pasarela._en_curso:
            break
        time.sleep(0.1)
    assert not pasarela._agenda and not pasarela._en_curso


def test_si_el_reloj_no_esta_vivo_la_siguiente_espera_lo_arranca(tienda, monkeypatch):
    """Aunque el hilo del reloj muriera por algo que no es una excepción (o lo matara otra cosa), agendar una espera
    arranca otro. Aquí el hilo de verdad sigue vivo y contesta el pago; lo que se mide es que se arrancó uno nuevo.
    Control positivo: sin _asegurar_reloj en _agendar, la última aserción sale roja."""
    from tienda import pasarela

    class Muerto:
        def is_alive(self):
            return False
    viejo = pasarela._hilo_reloj
    monkeypatch.setattr(pasarela, "_hilo_reloj", Muerto())
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": 0.3})
    assert _pagar(tienda, h, "revive-1") == 200
    assert pasarela._hilo_reloj is not viejo and pasarela._hilo_reloj.is_alive()


def test_una_entrada_que_no_se_puede_leer_no_atora_al_reloj(tienda):
    """Una entrada cuyo vencimiento no se puede comparar sale de la agenda en vez de atorar al reloj.
    Control positivo: sin _vence, el reloj se queda tropezando con ella y el pago con «tarda» da 504."""
    import heapq

    from tienda import pasarela
    with pasarela._reloj_cond:
        heapq.heappush(pasarela._agenda, (None, -2, -2, lambda: None))
        pasarela._reloj_cond.notify()
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": 0.3})
    assert _pagar(tienda, h, "ilegible-1") == 200


def test_si_el_pool_no_acepta_tareas_el_reloj_hace_el_trabajo(tienda, monkeypatch):
    """Control positivo: sin el respaldo de _despachar, el trabajo se pierde y el pago con «tarda» da 504."""
    from tienda import pasarela
    original = pasarela._hilos.submit

    def submit(fn, *args, **kwargs):
        if threading.current_thread().name == "pasarela-reloj":
            raise RuntimeError("cannot schedule new futures after shutdown")
        return original(fn, *args, **kwargs)
    monkeypatch.setattr(pasarela._hilos, "submit", submit)
    h = sesion(tienda)
    tienda.put("/control/pasarela", json={"modo": "tarda", "segundos": 0.3})
    assert _pagar(tienda, h, "sin-pool-1") == 200


# ---------------------------------------------------------------- L11: E8 vive solo en la página

def test_e8_no_cambia_la_api(tienda):
    """Con E8 encendido el pago por la API cobra igual: E8 es de la página."""
    h = sesion(tienda)
    error(tienda, "E8")
    llenar(tienda, h, playera_azul=1)
    pid = tienda.post("/api/pedidos", headers=h).json()["id"]
    r = tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"},
                    headers={**h, "Idempotency-Key": "e8-api"})
    assert r.status_code == 200 and r.json()["pedido"]["estado"] == "pagado"


def test_el_guion_de_la_pagina_no_cambia_con_e8(tienda):
    """El alumno puede leer app.js: si su texto cambiara con E8, delataría cuál está encendido (L14, modo lunes)."""
    apagado = tienda.get("/estaticos/app.js")
    error(tienda, "E8")
    encendido = tienda.get("/estaticos/app.js")
    assert apagado.status_code == encendido.status_code == 200
    assert encendido.headers["cache-control"] == "no-store"
    assert apagado.text == encendido.text
    assert '"X-Desde": "pagina"' in encendido.text and '"data-testid": `agregar-${p.id}`' in encendido.text


@pytest.mark.parametrize("encendido, estado", [(False, "pagado"), (True, "creado")])
def test_e8_el_pago_de_la_pagina_no_cobra(tienda, encendido, estado):
    """E8: al pago que manda la página se le contesta 200, pero no cobra y el pedido sigue «creado»."""
    h = sesion(tienda)
    error(tienda, "E8", encendido)
    llenar(tienda, h, playera_azul=1)
    pid = tienda.post("/api/pedidos", headers=h).json()["id"]
    r = tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"},
                    headers={**h, "Idempotency-Key": f"e8-pagina-{encendido}", "X-Desde": "pagina"})
    assert r.status_code == 200, r.text
    assert tienda.get(f"/api/pedidos/{pid}", headers=h).json()["estado"] == estado


def test_e8_el_pago_de_la_pagina_no_salta_la_regla_del_pedido_ajeno(tienda):
    h, otra = sesion(tienda), sesion(tienda, "Luis")
    error(tienda, "E8")
    llenar(tienda, h, playera_azul=1)
    pid = tienda.post("/api/pedidos", headers=h).json()["id"]
    r = tienda.post(f"/api/pedidos/{pid}/pago", json={"tarjeta": "4242424242424242"},
                    headers={**otra, "X-Desde": "pagina"})
    assert r.status_code == 404, r.text


def test_la_hoja_de_estilo_se_sigue_sirviendo(tienda):
    assert tienda.get("/estaticos/estilo.css").status_code == 200
