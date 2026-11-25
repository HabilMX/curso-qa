# Pruebas heredadas del carrito. Cada una imprime ✅ o ❌; si alguna falla, el script termina en 1.
BASE=${TIENDA_URL:-http://localhost:8080}
FALLAS=0
revisa() {  # revisa "nombre" "esperado" "obtenido"
  if [ "$2" = "$3" ]; then echo "✅ $1"; else echo "❌ $1: esperaba $2, llegó $3"; FALLAS=1; fi
}
TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)
carrito() {  # carrito <cantidad de playeras azules>
  curl -s -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d "{\"cantidad\":$1}"
}
revisa "una playera: subtotal" '$333.00' "$(carrito 1 | jq -r .subtotal.texto)"
revisa "una playera: paga envío" '$99.00' "$(carrito 1 | jq -r .envio.texto)"
revisa "tres playeras: subtotal" '$999.00' "$(carrito 3 | jq -r .subtotal.texto)"
revisa "tres playeras: envío" '$0.00' "$(carrito 3 | jq -r .envio.texto)"
revisa "dos playeras: paga envío" '$99.00' "$(carrito 2 | jq -r .envio.texto)"
exit $FALLAS
