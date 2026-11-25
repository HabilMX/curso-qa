"""Dinero en centavos enteros: nunca en flotante.

Un precio de $332.99 se guarda como 33299. Así la suma de tres playeras da exactamente $998.99 y no
$998.9900000001, que es justo la clase de orilla que el curso enseña a probar.
"""

import re

_FORMATO = re.compile(r"^\$?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d{1,2}))?$")


def a_texto(centavos: int) -> str:
    """33299 → «$332.99»; 5000001 → «$50,000.01». Es el formato que usan las lecciones."""
    signo = "-" if centavos < 0 else ""
    pesos, cent = divmod(abs(centavos), 100)
    return f"{signo}${pesos:,}.{cent:02d}"


def de_texto(texto: str) -> int:
    """«$1,234.56», «1234.56» o «$999» → centavos. Falla con ValueError si no es un monto."""
    limpio = texto.strip()
    m = _FORMATO.match(limpio)
    if not m:
        raise ValueError(f"no entiendo el monto «{texto}»; escríbelo como $1,234.56")
    pesos = int(m.group(1).replace(",", ""))
    cent = (m.group(2) or "0").ljust(2, "0")
    return pesos * 100 + int(cent)


def porcentaje(centavos: int, por_ciento: int) -> int:
    """El por_ciento de un monto, redondeado al centavo con la regla de la escuela (.5 sube)."""
    return (centavos * por_ciento + 50) // 100
