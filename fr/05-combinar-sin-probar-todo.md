# Leçon 05 — Combiner sans tout tester

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Variable :** quelque chose de l'achat qui peut changer d'un test à l'autre : le montant du panier, le coupon, le
  client, la langue.
- **Valeur :** chaque option que prend une variable. Le coupon en a trois : sans coupon, première fois, déjà utilisé.
- **Combinaison :** une valeur de chaque variable, ensemble. Une combinaison est un test.
- **Paire :** deux valeurs de deux variables différentes, ensemble. « Montant $1,110.00 (pesos mexicains) avec coupon
  première fois » est une paire.

**Ce que tu en retires :** tu montes à la main une table de combinaisons pour quatre variables, tu vérifies qu'elle
couvre chaque paire et tu décides où il vaut la peine de passer aux combinaisons de trois.

**Idée nouvelle de cette leçon (la seule) :** avec peu de combinaisons bien choisies, on couvre chaque paire de valeurs.
Avec elle, tu t'exerces aussi à une décision : où il vaut la peine de vérifier des combinaisons de trois.

**Dans quel ordre :** tu comptes les combinaisons (étape 1), tu comptes les paires (étape 2), tu montes la table
(étape 3), tu vérifies qu'elle couvre chaque paire (étape 4), tu y mets des résultats et des scénarios (étape 5) et tu
décides où passer à trois (étape 6).

---

## La scène

*Scénario inventé ; les montants, les messages et l'erreur de la boutique, eux, sont réels.*

Vendredi, 16:00. La boutique ouvre lundi et il reste un après-midi à la QA. Elle a quatre choses à faire bouger dans le
résumé de l'achat : le montant du panier, le coupon, le client et la langue de la boutique. Tout tester, ce sont 36
combinaisons, et elle n'a pas le temps.

Elle fait ce qui semble raisonnable : que **chaque valeur sorte au moins une fois**. Trois tests, et on y voit les trois
montants, les trois cas du coupon, les deux clients et les deux langues. Les trois sortent au vert. Lundi, c'est en
ligne.

Mardi, une cliente écrit : elle a composé un panier de $1,110.00, y a mis le coupon, le total est tombé à $999.00
pile… et on lui a facturé $99.00 de livraison. Depuis la leçon 02, tu sais qu'à partir de $999.00 la livraison est
gratuite.

Chaque valeur a été testée. Ce que personne n'a testé, c'est **cette paire** : $1,110.00 **avec** le coupon première
fois. Aucun des trois tests ne les avait ensemble.

Cette leçon sert à choisir peu de tests sans laisser aucune paire de côté.

---

## Avant de commencer

**Pas d'ordinateur pour les étapes 1 à 4.** Papier et crayon, ou un tableur : tu vas monter une table et cocher des
paires. Pour l'étape 5, il te faut ton éditeur, comme aux leçons précédentes.

**Fais la première tentative sans IA.** Ce que l'on mesure, c'est si **toi**, tu montes une table qui couvre chaque
paire et si tu sais le vérifier. Une IA peut te donner une table en quelques secondes ; la feuille de paires de l'étape
4 est celle qui te dit s'il en manque une.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 04, que chaque case d'une table peut devenir un scénario ;
ici, chaque ligne de la table réunit quatre valeurs et est un scénario. Et aussi, de la leçon 02, les groupes et les
bords du montant ($999.00 de la livraison et $3,000.00 des mensualités sans intérêts) ; de la 03, le coupon
BIENVENIDA10 et son minimum de $500.00, et que la livraison se mesure après la réduction.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Les variables, leurs valeurs et combien de combinaisons cela fait

Voici les quatre variables du résumé de l'achat et les valeurs que nous allons utiliser :

| Variable | Valeurs | Combien |
|---|---|---|
| Montant du panier | $600.00 · $1,110.00 · $3,330.00 | 3 |
| Coupon BIENVENIDA10 | sans coupon · première fois · déjà utilisé | 3 |
| Client | Marta · Luis | 2 |
| Langue de la boutique | espagnol · anglais | 2 |

