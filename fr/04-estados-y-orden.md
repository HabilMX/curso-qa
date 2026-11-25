# Leçon 04 — États et ordre

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **État :** où se trouve quelque chose sur son chemin. Une commande « payée » est un état ; « livrée » en est un autre.
- **Événement :** ce qui arrive et peut faire passer quelque chose d'un état à un autre : le client paie, l'entrepôt
  l'expédie, le client annule.
- **Transition :** le passage d'un état à un autre par un événement. « Payée → annule → annulée » est une transition.
- **Table d'états :** une table avec les états dans les lignes et les événements dans les colonnes ; dans chaque case,
  là où mène cet événement depuis cet état.

**Ce que tu en retires :** tu dessines les états d'une commande, tu remplis sa table d'états et tu sais lire ses cases
vides ; ensuite tu écris des scénarios qui testent des événements dans le désordre, et tu sais lequel d'entre eux
attrape l'erreur qui laisse annuler ce qui a déjà été livré.

**Idée nouvelle de cette leçon (la seule qui est évaluée) :** chaque case vide d'une table d'états est un scénario.

**Dans quel ordre :** tu trouves les états et les événements (étape 1), tu dessines le chemin (étape 2), tu remplis la
table (étape 3), tu lis les cases vides (étape 4) et tu écris un scénario par case (étape 5).

---

## La scène

*Scénario inventé ; les états, les montants et les messages de la boutique, eux, sont réels.*

Lundi, 10:00. Sofía reçoit son colis : un T-shirt bleu. À 10:20, elle entre dans « Mes commandes », voit le bouton
« Annuler » encore là et appuie dessus. La boutique lui répond « Commande 17 annulée » et rembourse $432.00 (pesos
mexicains) sur sa carte.

Sofía garde le T-shirt **et** son argent. Elle n'a pas triché : la boutique l'a laissée faire.

À la QA, personne n'a testé cela, et ce n'est pas par négligence. On a testé qu'on pouvait annuler une commande payée :
cela fonctionnait. On a testé qu'une commande passait de payée à livrée : cela fonctionnait. Chaque étape du chemin,
**dans son ordre**, était correcte. Ce que personne n'a testé, c'est un événement **hors de son tour** : annuler quand
la commande était déjà arrivée.

La règle, elle, était écrite, depuis la leçon 01 : « on peut annuler tant que la commande n'est pas sortie de
l'entrepôt ». Ce qui a manqué, c'est une façon de voir, d'un coup d'œil, **toutes** les fois où quelqu'un peut appuyer
sur un bouton au mauvais moment. Cette façon, c'est la table de cette leçon.

---

## Avant de commencer

**Pas d'ordinateur pour les étapes 1 à 4.** Papier et crayon : tu vas dessiner des cercles et des flèches, puis une
table. Pour l'étape 5, il te faut ton éditeur, comme aux leçons 01 à 03.

**Fais la première tentative sans IA.** Ce que l'on mesure, c'est si **toi**, tu trouves les cases vides et si tu en
fais des scénarios. Si une IA te remplit la table, il est facile qu'elle remplisse aussi les cases qui devraient rester
vides, et ce sont justement celles que tu cherches. Avec ta table en main, ensuite, tu peux comparer.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 01, l'histoire d'annuler une commande et ses règles ; de
la 03, qu'une table t'oblige à regarder toutes les combinaisons, et qu'une case que personne ne sait remplir est une
question.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Trouve les états et les événements

Ouvre la boutique d'entraînement, entre comme Marta et regarde « Mes commandes ». Chaque commande affiche un mot à côté
de son numéro : c'est son état. La boutique en utilise six :

| État | Ce que cela signifie |
|---|---|
| créée | Le client a monté la commande, mais il n'a pas encore payé |
| payée | La passerelle a approuvé le prélèvement |
| à l'entrepôt | L'entrepôt est en train de la préparer |
| expédiée | Elle est déjà partie avec le transporteur |
| livrée | Elle est arrivée entre les mains du client |
| annulée | Elle a été annulée ; si elle avait été payée, l'argent a été remboursé |

