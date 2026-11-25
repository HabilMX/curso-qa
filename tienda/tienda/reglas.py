"""Las reglas de negocio de la tienda, en funciones puras: sin base de datos ni HTTP.

Cada regla dice de qué renglón de la especificación sale (R1…R11) y, si un error sembrado la tuerce, cuál (E1…E8).
"""

from dataclasses import dataclass

from . import dinero, textos

UMBRAL_ENVIO_GRATIS_C = 99900      # R5: desde $999.00
COSTO_ENVIO_C = 9900               # R5: abajo, $99.00
MSI_DESDE_C = 300000               # R7: desde $3,000.00
MSI_HASTA_C = 5000000              # R7: hasta $50,000.00
PIEZAS_MIN = 1                     # R6
PIEZAS_MAX = 10                    # R6

ESTADOS = ("creado", "pagado", "en almacén", "enviado", "entregado")   # R8, en orden
CANCELADO = "cancelado"
CANCELABLES = ("creado", "pagado", "en almacén")                          # R9: mientras no salga del almacén


class ReglaRota(Exception):
    """Lo que el cliente intentó no se puede. `clave` es el texto que la tienda le muestra (textos/xx.json), que
    sale en el idioma de quien preguntó; `mensaje` es ese texto en español."""

    def __init__(self, clave: str, codigo: int = 422, **datos):
        super().__init__(clave)
        self.clave = clave
        self.codigo = codigo
        self.datos = datos

    def en(self, idioma: str) -> str:
        # un estado de pedido va como dato («pagado») y se muestra en el idioma de quien pregunta
        datos = {k: textos.t(f"estado.{v}", idioma) if k == "estado" else v for k, v in self.datos.items()}
        return textos.t(self.clave, idioma, **datos)

    @property
    def mensaje(self) -> str:
        return self.en("es")


def costo_envio(mercancia_c: int, e1_encendido: bool = False) -> int:
    """R5 — el envío es gratis cuando lo que se paga por la mercancía, YA CON EL CUPÓN, es desde $999.00.

    Es la ÚNICA función que decide el envío (decisión de la PO del 21-nov: se mide después del cupón).
    E1 «límite corrido»: compara con > en vez de >=, y un carrito de exactamente $999.00 paga $99.00.
    """
    gratis = mercancia_c > UMBRAL_ENVIO_GRATIS_C if e1_encendido else mercancia_c >= UMBRAL_ENVIO_GRATIS_C
    return 0 if gratis else COSTO_ENVIO_C


def descuento_cupon(subtotal_c: int, por_ciento: int, minimo_c: int) -> int:
    """R1 y R2 — el 10% del subtotal, sin contar el envío; nada si el subtotal no llega al mínimo."""
    return dinero.porcentaje(subtotal_c, por_ciento) if subtotal_c >= minimo_c else 0


def meses_disponibles(total_c: int) -> bool:
    """R7 — meses sin intereses desde $3,000.00 y hasta $50,000.00, las dos orillas incluidas."""
    return MSI_DESDE_C <= total_c <= MSI_HASTA_C


def validar_cantidad(valor) -> int:
    """R6 — de 1 a 10 piezas, enteras, y obligatoria (L02). Acepta el número tal cual llegó en el JSON o como texto."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ReglaRota("error.cantidad_obligatoria")
    if isinstance(valor, bool):
        raise ReglaRota("error.cantidad_numero")
    if isinstance(valor, str):
        texto = valor.strip()
        try:
            valor = int(texto)
        except ValueError:
            try:
                valor = float(texto)
            except ValueError:
                raise ReglaRota("error.cantidad_numero") from None
    if isinstance(valor, float):
        if valor != valor or valor in (float("inf"), float("-inf")):
            raise ReglaRota("error.cantidad_numero")
        if not valor.is_integer():
            raise ReglaRota("error.cantidad_entera")
        valor = int(valor)
    if not isinstance(valor, int):
        raise ReglaRota("error.cantidad_numero")
    if valor < PIEZAS_MIN:
        raise ReglaRota("error.cantidad_minima")
    if valor > PIEZAS_MAX:
        raise ReglaRota("error.cantidad_maxima")
    return valor


@dataclass(frozen=True)
class Cuenta:
    """Lo que cuesta un carrito o un pedido, en centavos."""

    subtotal_c: int
    descuento_c: int
    envio_c: int

    @property
    def mercancia_c(self) -> int:
        return self.subtotal_c - self.descuento_c

    @property
    def total_c(self) -> int:
        return self.mercancia_c + self.envio_c


def cuenta(subtotal_c: int, cupon: tuple[int, int] | None, e1_encendido: bool = False) -> Cuenta:
    """Subtotal → descuento del cupón (si hay y aplica) → envío sobre lo que queda → total.

    `cupon` es (por_ciento, minimo_c) o None. Un carrito vacío no paga envío.
    """
    descuento = descuento_cupon(subtotal_c, *cupon) if cupon else 0
    envio = 0 if subtotal_c == 0 else costo_envio(subtotal_c - descuento, e1_encendido)
    return Cuenta(subtotal_c, descuento, envio)


def puede_cancelarse(estado: str, e3_encendido: bool = False) -> bool:
    """R9 — se cancela mientras no haya salido del almacén.

    E3 «cancelar lo entregado»: deja cancelar también lo enviado y lo entregado (y lo reembolsa).
    """
    if estado == CANCELADO:
        return False
    if e3_encendido:
        return True
    return estado in CANCELABLES


def siguiente_estado(estado: str) -> str:
    """R8 — creado → pagado → en almacén → enviado → entregado."""
    if estado not in ESTADOS or estado == ESTADOS[-1]:
        raise ReglaRota("error.no_avanza", 409, estado=estado)
    if estado == ESTADOS[0]:
        # Avanzar es el almacén o la paquetería: a «pagado» solo se llega con un pago aprobado.
        raise ReglaRota("error.sin_pagar", 409)
    return ESTADOS[ESTADOS.index(estado) + 1]
