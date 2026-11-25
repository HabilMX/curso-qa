# Mantenimiento de la tienda de práctica

La portada del curso, para quien lo toma, es el [README](README.md). Aquí está lo de quien mantiene la tienda: cómo
se levanta, sus comandos y cómo se prueba.

## La tienda de práctica

Una tienda chiquita con catálogo, carrito, cupón, pago con una pasarela simulada y pedidos. Corre en tu
computadora dentro de Docker, junto con todo lo que vas a usar para probarla (behave, curl, newman y un
navegador sin ventana): no instalas nada más.

```bash
./practicar
```

La primera vez construye la imagen (tarda unos minutos) y luego te deja en la terminal de la tienda. La página
queda en **http://localhost:8080** y la API en **http://localhost:8080/api** (su documentación, en
http://localhost:8080/docs).

Clientes de prueba: **Marta** (contraseña `marta-practica`) y **Luis** (`luis-practica`).

| Comando | Qué hace |
|---|---|
| `./practicar` | Levanta la tienda y entra a su terminal |
| `./practicar error estado` | Dice qué errores sembrados están encendidos |
| `./practicar error E1 on` · `off` | Enciende o apaga un error (E1 a E8); la lección te dice cuándo |
| `./practicar reiniciar` | Deja la tienda como recién abierta |
| `./practicar apagar` | Apaga la tienda; tu trabajo se queda guardado |
| `./practicar desde-cero` | Borra tu carpeta de práctica y los pedidos (pide confirmación) |
| `./practicar reconstruir` | Actualiza la imagen cuando el curso trae algo nuevo |

Adentro de la terminal tienes además:

| Comando | Qué hace |
|---|---|
| `verifica 00` | Revisa la lección y te dice qué falta |
| `tienda --help` | Mueve el reloj de la tienda, cambia cómo contesta la pasarela de pago o avanza un pedido |

Está hecha para Linux, macOS y Windows con WSL2. Se midió en Linux x86_64 (Docker 29): la imagen pesa
unos 1.3 GB, se construye en unos 2 minutos y la tienda arranca en 2 segundos. En macOS y en WSL2 todavía no
se mide.

## Para quien mantiene el curso

La tienda está en `tienda/` (Python con FastAPI y SQLite). Sus pruebas corren sin Docker:

```bash
python3 -m venv .venv && .venv/bin/pip install fastapi uvicorn httpx pytest behave==1.3.3
.venv/bin/python -m pytest pruebas
```

Las pruebas de navegador (lecciones 11 y la página) necesitan Playwright con su Chromium; sin él se saltan, y lo de
navegador se mide dentro de la imagen con `pruebas/medir-imagen.sh`. La tabla de errores sembrados y de reglas está
en [pruebas/README.md](pruebas/README.md).

Prueban cada regla de la tienda, que cada error sembrado rompa su regla al encenderse (y no antes), que el
catálogo de pasos corra los escenarios de las lecciones contra una tienda de verdad, y el `verifica`.