Et trois événements peuvent faire bouger une commande :

| Événement | Qui le provoque |
|---|---|
| **paie** | Le client, avec sa carte |
| **avance** | L'entrepôt ou le transporteur : il la prépare, l'expédie, la livre |
| **annule** | Le client, avec le bouton « Annuler » |

Les règles qui décident quel événement fait bouger quel état sont trois. Celle d'annuler, nous la reprenons de la
leçon 01 ; les deux autres sont propres à cette boutique :

- La commande suit cet ordre : créée → payée → à l'entrepôt → expédiée → livrée. Seul le paiement la fait passer de
  « créée » à « payée ».
- On peut annuler tant que la commande n'est pas sortie de l'entrepôt. Si elle a déjà été payée, elle est remboursée sur
  la même carte ; dans la règle de la leçon 01, l'argent arrive en 5 jours ouvrés au maximum. La boutique
  d'entraînement enregistre le remboursement sur le moment.
- Une commande se paie une seule fois.

---

## Étape 2 · Dessine le chemin

Dessine un cercle par état et une flèche pour chaque événement qui fait **bien** bouger la commande. Sur chaque flèche,
écris l'événement ; si en plus la boutique fait quelque chose, ajoute-le après une barre oblique. Le programme de
l'ISTQB utilise cette même forme : « événement / action ».

Voilà ce que cela donne (sur papier, c'est plus joli ; ici, c'est en texte) :

```text
 créée ──paie──▶ payée ──avance──▶ à l'entrepôt ──avance──▶ expédiée ──avance──▶ livrée
   │               │                    │
 annule      annule / rembourse   annule / rembourse
   │               │                    │
   └───────────────┴────────────────────┴──────────▶ annulée
```

Compte les flèches : il y en a **sept**. Chacune est une **transition valide** : un événement que, depuis cet état, la
boutique accepte.

Regarde maintenant ce que le dessin **n'a pas**. Il n'y a pas de flèche de « expédiée » à « annulée ». Ni de « livrée »
vers nulle part, ni de « annulée » vers nulle part. Dans le dessin, ce qui ne se peut pas **ne se voit pas** : il n'y a
simplement pas de flèche. Et ce qui ne se voit pas est très facile à ne pas tester.

---

## Étape 3 · Remplis la table d'états

La table d'états dit la même chose que le dessin, mais avec une différence qui compte : elle a une **case pour chaque
état et chaque événement**, y compris pour ceux qui ne doivent pas arriver. Le programme de l'ISTQB l'explique ainsi :
contrairement au diagramme, la table montre explicitement les transitions invalides, et elle les représente par des
cases vides.

Lignes : les six états. Colonnes : les trois événements. Dans chaque case, l'état où mène cet événement depuis cet état,
et l'action s'il y en a une. Si l'événement ne doit pas faire bouger la commande, la case reste **vide**.

Avant de continuer, **prédis** : avec six états et trois événements, combien de cases a la table, et combien restent
vides ? Écris-le.

| État \ Événement | paie | avance | annule |
|---|---|---|---|
| créée | payée | | annulée |
| payée | | à l'entrepôt | annulée / rembourse |
| à l'entrepôt | | expédiée | annulée / rembourse |
| expédiée | | livrée | |
| livrée | | | |
| annulée | | | |

Cela fait 6 × 3 = **18 cases**. Sept sont remplies : ce sont les sept flèches du dessin. **Onze sont vides.**

> **Un détail sur « créée → annule ».** Annuler une commande qui n'a pas été payée ne rembourse rien, parce que rien n'a
> été prélevé. La case dit seulement « annulée », sans « rembourse ».

> **Cette table est celle des règles**, pas une photo de la boutique. Si la boutique fait autre chose dans une case, la
> table t'aide à le remarquer. Vérifie-le avec l'outil avec lequel l'entrepôt fait avancer les commandes dans la
> boutique d'entraînement : `tienda pedido 1 avanzar` sur une commande « créée » répond « cette commande n'est pas
> payée : l'entrepôt ne déplace que les commandes payées », et la commande ne bouge pas. C'est la case créée × avance,
> vide : seul le paiement mène à « payée ».

