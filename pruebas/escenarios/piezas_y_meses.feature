# language: es
Característica: Piezas por producto y meses sin intereses

  Regla: Se pueden poner de 1 a 10 piezas de cada producto

    Esquema del escenario: Cantidad que se acepta
      Dado que Marta tiene la playera azul en su carrito
      Cuando cambia la cantidad a <piezas>
      Entonces su carrito muestra <piezas> piezas de la playera azul

      Ejemplos:
        | piezas |
        | 1      |
        | 10     |

    Esquema del escenario: Cantidad que se rechaza
      Dado que Marta tiene 1 pieza de la playera azul en su carrito
      Cuando cambia la cantidad a <piezas>
      Entonces la tienda le dice que <mensaje>
      Y su carrito sigue con 1 pieza de la playera azul

      Ejemplos:
        | piezas | mensaje                             |
        | -1     | el mínimo es 1 pieza                |
        | 0      | el mínimo es 1 pieza                |
        | 11     | el máximo es 10 piezas              |
        | 12     | el máximo es 10 piezas              |
        | 2.5    | la cantidad tiene que ser entera    |
        | dos    | la cantidad tiene que ser un número |

    Escenario: Cantidad vacía
      Dado que Marta tiene 1 pieza de la playera azul en su carrito
      Cuando deja vacía la cantidad
      Entonces la tienda le dice que la cantidad es obligatoria
      Y su carrito sigue con 1 pieza de la playera azul

  Regla: Se puede pagar a meses sin intereses en compras desde $3,000.00 y hasta $50,000.00

    Esquema del escenario: Opción de meses según el total
      Dado que Marta tiene en su carrito productos por <total>
      Cuando elige cómo pagar
      Entonces la opción de meses sin intereses <aparece>

      Ejemplos:
        | total      | aparece    |
        | $2,999.98  | no aparece |
        | $2,999.99  | no aparece |
        | $3,000.00  | aparece    |
        | $3,000.01  | aparece    |
        | $49,999.99 | aparece    |
        | $50,000.00 | aparece    |
        | $50,000.01 | no aparece |
        | $50,000.02 | no aparece |
