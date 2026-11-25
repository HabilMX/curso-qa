"""La API JSON de la tienda y la página. Las rutas del alumno viven bajo /api; las de control, bajo /control.

Las de /control solo contestan desde adentro del contenedor (127.0.0.1): son las que usan el `practicar`, el
`verifica` y el catálogo de pasos para encender errores, mover el reloj o la pasarela, y dejar la tienda limpia.
"""

import json
import os
import secrets
import threading
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from concurrent.futures import TimeoutError as EsperaAgotada
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import datos, dinero, pasarela, reglas, textos
from .textos import t
from .reglas import ReglaRota

ESPERA_PASARELA_S = float(os.environ.get("TIENDA_ESPERA_PASARELA", "5"))
PAGINA = Path(__file__).parent / "pagina"



@asynccontextmanager
async def _vida(_: FastAPI):
    con = datos.conectar()
    try:
        datos.preparar(con)
    finally:
        con.close()
    yield


app = FastAPI(title="Tienda de práctica — QA desde cero", version="0.1.0", lifespan=_vida,
              description="La tienda del curso «QA desde cero». Trae errores sembrados a propósito.")


@app.get("/estaticos/app.js", include_in_schema=False)
def guion_de_la_pagina():
    """El guion de la página. E8 «la página no deja pagar» vive solo aquí: el botón «Pagar» crea el pedido, no manda
    el pago y aun así dice que quedó pagado. La API no cambia, así que una colección no lo ve; un navegador, sí."""
    con = datos.conectar()
    try:
        e8 = datos.error_encendido(con, "E8")
    finally:
        con.close()
    js = (PAGINA / "app.js").read_text(encoding="utf-8")
    if e8:
        js = js.replace("const LA_PAGINA_PAGA = true;", "const LA_PAGINA_PAGA = false;", 1)
    return Response(js, media_type="text/javascript; charset=utf-8", headers={"Cache-Control": "no-store"})


app.mount("/estaticos", StaticFiles(directory=PAGINA), name="estaticos")


def _idioma(request: Request) -> str:
    return textos.elegir(request.query_params.get("idioma"), request.headers.get("accept-language"))


@app.middleware("http")
async def _con_idioma(request: Request, siguiente):
    """Los mensajes y los nombres salen en el idioma de quien pregunta (?idioma=, Accept-Language, o el del
    contenedor). Las claves del JSON, los ids y los estados no se traducen: son los mismos en los cinco idiomas."""
    ficha = textos.fijar(_idioma(request))
    try:
        respuesta = await siguiente(request)
    finally:
        textos.soltar(ficha)
    respuesta.headers["Content-Language"] = _idioma(request)
    return respuesta


# ---------------------------------------------------------------- registro de peticiones (verifica 06)
# Qué peticiones a /api recibió la tienda desde el último reinicio: quién (la clienta de la sesión, o «sin sesión»),
# método, ruta, código y hora. NUNCA cuerpos, encabezados, contraseñas ni tokens. Vive en memoria y se borra con el
# reinicio. Lo lee el `verifica 06` por /control/peticiones para saber que el alumno hizo su práctica con curl.
SIN_SESION = "sin sesión"
# El healthcheck de la imagen pide /api/salud cada 10 s: anotarlo llenaría el registro (5000 renglones en ~14 h)
# y empujaría fuera la práctica del alumno. No es una petición del alumno.
FUERA_DEL_REGISTRO = frozenset({"/api/salud"})
_registro: deque = deque(maxlen=5000)
_registro_candado = threading.Lock()


def _quien(authorization: str | None) -> str:
    token = (authorization or "").removeprefix("Bearer ").strip()
    if not token:
        return SIN_SESION
    con = datos.conectar()
    try:
        fila = con.execute("SELECT c.nombre FROM sesiones s JOIN clientes c ON c.id = s.cliente_id WHERE s.token = ?",
                           (token,)).fetchone()
    finally:
        con.close()
    return fila["nombre"] if fila else SIN_SESION