> **Et un détail sur « paie ».** Si le client répète le paiement avec la **même** clé d'idempotence (celle de la leçon
> 00), ce n'est pas un autre paiement : la boutique lui répète la réponse précédente et ne prélève pas une seconde fois.
> La colonne « paie » de cette table est un nouveau paiement. Les relances arrivent à la leçon 08.

---

## Étape 4 · Lis les cases vides

Une case vide dit : **« depuis ici, cet événement ne doit pas faire bouger la commande »**. Elle ne dit pas que
l'événement ne peut pas arriver. Sofía a bien appuyé sur « Annuler » avec la commande livrée ; le bouton était là. La
case vide dit ce que la boutique **devrait** faire quand cela arrive : ne pas la faire bouger, et lui dire pourquoi.

C'est pourquoi **chaque case vide est un scénario**. Il y en a onze, et chacune est un événement hors de son tour :

| Case vide | Ce que quelqu'un tente | Ce qui doit se passer |
|---|---|---|
| payée × paie | Payer de nouveau ce qui est déjà payé | Rien n'est prélevé ; la commande reste « payée » |
| expédiée × annule | Annuler ce qui est déjà parti | Elle n'est pas annulée ; la boutique dit pourquoi |
| livrée × annule | Annuler ce qui est déjà arrivé (Sofía) | Elle n'est pas annulée ; la boutique dit pourquoi |
| annulée × paie | Payer une commande annulée | Rien n'est prélevé |
| livrée × avance | Faire avancer ce qui est déjà arrivé | Elle ne bouge pas |
| … | (les six autres, sur ta feuille) | |

