# Leçon 01 — De l'histoire au scénario

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, cinq mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Récit utilisateur :** une phrase courte qui dit qui a besoin de quelque chose, de quoi il a besoin et pourquoi. C'est
  la demande qui t'arrive pour que tu la testes.
- **Règle :** quelque chose que le métier a décidé et que le système doit respecter. « Le coupon ne s'applique qu'à
  partir de $500 (pesos mexicains) » est une règle.
- **Exemple :** un cas concret, avec des données, qui montre une règle en action. « Marta achète pour $500.00 et le
  coupon s'applique bien » est un exemple.
- **Scénario :** un exemple écrit de façon que n'importe qui puisse le refaire et le vérifier : d'où l'on part, ce que
  l'on fait et ce qui doit se produire.
- **Parcours nominal :** le scénario où tout se passe bien. C'est le premier qui vient à l'esprit de tout le monde, et
  ce n'est presque jamais là que se trouvent les erreurs.

**Ce que tu en retires :** tu reçois un récit utilisateur et, avant de toucher au système, tu le sépares en règles, en
exemples et en questions ; tu écris chaque exemple comme un scénario, avec des données concrètes, sous la forme
**Soit / Quand / Alors** ; et tu reconnais si un scénario est le parcours nominal ou l'un des dix autres types où se
cachent les erreurs.

**Idée nouvelle de cette leçon (la seule qui est évaluée) :** un scénario naît d'une **règle métier**, pas d'un écran.
Si tu ne sais pas quelle règle tu testes, tu ne sais pas ce qui doit se produire.

**Dans quel ordre :** tu lis le récit et tu le sépares en cartes de couleur (étape 1), tu transformes chaque exemple en
scénario (étape 2), tu vérifies que tes scénarios disent ce qui se passe et non les touches sur lesquelles on appuie
(étape 3), et tu places chaque scénario dans sa famille (étape 4). À la fin, tu refais seul la même chose avec un autre
récit et tu compares tes réponses.

---

## La scène

*Scénario inventé.*

Lundi, 10:15. Sofía est stagiaire en QA depuis une semaine. Sa première carte arrive sur le tableau :

> **En tant que** client de la boutique, **je veux** appliquer un coupon de réduction au moment de payer, **afin que**
> mon achat me coûte moins cher.

En dessous, quelqu'un a écrit : « Tester le coupon. Urgent ».

Sofía ouvre la boutique, met deux t-shirts dans le panier, tape le coupon `BIENVENIDA10`, voit le total baisser et
écrit sur la carte : « Testé, ça marche ».

Jeudi, le service des finances demande pourquoi des clients ont utilisé le même coupon quatre fois. Et pourquoi
d'autres l'ont utilisé pour un achat de $80, alors que le coupon était « pour les achats à partir de $500 ».

Sofía n'a rien fait de mal : elle a testé ce qu'on lui demandait. Le problème, c'est que **personne ne lui a dit quelles
étaient les règles**, et elle n'a pas demandé non plus. Tester l'écran était un bon début ; il manquait de s'accorder
sur les règles métier auxquelles le comparer.

Cette leçon est faite pour que, toi, tu demandes, et que tu saches quoi demander.

---

## Avant de commencer

**Tu n'as pas besoin de l'ordinateur pour les étapes 1 à 4.** Il te faut du papier, ou une page blanche dans ton
éditeur, et quatre couleurs : jaune, bleu, vert et rouge. Si tu n'as pas de cartes de couleur, quatre marqueurs
suffisent, ou écris le nom de la couleur entre crochets, comme ceci : `[bleu]`.

**Fais la première tentative sans IA.** L'exercice de cette leçon mesure si c'est toi qui trouves les règles. Avec ta
propre liste en main, tu pourras ensuite comparer ce qu'une IA te suggère et remarquer ce qui lui manque. À la leçon 13,
tu apprends à relire ce qu'une IA te propose.

