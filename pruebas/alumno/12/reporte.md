# Un pedido entregado se puede cancelar, y se reembolsa

**Severidad:** alta
**Prioridad:** alta

## Pasos

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":1}' > /dev/null
PEDIDO=$(curl -s -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: reporte-$PEDIDO" -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}' > /dev/null
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
curl -s -o /dev/null -w 'cancelar: HTTP %{http_code}\n' -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion \
  -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

## Resultado esperado

La cancelación se rechaza con 409: un pedido enviado o entregado ya no se puede cancelar (regla de la tienda).

## Resultado obtenido

La cancelación responde 200, el pedido queda cancelado y la tienda reembolsa el cargo.

## Evidencia

```
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```
