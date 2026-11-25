# language: pt
Funcionalidade: O caminho do pedido

  Regra: Cancela-se enquanto o pedido não sair do armazém

    Cenário: Pago × cancela · cancela-se e devolve-se o que foi cobrado
      Dado que Marta tem um pedido pago
      Quando ela cancela o pedido
      Então o pedido fica cancelado
      E devolvem $432.00 ao cartão dela

    Cenário: No armazém × cancela · ainda dá
      Dado que Marta tem um pedido no armazém
      Quando ela cancela o pedido
      Então o pedido fica cancelado
      E devolvem $432.00 ao cartão dela

    Cenário: Enviado × cancela · já saiu do armazém
      Dado que Marta tem um pedido enviado
      Quando ela cancela o pedido
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado
      E o pedido continua enviado

  Regra: Um pedido se paga uma única vez

    Cenário: Cancelado × paga · não se cobra o que foi cancelado
      Dado que Marta tem um pedido cancelado
      Quando ela tenta pagar o pedido
      Então a loja diz a ela que este pedido não pode mais ser pago: está «cancelado»
      E o pedido continua cancelado
