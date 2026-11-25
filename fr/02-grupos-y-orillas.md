# Leçon 02 — Groupes et bords

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, cinq mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Groupe :** un ensemble de valeurs que le système devrait traiter de la même façon. « Toute quantité de 1 à 10
  pièces » est un groupe. Dans les livres, on parle de *partitionnement en classes d'équivalence*.
- **Groupe non valide :** les valeurs que le système doit rejeter. « 0 pièce » et « le mot *deux* » sont dans des
  groupes non valides.
- **Bord :** la valeur la plus petite ou la plus grande d'un groupe. Dans « de 1 à 10 », les bords sont 1 et 10. Dans
  les livres, on parle de *valeur limite*.
- **Voisin :** la valeur qui est collée à un bord, de l'autre côté ou du même côté. Le voisin de 10 vers l'extérieur
  est 11 ; vers l'intérieur, 9.
- **Précision :** le plus petit pas qui a un sens dans une donnée. En pièces, c'est 1 ; dans les pesos de ce cours, un
  centime.

**Ce que tu en retires :** tu reçois une règle et, avant de toucher au système, tu répartis ses données en groupes (y
compris ceux qu'il faut rejeter) ; tu choisis une valeur par groupe ; tu trouves les bords de chaque groupe et tu
choisis leurs valeurs de test avec **deux** ou **trois** valeurs par bord ; et tu les écris dans une seule table
Gherkin.

**Idée nouvelle de cette leçon (la seule qui est évaluée) :** les erreurs se regroupent aux **bords** des règles. Une
limite mal placée se voit juste au bord ; une valeur du milieu la laisse presque toujours passer.

**Dans quel ordre :** tu répartis une règle en groupes (étape 1), tu trouves ses bords (étape 2), tu décides quand une
troisième valeur vaut la peine (étape 3), tu apprends pourquoi le bord de l'argent se mesure en centimes (étape 4) et
tu écris le tout dans une table de scénarios (étape 5). À la fin, tu refais seul la même chose avec deux nouvelles
règles et tu compares tes réponses.

---

## La scène

*Scénario inventé.*

Lundi, 9:40. Sofía, la stagiaire en QA de la leçon 01, a déjà appris à demander. Sa nouvelle carte dit :

> **En tant que** client, **je veux** que la livraison soit gratuite pour les gros achats, **afin de** ne pas payer
> trop.

Cette fois, elle demande avant de tester, et la personne du produit lui répond par une règle claire : **« livraison
gratuite pour les achats à partir de $999.00 (pesos mexicains) ; en dessous, la livraison coûte $99.00 »**.

Sofía écrit deux scénarios : l'un avec un panier de $1,500.00 (livraison gratuite ✅) et l'autre avec un panier de
$300.00 (livraison à $99.00 ✅). Les deux passent. Elle écrit sur la carte : « Testé : au-dessus et en dessous de
$999.00 ».

Le vendredi arrive une plainte : une cliente a composé un panier d'**exactement $999.00** et on lui a facturé $99.00 de
livraison. La règle disait « à partir de $999.00 », donc c'était gratuit.

Le développeur ouvre le code et le voit en une seconde : il a écrit `subtotal > 999` (« plus de 999 ») là où la règle
disait `subtotal >= 999` (« à partir de 999 »). Un seul caractère. Et aucun des deux scénarios de Sofía ne pouvait le
voir : $1,500.00 et $300.00 tombent loin du bord, là où les deux codes, le bon et le mauvais, donnent le même résultat.

Sofía a testé une valeur de chaque côté. Il lui a manqué de tester **juste au bord**. C'est de cela que parle cette
leçon.

---

## Avant de commencer

**Tu n'as pas besoin de l'ordinateur pour les étapes 1 à 4.** Il te faut du papier ou une page blanche, et une règle
de 30 cm ou une ligne tracée : tu vas dessiner des droites avec des nombres.

**Fais la première tentative sans IA.** Comme à la leçon 01 : ce que l'on mesure, c'est si tu trouves les groupes et
les bords. Avec ta liste en main, tu pourras ensuite voir ce qui manque à celle d'une IA.

**Combien de temps :** environ 60 minutes la première fois (estimation ; nous l'ajusterons avec la première promotion
d'élèves).

---

## Étape 1 · Répartis l'entrée en groupes

La technique s'appelle **partitionnement en classes d'équivalence**. L'idée, telle que la décrit le programme officiel
de l'ISTQB (l'organisation internationale dont ce cours utilise le programme et le vocabulaire de test comme
référence) : si les valeurs d'un groupe sont toutes traitées de la même façon, et qu'une valeur du groupe trouve une
erreur, on s'attend à ce que n'importe quelle autre valeur du même groupe la trouve aussi. C'est pourquoi, en théorie,
**une valeur par groupe suffit** : c'est une façon efficace de choisir, pas une garantie.

Tu vas t'exercer avec une règle de la boutique :

> **Règle :** dans le panier, tu peux mettre **de 1 à 10 pièces** de chaque produit.

### 1a. Que peut-il arriver ?

Avant de répartir, demande quelles valeurs **peuvent arriver** au système, pas seulement lesquelles sont correctes.
Sur la page, le champ de quantité a de petites flèches qui ne descendent pas sous 1 ni ne montent au-dessus de 10. Mais
cela ne limite pas ce qui arrive : quelqu'un peut envoyer la requête directement à l'API (la porte par laquelle
d'autres programmes parlent à la boutique ; tu la vois à la leçon 06), ou modifier la page depuis le navigateur. Le
guide de MDN, la documentation de référence du web, le dit sans détour : ce que valide le navigateur **ne constitue pas
une protection**, et le serveur doit le revérifier.

Donc, pour cette règle, peuvent arriver :

- un nombre entier, positif, zéro ou négatif ;
- un nombre à décimales, comme `2.5` ;
- quelque chose qui n'est pas un nombre, comme `deux` ;
- rien (le champ vide).

### 1b. Répartis en groupes

Dessine une droite avec les entiers et marque où le comportement change :

```
   ... -1   0 │ 1   2   3   4   5   6   7   8   9  10 │ 11  12 ...
   ─────────────┼─────────────────────────────────────────┼─────────────
   non valide   │           valide : accepté              │  non valide
   « moins de 1 »│                                        │  « plus de 10 »
```

Et à part, les groupes qui ne tiennent pas sur la droite, parce que ce ne sont pas des entiers :

| # | Groupe | Valide ? | Une valeur pour le tester | Ce qui doit se produire |
|---|---|---|---|---|
| G1 | Entiers de 1 à 10 | Oui | 4 | Accepté ; le panier affiche 4 pièces |
| G2 | Entiers de 0 ou moins | Non | −3 | Rejeté avec un message qui indique le minimum |
| G3 | Entiers de 11 ou plus | Non | 25 | Rejeté avec un message qui indique le maximum |
| G4 | Nombres qui ne sont pas entiers (2.5, −0.5) | Non | 2.5 | Rejeté : les demi-pièces n'existent pas |
| G5 | Quelque chose d'écrit qui ne se lit pas comme un nombre | Non | `deux` | Rejeté |
| G6 | Champ vide ou qui n'est pas arrivé | Non | (rien) | Rejeté |

Remarque comment ils sont écrits : on sépare d'abord le **type** (entier, nombre à décimales, texte, rien) et ensuite
l'intervalle. Ainsi −0.5 tombe dans un seul groupe, G4, et non dans deux. Et si la boutique traite différemment « vide »
et « pas arrivé », ce sont deux groupes : écris-le sur une carte rouge.

Six groupes, un valide et cinq non valides. Remarque trois choses :

1. **Les groupes ne se chevauchent pas.** Chaque valeur tombe dans un seul. Si une valeur semble être dans deux, ta
   répartition a un trou dans la règle : écris-le sur une carte rouge, comme à la leçon 01.
2. **Aucun groupe n'est vide.** Si tu ne peux pas donner un exemple d'un groupe, revois la règle : peut-être que ce
   groupe est impossible, ou peut-être qu'il manque à le définir.
3. **Chaque groupe non valide se teste séparément** (règle du cours ; plus bas, on dit pourquoi). Si tu envoies `−3` et
   `deux` dans la même requête et que la boutique la rejette, tu ne sais pas lequel des deux l'a provoqué. C'est la
   même idée que celle de la leçon 01, « un scénario, une règle », appliquée aux données : **une valeur non valide à la
   fois**.

Avec six valeurs (4, −3, 25, 2.5, `deux` et vide), tu as testé chaque groupe une fois. C'est ce que l'ISTQB appelle
couvrir 100 % des partitions que tu as identifiées.

**Est-ce suffisant ?** Pour trouver un groupe oublié, oui. Pour trouver une limite mal placée, non. Voilà Sofía : ses
deux valeurs étaient des représentants parfaits de ses deux groupes, et l'erreur est passée quand même. Il manque
l'étape 2.

---

## Étape 2 · Cherche les bords

La deuxième technique s'appelle **analyse des valeurs limites**. Le programme de l'ISTQB explique pourquoi elle existe :
aux bords des groupes, il est **plus probable** que le développeur se trompe (le guide SWEBOK de l'IEEE Computer
Society dit la même chose : beaucoup de défaillances se concentrent près des valeurs extrêmes), et l'erreur typique est
une limite décalée d'un cran vers le haut ou vers le bas, ou qui manque complètement. Celle de Sofía est exactement
cela : la limite s'est retrouvée décalée d'un centime.

Elle ne fonctionne qu'avec des groupes **ordonnés et sans trous** : toute valeur entre deux valeurs du groupe doit être
du même groupe. G1, G2 et G3 le respectent : ce sont des tronçons de la droite des entiers. G4 non : entre 0.5 et 1.5
il y a le 1, qui est d'un autre groupe. G5 et G6 n'ont pas d'ordre. Ces trois-là gardent leur valeur de l'étape 1.

### 2a. Les bords sont des valeurs, pas des traits

Il est facile de confondre le bord et le trait ; un article de l'ISTQB les sépare ainsi : le bord **n'est pas le trait**
entre deux groupes ; c'est une **valeur** qui appartient à un groupe. Chaque groupe a les siens :

| Groupe | Son bord le plus petit | Son bord le plus grand |
|---|---|---|
| G2, moins de 1 | (il n'en a pas : il continue vers les négatifs) | 0 |
| G1, de 1 à 10 | 1 | 10 |
| G3, plus de 10 | 11 | (il n'en a pas : il continue vers le haut) |

Quatre bords : **0, 1, 10 et 11**.

### 2b. Deux valeurs par bord

Dans la forme à **deux valeurs**, pour chaque bord tu testes le bord lui-même et son voisin le plus proche **de l'autre
côté** :

| Bord | Le bord | Son voisin de l'autre côté |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 0 |
| 10 | 10 | 11 |
| 11 | 11 | 10 |

Elles se répètent, parce que le voisin d'un bord est le bord du groupe d'à côté. Rassemble les valeurs sans répétition :
**{0, 1, 10, 11}**. Quatre tests couvrent les quatre bords.

```
          0 │ 1                          10 │ 11
   ─────●───┼───●──────────────────────●────┼───●─────
```

### 2c. Lis la règle à la loupe

Les bords sortent des mots de la règle, et les mots trompent. Avant de choisir des valeurs, souligne dans la règle
chacune de ces expressions et demande ce qu'elle signifie exactement :

| La règle dit… | Question en rouge avant de continuer |
|---|---|
| « à partir de 999 », « dès 999 » | Le 999 est-il compris ? (Presque toujours oui, mais fais-toi le confirmer) |
| « plus de 999 », « au-dessus de 999 » | Le 999 est-il compris ? (Presque toujours non) |
| « jusqu'à 10 », « maximum 10 » | Le 10 est-il compris ? |
| « entre 1 et 10 » | Le 1 et le 10 sont-ils compris ? Ici, la réponse change d'une personne à l'autre |
| « moins de », « au moins » | Pareil : le bord est-il compris ou non ? |

L'article de l'ISTQB sur les valeurs limites recommande justement cela : relire la règle avec une liste avant de tester,
parce que « au moins », « au plus » et « entre » se comprennent de travers. Dans la scène, la règle de Sofía disait « à
partir de $999.00 » et le code disait « plus de 999 ». La question en rouge, « le $999.00 est-il compris ? », aurait mis
l'erreur sur la table avant qu'on écrive une ligne de code.

---

## Étape 3 · Trois valeurs quand une erreur coûte plus cher

Il existe une seconde forme, celle à **trois valeurs** : pour chaque bord, tu testes le bord et **ses deux voisins**,
celui de l'extérieur et celui de l'intérieur.

| Bord | Voisin d'un côté | Le bord | Voisin de l'autre côté |
|---|---|---|---|
| 0 | −1 | 0 | 1 |
| 1 | 0 | 1 | 2 |
| 10 | 9 | 10 | 11 |
| 11 | 10 | 11 | 12 |

Rassemblées sans répétition : **{−1, 0, 1, 2, 9, 10, 11, 12}**. Huit tests au lieu de quatre.

```
     -1   0 │ 1   2                  9   10 │ 11  12
   ──○────●─┼───●───○────────────────○────●─┼───●───○──
          ● = deux valeurs     ○ = ce qu'ajoutent trois valeurs
```

**À quoi servent les quatre de plus ?** Le programme de l'ISTQB donne cet exemple : la règle dit « si x est **inférieur
ou égal** à 10 » et le développeur écrit « si x est **égal** à 10 ». Avec deux valeurs, tu testes 10 et 11, et le code
erroné donne le même résultat que le bon dans les deux cas. Le 9, qui n'apparaît qu'avec trois valeurs, le trahit : la
règle dit oui et le code dit non.

Que l'erreur soit un opérateur changé (`>` au lieu de `>=`, `<=` au lieu de `=`) n'est pas rare : c'est un caractère.
L'article de l'ISTQB fait le décompte complet pour une règle de longueur minimale : sur **dix** façons d'écrire mal la
comparaison, les deux valeurs en attrapent **huit** ; les trois valeurs, les **dix**. Il en va de même avec la règle de
la scène (tu le verras à l'étape 4).

**Alors toujours trois ?** Non. Trois valeurs demandent plus de tests (ici, de quatre à huit), et l'ISTQB laisse la
décision au risque : les trois sont plus rigoureuses, et l'effort supplémentaire peut valoir la peine ou non. Dans ce
cours, nous utilisons cette **règle du cours** (elle ne vient pas de l'ISTQB ; c'est la façon dont nous décidons
ici) :

> **Deux valeurs par bord, sauf quand la règle déplace de l'argent ou décide qui peut faire quelque chose : là, trois.**

**Pourquoi :** dans ces règles, l'erreur qui s'échappe n'est pas un écran moche ; c'est un prélèvement en trop, une
réduction qui n'était pas due ou une porte ouverte. Quatre tests de plus coûtent des minutes ; l'erreur coûte des
clients.

---

## Étape 4 · Le bord de l'argent se mesure en centimes

Reviens à la règle de Sofía : **« livraison gratuite à partir de $999.00 »**.

Il y a deux groupes, tous deux valides :

| Groupe | De… | À… | Livraison |
|---|---|---|---|
| E1 | $0.01 | $998.99 | $99.00 |
| E2 | $999.00 | (sans plafond) | Gratuite |

**Pourquoi $998.99 et pas $998 ?** Parce que le voisin d'un bord est à **un pas de précision**, et que dans ce cours
les montants sont en pesos avec centimes : le pas est de $0.01 (dans une règle réelle, confirme-le). Si ton voisin était
$998.00, tu laisserais sans tester 99 centimes entre lui et le bord, et une limite décalée à $998.50 passerait sans que
tu la voies. L'article de l'ISTQB le dit pour toute donnée continue : on choisit d'abord la précision, puis on cherche
les bords avec cette précision.

**Les valeurs pour le bord de $999.00**, avec trois valeurs parce que c'est de l'argent :

| Bord | Les trois valeurs |
|---|---|
| $998.99 (le plus grand de E1) | $998.98 · **$998.99** · $999.00 |
| $999.00 (le plus petit de E2) | $998.99 · **$999.00** · $999.01 |

Rassemblées sans répétition : **$998.98, $998.99, $999.00 et $999.01**.

Attention : E1 a aussi un bord en bas, $0.01. Ce tableau couvre **seulement le bord de $999.00**, celui qui décide de la
livraison ; le bord minimal du panier se teste avec sa propre règle, dans sa propre table.

Et maintenant, l'erreur de la scène : avec `subtotal > 999`, un panier de **$999.00** paie la livraison. La valeur
$999.00 est sur la liste dès la forme à deux valeurs ; Sofía l'aurait attrapée avec un seul test de plus.

Nous avons fait le décompte avec dix façons d'écrire mal cette comparaison (cinq opérateurs erronés contre $999.00 et
cinq contre $998.99 ; ce ne sont pas toutes les erreurs possibles, seulement celles d'un opérateur changé) : comme dans
l'article de l'ISTQB, les deux valeurs en attrapent **huit** et les trois valeurs attrapent les **dix**. L'une des deux
qui s'échappent avec deux valeurs est « livraison gratuite seulement si le sous-total est **égal** à $999.00 », qui ne
tombe qu'avec $999.01.

### Un avertissement pour quand tu automatiseras

Beaucoup de langages stockent les décimales de façon approximative : en Python, `0.1 + 0.1 + 0.1 == 0.3` donne
**faux** (sa documentation officielle l'explique). C'est pourquoi l'argent se programme avec des types décimaux ou en
centimes entiers, et Martin Fowler avertit qu'en arrondissant de l'argent, il est facile de perdre des centimes. Tu le
verras à fond à la leçon 07. Pour aujourd'hui, une seule question dans ta liste suffit : **le bord de $999.00
compare-t-il bien quand le sous-total vient de l'addition de trois t-shirts à $333.00 ?** C'est le même bord, atteint
par un autre chemin, et il vaut un test.

---

## Étape 5 · Écris-le dans une table de scénarios

Avec huit valeurs, écrire huit scénarios presque identiques est fastidieux, et en copiant huit fois, il est facile
qu'une différence s'échappe. Gherkin, le format que tu as utilisé à la leçon 01, a une forme pour cela : **`Plan du
scénario`** (en anglais, *Scenario Outline*) avec une table d'**`Exemples`**. Cucumber, le projet qui maintient
Gherkin, le décrit ainsi : les étapes du plan sont un modèle qui ne s'exécute pas tout seul ; il s'exécute **une fois
par ligne** de la table, sans compter la ligne de titres.

```gherkin
# language: fr
Fonctionnalité: Livraison gratuite pour les gros achats

  Règle: La livraison est gratuite pour les achats à partir de $999.00 ; en dessous, elle coûte $99.00

    Plan du scénario: Livraison selon le sous-total
      Soit Marta n'a aucun coupon appliqué
      Et elle a dans son panier des produits pour <sous-total>
      Quand elle passe au paiement
      Alors la livraison que lui montre la boutique est de <livraison>

      Exemples:
        | sous-total | livraison |
        | $998.98    | $99.00    |
        | $998.99    | $99.00    |
        | $999.00    | $0.00     |
        | $999.01    | $0.00     |
```

Quatre lignes, quatre scénarios. Si demain la règle passe à « à partir de $1,499.00 », tu changes quatre nombres et non
quatre scénarios.

Trois précautions qui viennent de la leçon 01 et restent valables :

1. **Une table, une règle.** Toutes les lignes testent « livraison à partir de $999.00 ». Si tu veux tester le nombre de
   pièces, cela va dans une autre table, sous sa propre `Règle:`.
2. **L'`Alors` se voit de l'extérieur :** la livraison que montre la boutique, pas un champ dans la base de données.
3. **Aucune autre donnée ne décide du résultat.** C'est pourquoi le premier `Soit` dit que Marta n'a pas de coupon :
   dans cette boutique, la livraison se mesure avec le coupon déjà appliqué, et les 10 % de la leçon 01 feraient passer
   le sous-total sous le bord.

Et une nouvelle, règle du cours : **les groupes non valides vont dans leur propre table**, avec le message qui doit
sortir. Par exemple, pour la règle des pièces :

```gherkin
# language: fr
Fonctionnalité: Pièces par produit dans le panier

  Règle: On peut mettre de 1 à 10 pièces de chaque produit

    Plan du scénario: Quantité qui est acceptée
      Soit Marta a le t-shirt bleu dans son panier
      Quand elle change la quantité à <pièces>
      Alors son panier affiche <pièces> pièces du t-shirt bleu

      Exemples:
        | pièces |
        | 1      |
        | 2      |
        | 9      |
        | 10     |

    Plan du scénario: Quantité qui est rejetée
      Soit Marta a 1 pièce du t-shirt bleu dans son panier
      Quand elle change la quantité à <pièces>
      Alors la boutique lui dit que <message>
      Et son panier contient toujours 1 pièce du t-shirt bleu

      Exemples:
        | pièces | message                                |
        | -1     | le minimum est de 1 pièce              |
        | 0      | le minimum est de 1 pièce              |
        | 11     | le maximum est de 10 pièces            |
        | 12     | le maximum est de 10 pièces            |
        | 2.5    | la quantité doit être un nombre entier |
        | deux   | la quantité doit être un nombre        |

    Scénario: Quantité vide
      Soit Marta a 1 pièce du t-shirt bleu dans son panier
      Quand elle laisse la quantité vide
      Alors la boutique lui dit que la quantité est obligatoire
      Et son panier contient toujours 1 pièce du t-shirt bleu
```

Le groupe « vide » va dans un scénario à part, sans table, parce qu'une cellule vide prête à confusion. Remarque aussi
que le `Soit` fixe combien de pièces il y avait (1) : ainsi, le dernier `Alors` a une valeur que l'on peut vérifier.

Ici, nous utilisons trois valeurs même si la règle ne déplace pas d'argent, pour que tu voies la forme complète. Avec
la règle du cours, 0, 1, 10 et 11 suffiraient, plus une valeur pour chaque groupe sans ordre.

---

## Comment on vérifie

**Ce que tu fais sans machine** (étapes 1 à 4 et tes exercices) se compare avec « Compare tes réponses », à la fin. Ce
qui doit coïncider : les groupes (ni chevauchés ni vides), les bords, et les valeurs à deux et à trois.

**Ton fichier de scénarios** est contrôlé par `verifica 02`. Enregistre-le sous le nom `envio.feature` dans `~/practica`
et, dans le terminal de la boutique, écris :

```bash
verifica 02
```

Il fait ce que le cours promet depuis le début : il exécute tes scénarios contre la boutique **sans** erreurs, où ils
doivent sortir au vert, et contre la boutique avec **la limite décalée** semée exprès (E1), où **au moins un doit sortir
au rouge**. Si tes scénarios sortent au vert dans les deux, c'est qu'ils ne regardaient pas le bord. Avant de
l'exécuter, la liste ci-dessous te dit si la forme est bonne.

**Avant d'enregistrer, relis ton fichier avec cette liste :**

- [ ] La première ligne est `# language: fr`, et il y a une seule `Fonctionnalité:`.
- [ ] Chaque `Plan du scénario:` a en dessous une table `Exemples:` avec une ligne de titres.
- [ ] Chaque `<nom>` des étapes est exactement un titre de la table (avec la même orthographe).
- [ ] Les quatre montants sont là : $998.98, $998.99, $999.00 et $999.01.
- [ ] Un `Soit` laisse de côté le coupon, pour qu'aucune ligne ne dépende d'une autre règle.
- [ ] Si l'erreur était `subtotal > 999`, au moins une ligne devrait sortir différemment. Laquelle ?

---

## Tes exercices

**Exercice 1, sans IA.** Règle de la boutique :

> Le nom imprimé sur une carte cadeau fait de **2 à 30 caractères**.

1. **Ce qui peut arriver :** note tout ce qui pourrait arriver au champ, pas seulement ce qui est correct.
2. **Groupes :** fais la table des groupes (valides et non valides) avec une valeur pour chacun.
3. **Bords :** écris les bords de chaque groupe ordonné et les valeurs à **deux** valeurs par bord.
4. **Carte rouge :** écris au moins une question que tu poserais avant de tester. (Indice : une espace compte-t-elle
   comme un caractère ? Et un emoji ?)

**Exercice 2, sans IA.** Règle de la boutique :

> Tu peux payer en mensualités sans intérêts pour des achats **à partir de $3,000.00 et jusqu'à $50,000.00**.

1. **Groupes :** combien il y en a et lesquels.
2. **Valeurs à trois pour les deux bords qui décident des mensualités** ($3,000.00 et $50,000.00), sans répétition.
   (Le bord tout en bas, le total le plus petit possible, est décidé par une autre règle.)
3. **Table :** écris le plan du scénario dans un fichier `meses.feature`, avec `# language: fr`.
4. Écris une erreur d'une seule ligne (comme le `>` de Sofía) que tes **trois** valeurs attrapent et que **deux**
   valeurs n'attrapent pas.

**Révision.** Il faut en réussir 7 sur 8, et ceux que tu ne peux **pas** te permettre de rater sont le 2, le 3 et le 8 :
ce sont ceux de l'idée de la leçon.

1. Règle « de 1 à 10 pièces ». De combien de valeurs as-tu besoin pour couvrir tous les groupes ordonnés, une par
   groupe ?
2. Même règle. Quelles valeurs sortent avec deux valeurs par bord ?
3. Même règle. Quelles valeurs la forme à trois valeurs ajoute-t-elle ?
4. Règle « livraison gratuite à partir de $999.00 ». Quel est le voisin extérieur de $999.00, et pourquoi n'est-ce pas
   $998.00 ?
5. Les bords sont-ils le trait entre deux groupes, ou des valeurs qui appartiennent à un groupe ?
6. Tu envoies `−3` et `deux` dans la même requête, et la boutique la rejette. Que ne sais-tu pas ?
7. La page ne te laisse pas écrire 11 dans la quantité. N'y a-t-il plus besoin de tester le 11 ? Pourquoi ?
8. Règle « si x est inférieur ou égal à 10 », programmée comme « si x est égal à 10 ». Quelle valeur la trahit : le 10,
   le 11 ou le 9 ?

---

## Pour conclure

Sofía n'avait pas besoin de plus de tests, mais d'**un autre** test : un juste à $999.00. Deux scénarios loin du bord
lui ont dit que la règle existait ; aucun ne lui a dit si elle était bien placée.

Ce que tu retiens d'ici :

- D'abord, **ce qui peut arriver**, pas seulement ce qui est correct.
- Répartis en **groupes** qui ne se chevauchent pas, valides et non valides, et teste les non valides **un à la fois**.
- Les erreurs se regroupent aux **bords** : teste le bord et son voisin de l'autre côté (deux valeurs), ou le bord et
  ses deux voisins (trois valeurs).
- Le voisin est à **un pas de précision** : une pièce, un centime, une seconde.
- **Lis la règle à la loupe :** « à partir de », « plus de » et « entre » se demandent avant de tester.

À la leçon 03, tu construis une table de décision pour une promotion à plusieurs conditions : tu verras ce qui se passe
quand le coupon de la leçon 01 et la livraison gratuite décident ensemble du même panier.

---

## Compare tes réponses

**Exercice 1, nom de 2 à 30 caractères.** Ce que l'on teste, c'est la **longueur** du nom, et une longueur ne peut pas
être négative. L'article de l'ISTQB appelle cela le *domaine* : les valeurs qui sont possibles. C'est pourquoi il n'y a
pas de −1.

| Groupe | Valide ? | Une valeur |
|---|---|---|
| Longueur 0 (vide) et 1 | Non | `A` (1 caractère) |
| Longueur de 2 à 30 | Oui | `Lupita` (6) |
| Longueur de 31 et plus | Non | un nom de 40 caractères |

Bords : **0 et 1** (ceux du groupe court), **2 et 30** (ceux du valide) et **31** (le plus petit du long). Avec deux
valeurs : **{0, 1, 2, 30, 31}**. Le 0 n'a pas de voisin extérieur : une longueur de −1 n'existe pas. Si tu as séparé
« vide » comme groupe à part, c'est bien aussi : c'est un cas que beaucoup de systèmes traitent différemment (« le nom
est obligatoire » au lieu de « il est trop court »), et il vaut la carte rouge.

Questions rouges qui valent la peine d'être posées : les espaces au début et à la fin comptent-ils ? Un emoji compte-t-il
pour un seul caractère ou pour plusieurs ? Les accents et le ñ sont-ils acceptés ? Que se passe-t-il avec un nom fait
uniquement d'espaces ?

**Exercice 2, mensualités sans intérêts de $3,000.00 à $50,000.00.** Trois groupes : en dessous de $3,000.00 (ne
s'applique pas), de $3,000.00 à $50,000.00 (s'applique) et au-dessus de $50,000.00 (ne s'applique pas).

| Bord | Les trois valeurs |
|---|---|
| $2,999.99 | $2,999.98 · $2,999.99 · $3,000.00 |
| $3,000.00 | $2,999.99 · $3,000.00 · $3,000.01 |
| $50,000.00 | $49,999.99 · $50,000.00 · $50,000.01 |
| $50,000.01 | $50,000.00 · $50,000.01 · $50,000.02 |

Sans répétition : **$2,999.98, $2,999.99, $3,000.00, $3,000.01, $49,999.99, $50,000.00, $50,000.01 et $50,000.02**.
Huit.

Une forme du fichier :

```gherkin
# language: fr
Fonctionnalité: Mensualités sans intérêts

  Règle: On peut payer en mensualités sans intérêts pour des achats à partir de $3,000.00 et jusqu'à $50,000.00

    Plan du scénario: Option de mensualités selon le total
      Soit Marta a dans son panier des produits pour <total>
      Quand elle choisit comment payer
      Alors l'option des mensualités sans intérêts <résultat>

      Exemples:
        | total      | résultat       |
        | $2,999.98  | n'apparaît pas |
        | $2,999.99  | n'apparaît pas |
        | $3,000.00  | apparaît       |
        | $3,000.01  | apparaît       |
        | $49,999.99 | apparaît       |
        | $50,000.00 | apparaît       |
        | $50,000.01 | n'apparaît pas |
        | $50,000.02 | n'apparaît pas |
```

Une erreur que trois valeurs attrapent et que deux n'attrapent pas : « mensualités seulement si le total est **égal** à
$3,000.00 » au lieu de « à partir de $3,000.00 ». Avec deux valeurs ($2,999.99 et $3,000.00), le mauvais code se
comporte comme le bon ; $3,000.01 le trahit. Une autre : « mensualités si le total est **différent** de $2,999.99 »,
qui accepte tout sauf cette valeur ; avec deux valeurs, elle passe, et $2,999.98 la trahit.

**Révision :**

1. Trois : une par groupe ordonné (par exemple −3, 4 et 25).
2. {0, 1, 10, 11}.
3. −1, 2, 9 et 12.
4. $998.99, parce que la précision de l'argent est d'un centime. Avec $998.00, il reste 99 centimes sans test.
5. Des valeurs qui appartiennent à un groupe. Le trait ne peut pas se tester ; les valeurs, si.
6. Lequel des deux a provoqué le rejet. Les non valides vont un à la fois.
7. Si, il faut le tester : la page n'est pas la seule porte. L'API peut recevoir un 11, et le serveur doit le rejeter.
8. Le 9. Avec « égal à 10 », le 10 donne la même chose que la règle (oui) et le 11 aussi (non) ; le 9 donne « non » là
   où la règle dit « oui ».

Si tu n'as pas réussi le 4 ou le 8, revois les étapes 3 et 4 : c'est là que se rejoignent la précision et les trois
valeurs.

---

## Sources de la leçon

Consultées et lues le 21 nov. 2026.

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 15 septembre 2024, §4.2.1 « Equivalence Partitioning »
   et §4.2.2 « Boundary Value Analysis ». Les groupes ne se chevauchent pas et ne sont pas vides ; une valeur par
   groupe ; les bords sont le minimum et le maximum d'un groupe ordonné ; les développeurs se trompent davantage aux
   bords ; les formes à deux et à trois valeurs, et l'exemple de « x ≤ 10 » écrit « x = 10 ».
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Matthias Hamburg et Adam Roman, « Boundary Value Analysis According to the ISTQB® Foundation Level Syllabus »,
   ISTQB, 2025. Les bords ne sont pas le trait ; les six étapes ; le domaine des valeurs possibles ; les dix
   comparaisons mal écrites (deux valeurs en attrapent huit) ; la précision dans les données continues ; relire « au
   moins », « entre » et « au plus ».
   https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf
3. IEEE Computer Society, *SWEBOK Guide* v4.0a, chapitre 5 « Software Testing », §3.1.1 et §3.1.2. La partition inclut
   des valeurs valides et hors plage ; beaucoup de défaillances se concentrent près des valeurs extrêmes.
   https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf
4. Cucumber, « Gherkin Reference », section *Scenario Outline* et *Examples* : le plan est un modèle qui s'exécute une
   fois par ligne. https://cucumber.io/docs/gherkin/reference/
5. Cucumber, mots-clés de Gherkin en français (`gherkin-languages.json`) : « Plan du scénario » et « Exemples ».
   https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
6. MDN Web Docs, `<input type="number">` : la validation du navigateur ne constitue pas une protection ; le serveur
   doit vérifier. https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/number
7. OWASP, *Input Validation Cheat Sheet* : pour les nombres, on définit type, format, minimum et maximum, et on valide
   côté serveur même si le navigateur contrôle déjà le même champ.
   https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
8. Python, « Floating-Point Arithmetic: Issues and Limitations » : `0.1 + 0.1 + 0.1 == 0.3` donne `False`.
   https://docs.python.org/3/tutorial/floatingpoint.html
9. Microsoft Learn, « Floating-point numeric types (C# reference) » : le type `decimal` est celui qui convient aux
   montants d'argent. https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types
10. Martin Fowler, « Money », *Patterns of Enterprise Application Architecture*, 2003 : en arrondissant de l'argent, il
    est facile de perdre des centimes. https://martinfowler.com/eaaCatalog/money.html

**Règles du cours** (sans deux sources ; elles disent pourquoi elles existent) :

- « Deux valeurs par bord, sauf argent ou droits : trois ». Pourquoi : là, l'erreur qui s'échappe coûte des clients, et
  quatre tests de plus coûtent des minutes.
- « Les non valides, un à la fois ». Cela vient de « un scénario, une règle » de la leçon 01 : si deux choses échouent
  ensemble, tu ne sais pas laquelle a échoué.
- « Les groupes non valides vont dans leur propre table ». Pourquoi : chaque table teste une seule chose, et le message
  attendu change selon le groupe.
