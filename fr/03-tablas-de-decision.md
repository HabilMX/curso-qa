# Leçon 03 — Tables de décision

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Condition :** une question que le système se pose et à laquelle on répond par oui ou par non. « Le client
  a-t-il appliqué le coupon ? » est une condition.
- **Action :** ce que le système fait selon les réponses : retirer une réduction, facturer la livraison, afficher un
  avis.
- **Table de décision :** une table avec les conditions et les actions dans les lignes, et dans chaque colonne une
  combinaison de réponses avec ce que le système doit faire.
- **Combinaison :** les réponses de toutes les conditions ensemble. Avec trois conditions de oui ou non, il y en a huit.

**Ce que tu en retires :** quand plusieurs règles décident ensemble, tu construis leur table de décision, tu rends
visibles les combinaisons que personne n'a définies et tu les transformes en questions pour le métier ; ensuite, tu
écris un scénario par colonne, et tu sais lequel d'entre eux attrape l'erreur qu'une règle seule ne laisse pas voir.

**Idée nouvelle de cette leçon (la seule qui est évaluée) :** quand plusieurs conditions décident ensemble, une table
montre la règle que personne n'a écrite.

**Dans quel ordre :** tu trouves les conditions et les actions (étape 1), tu remplis toutes les combinaisons
(étape 2), tu retires les impossibles et tu réunis celles qui sont indifférentes (étape 3), tu cherches la colonne que
personne n'a définie et tu la transformes en question (étape 4), et tu écris un scénario par colonne (étape 5).

---

## La scène

*Scénario inventé ; les montants et les messages de la boutique, eux, sont réels.*

Mardi, 17:30. Ramiro, du marketing, envoie à l'équipe la promotion de fin de mois :

> « Coupon BIENVENIDA10 : 10 % sur les achats à partir de $500 (pesos mexicains). Et livraison gratuite à partir de
> $999. Les deux sont cumulables ! »

La programmation l'implémente le soir même. La QA teste le coupon avec un panier de $1,200 : réduction de $120,
livraison gratuite. Elle teste la livraison avec un panier de $999 sans coupon : livraison gratuite. Les deux règles
fonctionnent. Mise en ligne mercredi.

Jeudi, une cliente écrit, furieuse. Elle a composé un panier de $999 justement pour ne pas payer la livraison, elle y a
mis le coupon, le total est tombé à $899.10… et on lui a facturé $99 de livraison. Une heure plus tard, une autre
écrit : panier de $1,050, coupon, $99 de livraison. Toutes les deux citent l'annonce : « livraison gratuite à partir
de $999 ».

Personne ne s'est trompé en testant chaque règle. Le problème est **là où les deux règles se croisent** : les $999 de
la livraison gratuite se comptent-ils avant ou après le coupon ? Ramiro ne l'a pas écrit, la programmation a choisi une
manière, et personne n'a posé la question parce que personne n'a regardé les deux règles **en même temps**.

Cette leçon sert à les regarder en même temps. Et à ce que cette question surgisse le mardi autour de la table, et pas
le jeudi au service client.

---

## Avant de commencer

**Pas d'ordinateur pour les étapes 1 à 4.** Du papier, ou un tableur si tu es plus à l'aise ainsi : une table de
décision est littéralement une table. Pour l'étape 5, il te faut ton éditeur, comme aux leçons 01 et 02.

**Fais la première tentative sans IA.** Ce que l'on mesure, c'est si **toi**, tu trouves la colonne que personne n'a
définie. Une IA peut te remplir la table très vite, et le plus facile pour elle est de choisir une réponse pour la case
que personne n'a définie et de l'écrire comme si c'était une règle, ce qui est exactement ce qu'a fait la
programmation avec Ramiro. Avec ta table en main, ensuite, tu peux comparer.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 01, qu'un scénario sort d'une règle et que ce que
personne ne sait s'écrit comme une question ; de la 02, les bords, surtout celui de $999.00.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Trouve les conditions et les actions