@app.middleware("http")
async def _anotar(request: Request, siguiente):
    respuesta = await siguiente(request)
    if request.url.path.startswith("/api/") and request.url.path not in FUERA_DEL_REGISTRO:
        renglon = {"cliente": _quien(request.headers.get("authorization")), "metodo": request.method,
                   "ruta": request.url.path, "codigo": respuesta.status_code,
                   "hora": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        with _registro_candado:
            _registro.append(renglon)
    return respuesta


# RFC 9110 §15.5.2: todo 401 dice cómo autenticarse.
_AUTENTICARSE = {"WWW-Authenticate": "Bearer"}


@app.exception_handler(ReglaRota)
def _regla_rota(request: Request, exc: ReglaRota):
    return JSONResponse({"mensaje": exc.en(_idioma(request))}, status_code=exc.codigo,
                        headers=_AUTENTICARSE if exc.codigo == 401 else None)


@app.exception_handler(StarletteHTTPException)
def _http(request: Request, exc: StarletteHTTPException):
    """La ruta que no existe (404) y el método no permitido (405) contestan como el resto: {"mensaje"} en el idioma."""
    clave = {404: "error.ruta_no_existe", 405: "error.metodo_no_permitido"}.get(exc.status_code)
    mensaje = t(clave, _idioma(request)) if clave else str(exc.detail)
    return JSONResponse({"mensaje": mensaje}, status_code=exc.status_code, headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
def _peticion_mal_formada(request: Request, exc: RequestValidationError):
    # Solo dónde y qué faltó: el cuerpo crudo («input») puede venir en bytes y no se puede mandar como JSON
    # (sin Content-Type, curl -d tumbaba la tienda con un 500).
    detalle = [{"donde": e.get("loc"), "que": e.get("msg"), "tipo": e.get("type")} for e in exc.errors()]
    return JSONResponse({"mensaje": t("error.peticion", _idioma(request)), "detalle": detalle}, status_code=400)


def con_base():
    con = datos.conectar()
    try:
        yield con
    finally:
        con.close()


def m(centavos: int) -> dict:
    """Un monto como lo lee una persona y como lo compara un programa."""
    return {"texto": dinero.a_texto(centavos), "centavos": centavos}


# ---------------------------------------------------------------- sesión

def cliente_actual(authorization: str | None = Header(default=None), con=Depends(con_base)) -> dict:
    token = (authorization or "").removeprefix("Bearer ").strip()
    fila = con.execute("SELECT c.id, c.nombre FROM sesiones s JOIN clientes c ON c.id = s.cliente_id "
                       "WHERE s.token = ?", (token,)).fetchone() if token else None
    if fila is None:
        raise ReglaRota("error.sin_sesion", 401)
    return {"id": fila["id"], "nombre": fila["nombre"]}


@app.post("/api/sesiones", status_code=201, tags=["sesión"])
def iniciar_sesion(cuerpo: dict, con=Depends(con_base)):
    """Cuerpo: {"cliente": "Marta", "contrasena": "marta-practica"}. Devuelve el token para el encabezado
    Authorization: Bearer <token>."""
    fila = con.execute("SELECT id, nombre, contrasena FROM clientes WHERE nombre = ?",
                       (str(cuerpo.get("cliente", "")),)).fetchone()
    if fila is None or not secrets.compare_digest(fila["contrasena"], str(cuerpo.get("contrasena", ""))):
        raise ReglaRota("error.credenciales", 401)
    token = secrets.token_urlsafe(24)
    con.execute("INSERT INTO sesiones (token, cliente_id) VALUES (?, ?)", (token, fila["id"]))
    return {"token": token, "cliente": fila["nombre"]}


# ---------------------------------------------------------------- catálogo

def _producto(fila) -> dict:
    return {"id": fila["id"], "nombre": t(f"producto.{fila['id']}"), "precio": m(fila["precio_c"]),
            "categoria": t(f"categoria.{fila['categoria']}")}


@app.get("/api/salud", tags=["catálogo"])
def salud(con=Depends(con_base)):
    con.execute("SELECT 1").fetchone()
    return {"estado": "arriba", "hora_de_la_tienda": datos.ahora(con).isoformat(timespec="seconds")}


@app.get("/api/productos", tags=["catálogo"])
def productos(con=Depends(con_base)):
    return [_producto(f) for f in con.execute("SELECT * FROM productos ORDER BY orden")]


@app.get("/api/productos/{producto_id}", tags=["catálogo"])
def producto(producto_id: str, con=Depends(con_base)):
    fila = con.execute("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
    if fila is None:
        raise ReglaRota("error.producto_no_existe", 404)
    return _producto(fila)


# ---------------------------------------------------------------- carrito

def _cupon(con, codigo: str):
    return con.execute("SELECT * FROM cupones WHERE codigo = ?", (codigo,)).fetchone()


def _cuenta_carrito(con, cliente_id: int):
    filas = con.execute("SELECT p.id, p.nombre, p.precio_c, cp.cantidad FROM carrito_productos cp "
                        "JOIN productos p ON p.id = cp.producto_id WHERE cp.cliente_id = ? ORDER BY p.orden",
                        (cliente_id,)).fetchall()
    subtotal = sum(f["precio_c"] * f["cantidad"] for f in filas)
    carrito = con.execute("SELECT cupon FROM carritos WHERE cliente_id = ?", (cliente_id,)).fetchone()
    codigo = carrito["cupon"] if carrito else None
    cupon = _cupon(con, codigo) if codigo else None
    cuenta = reglas.cuenta(subtotal, (cupon["por_ciento"], cupon["minimo_c"]) if cupon else None,
                           datos.error_encendido(con, "E1"))
    return filas, codigo, cupon, cuenta


def _vista_carrito(con, cliente_id: int) -> dict:
    filas, codigo, cupon, cuenta = _cuenta_carrito(con, cliente_id)
    vista_cupon = None
    if codigo:
        aplicado = cuenta.descuento_c > 0
        vista_cupon = {"codigo": codigo, "aplicado": aplicado}
        if not aplicado:
            vista_cupon["aviso"] = t("aviso.cupon_minimo", minimo=dinero.a_texto(cupon["minimo_c"]))
    return {
        "productos": [{"id": f["id"], "nombre": t(f"producto.{f['id']}"), "precio": m(f["precio_c"]),
                       "cantidad": f["cantidad"],
                       "importe": m(f["precio_c"] * f["cantidad"])} for f in filas],
        "piezas": sum(f["cantidad"] for f in filas),
        "cupon": vista_cupon,
        "subtotal": m(cuenta.subtotal_c),
        "descuento": m(cuenta.descuento_c),
        "envio": m(cuenta.envio_c),
        "total": m(cuenta.total_c),
        "meses_sin_intereses": reglas.meses_disponibles(cuenta.total_c),
    }


@app.get("/api/carrito", tags=["carrito"])
def ver_carrito(cliente=Depends(cliente_actual), con=Depends(con_base)):
    return _vista_carrito(con, cliente["id"])


@app.put("/api/carrito/productos/{producto_id}", tags=["carrito"])
def poner_en_carrito(producto_id: str, cuerpo: dict, cliente=Depends(cliente_actual), con=Depends(con_base)):
    """Cuerpo: {"cantidad": 3}. Pone esa cantidad (no la suma). R6: de 1 a 10 piezas, enteras."""
    if con.execute("SELECT 1 FROM productos WHERE id = ?", (producto_id,)).fetchone() is None:
        raise ReglaRota("error.producto_no_existe", 404)
    cantidad = reglas.validar_cantidad(cuerpo.get("cantidad"))
    with datos.transaccion(con):
        con.execute("INSERT INTO carrito_productos (cliente_id, producto_id, cantidad) VALUES (?, ?, ?) "
                    "ON CONFLICT (cliente_id, producto_id) DO UPDATE SET cantidad = excluded.cantidad",
                    (cliente["id"], producto_id, cantidad))
    return _vista_carrito(con, cliente["id"])


@app.delete("/api/carrito/productos/{producto_id}", tags=["carrito"])
def quitar_de_carrito(producto_id: str, cliente=Depends(cliente_actual), con=Depends(con_base)):
    con.execute("DELETE FROM carrito_productos WHERE cliente_id = ? AND producto_id = ?", (cliente["id"], producto_id))
    return _vista_carrito(con, cliente["id"])


def _ya_uso(con, cliente_id: int, codigo: str) -> bool:
    return con.execute("SELECT 1 FROM cupon_usos WHERE cliente_id = ? AND codigo = ?",
                       (cliente_id, codigo)).fetchone() is not None


def _validar_cupon(con, cliente_id: int, codigo: str, subtotal_c: int):
    """R2, R3 y R4, en el orden en que se le dicen al cliente."""
    cupon = _cupon(con, codigo)
    if cupon is None:
        raise ReglaRota("error.cupon_no_existe")
    if datos.ahora(con) > datetime.fromisoformat(cupon["vence"]):
        raise ReglaRota("error.cupon_vencido")
    if subtotal_c < cupon["minimo_c"]:
        raise ReglaRota("error.cupon_minimo", minimo=dinero.a_texto(cupon["minimo_c"]))
    if _ya_uso(con, cliente_id, codigo):
        raise ReglaRota("error.cupon_usado")
    return cupon


@app.post("/api/carrito/cupon", tags=["carrito"])
def aplicar_cupon(cuerpo: dict, cliente=Depends(cliente_actual), con=Depends(con_base)):
    """Cuerpo: {"codigo": "BIENVENIDA10"}."""
    codigo = str(cuerpo.get("codigo", "")).strip().upper()
    _, _, _, cuenta = _cuenta_carrito(con, cliente["id"])
    _validar_cupon(con, cliente["id"], codigo, cuenta.subtotal_c)
    con.execute("INSERT INTO carritos (cliente_id, cupon) VALUES (?, ?) "
                "ON CONFLICT (cliente_id) DO UPDATE SET cupon = excluded.cupon", (cliente["id"], codigo))
    return _vista_carrito(con, cliente["id"])


@app.delete("/api/carrito/cupon", tags=["carrito"])
def quitar_cupon(cliente=Depends(cliente_actual), con=Depends(con_base)):
    con.execute("UPDATE carritos SET cupon = NULL WHERE cliente_id = ?", (cliente["id"],))
    return _vista_carrito(con, cliente["id"])


@app.get("/api/carrito/formas-de-pago", tags=["carrito"])
def formas_de_pago(cliente=Depends(cliente_actual), con=Depends(con_base)):
    _, _, _, cuenta = _cuenta_carrito(con, cliente["id"])
    formas = [{"forma": "una sola exhibición"}]
    if reglas.meses_disponibles(cuenta.total_c):
        formas.append({"forma": "meses sin intereses", "meses": [3, 6, 12]})
    return {"total": m(cuenta.total_c), "meses_sin_intereses": reglas.meses_disponibles(cuenta.total_c),
            "formas": formas}


# ---------------------------------------------------------------- pedidos

def _pedido_de(con, pedido_id: int, cliente_id: int):
    """R10 — un pedido ajeno no existe para quien no lo hizo: ni se ve ni se cancela."""
    fila = con.execute("SELECT * FROM pedidos WHERE id = ? AND cliente_id = ?", (pedido_id, cliente_id)).fetchone()
    if fila is None:
        raise ReglaRota("error.pedido_no_existe", 404)
    return fila


def _enmascarar(tarjeta: str | None) -> str:
    """Una API no devuelve la tarjeta completa, ni la de prueba: solo los últimos 4 («•••• 4242»)."""
    digitos = "".join(ch for ch in (tarjeta or "") if ch.isdigit())
    return f"•••• {digitos[-4:]}" if len(digitos) >= 4 else "••••"


def _vista_pedido(con, fila) -> dict:
    productos_ = con.execute("SELECT * FROM pedido_productos WHERE pedido_id = ?", (fila["id"],)).fetchall()
    cargos = con.execute("SELECT * FROM cargos WHERE pedido_id = ? ORDER BY id", (fila["id"],)).fetchall()
    historial = con.execute("SELECT * FROM historial WHERE pedido_id = ? ORDER BY rowid", (fila["id"],)).fetchall()
    return {
        "id": fila["id"],
        "estado": fila["estado"],
        "productos": [{"id": p["producto_id"], "nombre": t(f"producto.{p['producto_id']}"), "precio": m(p["precio_c"]),
                       "cantidad": p["cantidad"]} for p in productos_],
        "cupon": fila["cupon"],
        "subtotal": m(fila["subtotal_c"]),
        "descuento": m(fila["descuento_c"]),
        "envio": m(fila["envio_c"]),
        "total": m(fila["total_c"]),
        "meses": fila["meses"],
        "movimientos": [{"tipo": c["tipo"], "monto": m(c["monto_c"]), "tarjeta": _enmascarar(c["tarjeta"]),
                         "cuando": c["cuando"]} for c in cargos],
        "cobrado": m(sum(c["monto_c"] if c["tipo"] == "cargo" else -c["monto_c"] for c in cargos)),
        "historial": [{"estado": h["estado"], "cuando": h["cuando"]} for h in historial],
        "creado": fila["creado"],
    }


def _anotar(con, pedido_id: int, estado: str) -> None:
    con.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (estado, pedido_id))
    con.execute("INSERT INTO historial (pedido_id, estado, cuando) VALUES (?, ?, ?)",
                (pedido_id, estado, datos.ahora(con).isoformat()))


def _hora_del_pedido(con) -> str:
    """La hora en que nace el pedido, con la zona de la tienda («2026-12-31T23:30:00-06:00»).

    E6 «fecha en UTC»: la pasa a UTC y le quita la zona («2027-01-01T05:30:00»). A mediodía la fecha no cambia;
    de noche (desde las 18:00 de la Ciudad de México) el pedido cae en el día siguiente, y el 31 de diciembre, en el
    año siguiente."""
    ahora = datos.ahora(con)
    if datos.error_encendido(con, "E6"):
        return ahora.astimezone(timezone.utc).replace(tzinfo=None).isoformat()
    return ahora.isoformat()


@app.post("/api/pedidos", status_code=201, tags=["pedidos"])
def crear_pedido(cliente=Depends(cliente_actual), con=Depends(con_base)):
    """Convierte el carrito en un pedido «creado» y vacía el carrito. El cobro es aparte: POST …/pago."""
    with datos.transaccion(con):
        filas, codigo, cupon, cuenta = _cuenta_carrito(con, cliente["id"])
        if not filas:
            raise ReglaRota("error.carrito_vacio")
        if codigo:
            _validar_cupon(con, cliente["id"], codigo, cuenta.subtotal_c)
        cur = con.execute("INSERT INTO pedidos (cliente_id, estado, subtotal_c, descuento_c, envio_c, total_c, cupon, "
                          "creado) VALUES (?, 'creado', ?, ?, ?, ?, ?, ?)",
                          (cliente["id"], cuenta.subtotal_c, cuenta.descuento_c, cuenta.envio_c, cuenta.total_c,
                           codigo, _hora_del_pedido(con)))
        pedido_id = cur.lastrowid
        con.executemany("INSERT INTO pedido_productos (pedido_id, producto_id, nombre, precio_c, cantidad) "
                        "VALUES (?, ?, ?, ?, ?)",
                        [(pedido_id, f["id"], f["nombre"], f["precio_c"], f["cantidad"]) for f in filas])
        con.execute("INSERT INTO historial (pedido_id, estado, cuando) VALUES (?, 'creado', ?)",
                    (pedido_id, datos.ahora(con).isoformat()))
        con.execute("DELETE FROM carrito_productos WHERE cliente_id = ?", (cliente["id"],))
        con.execute("UPDATE carritos SET cupon = NULL WHERE cliente_id = ?", (cliente["id"],))
    return _vista_pedido(con, _pedido_de(con, pedido_id, cliente["id"]))


@app.get("/api/pedidos", tags=["pedidos"])
def mis_pedidos(cliente=Depends(cliente_actual), con=Depends(con_base)):
    filas = con.execute("SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY id", (cliente["id"],)).fetchall()
    return [_vista_pedido(con, f) for f in filas]


@app.get("/api/pedidos/{pedido_id}", tags=["pedidos"])
def ver_pedido(pedido_id: int, cliente=Depends(cliente_actual), con=Depends(con_base)):
    # E5 «pedido ajeno»: la consulta busca el pedido solo por su número, sin revisar de quién es; así Luis ve el de
    # Marta. Solo la consulta: cancelar y pagar siguen revisando el dueño (R10).
    if datos.error_encendido(con, "E5"):
        fila = con.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        if fila is None:
            raise ReglaRota("error.pedido_no_existe", 404)
        return _vista_pedido(con, fila)
    return _vista_pedido(con, _pedido_de(con, pedido_id, cliente["id"]))


def _guardar_respuesta(con, llave: str, estado: str, codigo: int, cuerpo: dict) -> JSONResponse:
    con.execute("UPDATE pagos SET estado = ?, codigo = ?, respuesta = ? WHERE llave = ?",
                (estado, codigo, json.dumps(cuerpo, ensure_ascii=False), llave))
    return JSONResponse(cuerpo, status_code=codigo)


VENTANA_E2_S = float(os.environ.get("TIENDA_VENTANA_E2_S", "1.0"))   # la ventana entre revisar y anotar, con E2


def _revisar_cupon_sin_candado(con, pedido_id: int, cliente_id: int) -> None:
    """E2 «cupón dos veces»: revisa si el cupón ya se usó FUERA de la transacción y, después de una pausa, el pago
    lo anota sin volver a revisar. Uno tras otro, el segundo pago ve el uso del primero y recibe 422; dos pagos al
    mismo tiempo revisan los dos antes de que alguno anote, y el cupón se usa dos veces."""
    pedido = _pedido_de(con, pedido_id, cliente_id)
    if not pedido["cupon"] or pedido["estado"] != "creado":
        return
    uso = con.execute("SELECT pedido_id FROM cupon_usos WHERE cliente_id = ? AND codigo = ?",
                      (cliente_id, pedido["cupon"])).fetchone()
    if uso is not None and uso["pedido_id"] != pedido_id:
        raise ReglaRota("error.cupon_usado")
    time.sleep(VENTANA_E2_S)


@app.post("/api/pedidos/{pedido_id}/pago", tags=["pedidos"])
def pagar(pedido_id: int, cuerpo: dict, cliente=Depends(cliente_actual), con=Depends(con_base),
          idempotency_key: str | None = Header(default=None)):
    """Cuerpo: {"tarjeta": "4242 4242 4242 4242", "meses": 0}. Encabezado opcional Idempotency-Key.

    R11: si repites el cobro con la misma llave, se cobra una sola vez y te contesta lo mismo. Si la pasarela no
    contesta a tiempo, la tienda dice 504 y NO sabe si se cobró: reintenta con la MISMA llave.
    """
    llave = (idempotency_key or "").strip() or f"auto-{uuid.uuid4()}"
    tarjeta = str(cuerpo.get("tarjeta", "")).replace(" ", "")
    meses = cuerpo.get("meses", 0) or 0
    e2 = datos.error_encendido(con, "E2")
    e4 = datos.error_encendido(con, "E4")
    if e2:
        _revisar_cupon_sin_candado(con, pedido_id, cliente["id"])

    with datos.transaccion(con):
        pedido = _pedido_de(con, pedido_id, cliente["id"])
        previo = con.execute("SELECT * FROM pagos WHERE llave = ?", (llave,)).fetchone()
        if previo is not None and previo["pedido_id"] != pedido_id:
            raise ReglaRota("error.llave_de_otro_pedido")
        if previo is not None and previo["estado"] in ("aprobado", "rechazado"):
            # R11: la misma llave recibe la misma respuesta, sin volver a cobrar
            return JSONResponse(json.loads(previo["respuesta"]), status_code=previo["codigo"])
        if previo is not None and previo["estado"] == "en proceso" and not e4:
            raise ReglaRota("error.pago_en_proceso", 409)
        # Un reintento con la misma llave de un cobro que se quedó sin respuesta va a la pasarela aunque el pedido ya
        # esté pagado: el cargo tardío lo concilió, y la misma llave tiene que recibir la misma respuesta (R11).
        if pedido["estado"] != "creado" and not (previo is not None and pedido["estado"] == "pagado"):
            raise ReglaRota("error.no_se_puede_pagar", 409, estado=pedido["estado"])
        if not tarjeta.isdigit() or not 12 <= len(tarjeta) <= 19:
            raise ReglaRota("error.tarjeta")
        if not isinstance(meses, int) or isinstance(meses, bool) or meses not in (0, 3, 6, 12):
            raise ReglaRota("error.meses_validos")
        if meses and not reglas.meses_disponibles(pedido["total_c"]):
            raise ReglaRota("error.sin_meses")
        if pedido["cupon"]:
            # R3 se cumple AL PAGAR, adentro de la transacción: dos pagos a la vez no pueden anotar el mismo cupón.
            # E2: ya se revisó afuera, antes de la espera; aquí se anota sin volver a revisar.
            if e2:
                con.execute("INSERT OR IGNORE INTO cupon_usos (cliente_id, codigo, pedido_id) VALUES (?, ?, ?)",
                            (cliente["id"], pedido["cupon"], pedido_id))
            else:
                uso = con.execute("SELECT pedido_id FROM cupon_usos WHERE cliente_id = ? AND codigo = ?",
                                  (cliente["id"], pedido["cupon"])).fetchone()
                if uso is not None and uso["pedido_id"] != pedido_id:
                    raise ReglaRota("error.cupon_usado")
                if uso is None:
                    con.execute("INSERT INTO cupon_usos (cliente_id, codigo, pedido_id) VALUES (?, ?, ?)",
                                (cliente["id"], pedido["cupon"], pedido_id))
        if previo is None:
            con.execute("INSERT INTO pagos (llave, pedido_id, estado) VALUES (?, ?, 'en proceso')", (llave, pedido_id))
        else:
            con.execute("UPDATE pagos SET estado = 'en proceso' WHERE llave = ?", (llave,))
        con.execute("UPDATE pedidos SET meses = ?, tarjeta = ? WHERE id = ?", (meses, tarjeta, pedido_id))

    # E4 «cobro doble al reintentar»: la tienda no le pasa a la pasarela la llave del cliente sino una nueva en
    # cada intento, así que un reintento después de un 504 es, para la pasarela, un cobro distinto. Es UN solo error:
    # el reintento cobra doble y nadie lo corrige; por eso con E4 la tienda tampoco concilia (ver pasarela.py).
    llave_pasarela = f"{llave}#{uuid.uuid4()}" if e4 else llave
    futuro = pasarela.cobrar(llave_pasarela, pedido_id, pedido["total_c"], tarjeta)
    try:
        respuesta = futuro.result(timeout=ESPERA_PASARELA_S)
    except (EsperaAgotada, TimeoutError):
        cuerpo_ = {"mensaje": t("error.pasarela_sin_respuesta"), "llave": llave}
        con.execute("UPDATE pagos SET estado = 'sin respuesta' WHERE llave = ?", (llave,))
        return JSONResponse(cuerpo_, status_code=504)

    with datos.transaccion(con):
        if not respuesta.aprobado:
            if pedido["cupon"] and not e2:
                con.execute("DELETE FROM cupon_usos WHERE cliente_id = ? AND codigo = ? AND pedido_id = ?",
                            (cliente["id"], pedido["cupon"], pedido_id))
            return _guardar_respuesta(con, llave, "rechazado", 402, {"mensaje": t("error.pasarela_rechazo"), "llave": llave})
        actual = con.execute("SELECT estado FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        if actual["estado"] == "creado":
            _anotar(con, pedido_id, "pagado")
        vista = _vista_pedido(con, _pedido_de(con, pedido_id, cliente["id"]))
        return _guardar_respuesta(con, llave, "aprobado", 200, {"mensaje": t("ok.pago_aprobado"), "llave": llave,
                                                                  "pedido": vista})


@app.post("/api/pedidos/{pedido_id}/cancelacion", tags=["pedidos"])
def cancelar(pedido_id: int, cliente=Depends(cliente_actual), con=Depends(con_base)):
    """R9: se cancela mientras no haya salido del almacén; si ya se cobró, se reembolsa a la misma tarjeta.
    R12: si el pedido usó un cupón, el cupón no se devuelve; la respuesta trae el aviso."""
    with datos.transaccion(con):
        pedido = _pedido_de(con, pedido_id, cliente["id"])
        if pedido["estado"] == reglas.CANCELADO:
            raise ReglaRota("error.ya_cancelado", 409)
        if not reglas.puede_cancelarse(pedido["estado"], datos.error_encendido(con, "E3")):
            raise ReglaRota("error.ya_salio", 409)
        devuelto = pasarela.reembolsar(con, pedido_id, pedido["tarjeta"] or "")
        _anotar(con, pedido_id, reglas.CANCELADO)
    vista = _vista_pedido(con, _pedido_de(con, pedido_id, cliente["id"]))
    vista["reembolso"] = m(devuelto)
    if pedido["cupon"]:
        # R12 — cancelar no devuelve el cupón: queda usado, y la tienda lo dice
        vista["aviso"] = t("aviso.cupon_no_se_devuelve", codigo=pedido["cupon"])
    return vista


# ---------------------------------------------------------------- la página

NOMBRES_DE_IDIOMA = {"es": "Español", "en": "English", "fr": "Français", "pt": "Português", "bg": "Български"}


@app.get("/api/textos", tags=["página"])
def textos_de_la_pagina():
    """Los textos de la página en el idioma de la petición; sin Accept-Language, en el idioma de la tienda."""
    idioma = textos.actual()
    todos = textos.catalogo(idioma) or textos.catalogo("es")
    return {"idioma": idioma, "idiomas": NOMBRES_DE_IDIOMA,
            "textos": {k: v for k, v in todos.items() if k.startswith(("pagina.", "estado."))}}


@app.get("/", include_in_schema=False)
def pagina():
    return FileResponse(PAGINA / "index.html")


# ---------------------------------------------------------------- control (solo desde adentro del contenedor)

def solo_adentro(request: Request) -> None:
    if request.client is None or request.client.host not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(404)


@app.post("/control/reinicio", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_reinicio(con=Depends(con_base)):
    vieja = datos.generacion(con)
    datos.reiniciar(con)
    pasarela.reiniciada(vieja)
    with _registro_candado:
        _registro.clear()
    return {"mensaje": t("ok.reinicio")}


@app.get("/control/peticiones", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_peticiones():
    """El registro de peticiones a /api desde el último reinicio (ver _anotar)."""
    with _registro_candado:
        return list(_registro)


@app.get("/control/errores", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_errores(con=Depends(con_base)):
    return {e: datos.error_encendido(con, e) for e in datos.ERRORES}


@app.put("/control/errores/{error}", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_error(error: str, cuerpo: dict, con=Depends(con_base)):
    error = error.upper()
    if error not in datos.ERRORES:
        raise ReglaRota("error.no_hay_error", 404, error=error, errores=", ".join(datos.ERRORES))
    datos.escribir_control(con, f"error.{error}", "on" if cuerpo.get("encendido") else "off")
    return {e: datos.error_encendido(con, e) for e in datos.ERRORES}


@app.put("/control/reloj", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_reloj(cuerpo: dict, con=Depends(con_base)):
    """{"ahora": "2026-12-31T23:59:59"} fija la hora (de la Ciudad de México si no trae zona); {"ahora": null}
    regresa a la hora real."""
    valor = cuerpo.get("ahora")
    try:
        datos.fijar_reloj(con, datetime.fromisoformat(valor) if valor else None)
    except ValueError:
        raise ReglaRota("error.formato_hora") from None
    return {"hora_de_la_tienda": datos.ahora(con).isoformat(timespec="seconds")}


@app.put("/control/pasarela", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_pasarela(cuerpo: dict, con=Depends(con_base)):
    """{"modo": "aprueba" | "rechaza" | "tarda" | "no contesta", "segundos": 8}"""
    modo = cuerpo.get("modo")
    if modo not in ("aprueba", "rechaza", "tarda", "no contesta"):
        raise ReglaRota("error.modo_pasarela")
    datos.escribir_control(con, "pasarela.modo", modo)
    datos.escribir_control(con, "pasarela.segundos", str(float(cuerpo.get("segundos", 0) or 0)))
    return {"modo": modo, "segundos": float(cuerpo.get("segundos", 0) or 0)}


@app.post("/control/pedidos/{pedido_id}/avance", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_avance(pedido_id: int, con=Depends(con_base)):
    """R8 — mueve un pedido al siguiente estado, como lo haría el almacén o la paquetería."""
    with datos.transaccion(con):
        fila = con.execute("SELECT estado FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        if fila is None:
            raise ReglaRota("error.pedido_no_existe", 404)
        nuevo = reglas.siguiente_estado(fila["estado"])
        _anotar(con, pedido_id, nuevo)
    return {"id": pedido_id, "estado": nuevo}


@app.put("/control/clientes/{nombre}/cupones/{codigo}", include_in_schema=False,
         dependencies=[Depends(solo_adentro)])
def control_uso_cupon(nombre: str, codigo: str, cuerpo: dict, con=Depends(con_base)):
    """{"usado": true} lo marca como ya usado en una compra anterior; {"usado": false} como nunca usado."""
    fila = con.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre,)).fetchone()
    if fila is None:
        raise ReglaRota("error.cliente_no_existe", 404)
    con.execute("DELETE FROM cupon_usos WHERE cliente_id = ? AND codigo = ?", (fila["id"], codigo.upper()))
    if cuerpo.get("usado"):
        con.execute("INSERT INTO cupon_usos (cliente_id, codigo, pedido_id) VALUES (?, ?, NULL)",
                    (fila["id"], codigo.upper()))
    return {"cliente": nombre, "codigo": codigo.upper(), "usado": bool(cuerpo.get("usado"))}


@app.get("/control/pedidos", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_pedidos(con=Depends(con_base)):
    """Todos los pedidos con su cliente: lo usa el `verifica`."""
    filas = con.execute("SELECT p.*, c.nombre AS cliente FROM pedidos p JOIN clientes c ON c.id = p.cliente_id "
                        "ORDER BY p.id").fetchall()
    return [{**_vista_pedido(con, f), "cliente": f["cliente"]} for f in filas]


@app.get("/control/sesiones", include_in_schema=False, dependencies=[Depends(solo_adentro)])
def control_sesiones(con=Depends(con_base)):
    """Cuántas sesiones abrió cada cliente desde el último reinicio: con esto el `verifica` sabe con quién entró
    una colección, aunque al final deje el carrito como lo encontró."""
    filas = con.execute("SELECT c.nombre, COUNT(*) AS n FROM sesiones s JOIN clientes c ON c.id = s.cliente_id "
                        "GROUP BY c.nombre").fetchall()
    return {f["nombre"]: f["n"] for f in filas}
