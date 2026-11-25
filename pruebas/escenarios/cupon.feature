# language: es
Característica: Aplicar un cupón de descuento

  Antecedentes:
    Dado que el cupón BIENVENIDA10 está vigente
    Y Marta no ha usado nunca el cupón BIENVENIDA10

  Regla: El cupón descuenta 10% del subtotal, sin contar el envío

    Escenario: El descuento es el 10% del subtotal
      Dado que Marta tiene en su carrito productos por $1,200.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra un descuento de $120.00

  Regla: El cupón solo aplica si el subtotal es de $500.00 o más

    Escenario: Subtotal exactamente en el mínimo
      Dado que Marta tiene en su carrito productos por $500.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le muestra que el cupón quedó aplicado

    Escenario: Subtotal un centavo abajo del mínimo
      Dado que Marta tiene en su carrito productos por $499.99
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que el cupón es para compras de $500.00 o más
      Y su subtotal sigue en $499.99

  Regla: Cada cliente puede usar el cupón una sola vez

    Escenario: Segunda vez que lo intenta
      Dado que Marta ya usó el cupón BIENVENIDA10 en una compra anterior
      Y tiene en su carrito productos por $600.00
      Cuando aplica el cupón BIENVENIDA10
      Entonces la tienda le dice que ya usó este cupón
      Y su subtotal sigue en $600.00