**Combien de temps :** environ 60 minutes la première fois (estimation ; nous l'ajusterons avec la première promotion
d'élèves).

---

## Étape 1 · Sépare le récit en cartes de couleur

La technique s'appelle **cartographie d'exemples** (en anglais, *Example Mapping*). Elle a été publiée par Matt Wynne,
responsable du projet Cucumber, en 2015, et on l'utilise parce qu'elle est rapide et qu'elle met en évidence ce que
personne ne sait. Elle fonctionne avec quatre couleurs :

| Couleur | Ce que tu écris | Sur la table, elle va… |
|---|---|---|
| **Jaune** | Le récit utilisateur | Tout en haut, un seul |
| **Bleu** | Chaque **règle** que tu connais déjà | En rangée, sous le récit |
| **Vert** | Chaque **exemple** qui illustre une règle | Sous sa règle |
| **Rouge** | Chaque **question** à laquelle personne autour de la table ne sait répondre | À côté |

L'ordre compte : d'abord le récit, puis les règles, puis les exemples de chaque règle. Quand surgit quelque chose que
personne ne sait, **on n'en discute pas** : on l'écrit en rouge et on continue. Ainsi, un doute que personne n'avait vu
devient une question concrète que quelqu'un peut aller poser.

### Fais-le avec le récit de Sofía

**1. Jaune.** Recopie le récit :

```
[jaune] En tant que client, je veux appliquer un coupon de réduction au moment de payer,
        afin que mon achat me coûte moins cher.
```

**2. Bleu.** Quelles règles connais-tu ? Le récit n'en donne aucune, il faut donc aller demander à la personne qui l'a
demandé. Ici, la personne du produit répond :

```
[bleu] R1. Le coupon BIENVENIDA10 retire 10 % du sous-total (sans compter la livraison).
[bleu] R2. Il ne s'applique que si le sous-total est de $500.00 ou plus.
[bleu] R3. Chaque client ne peut l'utiliser qu'une seule fois.
[bleu] R4. Il expire le 31 décembre à 23:59, heure de Mexico.
```

Remarque : aucune de ces quatre règles ne se voit sur l'écran de paiement. Sofía ne pouvait pas les deviner en
regardant la boutique.

**3. Vert.** Pour chaque règle, un ou plusieurs exemples avec des **données concrètes**. Pas « un gros achat », mais
« un achat de $500.00 » :

```
[bleu] R2. Il ne s'applique que si le sous-total est de $500.00 ou plus.
   [vert] Sous-total $500.00 → il s'applique, il paie $450.00
   [vert] Sous-total $499.99 → il ne s'applique pas, la boutique lui dit pourquoi
   [vert] Sous-total $1,200.00 → il s'applique, il paie $1,080.00

[bleu] R3. Chaque client ne peut l'utiliser qu'une seule fois.
   [vert] Marta l'utilise pour son premier achat → il s'applique
   [vert] Marta essaie de l'utiliser pour son deuxième achat → il ne s'applique pas
```

Pourquoi $499.99 et pas $300 ? Parce que le **bord** d'une règle est un endroit fréquent où chercher des erreurs : il
suffit que quelqu'un écrive « supérieur à 500 » là où il fallait « supérieur ou égal à 500 ». Avec $300, cette erreur
passe inaperçue. À la leçon 02, tu travailles cela à fond ; pour l'instant, dans les règles à valeurs ordonnées, comme
l'argent ou les quantités, mets un exemple de chaque côté du bord.

**4. Rouge.** Pendant que tu écrivais les exemples, des doutes te sont sûrement venus. Écris-les :

```
[rouge] Si Marta annule la commande où elle a utilisé le coupon, peut-elle le réutiliser ?
[rouge] Les 10 % se calculent-ils avant ou après la livraison gratuite ?
[rouge] Que se passe-t-il si le coupon est appliqué à 23:59 et que le paiement est confirmé à 00:01 ?
```

Aucune de ces trois questions n'a sa réponse dans le récit. Si personne ne les pose, le développeur décide de son côté,
et la QA teste ce que le développeur a décidé, pas ce que le métier voulait.

### Comment savoir si le récit est prêt

La règle pratique de la cartographie d'exemples : en équipe, un petit groupe cartographie un récit bien compris et de
bonne taille **en 25 minutes environ**. Si cela prend beaucoup plus, ou si les cartes rouges n'arrêtent pas d'arriver,
le récit est trop gros ou comporte encore trop de doutes, et mieux vaut le découper ou le renvoyer avec les questions.
Quand tu le fais seul, prends ces 25 minutes comme un signal qu'il manque des réponses, pas comme un examen de vitesse.

Regarde ta table : **beaucoup de rouges** veut dire qu'il faut parler à quelqu'un. **Beaucoup de bleues** veut dire que
le récit est gros et qu'il y en a peut-être deux. **Une bleue avec beaucoup de vertes** peut indiquer une règle
compliquée, ou plusieurs règles mélangées dans une seule carte.

> **Pourquoi ne pas commencer par l'écran ?** Parce que l'écran montre ce que quelqu'un a déjà programmé. Si ce qui a
> été programmé est faux, l'écran te montre l'erreur le plus naturellement du monde, et tu n'as rien contre quoi la
> comparer. La règle est ton point de comparaison.

---

## Étape 2 · Transforme chaque exemple en scénario

Une carte verte dit « Sous-total $499.99 → ne s'applique pas ». Cela suffit aux personnes qui étaient autour de la
table. Pour que n'importe qui puisse le refaire et le vérifier, il faut plus de précision : d'où l'on part, ce que l'on
fait et ce qui doit se produire exactement.

Pour cela, on utilise la forme **Soit / Quand / Alors** (en anglais, *Given / When / Then*). Elle a été proposée par Dan
North et Chris Matts dans le cadre d'une façon de travailler appelée développement piloté par le comportement (BDD,
de l'anglais *behavior-driven development*). Chaque partie a son rôle :

| Partie | Ce qu'elle décrit | Demande-toi |
|---|---|---|
| **Soit** | Le point de départ : comment est le système avant de commencer. C'est presque toujours quelque chose qui s'est déjà produit | Qu'est-ce qui doit être vrai au préalable ? |
| **Quand** | L'action ou l'événement : ce que fait la personne, ou ce que fait un autre système | Que se passe-t-il ? |
| **Alors** | Le résultat attendu, et qui peut se **voir de l'extérieur** | Comment sais-je que tout s'est bien passé ? |

Si tu as besoin de deux choses dans la même partie, la seconde va avec **Et** (« Et son sous-total reste à $499.99 »),
ou avec **Mais** s'il s'agit d'un contraste.

### Tes deux premiers scénarios

Prends les deux cartes vertes du bord de R2, plus une de R1, et écris-les ainsi :

```gherkin
# language: fr
Fonctionnalité: Appliquer un coupon de réduction

  Contexte:
    Soit le coupon BIENVENIDA10 est en vigueur
    Et Marta n'a jamais utilisé le coupon BIENVENIDA10

  Règle: Le coupon retire 10 % du sous-total, sans compter la livraison

    Scénario: La réduction est de 10 % du sous-total
      Soit Marta a dans son panier des produits pour $1,200.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre une réduction de $120.00

  Règle: Le coupon ne s'applique que si le sous-total est de $500.00 ou plus

    Scénario: Sous-total exactement au minimum
      Soit Marta a dans son panier des produits pour $500.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre que le coupon a été appliqué

    Scénario: Sous-total un centime sous le minimum
      Soit Marta a dans son panier des produits pour $499.99
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui dit que le coupon est réservé aux achats de $500.00 ou plus
      Et son sous-total reste à $499.99
```

Lis le bloc posément. Quatre choses à remarquer :

1. **`# language: fr`** sur la première ligne indique à l'outil que les mots-clés sont en français. Le format s'appelle
   **Gherkin**, et il accepte `Fonctionnalité`, `Règle`, `Scénario`, `Soit`, `Quand`, `Alors`, `Et` et `Mais`. Tu vas
   l'exécuter pour de vrai contre la boutique d'entraînement ; pour l'instant, ce qui compte, c'est la forme.
2. **La règle est écrite au-dessus de ses scénarios** (`Règle:`). Qui lit le fichier sait ce que l'on teste et pourquoi
   chaque scénario existe. C'est ta carte bleue, remise au propre.
3. **`Contexte` n'est pas superflu.** Ce qui s'y trouve est vrai avant chaque scénario du fichier : le coupon est en
   vigueur (R4) et Marta ne l'a pas utilisé (R3). Sans ces deux lignes, un scénario de R2 pourrait échouer parce que le
   coupon a expiré ou parce que Marta l'avait déjà utilisé, et tu le lirais comme une erreur du minimum. Un bon
   **Soit** laisse de côté les autres règles, pour qu'une seule décide du résultat.
4. **Chaque Alors ne regarde que sa règle.** Celui de R1 vérifie le montant de la réduction ; ceux de R2 vérifient
   seulement si le coupon a été appliqué ou non. Si le scénario du minimum vérifiait aussi « il paie $450.00 », une
   erreur dans les 10 % (R1) le ferait échouer, et tu penserais que le problème est dans le minimum.

### À toi : deux de plus

Écris les scénarios de R3 (les deux cartes vertes de Marta) dans un nouveau fichier, avec son `# language: fr` et sa
`Fonctionnalité:`. Veille à ce que le **Soit** dise clairement si Marta a déjà utilisé le coupon ou non, à ce que le
sous-total soit au-dessus de $500.00 pour que R2 ne gêne pas, et à ce que l'**Alors** dise ce que l'on voit. Compare
avec la section « Compare tes réponses », à la fin.

---

## Étape 3 · Qu'il dise ce qui se passe, pas sur quelles touches on appuie

Regarde ce scénario. Il teste la même règle que le deuxième de l'étape 2. *C'est un fragment à comparer, ne le recopie
pas comme fichier :*

```gherkin
    Scénario: Coupon au minimum
      Soit j'ouvre la page de la boutique
      Et je clique sur « T-shirts »
      Et je clique deux fois sur « Ajouter au panier »
      Et je clique sur l'icône du panier
      Et j'écris "BIENVENIDA10" dans la zone de texte d'id "cupon"
      Quand je clique sur le bouton bleu « Appliquer »
      Alors je vois "$450.00" dans le coin inférieur droit
```

Il a plus de lignes et en dit moins. Combien coûtent les deux t-shirts ? Il ne le dit pas : si le prix change demain, le
scénario peut échouer sans que la règle ait changé. Quelle règle teste-t-il ? Il faut la deviner. Et si quelqu'un
déplace le bouton ou change sa couleur, il peut aussi échouer.

Cette façon d'écrire s'appelle **impérative** : elle décrit les étapes mécaniques de l'écran. Celle de l'étape 2 est
**déclarative** : elle décrit ce que fait le métier. Le guide de Cucumber recommande la déclarative parce qu'elle casse
moins et se lit comme de la documentation du système ; l'impérative a sa place, mais elle demande souvent plus de
travail de maintenance, car lorsque l'écran change, il faut souvent la corriger.

**Le test rapide :** lis ton scénario à voix haute à quelqu'un du métier. S'il comprend ce que l'on teste et pourquoi
c'est important, il est déclaratif. S'il te demande « et ça sert à quoi ? », il a trop d'écran.

Encore une chose sur l'**Alors** : ce que l'on vérifie doit **sortir du système**, quelque chose qu'une personne ou un
autre système peut voir : un message, un total, un courriel, ou la réponse qu'un système donne à un autre (une **API** ;
tu la découvres à fond à la leçon 06). « Un enregistrement est ajouté dans la table des coupons » ne convient pas comme
**Alors**, parce que cela, personne ne le voit de l'extérieur. La bonne question est : que remarquerait le client ?

