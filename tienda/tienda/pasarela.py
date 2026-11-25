"""La pasarela de pago simulada: hace como que es un banco que vive en otro lado.

Tiene cuatro modos, que se cambian desde el control: aprueba · rechaza · tarda N segundos · no contesta.

Como una pasarela de verdad, es idempotente por llave: si le piden dos veces el mismo cobro con la misma llave,
cobra una sola vez y a la segunda contesta lo mismo que a la primera; si la primera todavía no termina, la
segunda espera a que termine. Lo que la tienda haga con esa llave es asunto de la tienda (ver E4 en api.py).

Cada cobro nace en una «generación» de la tienda, que `tienda reiniciar` cambia. Un cobro que seguía en camino
cuando la tienda se reinició ya no se anota: si se anotara, caería en el pedido nuevo que tomó el mismo número,
aunque fuera de otra clienta. Y el reinicio suelta a los que esperaban («tarda», «no contesta»): un cobro de otra
generación ya no tiene a quién avisar.

Cuando el cargo se anota, la tienda lo CONCILIA con el pedido: si el pedido seguía «creado» y con eso queda
cobrado completo, pasa a «pagado» aunque quien pagó ya se haya ido con un 504; si el pedido ya estaba pagado (otro
cargo, con otra llave, llegó antes) o se canceló, lo que sobra se devuelve solo como «reembolso». Así ningún
pedido termina con dinero cobrado que no le corresponde. E7 «el cargo que llega tarde no se concilia» apaga esto:
el cargo se anota y nada más. Con E4 tampoco se concilia (ver _contestar).
"""

import heapq
import itertools
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

from . import datos

TOPE_NO_CONTESTA_S = 600          # «no contesta» de verdad no contesta; a los 10 minutos se rinde, sin cobrar

_hilos = ThreadPoolExecutor(max_workers=32, thread_name_prefix="pasarela")
_en_curso: dict[str, Future] = {}
_candado = threading.Lock()
_soltar = threading.Event()        # solo para las pruebas: corta las esperas largas


@dataclass(frozen=True)
class Respuesta:
    aprobado: bool
    cargo_id: int | None = None
    motivo: str = ""


def cobrar(llave: str, pedido_id: int, monto_c: int, tarjeta: str) -> Future:
    """Pide el cobro. Devuelve un Future: quien llama decide cuánto lo espera."""
    with _candado:
        con = datos.conectar()
        try:
            generacion = datos.generacion(con)
            existente = _en_curso.get((generacion, llave))
            if existente is not None:
                return existente
            previo = con.execute("SELECT id FROM cargos WHERE llave = ? AND tipo = 'cargo'", (llave,)).fetchone()
            modo = datos.leer_control(con, "pasarela.modo", "aprueba")
            segundos = float(datos.leer_control(con, "pasarela.segundos", "0"))
        finally:
            con.close()
        futuro: Future = Future()
        if previo is not None:
            futuro.set_result(Respuesta(True, previo["id"]))
            return futuro
        _en_curso[(generacion, llave)] = futuro
    _hilos.submit(_procesar, futuro, generacion, llave, pedido_id, monto_c, tarjeta, modo, segundos)
    return futuro


# Las esperas («tarda», «no contesta») no ocupan una tarea de _hilos: las lleva un solo reloj que, al vencer cada
# una, manda a _hilos el trabajo corto que sigue. Así 40 cobros sin respuesta no dejan sin tareas al siguiente.
_agenda: list = []                 # montículo de (vence, n, generacion, trabajo)
_turno = itertools.count()
_reloj_cond = threading.Condition()
_soltadas: set = set()             # generaciones que la tienda ya dejó atrás: lo agendado en ellas vence ya


_log = logging.getLogger("tienda.pasarela")
_hilo_reloj: threading.Thread | None = None


def _agendar(segundos: float, generacion: int, trabajo) -> None:
    with _reloj_cond:
        heapq.heappush(_agenda, (time.monotonic() + segundos, next(_turno), generacion, trabajo))
        _asegurar_reloj()
        _reloj_cond.notify()