Relis le courriel de Ramiro et sépare-le en deux listes : **ce que le système demande** et **ce que le système
fait**.

Ce qu'il demande, chaque chose sous forme de question de oui ou non :

| # | Condition |
|---|---|
| C1 | Le client essaie-t-il d'appliquer le coupon `BIENVENIDA10` ? |
| C2 | Le sous-total est-il de $500.00 ou plus ? |
| C3 | Le sous-total est-il de $999.00 ou plus ? |

Ce qu'il fait :

| # | Action |
|---|---|
| A1 | Retire 10 % du sous-total |
| A2 | Lui dit : « le coupon est réservé aux achats de $500.00 ou plus » |
| A3 | Livraison gratuite |
| A4 | Livraison de $99.00 |

Deux détails qui ne sont pas évidents :

- **C1 dit « essaie ».** Essayer d'appliquer le coupon et que le coupon soit appliqué ne sont pas la même chose : avec
  moins de $500.00, le client l'essaie et la boutique le rejette avec un avis. Cette différence, c'est justement la
  colonne 5.
- **C2 et C3 s'écrivent avec le « ou plus ».** C'est le bord de la leçon 02 : $500.00 exactement comptent, $999.00
  exactement aussi. Si la règle ne dit pas si le bord est compris, c'est déjà une question (leçon 01).
- **« Le sous-total » est ce que font les produits ensemble, sans la réduction et sans la livraison.** Nous l'avons écrit
  ainsi exprès. À l'étape 4, tu verras que c'est justement le mot qui cache le problème.

---

## Étape 2 · Remplis toutes les combinaisons

Une **table de décision complète** a une colonne pour chaque combinaison de réponses. Avec trois conditions de oui ou
non, cela fait 2 × 2 × 2 = **8 colonnes**.

Pour n'en sauter aucune, remplis-les avec un motif : la dernière condition change à chaque colonne, celle du milieu
toutes les deux, la première toutes les quatre.

Le programme de l'ISTQB écrit T/F dans les conditions et permet d'autres notations ; ici, nous utilisons **O** (oui) et
**N** (non). Dans les actions, comme dans le programme, **X** si l'action a lieu et vide si elle n'a pas lieu.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C1 Essaie d'appliquer le coupon ? | N | N | N | N | O | O | O | O |
| C2 Sous-total à partir de $500 ? | N | N | O | O | N | N | O | O |
| C3 Sous-total à partir de $999 ? | N | O | N | O | N | O | N | O |

Maintenant, avant de remplir les actions, **prédis** : y a-t-il une colonne qui ne peut pas exister ? Écris-le et
continue.

---

## Étape 3 · Retire l'impossible, réunis ce qui est indifférent

**L'impossible.** Les colonnes 2 et 6 demandent un sous-total **inférieur** à $500 et **de $999 ou plus** en même
temps. Aucun panier ne remplit cela. Le programme de l'ISTQB les appelle des combinaisons **impossibles**
(*infeasible*) et elles se marquent **N/A** : on ne les teste pas, parce qu'aucune donnée ne les produit.

Il reste six colonnes possibles. Remplis leurs actions avec ce que dit le courriel de Ramiro :

| | 1 | 3 | 4 | 5 | 7 | 8 |
|---|---|---|---|---|---|---|
| C1 Essaie d'appliquer le coupon ? | N | N | N | O | O | O |
| C2 Sous-total à partir de $500 ? | N | O | O | N | O | O |
| C3 Sous-total à partir de $999 ? | N | N | O | N | N | O |
| A1 Retire 10 % | | | | | X | X |
| A2 Avis du minimum | | | | X | | |
| A3 Livraison gratuite | | | X | | | **?** |
| A4 Livraison de $99.00 | X | X | | X | X | **?** |
| **Un panier d'exemple** | $480.00 | $998.99 | $999.00 | $499.99 | $998.00 | ??? |