---

## Étape 4 · Place chaque scénario dans sa famille

Jusqu'ici, tous tes scénarios sont nés de règles. Il reste la dernière question : **quels types de scénario te
manquent ?**

Dans l'article [« Au-delà du parcours nominal »](https://www.habil.mx/fr/blog/scenarios-de-test-au-dela-du-parcours-nominal/), nous regroupons les scénarios en familles. Chaque famille est une question
différente que tu poses au système :

| Famille | La question |
|---|---|
| **Parcours nominal** | Cela fonctionne-t-il quand tout se passe bien ? |
| **Limites** | Que se passe-t-il juste au bord d'une règle ? |
| **Négatifs** | Rejette-t-il bien ce qu'il doit rejeter ? |
| **Concurrence** | Que se passe-t-il si deux choses arrivent en même temps ? |
| **État et ordre** | Respecte-t-il la séquence ? Que se passe-t-il si une étape est sautée ? |
| **Temps et fuseau horaire** | Que se passe-t-il au changement de jour, de mois, d'année ou d'heure ? |
| **Données sales** | Tient-il le coup face à ce que les gens écrivent vraiment ? |
| **Intégrations en panne** | Que se passe-t-il si l'autre système tarde ou ne répond pas ? |
| **Droits** | Chacun voit-il et fait-il seulement ce qui le concerne ? |
| **Idempotence et relances** | Répéter la même requête produit-il l'effet une seule fois ? (*L'idempotence*, c'est cela : répéter sans répéter l'effet) |
| **Qualité d'usage et exploitation** | Reste-t-il utilisable, accessible (y compris pour qui n'utilise que le clavier ou un lecteur d'écran) et rapide avec la charge prévue ? |

