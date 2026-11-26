# El envío se cobra en un carrito de exactamente $999.00

**Severidad:** alta — cobra de más a la clienta.
**Prioridad:** media — en lo medido solo le pasa a un carrito de exactamente $999.00; propongo el trabajo planeado.

## Pasos

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

## Resultado esperado

El envío es gratis desde $999.00 (CA-1): `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}`.

## Resultado obtenido

La tienda cobra $99.00 de envío en un carrito de exactamente $999.00.

## Evidencia

```
{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}
```
