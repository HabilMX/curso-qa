# Pruebas de la tienda — para quien la mantiene

Esta carpeta no es para el alumno. Aquí está qué hace cada error sembrado, y el alumno lo tiene que descubrir con
sus pruebas: por eso ni la ayuda de `tienda`, ni la de `./practicar`, ni el README del curso lo dicen.

## Los errores sembrados

| Error | Qué hace, en una línea | Dónde vive |
|---|---|---|
| E1 «límite corrido» | Compara con `>` en vez de `>=`: un carrito de exactamente $999.00 paga $99.00 de envío | `reglas.py` |
| E2 «cupón dos veces» | Revisa el cupón fuera de la transacción y anota después de una pausa: uno tras otro da 422, dos pagos al mismo tiempo lo usan dos veces | `api.py` |
| E3 «cancelar lo entregado» | Deja cancelar también lo enviado y lo entregado, y lo reembolsa | `reglas.py` |
| E4 «cobro doble al reintentar» | El reintento cobra doble y nadie lo corrige: manda una llave nueva a la pasarela en cada intento y la tienda tampoco concilia | `api.py`, `pasarela.py` |
| E5 «pedido ajeno» | La consulta de un pedido no revisa de quién es; cancelar y pagar sí | `api.py` |
| E6 «fecha en UTC» | El pedido nace con la hora en UTC y sin zona: de noche cae en el día siguiente, el 31-dic en el año siguiente | `api.py` |
| E7 «el cargo que llega tarde no se concilia» | El cargo que llega después del 504 se anota y nada más: el pedido sigue «creado» con dinero cobrado | `pasarela.py` |
| E8 «la página no deja pagar» | El botón «Pagar» de la página crea el pedido pero no manda el pago, y aun así dice que quedó pagado; la API no cambia | `api.py` (sirve `app.js`), `pagina/app.js` |

Qué lección usa cada error lo dice la lección misma (`tienda error EN on`); no se repite aquí para que no se
desactualice.

Sin errores encendidos, la tienda cumple sus reglas (R1…R12, en `reglas.py` y `api.py`). Además, al anotar un cargo,
lo concilia con el pedido: si queda cobrado completo pasa a «pagado», y lo que sobra se devuelve solo como «reembolso».

## Qué hay aquí

- `test_tienda.py`: cada regla, y que cada error rompa su regla al encenderse (y no antes).
- `test_verifica*.py`: el `verifica` de cada lección, con el ejemplo de alumno de `alumno/NN` y sus negativos.
- `test_pasos*.py`: el catálogo de pasos contra una tienda de verdad.
- `medir-imagen.sh`: la medición de la imagen completa con Docker (se corre en un servidor, no en la máquina de
  quien programa).
