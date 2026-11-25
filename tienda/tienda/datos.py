"""Dónde vive el estado de la tienda: un archivo SQLite.

Todo lo que la tienda recuerda —carritos, pedidos, cargos, el reloj, la pasarela y qué errores están
encendidos— vive aquí, para que sobreviva a que el proceso se reinicie y para que el `verifica` lo pueda medir.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ZONA = ZoneInfo("America/Mexico_City")
ERRORES = ("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8")

# (id, nombre, precio en centavos, categoría). Los primeros seis llegan EXACTO a las orillas de las lecciones:
# 3 playeras azules = $999.00 · azul + azul + gris = $998.99 · la estampa suma o resta un centavo ·
# la mochila es la orilla de meses sin intereses · 3 azules + gorra = $1,110.00, con cupón $999.00 (L03).
CATALOGO = (
    ("playera-azul", "Playera azul", 33300, "Playeras"),
    ("playera-gris", "Playera gris", 33299, "Playeras"),
    ("calcetines", "Calcetines", 12000, "Accesorios"),
    ("estampa", "Estampa", 1, "Accesorios"),
    ("mochila", "Mochila", 299999, "Mochilas"),
    ("gorra", "Gorra", 11100, "Accesorios"),
    ("sudadera", "Sudadera", 64900, "Sudaderas"),
    ("tenis", "Tenis", 149900, "Calzado"),
    ("chamarra", "Chamarra", 499900, "Chamarras"),
    ("reloj", "Reloj", 799900, "Accesorios"),
    ("termo", "Termo", 25990, "Accesorios"),
    ("taza", "Taza", 17500, "Accesorios"),
    ("llavero", "Llavero", 4999, "Accesorios"),
    ("lapiz", "Lápiz", 1350, "Accesorios"),
    ("pin", "Pin", 11, "Accesorios"),
)
# Los últimos cuatro no salen en las lecciones: están para que el catálogo de pasos pueda armar un carrito de
# EXACTAMENTE el monto que el alumno escriba en su escenario (p. ej. $2,999.98), sin pasar de 10 piezas por producto.

CLIENTES = (("Marta", "marta-practica"), ("Luis", "luis-practica"))

CUPON = "BIENVENIDA10"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS productos (id TEXT PRIMARY KEY, nombre TEXT NOT NULL, precio_c INTEGER NOT NULL,
    categoria TEXT NOT NULL, orden INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE COLLATE NOCASE,
    contrasena TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sesiones (token TEXT PRIMARY KEY, cliente_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS carritos (cliente_id INTEGER PRIMARY KEY, cupon TEXT);
CREATE TABLE IF NOT EXISTS carrito_productos (cliente_id INTEGER NOT NULL, producto_id TEXT NOT NULL,
    cantidad INTEGER NOT NULL, PRIMARY KEY (cliente_id, producto_id));
CREATE TABLE IF NOT EXISTS cupones (codigo TEXT PRIMARY KEY, por_ciento INTEGER NOT NULL,
    minimo_c INTEGER NOT NULL, vence TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cupon_usos (cliente_id INTEGER NOT NULL, codigo TEXT NOT NULL, pedido_id INTEGER);
CREATE UNIQUE INDEX IF NOT EXISTS cupon_una_vez ON cupon_usos (cliente_id, codigo);
CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, cliente_id INTEGER NOT NULL, estado TEXT NOT NULL,
    subtotal_c INTEGER NOT NULL, descuento_c INTEGER NOT NULL, envio_c INTEGER NOT NULL, total_c INTEGER NOT NULL,
    cupon TEXT, meses INTEGER NOT NULL DEFAULT 0, tarjeta TEXT, creado TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pedido_productos (pedido_id INTEGER NOT NULL, producto_id TEXT NOT NULL,
    nombre TEXT NOT NULL, precio_c INTEGER NOT NULL, cantidad INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS historial (pedido_id INTEGER NOT NULL, estado TEXT NOT NULL, cuando TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pagos (llave TEXT PRIMARY KEY, pedido_id INTEGER NOT NULL, estado TEXT NOT NULL,
    codigo INTEGER, respuesta TEXT);
CREATE TABLE IF NOT EXISTS cargos (id INTEGER PRIMARY KEY, llave TEXT NOT NULL, pedido_id INTEGER NOT NULL,
    tipo TEXT NOT NULL, monto_c INTEGER NOT NULL, tarjeta TEXT, cuando TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS control (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);
"""