**Ce qui est indifférent.** Regarde les colonnes 1 et 3 : sans coupon, la réponse de C2 ne change rien ; les deux
facturent la livraison. Quand une condition n'affecte pas le résultat, les colonnes peuvent être **réunies** en une
seule, et dans cette condition on écrit **–** (« peu importe »). Ainsi la table est plus courte et tu as un scénario de
moins à écrire. Réunir est facultatif ; l'important est de ne pas réunir deux colonnes dont les actions, elles, sont
différentes.

---

## Étape 4 · La colonne que personne n'a définie

Regarde la colonne 8 : coupon appliqué et un sous-total de $999 ou plus. Il y a une réduction, bien sûr. Et la
livraison ?

Le courriel de Ramiro dit « livraison gratuite à partir de $999 » et « les deux sont cumulables ». Avec un sous-total de
$999.00 et le coupon, le client paie $899.10 pour les produits. N'atteint-il plus $999 ? Cela dépend d'un mot que le
courriel ne dit pas : **les $999 se mesurent-ils avant ou après la réduction ?**

C'est la **règle que personne n'a écrite**. Dans cet exemple, le problème commence dans l'exigence, avant le code : il y
a un trou. La table le rend visible, parce qu'elle t'oblige à remplir une case que ni Ramiro ni la programmation n'ont
remplie.

Ce que tu fais d'une case comme celle-là, c'est la même chose qu'avec une carte rouge de la leçon 01 : **tu l'écris
comme une question et tu l'apportes à celui qui décide.** Ne la réponds pas encore : ainsi la décision reste entre les
mains du métier, et non du code par accident.

> **Question pour le métier :** « Avec le coupon appliqué, la livraison gratuite à partir de $999.00 se mesure-t-elle
> sur le sous-total (avant la réduction) ou sur ce que le client paie pour les produits (après la réduction) ? »

**Ce qu'a décidé la boutique d'entraînement.** Pour cette boutique, la réponse existe déjà : la livraison gratuite se
mesure **après** le coupon. C'est une décision du métier, pas la seule correcte ; une autre boutique pourrait décider
le contraire et ce serait bien, pourvu qu'elle l'**écrive**.

Avec cette réponse, la colonne 8 n'en est plus une seule. Il faut la scinder selon ce que le client paie **après** la
réduction. Pour cela, il faut une nouvelle condition, C3' : elle ne regarde plus le sous-total, mais ce que le client
paie pour les produits une fois la réduction faite. Sans coupon, les deux donnent la même chose ; avec coupon, il faut
faire le calcul.

| | 8a | 8b |
|---|---|---|
| C1 Essaie d'appliquer le coupon ? | O | O |
| C2 Sous-total à partir de $500 ? | O | O |
| C3' Ce qu'il paie **déjà avec le coupon** est-il de $999 ou plus ? | N | O |
| A1 Retire 10 % | X | X |
| A3 Livraison gratuite | | X |
| A4 Livraison de $99.00 | X | |
| **Un panier d'exemple** | $999.00 → il paie $899.10 | $1,110.00 → il paie $999.00 |

Regarde l'exemple de la 8b. Un sous-total de $1,110.00 avec le coupon tombe sur **exactement $999.00** : c'est
pile sur le bord de la leçon 02, mais maintenant le bord apparaît **après un calcul**. Un scénario qui teste une seule
règle ne le cherche pas là. Pour y arriver, il faut combiner le coupon avec la livraison et choisir le sous-total exprès.

> **D'où sort $1,110.00.** Si ce que l'on paie après les 10 % doit être $999.00, le sous-total est
> $999.00 ÷ 0.9 = $1,110.00. Dans la boutique d'entraînement, trois T-shirts bleus ($333.00 chacun) et une casquette
> ($111.00) font ce total.

