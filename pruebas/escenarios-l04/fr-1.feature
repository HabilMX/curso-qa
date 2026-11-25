# language: fr
Fonctionnalité: Le chemin de la commande

  Règle: On annule tant que la commande n'est pas sortie de l'entrepôt

    Scénario: Livrée × annule · on n'annule pas ce qui est déjà arrivé
      Soit Marta a une commande livrée
      Quand elle annule la commande
      Alors la boutique lui dit que la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée
      Et la commande reste livrée