def _asegurar_reloj() -> None:
    """Si el reloj no está vivo, arranca otro. Sin reloj ninguna espera vence y la tienda se cuelga: es el mismo
    síntoma que tenía la pasarela cuando las esperas ocupaban tareas. Se llama con _reloj_cond tomado."""
    global _hilo_reloj
    if _hilo_reloj is None or not _hilo_reloj.is_alive():
        _hilo_reloj = threading.Thread(target=_reloj, name="pasarela-reloj", daemon=True)
        _hilo_reloj.start()


def _vencidos() -> list:
    """Espera a que algo de la agenda venza y lo saca. Se llama con _reloj_cond tomado."""
    while True:
        ahora = time.monotonic()
        vencidos = [x for x in _agenda if _vence(x, ahora)]
        if vencidos:
            ids = {id(x) for x in vencidos}
            _agenda[:] = [x for x in _agenda if id(x) not in ids]
            heapq.heapify(_agenda)
            return vencidos
        _reloj_cond.wait(min(_agenda[0][0] - ahora, 1.0) if _agenda else 1.0)


def _vence(x, ahora: float) -> bool:
    """Una entrada que no se puede leer cuenta como vencida: sale de la agenda y su tropiezo se anota al
    despacharla, en vez de atorar al reloj en un bucle que no deja vencer a ninguna otra."""
    try:
        return x[0] <= ahora or x[2] in _soltadas or _soltar.is_set()
    except Exception:  # noqa: BLE001
        return True


def _despachar(trabajo) -> None:
    try:
        _hilos.submit(trabajo)
    except RuntimeError:            # el pool ya no acepta tareas: el trabajo es corto y lo hace el reloj mismo
        trabajo()


def _reloj() -> None:
    """Un tropiezo con una entrada de la agenda no detiene al reloj: se anota y sigue con las demás."""
    while True:
        try:
            with _reloj_cond:
                vencidos = _vencidos()
        except Exception:  # noqa: BLE001 — el reloj no puede morir: sin él, ninguna espera vence
            _log.exception("el reloj de la pasarela tropezó al revisar la agenda; sigue")
            time.sleep(0.05)
            continue
        for x in vencidos:
            try:
                _despachar(x[3])
            except Exception:  # noqa: BLE001
                _log.exception("el reloj de la pasarela no pudo despachar una espera; sigue con las demás")


with _reloj_cond:
    _asegurar_reloj()


def _procesar(futuro: Future, generacion, llave, pedido_id, monto_c, tarjeta, modo, segundos) -> None:
    if modo == "no contesta":
        _agendar(TOPE_NO_CONTESTA_S, generacion,
                 lambda: _terminar(futuro, generacion, llave, TimeoutError("la pasarela nunca contestó")))
    elif modo == "tarda" and segundos > 0:
        _agendar(segundos, generacion, lambda: _contestar(futuro, generacion, llave, pedido_id, monto_c, tarjeta, modo))
    else:
        _contestar(futuro, generacion, llave, pedido_id, monto_c, tarjeta, modo)


def _terminar(futuro: Future, generacion, llave, resultado) -> None:
    try:
        if not futuro.done():
            if isinstance(resultado, BaseException):
                futuro.set_exception(resultado)
            else:
                futuro.set_result(resultado)
    finally:
        with _candado:
            if _en_curso.get((generacion, llave)) is futuro:
                del _en_curso[(generacion, llave)]


def _contestar(futuro: Future, generacion, llave, pedido_id, monto_c, tarjeta, modo) -> None:
    try:
        if modo == "rechaza":
            return _terminar(futuro, generacion, llave, Respuesta(False, motivo="la pasarela rechazó el pago"))
        con = datos.conectar()
        try:
            with datos.transaccion(con):
                # Dentro de la transacción: el reinicio también escribe con BEGIN IMMEDIATE, así que no se cruzan.
                if datos.generacion(con) != generacion:
                    return _terminar(futuro, generacion, llave,
                                     TimeoutError("la tienda se reinició: este cobro ya no se anota"))
                cur = con.execute("INSERT INTO cargos (llave, pedido_id, tipo, monto_c, tarjeta, cuando) "
                                  "VALUES (?, ?, 'cargo', ?, ?, ?)",
                                  (llave, pedido_id, monto_c, tarjeta, datos.ahora(con).isoformat()))
                # E7 «el cargo que llega tarde no se concilia». Con E4 la tienda tampoco concilia: manda cada reintento
                # como un cobro nuevo y pierde la cuenta de sus cobros; el doble cargo es lo que la L08 enseña a ver.
                if not (datos.error_encendido(con, "E7") or datos.error_encendido(con, "E4")):
                    _conciliar(con, pedido_id, llave, tarjeta)
            _terminar(futuro, generacion, llave, Respuesta(True, cur.lastrowid))
        finally:
            con.close()
    except Exception as exc:  # noqa: BLE001 — cualquier falla de la pasarela le llega a quien espera
        _terminar(futuro, generacion, llave, exc)


