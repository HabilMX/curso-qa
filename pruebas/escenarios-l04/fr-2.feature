# language: fr
Fonctionnalité: Le chemin de la commande

  Règle: On annule tant que la commande n'est pas sortie de l'entrepôt

    Scénario: Payée × annule · elle est annulée et ce qui a été prélevé est remboursé
      Soit Marta a une commande payée
      Quand elle annule la commande
      Alors la commande devient annulée
      Et on lui rembourse $432.00 sur sa carte

    Scénario: À l'entrepôt × annule · c'est encore possible
      Soit Marta a une commande à l'entrepôt
      Quand elle annule la commande
      Alors la commande devient annulée
      Et on lui rembourse $432.00 sur sa carte

    Scénario: Expédiée × annule · elle est déjà sortie de l'entrepôt
      Soit Marta a une commande expédiée
      Quand elle annule la commande
      Alors la boutique lui dit que la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée
      Et la commande reste expédiée

  Règle: Une commande se paie une seule fois

    Scénario: Annulée × paie · on ne prélève pas ce qui est annulé
      Soit Marta a une commande annulée
      Quand elle essaie de payer la commande
      Alors la boutique lui dit que cette commande ne peut plus être payée : elle est « annulée »
      Et la commande reste annulée