Il y en a onze : le parcours nominal et **dix autres**. Sofía n'a testé que la première.

Maintenant, range les cartes du coupon :

- « Sous-total $1,200.00 → réduction de $120.00 » est un **parcours nominal**.
- « Sous-total $500.00 » et « $499.99 » sont des **limites**.
- « Marta essaie de l'utiliser pour son deuxième achat » est un **négatif** : la boutique doit le rejeter.
- La carte rouge de 23:59 et 00:01 relève de **temps et fuseau horaire**.

Et les familles qui n'apparaissent pas ? C'est là que se trouvent les erreurs du jeudi de Sofía. Que se passe-t-il si
Marta appuie deux fois très vite sur « Appliquer le coupon » (idempotence) ? Si elle ouvre deux onglets et paie dans
les deux en même temps (concurrence) ? Si elle écrit `bienvenida10` en minuscules ou avec une espace à la fin (données
sales) ?

Toutes les familles ne s'appliquent pas à toutes les histoires. Mais dans ce cours, **chaque famille que tu écartes, tu
l'écartes exprès**, pas parce que tu l'as oubliée. La question de cette étape est celle-là : laquelle as-tu écartée, et
pourquoi ?

---

## Comment on vérifie

Cette leçon a deux parties qui se vérifient de façon différente.

