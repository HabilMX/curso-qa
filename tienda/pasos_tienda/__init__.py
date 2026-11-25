"""El catálogo de pasos de la tienda: las frases que el alumno puede usar en sus escenarios, en los cinco idiomas
del curso (es, en, fr, pt y bg).

El alumno no programa los pasos: escribe escenarios con estas frases y behave las conecta con la tienda de
verdad, por su API. Cada escenario empieza con la tienda recién abierta (los errores encendidos se quedan como
estaban: los decide el `verifica`).

El idioma sale del `# language:` del archivo .feature: con ese idioma se le pide todo a la tienda, así que los
nombres de producto y los mensajes que el escenario compara son los de ese idioma. Los montos van igual en los
cinco: $1,234.56.

Para usarlo, la carpeta de escenarios trae `steps/tienda.py` con una sola línea: `from pasos_tienda import *`.
"""

import json
import os
import re
import urllib.error
import urllib.request

from behave import step, use_step_matcher

try:  # adentro del contenedor los textos están a la vista del alumno, en /opt/pasos/textos_tienda
    import textos_tienda as textos
except ImportError:  # en el repo viven junto a la tienda; se cargan por ruta («tienda» lo tapa steps/tienda.py)
    import importlib.util
    import sys
    from pathlib import Path

    _ruta = Path(__file__).resolve().parents[1] / "tienda" / "textos" / "__init__.py"
    _spec = importlib.util.spec_from_file_location("textos_tienda", _ruta)
    textos = importlib.util.module_from_spec(_spec)
    sys.modules["textos_tienda"] = textos
    _spec.loader.exec_module(textos)

URL = os.environ.get("TIENDA_URL", "http://127.0.0.1:8080")
CLIENTES = {"marta": ("Marta", "marta-practica"), "luis": ("Luis", "luis-practica")}
ALIAS_CLIENTE = {"марта": "marta", "луис": "luis"}
MONTO = r"(?P<monto>\$?[\d,]+(?:\.\d{1,2})?)"
NOMBRE = r"(?P<cliente>[A-ZÁÉÍÓÚÑА-Я][a-záéíóúñа-я]+)"
APARECE = {"aparece", "appears", "apparaît", "се появява"}

# Artículos y contracciones que se quitan antes de buscar un producto por nombre (el más largo primero).
# Con espacio después, salvo el apóstrofo del francés: así «Thermos» o «Adesivo» no pierden su principio.
ARTICULOS = re.compile(r"^(?:(?:de la|de los|de las|la|el|los|las|una|un|de|the|an|a|le|les|du|des|"
                       r"da|do|das|dos|o|as|os|um|uma)\s+|(?:de l'|l')\s*)", re.I)
# En búlgaro el artículo va pegado al final: «синята тениска» es «синя тениска».
DEFINIDO_BG = {
    "синята тениска": "синя тениска", "сивата тениска": "сива тениска", "чорапите": "чорапи",
    "стикера": "стикер", "стикерът": "стикер", "раницата": "раница", "шапката с козирка": "шапка с козирка",
    "суитшърта": "суитшърт", "суитшъртът": "суитшърт", "маратонките": "маратонки", "якето": "яке",
    "часовника": "часовник", "часовникът": "часовник", "термоса": "термос", "термосът": "термос",
    "чашата": "чаша", "ключодържателя": "ключодържател", "ключодържателят": "ключодържател",
    "молива": "молив", "моливът": "молив", "значката": "значка",
}

use_step_matcher("re")
_idioma = "es"


def _m(clave: str, **datos) -> str:
    return textos.t(f"pasos.{clave}", _idioma, **datos)


# ---------------------------------------------------------------- cómo se habla con la tienda

class Respuesta:
    def __init__(self, codigo: int, cuerpo):
        self.codigo, self.cuerpo = codigo, cuerpo

    @property
    def mensaje(self) -> str:
        return self.cuerpo.get("mensaje", "") if isinstance(self.cuerpo, dict) else ""