Dans la boutique d'entraînement, dans ces cases vides, la commande ne bouge pas et la boutique répond par un message
(`<état>` est l'état de la commande). Mesuré le 21 nov. 2026 :

| Tentative | Ce que répond la boutique |
|---|---|
| Annuler une commande « expédiée » ou « livrée » | « la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée » |
| Annuler une commande « annulée » | « la commande était déjà annulée » |
| Payer une commande « payée », « expédiée » ou « annulée » | « cette commande ne peut plus être payée : elle est « `<état>` » » |
| Faire avancer une commande « livrée » ou « annulée » | « une commande « `<état>` » n'avance plus » |

**Une case vide par scénario.** Si un scénario tente deux événements hors de leur tour à la suite et que le premier
échoue comme il le doit, tu ne sauras jamais ce qu'a fait le second : le premier échec cache l'autre. Le programme de
l'ISTQB appelle cela le **masquage de défauts** et recommande de ne tester qu'une seule transition invalide par cas de
test.

> **Et si personne ne sait comment remplir une case vide, c'est une question**, comme à la leçon 03. Ici, toutes ont une
> réponse, parce que les trois règles de l'étape 1 la donnent. À l'exercice 1, tu en trouveras une qui n'en a pas.

---

## Étape 5 · Un scénario par case

Pour écrire des scénarios de commandes, il y a six phrases du catalogue de ta boutique que tu n'as pas encore
utilisées : ce sont celles qui ont servi à exécuter les exemples de cette leçon avant de la publier. Écris ton
`pedidos.feature` avec elles. Les phrases :

| Type | Phrase |
|---|---|
| Soit | Marta a une commande `<état>` |
| Quand | elle annule la commande |
| Quand | elle essaie de payer la commande |
| Quand | l'entrepôt fait avancer la commande |
| Alors | la commande devient `<état>` / la commande reste `<état>` |
| Alors | on lui rembourse `<montant>` sur sa carte |
| Alors | la boutique lui dit que `<message>` (la même que dans les leçons 01 à 03) |

La commande de ces phrases est toujours la même : un T-shirt bleu, $432.00 avec la livraison. Et le **Soit** ne fait pas
apparaître la commande dans son état : il la crée, la paie et la fait avancer par le vrai chemin jusqu'à l'y laisser.

Le **Soit** met la commande dans l'état de la ligne, le **Quand** déclenche l'événement de la colonne, et l'**Alors**
vérifie ce que dit la case. Voilà la case de Sofía, livrée × annule :

```gherkin
# language: fr
Fonctionnalité: Le chemin de la commande

  Règle: On annule tant que la commande n'est pas sortie de l'entrepôt

    Scénario: Livrée × annule · on n'annule pas ce qui est déjà arrivé
      Soit Marta a une commande livrée
      Quand elle annule la commande
      Alors la boutique lui dit que la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée
      Et la commande reste livrée
```

Lis l'**Alors** : il vérifie les deux choses que dit la case vide, le message et que la commande n'a pas bougé. Si tu ne
vérifiais que le message, une boutique qui dirait « on ne peut pas » mais annulerait quand même passerait ton test.

**À toi :** dans un fichier `pedidos.feature`, copie le scénario de Sofía et écris-en un pour chacune de ces cases. Ce
sont deux cases remplies, pour avoir le chemin permis sous les yeux, et deux cases vides de plus, pour chercher des
événements hors de leur tour ; chaque scénario ne teste qu'une seule case :

1. payée × annule (remplie : elle devient annulée et on lui rembourse $432.00).
2. à l'entrepôt × annule (remplie : elle devient annulée et on lui rembourse $432.00).
3. expédiée × annule (vide).
4. annulée × paie (vide).

Regroupe-les avec `Règle:`, une par règle de l'étape 1.

**Combien tu as testé.** Le programme de l'ISTQB mesure cette technique de trois façons, et précise qu'un cas de test
couvre normalement plusieurs transitions. Ici, cela se passe dans le **Soit** : pour laisser une commande « expédiée »,
il parcourt créée → payée → à l'entrepôt → expédiée. Ces transitions comptent aussi, parce qu'elles ont été exécutées :

- **Tous les états :** les états par lesquels une commande est passée, sur les six.
- **Transitions valides :** les cases remplies qui ont été exécutées (dans le Soit ou dans le Quand), sur les sept.
- **Toutes les transitions :** les cases remplies qui ont été exécutées et les vides que tu as tentées, sur les dix-huit.

Avec tes cinq scénarios, fais les trois comptes. Tu les compareras à l'exercice 2.

---

## Comment on vérifie

**Le dessin et la table** (étapes 2 et 3, et l'exercice 1) se comparent à « Compare tes réponses ». Ce qui doit
coïncider : six états, sept flèches, dix-huit cases, et les onze vides **vides**, pas remplies avec un état inventé.

**Ton fichier `pedidos.feature`** est contrôlé par `verifica 04`. Dans le terminal de la boutique, écris :

```bash
verifica 04
```

Il exécute tes scénarios avec la boutique propre, où ils doivent sortir **au vert**, et avec l'erreur de cette leçon
activée, où **au moins un doit sortir au rouge**. S'ils sortent au vert les deux fois, il te dit que tes tests ne
regardent pas là où est l'erreur. Avant de l'exécuter, la liste ci-dessous te dit si la forme est bonne. Les scénarios
de « Compare tes réponses » ont été exécutés contre la boutique avant de publier cette leçon, avec celui que tu copies
à l'étape 5 : au vert avec la boutique propre, et deux au rouge avec l'erreur activée.

**Avant d'enregistrer, relis ton fichier avec cette liste :**

- [ ] La première ligne est `# language: fr`.
- [ ] Il y a un scénario pour chaque case demandée, et le titre dit de quelle case il s'agit (état × événement).
- [ ] Le **Soit** met l'état de la ligne et le **Quand** déclenche l'événement de la colonne.
- [ ] Dans chaque case vide, l'**Alors** vérifie le message **et** que la commande reste dans son état.
- [ ] Chaque scénario tente **une seule** case vide.

---

## Tes exercices

1. **Les retours** (sans IA). La personne du produit te passe ces règles pour retourner une commande livrée :
   - Le client demande le retour : la demande est « demandée ».
   - Le service client l'accepte ou la refuse : elle devient « acceptée » ou « refusée ».
   - Le client peut annuler sa demande tant qu'elle n'a pas été acceptée : elle devient « annulée ».
   - Quand le colis d'une demande acceptée arrive à l'entrepôt, elle devient « reçue ».
   - Ce qui est reçu est remboursé : elle devient « remboursée ».

   Dessine les états, remplis la table d'états et trouve **au moins une** case vide que les règles ne résolvent pas : un
   événement qui peut arriver dans la vie réelle et dont personne n'a dit quoi faire. Écris-la comme une question pour
   le produit. Indice : les colis arrivent quand ils arrivent. Prends 25 minutes comme limite.
2. **Tes comptes.** Avec tes cinq scénarios de l'étape 5, quel pourcentage de chaque couverture as-tu ? Combien de
   scénarios de plus te faut-il pour atteindre 100 % de toutes les transitions ?
3. **Lequel attrape l'erreur ?** La boutique a une erreur semée : quand elle est activée, on peut annuler une commande
   expédiée ou livrée, et la boutique rembourse l'argent. Sans rien exécuter, écris lesquels de tes cinq scénarios
   passent au rouge et pourquoi les autres restent au vert.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'un ne sort pas, retourne à l'étape 3) :

1. Une table avec quatre états et trois événements, combien de cases a-t-elle ?
2. Dans la table de la boutique, la case payée × paie est-elle remplie ou vide ? Pourquoi ?
3. Pourquoi un scénario tente-t-il une seule case vide et pas deux ?
4. Une commande « à l'entrepôt » reçoit « annule ». Vers quel état va-t-elle et que fait en plus la boutique ?
5. Une commande « expédiée » reçoit « avance ». Vers quel état va-t-elle ?

---

## Pour conclure

Sofía n'a rien cassé : elle a appuyé sur un bouton qui était là. Ce qui manquait, c'était un test pour le mauvais
moment, et ce test ne sort pas du dessin, parce que dans le dessin, ce qui est interdit n'a pas de flèche. Il sort de
la table, parce que dans la table, ce qui est interdit a une case, et une case vide se remarque.

Ce que tu retiens d'ici :

- Un flux avec des étapes se dessine avec des **états** et des **événements** ; chaque flèche est une transition valide.
- La **table d'états** a une case par état et par événement ; les vides sont ce qui ne doit pas arriver.
- **Chaque case vide est un scénario** : l'**Alors** vérifie le message et que la commande n'a pas bougé.
- **Une case vide par scénario**, pour qu'un échec n'en cache pas un autre.
- Si personne ne sait quoi faire dans une case, c'est une **question pour le produit**.

À la leçon 05, tu changes encore de question : ce n'est plus quel ordre, mais que faire quand les combinaisons sont si
nombreuses que les tests ne suffisent pas pour toutes.

---

## Compare tes réponses

**Étape 3, prédiction.** 6 × 3 = 18 cases ; 7 remplies et 11 vides.

**Étape 4, les onze vides.** payée × paie, à l'entrepôt × paie, expédiée × paie, livrée × paie, annulée × paie ;
créée × avance, livrée × avance, annulée × avance ; expédiée × annule, livrée × annule, annulée × annule.

**Étape 5, les scénarios.** Voici ceux qui ont été exécutés contre la boutique (celui de Sofía est dans l'étape 5) :

```gherkin
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
```

**Exercice 1.** États : sans demande (la commande livrée), demandée, acceptée, refusée, annulée, reçue, remboursée.
Événements : demande le retour, accepte, refuse, annule, le colis arrive, rembourse. Une question qui sort de la
table : « Si le colis d'une demande **refusée** ou **annulée** arrive à l'entrepôt, que faisons-nous du colis et du
client ? ». Les règles disent seulement ce qui se passe quand arrive celui d'une demande acceptée, mais le client a pu
l'envoyer avant de connaître la réponse. Si tu as trouvé une autre case sans réponse qui tient la route (par exemple,
si l'on peut annuler une demande déjà refusée), elle vaut aussi.

**Exercice 2.** Compte aussi ce que parcourt chaque **Soit**. Toutes les commandes naissent « créées », et entre les
cinq elles passent par les six états : **6 sur 6**. Les sept cases remplies sont exécutées : créée × paie, payée ×
avance, à l'entrepôt × avance et expédiée × avance dans les Soit qui font avancer la commande ; créée × annule dans le
Soit de la commande annulée ; payée × annule et à l'entrepôt × annule dans les Quand. **7 sur 7** transitions valides.
Et sur les onze vides, tu en tentes trois (expédiée × annule, livrée × annule, annulée × paie) : 7 + 3 = **10 sur 18**
de toutes les transitions. Pour atteindre 100 %, il te faut **huit scénarios de plus**, un par chaque vide que tu n'as
pas tentée : payée × paie, à l'entrepôt × paie, expédiée × paie, livrée × paie, créée × avance, livrée × avance,
annulée × avance et annulée × annule.

**Exercice 3.** Passent au rouge celui de Sofía (livrée × annule) et celui de expédiée × annule : avec l'erreur, la
boutique les annule et rembourse l'argent, donc la commande ne « reste » pas où elle était et le message n'arrive pas.
C'est ce qui s'est passé à l'exécution : deux au rouge. Les autres restent au vert : annuler une commande payée ou à
l'entrepôt était déjà permis, et payer une commande annulée n'a rien à voir avec cette erreur.

Remarque une chose : avec **7 sur 7** transitions valides, tu as déjà 100 % de la couverture que le programme de
l'ISTQB appelle la plus utilisée, et pourtant l'erreur ne vit **que** dans des cases vides. Un test qui parcourt le
chemin dans son ordre, de créée à livrée, sort au vert avec l'erreur activée. Ce sont les vides que tu as tentées qui
l'attrapent.

**Révision.** 1, douze (4 × 3). 2, vide : une commande se paie une seule fois. 3, parce que si la première échoue comme
elle le doit, elle cache ce que ferait la seconde. 4, vers annulée, et elle rembourse ce qui a été prélevé sur la même
carte. 5, vers livrée.

---

## Sources de la leçon

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.4 « State Transition Testing »
   (pp. 41–42). Les états, les transitions déclenchées par un événement et la forme « event [guard condition] /
   action » ; la table d'états avec les états dans les lignes et les événements dans les colonnes ; « the state table
   explicitly shows invalid transitions, which are represented by empty cells » ; les trois couvertures (tous les
   états, transitions valides et toutes les transitions), avec « One test case may, and usually will, cover several
   transitions between states » et « Valid transitions coverage is the most widely used coverage criterion » ; et
   « Testing only one invalid transition in a single test case helps to avoid defect masking ».
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Cucumber, « Gherkin Reference » : « Given steps are used to describe the initial context of the system » ; « When
   steps are used to describe an event, or an action ». Elle appuie que le Soit met l'état et que le Quand déclenche
   l'événement. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, « Behaviour-Driven Development » : « It may also reveal gaps in our understanding, where we need more
   information before we know what to do ». Elle appuie qu'une case sans réponse devient une question.
   https://cucumber.io/docs/bdd/

Mesure propre : les états, les événements et les messages ont été mesurés contre la boutique du cours (hb-curso-qa,
develop 0ddda22) le 21 novembre 2026, avec son API lancée sans Docker. Les cinq scénarios de la leçon ont été exécutés
avec behave et une version de test des phrases de commandes : 5 sur 5 au vert avec la boutique propre ; avec l'erreur
E3 activée, 2 au rouge (expédiée et livrée).

Règles du cours, sans source externe :

- « Chaque case vide est un scénario » : le programme de l'ISTQB demande de tenter les transitions invalides pour la
  couverture de toutes les transitions ; le cours en fait une habitude pour qu'aucune case vide ne reste sans être
  testée.
- « L'Alors d'une case vide vérifie le message et que la commande n'a pas bougé » : elle existe parce qu'une boutique
  peut dire « on ne peut pas » et le faire quand même.