Les trois montants viennent des groupes de la leçon 02 : un en dessous de $999.00, un entre $999.00 et $3,000.00, et un
à partir de $3,000.00. Tous trois sont au-dessus de $500.00, pour que le coupon puisse entrer ; ce qui se passe sous le
minimum, tu l'as déjà testé à la leçon 03.

La langue de cette table est une donnée de la boutique : la langue dans laquelle la boutique parle au client. Ce n'est
pas la langue dans laquelle tu lis cette leçon ; c'est pourquoi ses valeurs sont espagnol et anglais dans toutes les
versions du cours.

Avant de continuer, **prédis** : combien de combinaisons y a-t-il si tu les testes toutes ?

Cela fait 3 × 3 × 2 × 2 = **36**. Avec quatre petites variables, l'après-midi ne suffit déjà plus. Et la boutique du cours
a cinq langues : avec les cinq, ce serait 90.

---

## Étape 2 · Compte les paires

Une paire réunit deux valeurs de deux variables différentes. Pour les compter, prends les variables deux par deux et
multiplie leurs valeurs :

| Les deux variables | Paires |
|---|---|
| Montant et coupon | 3 × 3 = 9 |
| Montant et client | 3 × 2 = 6 |
| Montant et langue | 3 × 2 = 6 |
| Coupon et client | 3 × 2 = 6 |
| Coupon et langue | 3 × 2 = 6 |
| Client et langue | 2 × 2 = 4 |
| **Total** | **37** |

Remarque une chose : une seule combinaison couvre **six paires** à la fois, une pour chaque ligne de cette table. C'est
pourquoi il faut moins de combinaisons que les 36.

Le programme avancé de l'ISTQB pour les analystes de test appelle cela le **test par paires** (*pairwise testing*) :
tester au moins une fois chaque paire de valeurs de chaque deux variables, sans tester toutes les combinaisons. On
l'emploie quand il y a plus de combinaisons que le temps n'en permet, comme dans l'après-midi du vendredi.

---

## Étape 3 · Monte la table à la main

Avant de continuer, **prédis** : combien de lignes te faut-il au minimum ? Indice : regarde la ligne la plus grande de
l'étape 2.

Le montant et le coupon à eux seuls ont déjà 9 paires, et chaque ligne n'en couvre qu'une seule. **9 lignes, c'est donc
le minimum.** La bonne nouvelle, c'est que 9 suffisent pour tout, si tu remplis bien les deux autres variables.

**1. La base.** Écris les 9 combinaisons du montant et du coupon, une par ligne. Tu couvres déjà leurs 9 paires.

**2. Le client.** Chaque montant doit sortir avec Marta et avec Luis, et chaque cas du coupon aussi. Mets Luis une fois
dans chaque groupe de montant, et chaque fois avec un coupon différent (lignes 2, 4 et 9). Dans les autres, Marta.

**3. La langue.** Pareil : anglais une fois dans chaque groupe de montant, chaque fois avec un coupon différent
(lignes 2, 6 et 7). Dans les autres, espagnol.

**4. Vérifie le dernier croisement.** Client et langue, ce sont 4 paires : Luis-anglais (ligne 2), Luis-espagnol (lignes
4 et 9), Marta-anglais (lignes 6 et 7) et Marta-espagnol (les autres). Les quatre y sont.

| # | Montant | Coupon | Client | Langue |
|---|---|---|---|---|
| 1 | $600.00 | sans coupon | Marta | espagnol |
| 2 | $600.00 | première fois | Luis | anglais |
| 3 | $600.00 | déjà utilisé | Marta | espagnol |
| 4 | $1,110.00 | sans coupon | Luis | espagnol |
| 5 | $1,110.00 | première fois | Marta | espagnol |
| 6 | $1,110.00 | déjà utilisé | Marta | anglais |
| 7 | $3,330.00 | sans coupon | Marta | anglais |
| 8 | $3,330.00 | première fois | Marta | espagnol |
| 9 | $3,330.00 | déjà utilisé | Luis | espagnol |