def _conciliar(con, pedido_id: int, llave: str, tarjeta: str) -> None:
    """Cuadra el pedido con su dinero justo después de anotar un cargo (adentro de la misma transacción)."""
    pedido = con.execute("SELECT estado, total_c FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    if pedido is None:
        return
    neto = _neto(con, pedido_id)
    if pedido["estado"] == "creado" and neto >= pedido["total_c"]:
        ahora = datos.ahora(con).isoformat()
        con.execute("UPDATE pedidos SET estado = 'pagado' WHERE id = ?", (pedido_id,))
        con.execute("INSERT INTO historial (pedido_id, estado, cuando) VALUES (?, 'pagado', ?)", (pedido_id, ahora))
        estado = "pagado"
    else:
        estado = pedido["estado"]
    le_toca = 0 if estado in ("creado", "cancelado") else pedido["total_c"]
    sobra = neto - le_toca if estado != "creado" else 0
    if sobra > 0:
        con.execute("INSERT INTO cargos (llave, pedido_id, tipo, monto_c, tarjeta, cuando) "
                    "VALUES (?, ?, 'reembolso', ?, ?, ?)",
                    (f"reembolso-{llave}", pedido_id, sobra, tarjeta, datos.ahora(con).isoformat()))


def _neto(con, pedido_id: int) -> int:
    return con.execute("SELECT COALESCE(SUM(CASE tipo WHEN 'cargo' THEN monto_c ELSE -monto_c END), 0) AS neto "
                       "FROM cargos WHERE pedido_id = ?", (pedido_id,)).fetchone()["neto"]


def reiniciada(generacion_vieja: int) -> None:
    """La tienda se reinició: lo que esperaba en esa generación (o antes) vence ya; al anotar, ve que la tienda
    cambió de generación y le contesta 504 a quien todavía esperara, sin cobrar."""
    with _reloj_cond:
        _soltadas.add(generacion_vieja)
        _asegurar_reloj()
        _reloj_cond.notify()


def reembolsar(con, pedido_id: int, tarjeta: str) -> int:
    """R9 — devuelve a la misma tarjeta lo que se cobró y aún no se ha devuelto. Regresa el monto devuelto."""
    fila = con.execute("SELECT COALESCE(SUM(CASE tipo WHEN 'cargo' THEN monto_c ELSE -monto_c END), 0) AS neto "
                       "FROM cargos WHERE pedido_id = ?", (pedido_id,)).fetchone()
    neto = fila["neto"]
    if neto > 0:
        con.execute("INSERT INTO cargos (llave, pedido_id, tipo, monto_c, tarjeta, cuando) "
                    "VALUES (?, ?, 'reembolso', ?, ?, ?)",
                    (f"reembolso-{pedido_id}", pedido_id, neto, tarjeta, datos.ahora(con).isoformat()))
    return neto


def soltar_esperas() -> None:
    """Para las pruebas: despierta los cobros que están esperando («tarda» o «no contesta»)."""
    with _reloj_cond:
        _soltar.set()
        pendientes = list(_agenda)
        _agenda.clear()
    for x in pendientes:
        try:
            _despachar(x[3])
        except Exception:  # noqa: BLE001
            _log.exception("no se pudo soltar una espera de la pasarela")


def rearmar() -> None:
    with _reloj_cond:
        _soltar.clear()
        _soltadas.clear()
