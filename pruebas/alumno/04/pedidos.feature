# language: es
Característica: El camino del pedido

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: Pagado × cancela · se cancela y se devuelve lo cobrado
      Dado que Marta tiene un pedido pagado
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: En almacén × cancela · todavía se puede
      Dado que Marta tiene un pedido en almacén
      Cuando cancela el pedido
      Entonces el pedido queda cancelado
      Y le devuelven $432.00 a su tarjeta

    Escenario: Enviado × cancela · ya salió del almacén
      Dado que Marta tiene un pedido enviado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue enviado

  Regla: Un pedido se paga una sola vez

    Escenario: Cancelado × paga · no se cobra lo cancelado
      Dado que Marta tiene un pedido cancelado
      Cuando intenta pagar el pedido
      Entonces la tienda le dice que este pedido ya no se puede pagar: está «cancelado»
      Y el pedido sigue cancelado