De 36 combinaisons à 9. Il existe des outils qui montent seuls ces tables quand les variables sont nombreuses ; ici, tu
la montes à la main pour comprendre ce qu'ils te livrent.

**Enregistre-la.** Copie la table dans un fichier `pares.md` dans `~/practica`, en Markdown et avec ses quatre
colonnes (celle du `#` est facultative). Le `verifica 05` la lit à cet endroit. Voici le début des deux premières
lignes :

```markdown
| # | Montant | Coupon | Client | Langue |
|---|---|---|---|---|
| 1 | $600.00 | sans coupon | Marta | espagnol |
| 2 | $600.00 | première fois | Luis | anglais |
```

Les valeurs s'écrivent comme dans la table : `première fois`, pas « première » ; `$1,110.00`, avec la virgule et les
centimes.

---

## Étape 4 · Vérifie qu'elle couvre chaque paire

Avant de faire confiance à une table, vérifie-la paire par paire. Copie cette feuille et coche chaque paire que tu
trouves dans la table de l'étape 3, et écris à côté de la case dans quelle ligne elle est. Voici le début : « $600 ·
première ☑ ligne 2 ». Avec le numéro de ligne, si quelque chose cloche, tu sais quelle ligne changer :

| Les deux variables | Paires qui doivent apparaître |
|---|---|
| Montant et coupon | $600 · sans ☐ · première ☐ · utilisé ☐ — $1,110 · sans ☐ · première ☐ · utilisé ☐ — $3,330 · sans ☐ · première ☐ · utilisé ☐ |
| Montant et client | $600 · Marta ☐ · Luis ☐ — $1,110 · Marta ☐ · Luis ☐ — $3,330 · Marta ☐ · Luis ☐ |
| Montant et langue | $600 · espagnol ☐ · anglais ☐ — $1,110 · espagnol ☐ · anglais ☐ — $3,330 · espagnol ☐ · anglais ☐ |
| Coupon et client | sans · Marta ☐ · Luis ☐ — première · Marta ☐ · Luis ☐ — utilisé · Marta ☐ · Luis ☐ |
| Coupon et langue | sans · espagnol ☐ · anglais ☐ — première · espagnol ☐ · anglais ☐ — utilisé · espagnol ☐ · anglais ☐ |
| Client et langue | Marta · espagnol ☐ · anglais ☐ — Luis · espagnol ☐ · anglais ☐ |

S'il reste une case non cochée, c'est qu'il manque cette paire à ta table : change une valeur d'une ligne ou ajoute-en
une.

**Fais l'épreuve à l'envers.** Efface la ligne 9 et recoche. Il te reste trois cases non cochées : $3,330 avec déjà
utilisé, $3,330 avec Luis, et déjà utilisé avec Luis. Chaque ligne porte des paires qu'aucune autre n'a.

**Et compare avec la table de la scène.** Les trois tests de « chaque valeur une fois » étaient ceux-ci :

| # | Montant | Coupon | Client | Langue |
|---|---|---|---|---|
| A | $600.00 | sans coupon | Marta | espagnol |
| B | $1,110.00 | déjà utilisé | Marta | anglais |
| C | $3,330.00 | première fois | Luis | espagnol |

Coche leurs paires sur une feuille neuve : ils couvrent **18 sur 37**. Et la paire de la cliente, $1,110.00 avec le
coupon première fois, n'y est pas.

---

## Étape 5 · Résultats attendus et scénarios

