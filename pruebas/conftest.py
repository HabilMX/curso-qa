"""Cada prueba arranca con una tienda recién abierta, en un archivo SQLite propio y desechable."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tienda"))


@pytest.fixture()
def tienda(tmp_path, monkeypatch):
    monkeypatch.setenv("TIENDA_DATOS", str(tmp_path / "tienda.db"))
    from fastapi.testclient import TestClient

    from tienda import api, pasarela

    monkeypatch.setattr(api, "ESPERA_PASARELA_S", 1.0)
    pasarela.rearmar()
    with TestClient(api.app) as cliente:
        yield cliente
    pasarela.soltar_esperas()


def sesion(tienda, nombre="Marta"):
    r = tienda.post("/api/sesiones", json={"cliente": nombre, "contrasena": f"{nombre.lower()}-practica"})
    assert r.status_code == 201, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def llenar(tienda, h, **piezas):
    r = None
    for producto, cantidad in piezas.items():
        r = tienda.put(f"/api/carrito/productos/{producto.replace('_', '-')}", json={"cantidad": cantidad}, headers=h)
        assert r.status_code == 200, r.text
    return r.json() if r is not None else None


def error(tienda, e, encendido=True):
    assert tienda.put(f"/control/errores/{e}", json={"encendido": encendido}).status_code == 200