def pedir(metodo: str, ruta: str, cuerpo=None, token: str = "") -> Respuesta:
    datos = None if cuerpo is None else json.dumps(cuerpo).encode()
    peticion = urllib.request.Request(URL + ruta, data=datos, method=metodo,
                                      headers={"Content-Type": "application/json", "Accept-Language": _idioma,
                                               **({"Authorization": f"Bearer {token}"} if token else {})})
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            return Respuesta(r.status, json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        return Respuesta(e.code, json.loads(e.read() or b"{}"))
    except urllib.error.URLError as e:
        raise AssertionError(_m("no_contesta", url=URL, motivo=e.reason)) from None


def centavos(texto: str) -> int:
    m = re.fullmatch(r"\$?\s*([\d,]+)(?:\.(\d{1,2}))?", texto.strip())
    if not m:
        raise AssertionError(_m("monto", texto=texto))
    return int(m.group(1).replace(",", "")) * 100 + int((m.group(2) or "0").ljust(2, "0"))


def pesos(c: int) -> str:
    return f"${c // 100:,}.{c % 100:02d}"


def idioma_del(context) -> str:
    """El idioma del archivo .feature (`# language: xx`); pt-BR cuenta como pt. Sin declarar, español."""
    feature = getattr(context, "feature", None)
    codigo = (getattr(feature, "language", None) or "es").lower()[:2]
    return codigo if codigo in textos.IDIOMAS else "es"


def _tienda(context):
    """La primera vez que un escenario toca la tienda, la deja recién abierta."""
    global _idioma
    _idioma = idioma_del(context)
    escenario = id(getattr(context, "scenario", None))
    if getattr(context, "_tienda_escenario", None) != escenario:
        r = pedir("POST", "/control/reinicio")
        assert r.codigo == 200, _m("no_reinicia", codigo=r.codigo, cuerpo=r.cuerpo)
        context._tienda_escenario = escenario
        context._tokens = {}
        context.cliente = "Marta"
        context.ultima = None


def _token(context, cliente: str | None = None) -> str:
    _tienda(context)
    if cliente:
        clave = ALIAS_CLIENTE.get(cliente.lower(), cliente.lower())
        context.cliente = CLIENTES[clave][0] if clave in CLIENTES else cliente
    clave = context.cliente.lower()
    if clave not in CLIENTES:
        raise AssertionError(_m("no_es_cliente", cliente=context.cliente))
    if clave not in context._tokens:
        nombre, contrasena = CLIENTES[clave]
        r = pedir("POST", "/api/sesiones", {"cliente": nombre, "contrasena": contrasena})
        assert r.codigo == 201, _m("no_entra", cliente=nombre, cuerpo=r.cuerpo)
        context._tokens[clave] = r.cuerpo["token"]
    return context._tokens[clave]


def _carrito(context) -> dict:
    r = pedir("GET", "/api/carrito", token=_token(context))
    assert r.codigo == 200, r.cuerpo
    return r.cuerpo


def _productos(context) -> list[dict]:
    _tienda(context)
    return pedir("GET", "/api/productos").cuerpo


def nombre_limpio(nombre: str) -> str:
    """El nombre de un producto sin artículo ni contracción: «la playera azul» → «playera azul»."""
    limpio = ARTICULOS.sub("", nombre.strip().lower(), count=1).strip()
    return DEFINIDO_BG.get(limpio, limpio)


def _producto(context, nombre: str) -> dict:
    buscado = nombre_limpio(nombre)
    for p in _productos(context):
        if p["nombre"].lower() == buscado or p["id"] == buscado:
            return p
    nombres = ", ".join(p["nombre"].lower() for p in _productos(context))
    raise AssertionError(_m("no_vende", producto=nombre.strip(), productos=nombres))


def armar(precios: dict[str, int], objetivo: int, tope: int = 10) -> dict[str, int] | None:
    """Qué piezas (hasta `tope` de cada producto) suman EXACTO el objetivo. None si no se puede."""
    productos = sorted(precios.items(), key=lambda p: -p[1])
    sin_salida: set[tuple[int, int]] = set()

    def buscar(i: int, falta: int) -> dict[str, int] | None:
        if falta == 0:
            return {}
        if i == len(productos) or (i, falta) in sin_salida:
            return None
        pid, precio = productos[i]
        for n in range(min(tope, falta // precio), -1, -1):
            resto = buscar(i + 1, falta - n * precio)
            if resto is not None:
                return ({pid: n} if n else {}) | resto
        sin_salida.add((i, falta))
        return None

    return buscar(0, objetivo)


def _llenar(context, piezas: dict[str, int]) -> None:
    token = _token(context)
    for p in _carrito(context)["productos"]:
        pedir("DELETE", f"/api/carrito/productos/{p['id']}", token=token)
    for pid, n in piezas.items():
        r = pedir("PUT", f"/api/carrito/productos/{pid}", {"cantidad": n}, token)
        assert r.codigo == 200, _m("no_pone", n=n, producto=pid, cuerpo=r.cuerpo)


def frases(*patrones):
    """Registra el mismo paso con varias frases: una por idioma."""
    def registrar(funcion):
        for patron in reversed(patrones):
            funcion = step(patron)(funcion)
        return funcion
    return registrar


# ---------------------------------------------------------------- Dado

@frases(r"que el cupón (?P<codigo>\S+) está vigente",
        r"the (?P<codigo>\S+) coupon is in force",
        r"le coupon (?P<codigo>\S+) est en vigueur",
        r"(?:que )?o cupom (?P<codigo>\S+) está vigente",
        r"купонът (?P<codigo>\S+) е в сила")
def cupon_vigente(context, codigo):
    _tienda(context)
    r = pedir("PUT", "/control/reloj", {"ahora": None})
    assert r.codigo == 200, r.cuerpo


@frases(rf"(?:que )?{NOMBRE} no ha usado nunca el cupón (?P<codigo>\S+)",
        rf"{NOMBRE} has never used the (?P<codigo>\S+) coupon",
        rf"{NOMBRE} n'a jamais utilisé le coupon (?P<codigo>\S+)",
        rf"(?:que )?{NOMBRE} nunca usou o cupom (?P<codigo>\S+)",
        rf"{NOMBRE} никога не е използвала? купона (?P<codigo>\S+)")
def nunca_uso(context, cliente, codigo):
    _token(context, cliente)
    r = pedir("PUT", f"/control/clientes/{context.cliente}/cupones/{codigo}", {"usado": False})
    assert r.codigo == 200, r.cuerpo


@frases(rf"(?:que )?{NOMBRE} ya usó el cupón (?P<codigo>\S+) en una compra anterior",
        rf"{NOMBRE} already used the (?P<codigo>\S+) coupon on a previous purchase",
        rf"{NOMBRE} a déjà utilisé le coupon (?P<codigo>\S+) lors d'un achat précédent",
        rf"(?:que )?{NOMBRE} já usou o cupom (?P<codigo>\S+) em uma compra anterior",
        rf"{NOMBRE} вече е използвала? купона (?P<codigo>\S+) при предишна покупка")
def ya_uso(context, cliente, codigo):
    _token(context, cliente)
    r = pedir("PUT", f"/control/clientes/{context.cliente}/cupones/{codigo}", {"usado": True})
    assert r.codigo == 200, r.cuerpo


@frases(rf"(?:que )?(?:{NOMBRE} )?tiene en su carrito productos por {MONTO}",
        rf"(?:(?:{NOMBRE}|she|he) )?has products worth {MONTO} in (?:her|his) cart",
        rf"(?:(?:{NOMBRE}|elle|il) )?a dans son panier des produits pour {MONTO}",
        rf"(?:que )?(?:(?:{NOMBRE}|ela|ele) )?tem no carrinho produtos no valor de {MONTO}",
        rf"(?:(?:{NOMBRE}|тя|той) )?има в количката си продукти за {MONTO}")
def carrito_por(context, monto, cliente=None):
    _token(context, cliente)
    objetivo = centavos(monto)
    piezas = armar({p["id"]: p["precio"]["centavos"] for p in _productos(context)}, objetivo)
    assert piezas is not None, _m("no_se_arma", monto=monto)
    _llenar(context, piezas)
    assert _carrito(context)["subtotal"]["centavos"] == objetivo


@frases(rf"(?:que )?(?:{NOMBRE} )?tiene (?P<producto>(?:la|el|una|un) .+) en su carrito",
        rf"(?:(?:{NOMBRE}|she|he) )?has (?P<producto>(?:the|a|an) .+) in (?:her|his) cart",
        rf"(?:(?:{NOMBRE}|elle|il) )?a (?P<producto>(?:le |la |l'|un |une ).+) dans son panier",
        rf"(?:que )?(?:(?:{NOMBRE}|ela|ele) )?tem (?P<producto>(?:a|o|um|uma) .+) no carrinho",
        rf"(?:(?:{NOMBRE}|тя|той) )?има (?P<producto>[^\d\s].*) в количката си")
def tiene_producto(context, producto, cliente=None):
    _token(context, cliente)
    _llenar(context, {_producto(context, producto)["id"]: 1})


@frases(rf"(?:que )?(?:{NOMBRE} )?no tiene ningún cupón aplicado",
        rf"(?:(?:{NOMBRE}|she|he) )?has no coupon applied",
        rf"(?:(?:{NOMBRE}|elle|il) )?n'a aucun coupon appliqué",
        rf"(?:que )?(?:(?:{NOMBRE}|ela|ele) )?não tem nenhum cupom aplicado",
        rf"(?:(?:{NOMBRE}|тя|той) )?няма приложен никакъв купон")
def sin_cupon(context, cliente=None):
    r = pedir("DELETE", "/api/carrito/cupon", token=_token(context, cliente))
    assert r.codigo == 200, r.cuerpo


@frases(rf"(?:que )?(?:{NOMBRE} )?tiene (?P<n>\d+) piezas? de (?P<producto>.+) en su carrito",
        rf"(?:(?:{NOMBRE}|she|he) )?has (?P<n>\d+) pieces? of (?P<producto>.+) in (?:her|his) cart",
        rf"(?:(?:{NOMBRE}|elle|il) )?a (?P<n>\d+) pièces? (?P<producto>.+) dans son panier",
        rf"(?:que )?(?:(?:{NOMBRE}|ela|ele) )?tem (?P<n>\d+) peças? (?P<producto>.+) no carrinho",
        rf"(?:(?:{NOMBRE}|тя|той) )?има (?P<n>\d+) бр\. от (?P<producto>.+) в количката си")
def tiene_piezas(context, n, producto, cliente=None):
    _token(context, cliente)
    _llenar(context, {_producto(context, producto)["id"]: int(n)})


# ---------------------------------------------------------------- Cuando

@frases(r"aplica el cupón (?P<codigo>\S+)",
        r"(?:she |he )?applies the (?P<codigo>\S+) coupon",
        r"(?:elle |il )?applique le coupon (?P<codigo>\S+)",
        r"(?:ela |ele )?aplica o cupom (?P<codigo>\S+)",
        r"(?:тя |той )?приложи купона (?P<codigo>\S+)")
def aplica_cupon(context, codigo):
    context.antes = _carrito(context)
    context.ultima = pedir("POST", "/api/carrito/cupon", {"codigo": codigo}, _token(context))


@frases(r"pasa a pagar",
        r"(?:she |he )?goes to pay",
        r"(?:elle |il )?passe au paiement",
        r"(?:ela |ele )?vai pagar",
        r"(?:тя |той )?премине към плащане")
def pasa_a_pagar(context):
    context.ultima = pedir("GET", "/api/carrito", token=_token(context))


@frases(r"elige cómo pagar",
        r"(?:she |he )?chooses how to pay",
        r"(?:elle |il )?choisit comment payer",
        r"(?:ela |ele )?escolhe como pagar",
        r"(?:тя |той )?избира как да плати")
def elige_como_pagar(context):
    context.ultima = pedir("GET", "/api/carrito/formas-de-pago", token=_token(context))


@frases(r"deja vacía la cantidad",
        r"(?:she |he )?leaves the quantity empty",
        r"(?:elle |il )?laisse la quantité vide",
        r"(?:ela |ele )?deixa a quantidade vazia",
        r"(?:тя |той )?остави количеството празно")
def deja_vacia(context):
    _cambiar(context, "")


@frases(r"cambia la cantidad a ?(?P<piezas>.*)",
        r"(?:she |he )?changes the quantity to ?(?P<piezas>.*)",
        r"(?:elle |il )?change la quantité à ?(?P<piezas>.*)",
        r"(?:ela |ele )?muda a quantidade para ?(?P<piezas>.*)",
        r"(?:тя |той )?смени количеството на ?(?P<piezas>.*)")
def cambia_cantidad(context, piezas):
    texto = piezas.strip()
    try:
        valor = int(texto)
    except ValueError:
        try:
            valor = float(texto)
        except ValueError:
            valor = texto
    _cambiar(context, valor)


def _cambiar(context, valor):
    """Cambia la cantidad del producto que está en el carrito (el escenario pone uno solo)."""
    carrito = _carrito(context)
    assert carrito["productos"], _m("sin_producto")
    pid = carrito["productos"][0]["id"]
    context.ultima = pedir("PUT", f"/api/carrito/productos/{pid}", {"cantidad": valor}, _token(context))


# ---------------------------------------------------------------- Entonces

def _vista(context) -> dict:
    assert context.ultima is not None, _m("falta_cuando")
    return context.ultima.cuerpo


@frases(r"la tienda le muestra que el cupón quedó aplicado",
        r"the store shows (?:her|him) that the coupon was applied",
        r"la boutique lui montre que le coupon a été appliqué",
        r"a loja mostra a (?:ela|ele) que o cupom foi aplicado",
        r"магазинът (?:ѝ|му) показва, че купонът е приложен")
def cupon_aplicado(context):
    vista = _vista(context)
    assert context.ultima.codigo == 200, _m("no_aplico", mensaje=context.ultima.mensaje)
    assert vista.get("cupon") and vista["cupon"]["aplicado"], _m("cupon_no_aplicado", cupon=vista.get("cupon"))


@frases(rf"la tienda le muestra un descuento de {MONTO}",
        rf"the store shows (?:her|him) a discount of {MONTO}",
        rf"la boutique lui montre une réduction de {MONTO}",
        rf"a loja mostra a (?:ela|ele) um desconto de {MONTO}",
        rf"магазинът (?:ѝ|му) показва отстъпка от {MONTO}")
def descuento_de(context, monto):
    vista = _vista(context)
    assert "descuento" in vista, _m("sin_descuento", mensaje=context.ultima.mensaje)
    real = vista["descuento"]["centavos"]
    assert real == centavos(monto), _m("descuento", real=pesos(real), esperado=monto)


@frases(r"la tienda le dice que (?P<mensaje>.+)",
        r"the store tells (?:her|him) (?:that )?(?P<mensaje>.+)",
        r"la boutique lui dit (?:que |qu')(?P<mensaje>.+)",
        r"a loja diz a (?:ela|ele) que (?P<mensaje>.+)",
        r"магазинът (?:ѝ|му) казва, че (?P<mensaje>.+)")
def le_dice(context, mensaje):
    _vista(context)
    real = context.ultima.mensaje
    assert real.strip().lower() == mensaje.strip().lower(), _m("dijo", real=real or _m("nada"), esperado=mensaje)


@frases(rf"el envío que le muestra la tienda es de {MONTO}",
        rf"the shipping the store shows (?:her|him) is {MONTO}",
        rf"la livraison que lui montre la boutique est de {MONTO}",
        rf"o frete que a loja mostra a (?:ela|ele) é de {MONTO}",
        rf"доставката, която (?:ѝ|му) показва магазинът, е {MONTO}")
def envio_de(context, monto):
    vista = _vista(context)
    real = vista["envio"]["centavos"]
    assert real == centavos(monto), _m("envio", real=pesos(real), esperado=monto)


@frases(rf"el total que le muestra la tienda es de {MONTO}",
        rf"the total the store shows (?:her|him) is {MONTO}",
        rf"le total que lui montre la boutique est de {MONTO}",
        rf"o total que a loja mostra a (?:ela|ele) é de {MONTO}",
        rf"общата сума, която (?:ѝ|му) показва магазинът, е {MONTO}")
def total_de(context, monto):
    """El total de la última respuesta (el carrito o las formas de pago); si no lo trae, el del carrito."""
    vista = _vista(context)
    total = vista.get("total") if isinstance(vista, dict) else None
    real = (total or _carrito(context)["total"])["centavos"]
    assert real == centavos(monto), _m("total", real=pesos(real), esperado=monto)


@frases(r"la opción de meses sin intereses (?P<aparece>aparece|no aparece)",
        r"the interest-free installments option (?P<aparece>appears|does not appear)",
        r"l'option des mensualités sans intérêts (?P<aparece>apparaît|n'apparaît pas)",
        r"a opção de parcelas sem juros (?P<aparece>aparece|não aparece)",
        r"опцията за безлихвени вноски (?P<aparece>се появява|не се появява)")
def meses(context, aparece):
    vista = _vista(context)
    esperado = aparece in APARECE
    real = vista["meses_sin_intereses"]
    assert real is esperado, _m("meses_aparece" if real else "meses_no_aparece", total=vista["total"]["texto"])


@frases(r"su carrito muestra (?P<piezas>-?\d+) piezas? de (?P<producto>.+)",
        r"(?:her|his) cart shows (?P<piezas>-?\d+) pieces? of (?P<producto>.+)",
        r"son panier affiche (?P<piezas>-?\d+) pièces? (?P<producto>.+)",
        r"o carrinho (?:dela|dele) mostra (?P<piezas>-?\d+) peças? (?P<producto>.+)",
        r"количката (?:ѝ|му) показва (?P<piezas>-?\d+) бр\. от (?P<producto>.+)")
def carrito_muestra(context, piezas, producto):
    pid = _producto(context, producto)["id"]
    linea = next((p for p in _carrito(context)["productos"] if p["id"] == pid), None)
    real = linea["cantidad"] if linea else 0
    assert real == int(piezas), _m("piezas", real=real, producto=producto, esperado=piezas)


@frases(rf"su subtotal sigue en {MONTO}",
        rf"(?:her|his) subtotal is still {MONTO}",
        rf"son sous-total reste à {MONTO}",
        rf"o subtotal (?:dela|dele) continua em {MONTO}",
        rf"междинната (?:ѝ|му) сума остава {MONTO}")
def subtotal_sigue(context, monto):
    real = _carrito(context)["subtotal"]["centavos"]
    assert real == centavos(monto), _m("subtotal", real=pesos(real), esperado=monto)


@frases(r"su carrito sigue con (?P<piezas>\d+) piezas? de (?P<producto>.+)",
        r"(?:her|his) cart still has (?P<piezas>\d+) pieces? of (?P<producto>.+)",
        r"son panier contient toujours (?P<piezas>\d+) pièces? (?P<producto>.+)",
        r"o carrinho (?:dela|dele) continua com (?P<piezas>\d+) peças? (?P<producto>.+)",
        r"количката (?:ѝ|му) остава с (?P<piezas>\d+) бр\. от (?P<producto>.+)")
def carrito_sigue_con(context, piezas, producto):
    carrito_muestra(context, piezas, producto)


__all__ = []  # los pasos se registran al importar; no hay nada más que exportar


# ---------------------------------------------------------------- pedidos (L04 «Estados y orden»)
# El estado se escribe como lo dice la tienda en cada idioma (estado.* de los textos) y se traduce de vuelta a su
# clave, que es la que contesta la API (los estados no se traducen en el JSON).

ORDEN = ["creado", "pagado", "en almacén", "enviado", "entregado"]
_ESTADOS = {}
for _l in textos.IDIOMAS:
    for _k, _v in textos.catalogo(_l).items():
        if _k.startswith("estado."):
            _ESTADOS[_v.lower()] = _k[len("estado."):]
ESTADO = "(?P<estado>" + "|".join(re.escape(e) for e in sorted(_ESTADOS, key=len, reverse=True)) + ")"


def _estado(texto: str) -> str:
    return _ESTADOS[texto.strip().lower()]


def _como_se_dice(clave: str) -> str:
    return textos.t(f"estado.{clave}", _idioma)


def _pagar(context) -> Respuesta:
    """Un pago nuevo, con su propia llave de idempotencia (la misma llave repetiría la respuesta y no cobraría)."""
    datos = json.dumps({"tarjeta": "4242424242424242", "meses": 0}).encode()
    peticion = urllib.request.Request(f"{URL}/api/pedidos/{context.pedido}/pago", data=datos, method="POST",
                                      headers={"Content-Type": "application/json", "Accept-Language": _idioma,
                                               "Authorization": f"Bearer {_token(context)}",
                                               "Idempotency-Key": os.urandom(16).hex()})
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            return Respuesta(r.status, json.loads(r.read() or b"{}"))
    except urllib.error.HTTPError as e:
        return Respuesta(e.code, json.loads(e.read() or b"{}"))


@frases(rf"(?:que )?(?:{NOMBRE} )?tiene un pedido {ESTADO}",
        rf"(?:(?:{NOMBRE}|she|he) )?has an order that is {ESTADO}",
        rf"(?:(?:{NOMBRE}|elle|il) )?a une commande {ESTADO}",
        rf"(?:que )?(?:(?:{NOMBRE}|ela|ele) )?tem um pedido {ESTADO}",
        rf"(?:(?:{NOMBRE}|тя|той) )?има поръчка, която е {ESTADO}")
def tiene_pedido(context, estado, cliente=None):
    """Recorre el camino real hasta ese estado: arma el carrito, crea el pedido, lo paga y el almacén lo avanza."""
    destino = _estado(estado)
    token = _token(context, cliente)
    r = pedir("PUT", "/api/carrito/productos/playera-azul", {"cantidad": 1}, token)
    assert r.codigo == 200, _m("no_llega_a", estado=estado, cuerpo=r.cuerpo)
    r = pedir("POST", "/api/pedidos", {}, token)
    assert r.codigo == 201, _m("no_llega_a", estado=estado, cuerpo=r.cuerpo)
    context.pedido = r.cuerpo["id"]
    if destino == "cancelado":
        r = pedir("POST", f"/api/pedidos/{context.pedido}/cancelacion", {}, token)
        assert r.codigo == 200, _m("no_llega_a", estado=estado, cuerpo=r.cuerpo)
        return
    if ORDEN.index(destino) >= 1:
        r = _pagar(context)
        assert r.codigo == 200, _m("no_llega_a", estado=estado, cuerpo=r.cuerpo)
    for _ in range(max(0, ORDEN.index(destino) - 1)):
        r = pedir("POST", f"/control/pedidos/{context.pedido}/avance")
        assert r.codigo == 200, _m("no_llega_a", estado=estado, cuerpo=r.cuerpo)


@frases(r"cancela el pedido",
        r"(?:she |he )?cancels the order",
        r"(?:elle |il )?annule la commande",
        r"(?:ela |ele )?cancela o pedido",
        r"(?:тя |той )?отмени поръчката")
def cancela_pedido(context):
    context.ultima = pedir("POST", f"/api/pedidos/{context.pedido}/cancelacion", {}, _token(context))


@frases(r"intenta pagar el pedido",
        r"(?:she |he )?tries to pay the order",
        r"(?:elle |il )?essaie de payer la commande",
        r"(?:ela |ele )?tenta pagar o pedido",
        r"(?:тя |той )?се опита да плати поръчката")
def intenta_pagar(context):
    context.ultima = _pagar(context)


@frases(r"el almacén avanza el pedido",
        r"the warehouse advances the order",
        r"l'entrepôt fait avancer la commande",
        r"o armazém avança o pedido",
        r"складът придвижи поръчката напред")
def almacen_avanza(context):
    _tienda(context)
    context.ultima = pedir("POST", f"/control/pedidos/{context.pedido}/avance")


@frases(rf"el pedido (?:queda|sigue) {ESTADO}",
        rf"the order (?:becomes|stays) {ESTADO}",
        rf"la commande (?:devient|reste) {ESTADO}",
        rf"o pedido (?:fica|continua) {ESTADO}",
        rf"поръчката (?:става|остава) {ESTADO}")
def pedido_queda(context, estado):
    real = pedir("GET", f"/api/pedidos/{context.pedido}", token=_token(context)).cuerpo["estado"]
    assert real == _estado(estado), _m("estado", real=_como_se_dice(real), esperado=estado)


@frases(rf"le devuelven {MONTO} a su tarjeta",
        rf"they refund {MONTO} to (?:her|his) card",
        rf"on lui rembourse {MONTO} sur sa carte",
        rf"devolvem {MONTO} ao cartão (?:dela|dele)",
        rf"(?:ѝ|му) връщат {MONTO} по картата")
def le_devuelven(context, monto):
    cuerpo = _vista(context) or {}
    real = (cuerpo.get("reembolso") or {}).get("centavos", 0) if isinstance(cuerpo, dict) else 0
    assert real == centavos(monto), _m("reembolso", real=pesos(real), esperado=monto)
