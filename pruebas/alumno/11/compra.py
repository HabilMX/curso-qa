"""La compra crítica, de punta a punta, con el navegador: entra, agrega una playera, paga y revisa en «Mis pedidos»
que el pedido quedó pagado. Sale con 0 si todo salió bien y con 1 si no."""
import os
import sys

from playwright.sync_api import expect, sync_playwright

TIENDA = os.environ["TIENDA_URL"]
CLIENTE = os.environ["CLIENTE"]
CONTRASENA = os.environ["CONTRASENA"]

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page()
    try:
        pagina.goto(TIENDA)
        pagina.fill("#cliente", CLIENTE)
        pagina.fill("#contrasena", CONTRASENA)
        pagina.click("#form-entrada button[type=submit]")
        pagina.get_by_test_id("agregar-playera-azul").click()
        expect(pagina.locator("#piezas")).to_have_text("1")
        pagina.click("#pagar")
        expect(pagina.locator("#piezas")).to_have_text("0")      # el carrito se vacía cuando terminó de pagar
        pagina.click("#ver-pedidos")
        estado = pagina.locator("#lista-pedidos .pedido .estado").first
        expect(estado).to_have_attribute("data-estado", "pagado")
        print("✅ el pedido quedó pagado")
    except Exception as falla:  # noqa: BLE001
        print(f"❌ {falla}")
        sys.exit(1)
    finally:
        navegador.close()
