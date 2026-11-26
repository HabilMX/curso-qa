# language: es
Característica: Comprar con cupón y cancelar a tiempo

  Regla: El envío es gratis desde $999.00, medido después del cupón

    Escenario: Sin cupón, justo en $999.00 · no paga envío
      Dado que Marta no tiene ningún cupón aplicado
      Y tiene en su carrito productos por $999.00
      Cuando pasa a pagar
      Entonces el envío que le muestra la tienda es de $0.00

    Escenario: Con cupón, $1,110.00 queda justo en $999.00 · no paga envío
      Dado que el cupón BIENVENIDA10 está vigente
      Y que Marta no ha usado nunca el cupón BIENVENIDA10
      Y tiene en su carrito productos por $1,110.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $111.00
      Y el envío que le muestra la tienda es de $0.00

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: En almacén · todavía se puede cancelar
      Dado que Marta tiene un pedido en almacén
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: Enviado · ya no se puede cancelar
      Dado que Marta tiene un pedido enviado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue enviado