TABLAS_DE_DATOS = ("productos", "clientes", "sesiones", "carritos", "carrito_productos", "cupones", "cupon_usos",
                   "pedidos", "pedido_productos", "historial", "pagos", "cargos")


def ruta() -> Path:
    return Path(os.environ.get("TIENDA_DATOS", Path.home() / ".tienda" / "tienda.db"))


def conectar() -> sqlite3.Connection:
    archivo = ruta()
    archivo.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(archivo, timeout=10, isolation_level=None, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=10000")
    return con


@contextmanager
def transaccion(con: sqlite3.Connection):
    """BEGIN IMMEDIATE: toma el candado de escritura al empezar, para que dos pagos no se crucen a la mitad."""
    con.execute("BEGIN IMMEDIATE")
    try:
        yield con
    except BaseException:
        con.execute("ROLLBACK")
        raise
    con.execute("COMMIT")


# ---------------------------------------------------------------- control: reloj, pasarela y errores

def leer_control(con, clave: str, omision: str = "") -> str:
    fila = con.execute("SELECT valor FROM control WHERE clave = ?", (clave,)).fetchone()
    return fila["valor"] if fila else omision


def generacion(con) -> int:
    """La generación de la tienda: sube con cada reinicio."""
    return int(leer_control(con, "tienda.generacion", "0"))


def escribir_control(con, clave: str, valor: str) -> None:
    con.execute("INSERT INTO control (clave, valor) VALUES (?, ?) "
                "ON CONFLICT (clave) DO UPDATE SET valor = excluded.valor", (clave, valor))


def error_encendido(con, error: str) -> bool:
    return leer_control(con, f"error.{error}", "off") == "on"


def ahora(con) -> datetime:
    """La hora de la tienda: la real más el desfase que alguien fijó. Sigue corriendo después de fijarla."""
    desfase = float(leer_control(con, "reloj.desfase", "0"))
    return datetime.now(ZONA) + timedelta(seconds=desfase)


def fijar_reloj(con, cuando: datetime | None) -> None:
    if cuando is None:
        escribir_control(con, "reloj.desfase", "0")
        return
    if cuando.tzinfo is None:
        cuando = cuando.replace(tzinfo=ZONA)
    escribir_control(con, "reloj.desfase", str((cuando - datetime.now(ZONA)).total_seconds()))


# ---------------------------------------------------------------- estado inicial

def preparar(con) -> None:
    """Crea las tablas y, si la tienda está vacía, la llena con su estado inicial."""
    con.executescript(ESQUEMA)
    if con.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0:
        reiniciar(con)


def reiniciar(con) -> None:
    """Deja la tienda como recién abierta: catálogo, clientes de prueba, el cupón, sin pedidos, pasarela que
    aprueba y reloj real. Los errores encendidos NO se tocan: eso lo decide quien los encendió."""
    con.executescript(ESQUEMA)
    with transaccion(con):
        for tabla in TABLAS_DE_DATOS:
            con.execute(f"DELETE FROM {tabla}")
        con.executemany("INSERT INTO productos (id, nombre, precio_c, categoria, orden) VALUES (?, ?, ?, ?, ?)",
                        [(*p, i) for i, p in enumerate(CATALOGO)])
        con.executemany("INSERT INTO clientes (nombre, contrasena) VALUES (?, ?)", CLIENTES)
        # Cada reinicio abre una generación nueva: la pasarela no anota los cobros que nacieron en otra.
        escribir_control(con, "tienda.generacion", str(generacion(con) + 1))
        escribir_control(con, "reloj.desfase", "0")
        escribir_control(con, "pasarela.modo", "aprueba")
        escribir_control(con, "pasarela.segundos", "0")
        # El cupón vence el 31 de diciembre del año en que se abre la tienda, a las 23:59:59.999 de la Ciudad
        # de México. Se calcula al reiniciar, no se escribe fijo: así la tienda sirve igual el año que entra.
        anio = ahora(con).year
        vence = datetime(anio, 12, 31, 23, 59, 59, 999000, tzinfo=ZONA)
        con.execute("INSERT INTO cupones (codigo, por_ciento, minimo_c, vence) VALUES (?, 10, 50000, ?)",
                    (CUPON, vence.isoformat()))