**Ce que tu fais sans machine** (étapes 1 à 4 et tes exercices) se compare avec « Compare tes réponses », à la fin. Il
n'y a pas une seule bonne réponse pour les règles et les questions ; ce qui doit coïncider, c'est que **chaque scénario
vise une seule règle** et que son **Alors** se voie de l'extérieur.

**Ton fichier de scénarios** sera contrôlé par `verifica 01` quand il existera : il vérifiera
que le fichier a la forme de Gherkin et qu'il s'exécute contre la boutique.

> ⚠️ **Note pour cette version du cours :** la boutique d'entraînement existe déjà (tu l'as lancée dans la leçon
> 00) ; son `verifica 01`, pas encore. Aujourd'hui, tu vérifies la **forme** avec la liste ci-dessous, qui reste celle
> qui compte ; l'exécution contre la boutique attend que `verifica 01` existe. Enregistre ton fichier sous le nom
> `cupon.feature`.

**Avant d'enregistrer, relis ton fichier avec cette liste :**

- [ ] La première ligne est `# language: fr`.
- [ ] Il y a une seule `Fonctionnalité:`, et elle vient avant tout le reste.
- [ ] Chaque `Règle:` a au moins un `Scénario:` en dessous.
- [ ] Chaque scénario a au moins un `Soit`, un `Quand` et un `Alors`, dans cet ordre.
- [ ] Chaque `Alors` nomme quelque chose qui se voit : un message, un montant ou une réponse.
- [ ] Si tu retires l'une des autres règles, le résultat de chaque scénario ne change pas.

---

## Tes exercices

**Nouveau récit** (sans IA) :

> **En tant que** client, **je veux** annuler une commande depuis mon compte, **afin de** ne pas payer quelque chose
> dont je n'ai plus besoin.

La personne du produit te donne ces règles :

- On peut annuler tant que la commande n'est pas sortie de l'entrepôt.
- Si elle a déjà été débitée, le remboursement va sur la même carte en 5 jours ouvrés au maximum (jours de travail).
- Seule la personne qui a passé la commande peut l'annuler.