La table dit **quoi** tester, pas ce qui doit arriver. Quand un outil monte les combinaisons, le programme de l'ISTQB
indique que c'est la personne qui teste qui y met le résultat attendu. Dans une table à la main, c'est pareil : c'est
toi qui décides ce qui doit arriver à chaque ligne. Voici ceux de la boutique, mesurés le 21 nov. 2026 :

| # | Ce qui doit arriver |
|---|---|
| 1 | Livraison $99.00, total $699.00, sans mensualités sans intérêts |
| 2 | Réduction $60.00, livraison $99.00, total $639.00 |
| 3 | Le coupon n'entre pas : « ya usó este cupón » ; total $699.00 |
| 4 | Livraison $0.00, total $1,110.00 |
| 5 | Réduction $111.00, le total tombe à $999.00 et la livraison est de $0.00 |
| 6 | Le coupon n'entre pas : « this coupon was already used » ; total $1,110.00 |
| 7 | Total $3,330.00, les mensualités sans intérêts apparaissent |
| 8 | Réduction $333.00, total $2,997.00 : **les mensualités sans intérêts n'apparaissent plus** |
| 9 | Le coupon n'entre pas ; le total reste à $3,330.00 et les mensualités sans intérêts apparaissent |

Regarde la ligne 8. Avec $3,330.00, il y a des mensualités sans intérêts, et le coupon première fois fonctionne ; mais
**ensemble**, la réduction fait passer le total sous $3,000.00 et l'option disparaît. C'est ce que dit la règle de la
leçon 02, et pourtant cela surprend qui ne l'avait pas vu venir. Ce genre de surprise vit dans les paires.

Chaque ligne devient un scénario, avec des phrases du catalogue. La ligne 5, celle de la cliente :

```gherkin
# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00
```

Les lignes en anglais vont dans un fichier à part, `pares-en.feature`, avec `# language: en`, parce que la langue de la
boutique, c'est le fichier qui la fixe. Voici la ligne 7 :

```gherkin
# language: en
Feature: The purchase summary, by pairs

  Scenario: Row 7 · $3,330.00, no coupon, Marta, English
    Given Marta has no coupon applied
    And she has products worth $3,330.00 in her cart
    When she chooses how to pay
    Then the interest-free installments option appears
```

> **Une limite du catalogue.** Après « elige cómo pagar », on peut vérifier si les mensualités sans intérêts
> apparaissent, mais plus la livraison ni la réduction. Si le coupon est entré, après l'avoir appliqué tu peux vérifier
> réduction, livraison et mensualités. Si le coupon n'est pas entré, la boutique répond seulement par son message ;
> pour voir ce qui s'est passé avec le compte, choisis comment payer et vérifie les mensualités. C'est pourquoi chaque
> scénario vérifie le plus important de sa ligne, pas tout ce qui est dans la table de résultats.

**À toi :** dans un fichier `pares.feature`, copie le scénario de la ligne 5 ci-dessus et écris ceux des lignes 1, 4 et
9. Pour la 9, l'**Alors** vérifie que les mensualités sans intérêts apparaissent toujours : c'est la façon de vérifier
que le coupon n'est pas entré.

---

## Étape 6 · Quand passer à trois ?

Par paires, ce n'est pas tout tester. Si une erreur a besoin de **trois** valeurs ensemble pour apparaître, la table de
paires peut ne pas les avoir.

