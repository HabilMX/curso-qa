"""Los textos que ve el alumno, en los cinco idiomas del curso: es, en, fr, pt y bg.

Cada idioma es un JSON con las mismas claves que `es.json`. Si a un idioma le falta una clave, sale en español
(y la prueba `test_textos_completos` lo marca). Los montos van igual en los cinco: $1,234.56, como en las lecciones.

El idioma de una petición sale de, en este orden: el parámetro `?idioma=`, el encabezado Accept-Language, y el idioma
con el que se levantó la tienda (TIENDA_IDIOMA, que fija el `practicar`). Si nada aplica, español.
"""

import json
import os
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

IDIOMAS = ("es", "en", "fr", "pt", "bg")
_DE_LA_PETICION: ContextVar[str | None] = ContextVar("idioma", default=None)
_AQUI = Path(__file__).parent


@lru_cache(maxsize=None)
def catalogo(idioma: str) -> dict[str, str]:
    archivo = _AQUI / f"{idioma}.json"
    if not archivo.exists():
        return {}
    return {k: v for k, v in json.loads(archivo.read_text(encoding="utf-8")).items() if not k.startswith("_")}


def omision() -> str:
    idioma = os.environ.get("TIENDA_IDIOMA", "es").strip().lower()[:2]
    return idioma if idioma in IDIOMAS else "es"


def elegir(parametro: str | None = None, accept_language: str | None = None) -> str:
    """El idioma de la petición. Del Accept-Language toma el primero que la tienda tenga (pt-BR cuenta como pt)."""
    if parametro and parametro.strip().lower()[:2] in IDIOMAS:
        return parametro.strip().lower()[:2]
    for parte in (accept_language or "").split(","):
        codigo = parte.split(";")[0].strip().lower()[:2]
        if codigo in IDIOMAS:
            return codigo
    return omision()


def fijar(idioma: str):
    """Fija el idioma de la petición en curso (lo hace el middleware de la API); devuelve la ficha para soltarlo."""
    return _DE_LA_PETICION.set(idioma)


def soltar(ficha) -> None:
    _DE_LA_PETICION.reset(ficha)


def actual() -> str:
    return _DE_LA_PETICION.get() or omision()


def t(clave: str, idioma: str | None = None, **datos) -> str:
    """El texto de `clave` en `idioma` (por omisión, el de la petición en curso), con sus {marcadores} llenos.
    Si no existe en ese idioma, sale en español."""
    texto = catalogo(idioma or actual()).get(clave) or catalogo("es").get(clave) or clave
    return texto.format(**datos) if datos else texto
