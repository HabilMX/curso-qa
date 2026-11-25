# language: es
Característica: Envío gratis en compras grandes

  Regla: El envío es gratis en compras desde $999.00; abajo cuesta $99.00

    Esquema del escenario: Envío según el subtotal
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por <subtotal>
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de <envío>

      Ejemplos:
        | subtotal | envío  |
        | $998.98  | $99.00 |
        | $998.99  | $99.00 |
        | $999.00  | $0.00  |
        | $999.01  | $0.00  |
