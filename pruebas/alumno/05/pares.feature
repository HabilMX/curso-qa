# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 1 · $600.00, sin cupón, Marta, español
    Dado que Marta no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $600.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $99.00

  Escenario: Fila 4 · $1,110.00, sin cupón, Luis, español
    Dado que Luis no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $1,110.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $0.00

  Escenario: Fila 9 · $3,330.00, cupón ya usado, Luis, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Luis ya usó el cupón BIENVENIDA10 en una compra anterior
    Y tiene en su carrito productos por $3,330.00
    Cuando aplica el cupón BIENVENIDA10
    Y elige cómo pagar
    Entonces la opción de meses sin intereses aparece

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces el envío que le muestra la tienda es de $0.00
