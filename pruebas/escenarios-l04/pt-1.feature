# language: pt
Funcionalidade: O caminho do pedido

  Regra: Cancela-se enquanto o pedido não sair do armazém

    Cenário: Entregue × cancela · não se cancela o que já chegou
      Dado que Marta tem um pedido entregue
      Quando ela cancela o pedido
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado
      E o pedido continua entregue