**Regarde maintenant la colonne 7 avec la C3'.** Un sous-total de $998.00 avec coupon paie $898.20 : C3' est « non »,
comme dans la 8a. Elles ont les mêmes réponses et les mêmes actions, donc elles forment **une seule colonne**, la
7 + 8a. Son meilleur exemple est celui de la 8a ($999.00), parce que c'est le panier qui, avant la réduction, atteignait
bien le seuil.

**La table finale** a six colonnes possibles : 1, 3, 4, 5, 7 + 8a et 8b (ou cinq, si tu as réuni la 1 et la 3).
Chacune est un scénario.

---

## Étape 5 · Un scénario par colonne

À la leçon 01, tu as appris que chaque scénario teste une règle. Ici, chaque scénario teste **une colonne** : une
combinaison complète de conditions. C'est pourquoi le scénario doit fixer **toutes** les conditions de la colonne, pas
une seule : le **Soit** pose le point de départ (le coupon en vigueur et jamais utilisé, ce qu'il y a dans le panier)
et le **Quand**, ce que fait le client (appliquer le coupon ou passer au paiement sans lui).

Utilise les phrases du catalogue de la boutique que tu connais déjà. Un **Et** continue le type d'étape précédent, donc
« Et elle a dans son panier… » après un Soit est aussi un Soit du catalogue. Voici la colonne 8b :

```gherkin
# language: fr
Fonctionnalité: Coupon et livraison gratuite ensemble

  Règle: Avec le coupon, la livraison se mesure sur ce que le client paie après la réduction

    Scénario: Colonne 8b · avec coupon, après la réduction elle atteint $999.00
      Soit le coupon BIENVENIDA10 est en vigueur
      Et Marta n'a jamais utilisé le coupon BIENVENIDA10
      Et elle a dans son panier des produits pour $1,110.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre une réduction de $111.00
      Et la livraison que lui montre la boutique est de $0.00
```

Lis l'**Alors** : il vérifie les deux actions de la colonne, la réduction et la livraison. Si tu ne vérifiais que la
réduction, le scénario sortirait au vert même avec une livraison fausse, et la colonne ne serait pas testée.

**À toi :** dans un fichier `promocion.feature`, copie la 8b et écris un scénario pour chacune des colonnes 3, 4, 5 et
8a. Utilise le panier d'exemple de chacune. Regroupe-les avec `Règle:` comme à la leçon 01 : une règle pour « sans
coupon » et une autre pour « avec coupon ».

**Combien de scénarios suffisent.** Le programme de l'ISTQB mesure la couverture de cette technique comme les colonnes
possibles que tu as testées divisées par le total des colonnes possibles. Avec la 1 et la 3 réunies, la table finale a
cinq colonnes, et tes cinq scénarios (3, 4, 5, 8a et 8b) couvrent les cinq. Le scénario de la 3 teste la colonne
1 + 3 avec un panier qui remplit aussi la C2. Une réserve honnête : dans la colonne 5, tu ne peux regarder que l'avis.
La boutique rejette le coupon et, dans cette réponse, ne te renvoie pas le panier ; la livraison de cette colonne reste
donc sans être observée. C'est pourquoi nous disons « cinq colonnes couvertes, dont une avec une action non regardée »,
et non un 100 % propre. Si un jour une table a trop de colonnes, on teste d'abord celles qui ont le plus de risque ;
c'est à cela que sert ce que tu as vu à la leçon 00 sur le parcours critique.

---

## Comment on vérifie

**La table** (étapes 1 à 4 et exercice 1) se compare avec « Compare tes réponses ». Ce qui doit coïncider : qu'il ne te
manque aucune combinaison possible, que les impossibles soient marquées, et que tu aies écrit la question de la
colonne 8 **avant** de lire la réponse de la boutique.

**Ton fichier `promocion.feature`** est contrôlé par `verifica 03`. Dans le terminal de la boutique, écris :

```bash
verifica 03
```

Il exécute tes scénarios deux fois : avec la boutique propre, ils doivent sortir **au vert**, et avec l'erreur de cette
leçon activée, **au moins un doit sortir au rouge**. S'ils sortent au vert les deux fois, il te dit que tes tests ne
regardent pas là où est l'erreur. Avant de l'exécuter, la liste ci-dessous te dit si la forme est bonne. Les scénarios
de « Compare tes réponses » ont été exécutés contre la boutique avant de publier cette leçon, avec celui que tu copies
à l'étape 5 : au vert avec la boutique propre, et deux au rouge avec l'erreur activée.

**Avant d'enregistrer, relis ton fichier avec cette liste :**

- [ ] La première ligne est `# language: fr`.
- [ ] Il y a un scénario pour chaque colonne demandée, et le titre dit de quelle colonne il s'agit.
- [ ] Entre le **Soit** et le **Quand**, chaque scénario fixe **toutes** les conditions de sa colonne : le sous-total, et
  si le coupon est appliqué ou non.
- [ ] L'**Alors** vérifie **toutes** les actions de sa colonne que la boutique te laisse voir.
- [ ] Aucun sous-total n'est « proche » d'un bord par hasard : si c'est un bord, tu l'as choisi exprès.

---

## Tes exercices

1. **La promotion des mensualités** (sans IA). Ramiro en envoie une autre : « Mensualités sans intérêts à partir de
   $3,000. Et avec le coupon BIENVENIDA10, aussi. » Dans la boutique, les mensualités sans intérêts vont de $3,000.00
   jusqu'à $50,000.00.
   - Écris les conditions et les actions.
   - Remplis la table complète, marque les impossibles et réunis celles qui sont indifférentes.
   - Trouve **au moins une** colonne sans action définie et écris-la comme une question pour Ramiro. Indice : le total
     d'un achat a plus d'une partie.
   Prends 25 minutes comme limite.
2. **Scénarios** (sans IA). Écris les scénarios des colonnes 3, 4, 5 et 8a de l'étape 5, si tu ne les y as pas écrits.
3. **Lequel attrape l'erreur ?** La boutique a une erreur semée : quand elle est activée, la livraison gratuite se donne
   seulement **au-dessus** de $999.00, et non **à partir de** $999.00. Sans rien exécuter, écris lesquels de tes cinq
   scénarios passent au rouge avec cette erreur, et pourquoi les autres restent au vert.

**Révision** (combien de colonnes a la table complète, sans rien retirer ? Essaie d'en réussir au moins 4 sur 5 ;
c'est de la pratique de l'étape 2, pas l'évaluation de la leçon) :

1. Deux conditions de oui ou non.
2. Quatre conditions de oui ou non.
3. Trois conditions de oui ou non, et l'une d'elles devient sans objet quand une autre est « non ». (Sans réunir.)
4. Une condition de oui ou non et une autre à trois réponses possibles (par exemple : moins de $500, de $500 à
   $998.99, et $999 ou plus).
5. Cinq conditions de oui ou non.

---

## Pour conclure

Ramiro n'a pas mal écrit la promotion : il a écrit deux règles qui, chacune de son côté, étaient bonnes. Ce que
personne n'a écrit, c'est ce qui se passe **quand elles se rejoignent**. Une table de décision ne te laisse pas sauter
cette partie, parce qu'elle a une case pour chaque combinaison, et une case vide se remarque.

Ce que tu retiens d'ici :

- Quand plusieurs conditions décident ensemble, **une colonne par combinaison**. Avec *n* conditions de oui ou non, cela
  fait 2 × 2 × … (*n* fois).
- Les combinaisons **impossibles** se marquent et ne se testent pas ; celles qui sont **indifférentes** peuvent être
  réunies.
- Une case que personne ne sait remplir est une **question pour le métier**, pas une décision de ta part ni du code.
- Chaque colonne est un scénario, et entre son **Soit** et son **Quand** on fixe toutes les conditions de la colonne.
- Les bords apparaissent aussi **après un calcul**, et c'est là qu'il est facile de les manquer.

À la leçon 04, tu changes de question : ce n'est plus quelle combinaison de données arrive, mais **dans quel ordre**
les choses se passent. Une commande créée, payée, expédiée, livrée, annulée… et ce qui se passe si quelqu'un tente une
étape hors de son tour.

---

## Compare tes réponses

**Étape 2, prédiction.** Les colonnes 2 et 6 ne peuvent pas exister : un sous-total ne peut pas être inférieur à $500 et
de $999 ou plus en même temps.

**Étape 3.** La table de six colonnes possibles, telle qu'elle est dans l'étape. **La table finale** (après l'étape 4,
avec la 7 et la 8a déjà réunies), si tu as aussi réuni la 1 et la 3, donne ceci :

| | 1 + 3 | 4 | 5 | 7 + 8a | 8b |
|---|---|---|---|---|---|
| C1 Essaie d'appliquer le coupon ? | N | N | O | O | O |
| C2 Sous-total à partir de $500 ? | – | O | N | O | O |
| C3' À partir de $999 (sans coupon : le sous-total ; avec coupon : ce qu'il paie déjà avec le coupon) ? | N | O | N | N | O |
| A1 Retire 10 % | | | | X | X |
| A2 Avis du minimum | | | X | | |
| A3 Livraison gratuite | | X | | | X |
| A4 Livraison de $99.00 | X | | X | X | |

**Étape 4, la question.** Toute formulation vaut si elle demande la même chose : avec le coupon, la livraison gratuite
se mesure-t-elle avant ou après la réduction ? Si tu l'as écrite comme une affirmation (« elle se mesure après »),
transforme-la maintenant en question : ainsi la décision reste entre les mains du métier.

**Étape 5, les scénarios.** Voici ceux qui ont été exécutés contre la boutique (la colonne 8b est dans l'étape 5) :

```gherkin
# language: fr
Fonctionnalité: Coupon et livraison gratuite ensemble

  Règle: Sans coupon, la livraison est gratuite à partir de $999.00

    Scénario: Colonne 4 · sans coupon, à partir de $999.00
      Soit Marta n'a aucun coupon appliqué
      Et elle a dans son panier des produits pour $999.00
      Quand elle passe au paiement
      Alors la livraison que lui montre la boutique est de $0.00

    Scénario: Colonne 3 · sans coupon, en dessous de $999.00
      Soit Marta n'a aucun coupon appliqué
      Et elle a dans son panier des produits pour $998.99
      Quand elle passe au paiement
      Alors la livraison que lui montre la boutique est de $99.00

  Règle: Avec le coupon, la livraison se mesure sur ce que le client paie après la réduction

    Scénario: Colonne 5 · avec coupon, en dessous du minimum du coupon
      Soit le coupon BIENVENIDA10 est en vigueur
      Et Marta n'a jamais utilisé le coupon BIENVENIDA10
      Et elle a dans son panier des produits pour $499.99
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui dit que le coupon est réservé aux achats de $500.00 ou plus

    Scénario: Colonne 8a · avec coupon, avant la réduction elle atteignait le seuil et après non
      Soit le coupon BIENVENIDA10 est en vigueur
      Et Marta n'a jamais utilisé le coupon BIENVENIDA10
      Et elle a dans son panier des produits pour $999.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre une réduction de $99.90
      Et la livraison que lui montre la boutique est de $99.00
```

**Exercice 1.** Une forme de la question : « Avec le coupon, les $3,000 se mesurent-ils sur le sous-total, sur ce qu'il
paie pour les produits après la réduction, ou sur le total livraison comprise ? » Dans la boutique d'entraînement, les
mensualités se mesurent sur le **total** ; un total de $3,000.00 exactement y entre. Si tu as trouvé une autre colonne
non définie qui tient la route (par exemple, ce qui se passe avec un total au-dessus de $50,000.00 et le coupon), elle
vaut aussi.

**Exercice 3.** Passent au rouge les scénarios où ce que l'on paie pour les produits tombe sur **exactement** $999.00 :
celui de la 4, avec un panier de $999.00 sans coupon, et celui de la 8b, avec $1,110.00 et coupon. C'est ce qui s'est
passé à l'exécution : deux au rouge. Les autres restent au vert parce que l'erreur ne change que ce qui se passe à
$999.00 exactement. Celui de la 3, avec $998.99, est le voisin immédiat du bord (leçon 02) et doit $99.00 avec ou sans
l'erreur.

Remarque une chose : la colonne 4, tu l'avais déjà depuis la leçon 02. La 8b est nouvelle. Les deux attrapent la même
erreur, mais la 8b l'attrape **dans une combinaison**, une combinaison qui peut aussi arriver à un client : avec son
coupon mis.

**Révision.** 1, quatre (2 × 2). 2, seize (2 × 2 × 2 × 2). 3, huit : la table complète a toutes les combinaisons même
si tu en réunis ensuite quelques-unes. 4, six (2 × 3). 5, trente-deux (2⁵).

**Si tu n'as pas trouvé 4,** retourne à l'étape 2 : le calcul consiste à multiplier le nombre de réponses de chaque
condition.

---

## Sources de la leçon

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.3 « Decision Table Testing » (p. 41).
   Les conditions et les actions sont les lignes et chaque colonne est une combinaison unique ; la notation T/F
   (ici O/N), « – » pour ce qui est indifférent, N/A pour l'impossible, X pour l'action qui a lieu ; la table complète,
   celle qui retire l'impossible et celle qui réunit des colonnes ; la couverture comme colonnes testées divisées par
   colonnes possibles ; et le fait que la technique aide à trouver des trous et des contradictions dans les exigences.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. ISTQB, *Certified Tester Advanced Level Test Analyst Syllabus* v3.1.2, §3.2.3 « Decision Table Testing » : « the
   inputs of the test case might be different parameters than in the conditions of the decision table » et l'exemple
   d'une condition qui « may require the tester to calculate ». Elle appuie la C3', qui demande de faire le calcul.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
3. Cucumber, « Gherkin Reference » : « Given steps are used to describe the initial context of the system » ; « When
   steps are used to describe an event, or an action » ; « Then steps are used to describe an expected outcome, or
   result ». Elle appuie la répartition entre Soit, Quand et Alors. https://cucumber.io/docs/gherkin/reference/
4. behave, « Tutorial » : « The “and” and “but” step types are renamed internally to take the preceding step’s keyword ».
   Elle appuie qu'un Et continue l'étape précédente. https://behave.readthedocs.io/en/stable/tutorial/
5. Cucumber, « Behaviour-Driven Development » : « It may also reveal gaps in our understanding, where we need more
   information before we know what to do ». Elle appuie de transformer le trou en question.
   https://cucumber.io/docs/bdd/

Mesure propre : les scénarios des colonnes 3, 4, 5, 8a et 8b ont été exécutés avec behave contre la boutique du cours
(HabilMX/curso-qa) le 21 novembre 2026. Avec la boutique propre, 5 sur 5 au vert ; avec l'erreur E1
activée, 2 au rouge (4 et 8b). Les montants ($111.00, $99.90, $899.10) et l'avis du minimum sortent de cette exécution.

Règles du cours, sans source externe :

- « Une case que personne ne sait remplir est une question pour le métier » : elle existe pour que le trou de
  l'exigence soit comblé par celui qui décide, et non par le code par accident.
- « Entre le Soit et le Quand, on fixe toutes les conditions de la colonne » : elle existe pour que, si le scénario
  échoue, tu saches quelle combinaison a échoué.
