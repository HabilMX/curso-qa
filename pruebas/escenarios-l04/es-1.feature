# language: es
Característica: El camino del pedido

  Regla: Se cancela mientras el pedido no salga del almacén

    Escenario: Entregado × cancela · no se cancela lo que ya llegó
      Dado que Marta tiene un pedido entregado
      Cuando cancela el pedido
      Entonces la tienda le dice que el pedido ya salió del almacén; ya no se puede cancelar
      Y el pedido sigue entregado