1. **Cartographie :** mets le récit en cartes : une jaune, trois bleues, des vertes et toutes les rouges qui te
   viennent. Comme consigne de cet exercice (pas de la technique), mets au moins deux vertes dans chaque règle qui a un
   bord ou une exception ; si une règle te paraît évidente, note pourquoi elle n'a pas d'exemple. Prends 25 minutes
   comme limite.
2. **Scénarios :** écris-en quatre en Soit / Quand / Alors, dans un fichier `cancelar.feature` avec `# language: fr`. Au
   moins un par règle, et au moins un qui **ne soit pas** un parcours nominal.
3. **Familles :** à côté de chacun de tes quatre scénarios, écris à quelle famille il appartient. Ensuite, note **deux
   familles que tu n'as pas utilisées** et une ligne sur le pourquoi (parce qu'elles ne s'appliquent pas, ou parce
   qu'elles te manquent).

**Révision** (choisis la **famille principale** de chaque scénario ; l'un peut toucher plusieurs familles, et il faut
en trouver 9 sur 11) :

1. Annuler une commande qui est déjà sortie de l'entrepôt.
2. Annuler une commande le 31 décembre à 23:59:59.
3. Un client change le numéro de commande dans l'adresse de la page et annule la commande de quelqu'un d'autre.
4. Le client appuie deux fois sur « Annuler » et le système lui fait deux remboursements.
5. Annuler une commande qui vient d'être passée, encore à l'entrepôt. Elle est annulée et le client en est informé.
6. La banque met 40 secondes à répondre pour le remboursement.
7. Le client écrit le motif de l'annulation avec des emojis et des guillemets.
8. Deux personnes du service client annulent la même commande à la même seconde.
9. Essayer d'annuler une commande qui n'existe pas.
10. Une personne qui n'utilise que le clavier ne peut pas atteindre le bouton « Annuler ».
11. La commande est marquée « sortie de l'entrepôt » à 10:00:00, et le client appuie sur « Annuler » à 09:59:59 et à
    10:00:01.

---

## Pour conclure

Sofía n'avait pas besoin de tester plus vite, mais de demander avant. Une brève conversation avec quatre cartes bleues
et trois rouges aurait rendu visibles le coupon de $80 et le coupon utilisé quatre fois **avant** la programmation, et
non le jeudi aux finances.

Ce que tu retiens d'ici :

- Un scénario naît d'une **règle**. S'il n'y a pas de règle, on demande d'abord.
- **Soit** laisse de côté les autres règles, **Quand** est une seule action et **Alors** se voit de l'extérieur.
- On écrit ce que fait le métier, pas les touches.
- Le parcours nominal est l'une des onze familles. Les dix autres s'écartent exprès, jamais par oubli.

À la leçon 02, tu restes au bord des règles : comment répartir les données en groupes et choisir les quelques valeurs
qui trouvent presque toutes les erreurs de limite.

---

## Compare tes réponses

**Étape 2, scénarios de R3.** Une façon de les écrire :

```gherkin
# language: fr
Fonctionnalité: Utiliser le coupon une seule fois

  Contexte:
    Soit le coupon BIENVENIDA10 est en vigueur

  Règle: Chaque client peut utiliser le coupon une seule fois

    Scénario: Première fois qu'elle l'utilise
      Soit Marta n'a jamais utilisé le coupon BIENVENIDA10
      Et elle a dans son panier des produits pour $600.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre que le coupon a été appliqué

    Scénario: Deuxième fois qu'elle essaie
      Soit Marta a déjà utilisé le coupon BIENVENIDA10 lors d'un achat précédent
      Et elle a dans son panier des produits pour $600.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui dit que ce coupon a déjà été utilisé
      Et son sous-total reste à $600.00
```

Remarque les $600.00 dans les deux : c'est au-dessus du minimum de R2, pour que **seule R3** décide du résultat. Si tu
as pris $300, ton deuxième scénario ne s'applique pas pour deux raisons à la fois et tu ne sais pas laquelle des deux
fonctionne.

**Exercice, cartographie.** Questions rouges qui valent la peine d'être posées (elles n'ont pas à te venir identiques) :

- « Sortir de l'entrepôt » est-il marqué par quelqu'un à la main ou par un système ? Que se passe-t-il dans la minute
  où cela change ?
