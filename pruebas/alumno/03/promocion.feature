# language: es
Característica: Cupón y envío gratis juntos

  Regla: Sin cupón, el envío es gratis desde $999.00

    Escenario: Columna 4 · sin cupón, desde $999.00
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $999.00
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $0.00

    Escenario: Columna 3 · sin cupón, debajo de $999.00
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $998.99
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $99.00

  Regla: Con cupón, el envío se mide sobre lo que paga después del descuento

    Escenario: Columna 5 · con cupón, debajo del mínimo del cupón
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $499.99
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que el cupón es para compras de $500.00 o más

    Escenario: Columna 8a · con cupón, antes del descuento sí llegaba y después no
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $999.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $99.90
      Y el envío que le muestra la tienda es de $99.00