À quelle fréquence cela arrive-t-il ? Le NIST (l'institut de normalisation des États-Unis) résume des études à lui et
d'autres équipes, qu'ils qualifient eux-mêmes de non concluantes : dans la plupart des défaillances observées, une
seule valeur ou deux valeurs ensemble ont suffi, et dans les six études résumées, il a fallu aller de 4 à 6. Le
programme de l'ISTQB en cite une sur des dispositifs médicaux : 66 % des défaillances avec une variable et 97 % avec
une ou deux. Et le NIST avertit que par paires, on peut laisser passer entre 10 % et 40 % ou plus des erreurs d'un
système, donc cela ne suffit pas pour un logiciel critique.

C'est pourquoi on passe à trois **là où le risque l'exige**, pas partout. Trois questions aident à décider :

1. **Y bouge-t-il de l'argent ?** Une erreur y facture trop ou pas assez à quelqu'un.
2. **Ces variables s'influencent-elles entre elles selon les règles ?** Le montant, le coupon et les mensualités sans
   intérêts, oui ; la langue ne change presque pas le compte.
3. **Quelle est la fréquence d'usage ?** Une combinaison qui passe à chaque achat pèse plus qu'une rare.

Passer à trois pour seulement trois variables, cela coûte : montant, coupon et client ont 3 × 3 × 2 = 18 triplets, et
la table de l'étape 3 en couvre 9. Pour tous les avoir, il te faut au moins 18 lignes.

---

## Comment on vérifie

**Ta table** (étape 3 et exercice 1) se vérifie avec la feuille de paires de l'étape 4 : **aucune case non cochée**.

**Ta table et ton fichier** sont contrôlés par `verifica 05`. Dans le terminal de la boutique, écris :

```bash
verifica 05
```

Il lit d'abord `~/practica/pares.md` et vérifie que ta table couvre les 37 paires. Ensuite il exécute `pares.feature`,
avec tout autre `pares*.feature` que tu aies (comme `pares-en.feature`), avec la boutique propre, où ils doivent sortir
**au vert**, et avec l'erreur E1 activée, où **au moins un doit sortir au rouge**. S'ils sortent au vert les deux fois,
il te dit qu'il manque encore un scénario qui regarde le point où est l'erreur.

Avant de l'exécuter, la feuille de paires de l'étape 4 et la liste ci-dessous te disent si tu es sur la bonne voie. Les
scénarios des 9 lignes ont été exécutés contre la boutique avant de publier cette leçon : 9 au vert avec la boutique
propre ; avec l'erreur activée, la ligne 5 au rouge.

**Avant d'enregistrer, relis ton fichier avec cette liste :**

- [ ] Il y a un fichier par langue, et la première ligne de chacun est son `# language:`.
- [ ] Le titre de chaque scénario dit sa ligne et ses quatre valeurs.
- [ ] Le **Soit** pose le montant, le coupon et le client de la ligne.
- [ ] L'**Alors** vérifie un résultat de la table de l'étape 5 pour cette ligne.
- [ ] Aucun scénario ne mélange des valeurs de deux lignes.

---

## Tes exercices

1. **Cinq langues** (sans IA). Change la variable langue pour les cinq de la boutique : espagnol, anglais, français,
   portugais et bulgare. Combien de combinaisons y a-t-il si tu les testes toutes ? Combien de lignes te faut-il au
   minimum pour couvrir chaque paire ? Monte la table et vérifie-la avec une feuille de paires. Indice pour la monter :
   fais un bloc par montant et, dans chaque bloc, écris une ligne par langue ; puis répartis le coupon et le client dans
   les blocs, comme à l'étape 3, pour que chaque valeur sorte avec chaque autre. Prends 25 minutes comme limite.
2. **Lequel attrape l'erreur ?** Avec l'erreur E1 activée, la livraison cesse d'être gratuite quand ce que l'on paie
   pour la marchandise est exactement $999.00. Sans rien exécuter, dis quelles lignes de la table de l'étape 3
   passent au rouge et pourquoi les trois tests de la scène sortent au vert.
3. **Où passes-tu à trois ?** (sans IA). Avec les trois questions de l'étape 6, choisis **un** triplet de trois
   variables de cette leçon où tu passerais aux combinaisons de trois et un autre où non. Justifie chacun en deux
   lignes.

**Révision** (essaie d'en réussir au moins 5 sur 6 ; si l'un ne sort pas, retourne à l'étape 2) :

1. Trois variables de 4, 3 et 2 valeurs. Combien de combinaisons y a-t-il en tout ?
2. Dans ces mêmes trois variables, combien de paires y a-t-il ?
3. Pourquoi la table de paires de cette leçon ne peut-elle pas avoir moins de 9 lignes ?
4. Que te dit une case non cochée dans la feuille de paires ?
5. Pourquoi ne suffit-il pas que chaque valeur sorte au moins une fois ?
6. Des variables de 2, 2 et 3 valeurs, et une table de 3 lignes. Peut-elle couvrir chaque paire ? Pourquoi ?

---

## Pour conclure

À la QA, il n'a pas manqué de soin le vendredi : elle a testé chaque valeur. Ce qui a manqué, c'est de tester les
valeurs **ensemble**, deux par deux, et pour cela il ne fallait pas 36 tests : 9 suffisaient.

Ce que tu retiens d'ici :

- Toutes les combinaisons, c'est la **multiplication** des valeurs ; elles croissent très vite.
- Une **paire**, ce sont deux valeurs de deux variables ; une combinaison couvre plusieurs paires à la fois.
- La table **par paires** couvre chaque paire au moins une fois, avec bien moins de lignes.
- Elle se **vérifie** avec la feuille de paires : aucune case non cochée.
- Le résultat attendu de chaque ligne, **c'est toi qui le poses**.
- Par paires, ce n'est pas tout : on passe à trois **là où le risque l'exige**.

À la leçon 06, tu quittes la page et les phrases du catalogue, et tu parles directement à l'API, à la main.

---

## Compare tes réponses

**Étape 1, prédiction.** 3 × 3 × 2 × 2 = 36.

**Étape 3, prédiction.** 9 : le montant et le coupon à eux seuls ont 9 paires, et chaque ligne n'en couvre qu'une seule.

**Étape 3, ton `pares.md`.** La table de l'étape 3, telle quelle :

```markdown
| # | Montant | Coupon | Client | Langue |
|---|---|---|---|---|
| 1 | $600.00 | sans coupon | Marta | espagnol |
| 2 | $600.00 | première fois | Luis | anglais |
| 3 | $600.00 | déjà utilisé | Marta | espagnol |
| 4 | $1,110.00 | sans coupon | Luis | espagnol |
| 5 | $1,110.00 | première fois | Marta | espagnol |
| 6 | $1,110.00 | déjà utilisé | Marta | anglais |
| 7 | $3,330.00 | sans coupon | Marta | anglais |
| 8 | $3,330.00 | première fois | Marta | espagnol |
| 9 | $3,330.00 | déjà utilisé | Luis | espagnol |
```

**Étape 5, ton `pares.feature`.** Les lignes 1, 4, 5 et 9, comme elles ont été exécutées contre la boutique :

```gherkin
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

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00

  Escenario: Fila 9 · $3,330.00, cupón ya usado, Luis, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Luis ya usó el cupón BIENVENIDA10 en una compra anterior
    Y tiene en su carrito productos por $3,330.00
    Cuando aplica el cupón BIENVENIDA10
    Y elige cómo pagar
    Entonces la opción de meses sin intereses aparece
```

**Exercice 1.** Toutes : 3 × 3 × 2 × 5 = 90. Le minimum, c'est le croisement le plus grand qui le fixe, montant et langue
ou coupon et langue : 3 × 5 = **15 lignes**. Une façon d'y arriver, déjà vérifiée (61 paires sur 61) : trois blocs de
cinq lignes, un par montant, avec les cinq langues dans le même ordre dans chaque bloc (espagnol, anglais, français,
portugais, bulgare). Le coupon, par bloc : à $600, sans–première–utilisé–sans–première ; à $1,110,
première–utilisé–sans–première–utilisé ; à $3,330, utilisé–sans–première–utilisé–sans. Le client :
Marta–Luis–Marta–Luis–Marta dans les blocs de $600 et $3,330, et Luis–Marta–Luis–Marta–Luis dans celui de $1,110. Si ta
feuille de paires n'a aucune case non cochée, ta table vaut, même si elle n'est pas égale à celle d'une autre personne.

**Exercice 2.** Seulement la ligne 5 : $1,110.00 avec le coupon première fois est la seule où ce que l'on paie pour la
marchandise tombe sur $999.00 pile. C'est ce qui s'est passé à l'exécution : avec E1 activée, la ligne 5 au rouge et
les huit autres au vert. Les trois tests de la scène sortent au vert avec E1 (ils ont aussi été exécutés) parce
qu'aucun n'a cette paire : le B a $1,110.00 mais avec le coupon déjà utilisé, qui n'entre pas, et le C a le coupon mais
avec $3,330.00.

**Exercice 3.** Une réponse défendable : **oui** pour montant, coupon et client, parce qu'il y a de l'argent en jeu, les
trois s'influencent entre eux (le coupon est à usage unique par client et change le total) et cela arrive dans de
nombreux achats. **Non** pour client, langue et coupon ensemble, parce que la langue change les textes, pas le compte.
Si tu en as choisi une autre et que tu la justifies avec les trois questions, cela vaut aussi.

**Révision.** 1, 4 × 3 × 2 = 24. 2, 4 × 3 + 4 × 2 + 3 × 2 = 26. 3, parce que montant et coupon ont 9 paires et que
chaque ligne en couvre une. 4, qu'il manque cette paire à ta table. 5, parce qu'une erreur peut avoir besoin de **deux**
valeurs ensemble, et « chaque valeur une fois » ne les réunit pas. 6, non : les deux variables de 2 valeurs ont
2 × 2 = 4 paires entre elles, et chaque ligne n'en couvre qu'une ; avec 3 lignes, il en manque toujours au moins une.

---

## Sources de la leçon

1. ISTQB, *Certified Tester Advanced Level Test Analyst (CTAL-TA) Syllabus* v3.1.2 (erratum du 2022-01-31), §3.2.6 « Pairwise
   Testing » (pp. 32–33). « Pairwise testing is used when testing software in which several input parameters, each with
   several possible values, must be tested in combination, giving rise to more combinations than are feasible to test
   in the time allowed » ; « a table is constructed with test cases represented by rows and one column for each
   parameter » ; « the Test Analyst must supply the expected results for each combination that is created by the
   tools » ; « 66% of failures were triggered by a single variable and 97% by either one variable or two variables
   interacting » ; « There is a residual risk that pairwise testing may not detect systems failures where three or more
   variables interact » ; « The 100% pairwise coverage requires every pair of values of any pair of parameters be
   included in at least one combination ». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
2. D. Richard Kuhn, Raghu N. Kacker et Yu Lei, *Practical Combinatorial Testing*, NIST Special Publication 800-142,
   octobre 2010. « the number of interactions involved in system failures is relatively low, with a maximum from 4
   to 6 in the six studies cited » ; « pairwise testing may miss 10% to 40% or more of system bugs, and is thus not
   sufficient for mission-critical software ». https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf

Mesure propre : les variables, les résultats attendus et les messages ont été mesurés contre la boutique du cours
(hb-curso-qa, develop 0ddda22) le 21 novembre 2026, avec son API lancée sans Docker. Les 9 lignes ont été exécutées
avec behave et uniquement des phrases du catalogue : 9 sur 9 au vert avec la boutique propre ; avec l'erreur E1
activée, la ligne 5 au rouge. Les 3 tests de « chaque valeur une fois » ont aussi été exécutés : verts avec E1
désactivée et avec E1 activée. La couverture de paires de chaque table a été comptée avec un script (37 sur 37 et 18 sur
37), et en retirant la ligne 9, il a signalé les trois paires qui se perdent.

Règles du cours, sans source externe :

- « Les trois questions pour passer à trois » (argent, règles qui se croisent, usage) : c'est la façon dont ce cours
  applique à cette boutique le « selon le risque » de l'ISTQB.