- Le remboursement peut-il être annulé si la banque l'a déjà traité ?
- Quelqu'un du service client peut-il annuler à la place du client ? (Cela heurte la troisième règle.)
- Les « 5 jours ouvrés » comptent-ils les jours fériés ?

**Révision :** 1 état et ordre · 2 temps et fuseau horaire · 3 droits · 4 idempotence et relances · 5 parcours nominal ·
6 intégrations en panne · 7 données sales · 8 concurrence · 9 négatifs · 10 qualité d'usage et exploitation ·
11 limites.

Pourquoi ces quatre-là, si tu as hésité : le **1** est aussi un négatif, mais ce qui le décide, c'est la **séquence**
(elle est déjà sortie de l'entrepôt). Le **2** est aussi un bord, mais ce qui le rend dangereux, c'est le **changement
d'année**. Le **10** est aussi un rejet, mais ce qui échoue, c'est qu'on puisse l'**utiliser**. Et le **11** est un
bord de temps dans la même matinée, sans changement de jour : c'est pourquoi c'est **limites**.

Si tu as confondu 4 et 8 : le 4, c'est **la même personne qui répète** la requête (idempotence) ; le 8, ce sont **deux
personnes différentes** en même temps (concurrence).

---

## Sources de la leçon

Consultées et lues le 21 nov. 2026.

1. Matt Wynne, « Introducing Example Mapping », blog de Cucumber, 8 décembre 2015. Les quatre couleurs, l'ordre, la
   question en rouge et les 25 minutes. https://cucumber.io/blog/bdd/example-mapping-introduction/
2. Cucumber, « Gherkin Reference ». Ce que décrit chaque étape : le **Given** est le contexte, presque toujours quelque
   chose qui s'est déjà produit ; le **When** est l'action ou l'événement ; le **Then** est un résultat observable, pas
   un enregistrement dans la base de données. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, mots-clés de Gherkin en français (`gherkin-languages.json`) : Fonctionnalité, Règle, Contexte, Scénario,
   Soit, Quand, Alors, Et, Mais. https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
4. Cucumber, « Writing better Gherkin ». Le style déclaratif face à l'impératif.
   https://cucumber.io/docs/bdd/better-gherkin/
5. Cucumber, « Behaviour-Driven Development ». Les trois pratiques : découverte, formulation et automatisation. Cette
   leçon couvre les deux premières. https://cucumber.io/docs/bdd/
6. Martin Fowler, « GivenWhenThen », 21 août 2013. Origine de la forme, avec Dan North et Chris Matts, et sa
   ressemblance avec le patron de test en quatre phases. https://martinfowler.com/bliki/GivenWhenThen.html
7. Dan North, « Introducing BDD ». La forme originale : « Given some initial context, When an event occurs, Then ensure
   some outcomes ». https://dannorth.net/blog/introducing-bdd/
8. Ron Jeffries, « Essential XP: Card, Conversation, Confirmation ». La carte est un rappel ; l'exigence se raconte dans
   la conversation et se confirme avec le test d'acceptation.
   https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/
9. Bill Wake, « INVEST in Good Stories, and SMART Tasks ». Un bon récit est testable : qui l'écrit promet de le
   comprendre assez pour lui écrire un test.
   https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
10. Mike Cohn, « User Stories », Mountain Goat Software. Le modèle « En tant que… je veux… afin de… » et la phrase comme
    rappel d'une conversation. https://www.mountaingoatsoftware.com/agile/user-stories
11. Gojko Adzic, *Specification by Example*, Manning, 2011. Études de plus de 50 projets qui s'accordent sur le
    comportement avec des exemples concrets. https://gojko.net/books/specification-by-example/

Du cours et de Hábil : les onze familles viennent de l'article [« Au-delà du parcours nominal »](https://www.habil.mx/fr/blog/scenarios-de-test-au-dela-du-parcours-nominal/) (Hábil, 2026). Ce sont des **règles
du cours**, sans source externe :

- « Un **Soit** laisse de côté les autres règles, et chaque **Alors** ne regarde que sa règle » : cela existe pour que,
  lorsqu'un scénario échoue, tu saches quelle règle a échoué.
- « Chaque famille que tu écartes, tu l'écartes exprès » : cela existe pour que le risque que l'on accepte reste visible.
