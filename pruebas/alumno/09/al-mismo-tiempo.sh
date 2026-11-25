#!/bin/bash
# Dos pedidos con el mismo cupón, pagados al mismo tiempo. Termina en 0 si el cupón se usó una vez y en 1 si se usó dos.
BASE=http://localhost:8080
CLIENTE=Marta
CONTRASENA=marta-practica

TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)

pedido_con_cupon() {
  curl -s -o /dev/null -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"cantidad":2}'
  curl -s -o /dev/null -X POST $BASE/api/carrito/cupon -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
  curl -s -X POST $BASE/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r 'select(.cupon == "BIENVENIDA10") | .id'
}

pagar() {
  curl -s -o /dev/null -w "pago del pedido $1: %{http_code}\n" -X POST $BASE/api/pedidos/$1/pago \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: al-mismo-tiempo-$1-$$" -d '{"tarjeta":"4242 4242 4242 4242"}'
}

UNO=$(pedido_con_cupon)
DOS=$(pedido_con_cupon)
if [ -z "$UNO" ] || [ -z "$DOS" ]; then
  echo "No pude hacer los dos pedidos con el cupón. Corre tienda reiniciar y vuelve a intentar."
  exit 2
fi

pagar $UNO &
pagar $DOS &
wait

PAGADOS=0
for P in $UNO $DOS; do
  ESTADO=$(curl -s $BASE/api/pedidos/$P -H "Authorization: Bearer $TOKEN" | jq -r .estado)
  echo "pedido $P: $ESTADO"
  if [ "$ESTADO" = "pagado" ]; then PAGADOS=$((PAGADOS + 1)); fi
done

if [ $PAGADOS -eq 2 ]; then
  echo "ROJO: el cupón se usó dos veces"
  exit 1
fi
if [ $PAGADOS -ne 1 ]; then
  echo "No pude comprobarlo: ningún pedido quedó pagado. ¿Está arriba la tienda?"
  exit 2
fi
echo "VERDE: el cupón se usó una sola vez"
