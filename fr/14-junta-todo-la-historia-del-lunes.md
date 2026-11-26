# Leçon 14 — Rassemble tout : l'histoire du lundi

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Cette leçon n'apporte aucune technique nouvelle.** Elle apporte une journée de travail : une histoire utilisateur qui
arrive le lundi, la boutique avec des erreurs que personne ne te dit, et tout ce que tu as appris dans le cours pour les
trouver. La seule nouveauté est une décision : **quoi tester en premier**, selon le risque.

**Avant de lire, trois mots.**

- **Mode lundi :** un mode de la boutique qui active plusieurs erreurs **sans te dire lesquelles**. C'est comme recevoir
  un vrai système : les erreurs sont déjà là et personne ne t'a passé la liste.
- **Impact :** les dégâts que fait un critère s'il échoue.
- **Probabilité :** les chances qu'il échoue.

**Ce que tu en retires :** quatre fichiers qui couvrent une histoire complète —des scénarios, une collection d'API, un
test de navigateur et un rapport—, et un tableau qui te dit quelle part du métier de QA ce cours couvre et ce qui te
manque.

**Dans quel ordre :** tu lis l'histoire et tu décides quoi tester en premier (étape 1) ; tu écris les scénarios
(étape 2), la collection (étape 3) et le test de navigateur (étape 4) contre la boutique propre ; tu actives le lundi et
tu lis les rouges (étape 5) ; tu en signales un (étape 6) ; et tu te situes par rapport à l'examen de
l'industrie (étape 7).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Lundi, 9:00. Une nouvelle histoire utilisateur arrive sur le tableau de l'équipe, avec quatre critères d'acceptation. La
programmeuse dit qu'elle est prête. Le produit veut la sortir mercredi. C'est à toi de dire si elle sort.

Personne ne te dit où sont les erreurs. Il se peut qu'il n'y en ait aucune. Il se peut qu'il y en ait plusieurs. Tout
ce que tu as, c'est ce que tu as appris en treize leçons : des scénarios, une collection qui tourne toute seule, un test
de navigateur et un rapport qu'on peut reproduire.

---

## Avant de commencer

**Il te faut la boutique levée.** Comme dans les leçons 06 à 13 : `./practicar` sur ton ordinateur et, dans une autre
fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.

> **Cette leçon utilise la boutique de la leçon 11**, avec les huit erreurs, de E1 à E8.

**Il te faut trois choses des leçons précédentes**, dans `~/practica` :

| Fichier | De la leçon |
|---|---|
| `tienda.postman_collection.json` | 07 |
| `permisos.postman_collection.json` et `local.postman_environment.json` (celui qui contient `otra_cliente`) | 08 |
| `compra.py` | 11 |

**Commence avec la boutique propre :**

```bash
tienda reiniciar
tienda error estado
```

Les huit doivent dire « désactivée ». Si l'une est activée, désactive-la avec `tienda error EX off`.

---

## Étape 1 · L'histoire, et quoi tester en premier

Voici l'histoire du lundi :

> **En tant que cliente, je veux acheter avec mon coupon depuis la page, voir ma commande et l'annuler tant qu'elle n'est
> pas sortie de l'entrepôt.**
>
> - **CA-1.** La livraison est gratuite à partir de $999.00, mesurée **après** le coupon.
> - **CA-2.** Si je paie depuis la page, ma commande est payée.
> - **CA-3.** Je peux annuler ma commande tant qu'elle n'est pas sortie de l'entrepôt ; ensuite, non.
> - **CA-4.** Je suis la seule à voir mes commandes.

Rien de tout cela n'est nouveau pour la boutique : ce sont des règles que tu as déjà testées séparément. La nouveauté,
c'est qu'aujourd'hui elles arrivent ensemble, et que tu as une journée.

En une journée, on ne teste pas tout. L'ISTQB appelle **tests basés sur les risques** le fait de décider quoi tester,
dans quel ordre et avec quel effort selon le risque de chaque chose ; le risque s'estime avec l'impact et la
probabilité. Pour chaque critère, pose-toi deux questions : quels dégâts fait-il s'il échoue (impact) ? Quelle est la
probabilité qu'il échoue (probabilité) ? Et une troisième, qui est une règle de ce cours : avec quel outil le vois-je
avec le moins d'effort ?

| CA | S'il échoue… | Impact | Probabilité | Ordre | Outil | Pourquoi celui-là |
|---|---|---|---|---|---|---|
| CA-2 payer depuis la page | Elle croit avoir payé et sa commande n'a jamais été payée | Élevé | Élevée : c'est la nouveauté de l'histoire | 1er | **Navigateur** (leçon 11) | On ne le voit que depuis la page |
| CA-1 livraison | La cliente paie $99.00 qu'elle ne devait pas | Élevé | Élevée : coupon et livraison ensemble, au bord | 2e | **Scénarios** (leçons 02 et 03) | C'est une règle avec des bords : $999.00 juste, avec et sans coupon |
| CA-4 seule moi | Une autre cliente voit la commande de Marta | Élevé | Moyenne : cela existait déjà | 3e | **Collection** (leçon 08) | C'est une permission : on la teste avec deux sessions contre l'API |
| CA-3 annuler | On rembourse quelque chose qui est déjà sorti de l'entrepôt | Élevé | Moyenne : cela existait déjà | 4e | **Scénarios** (leçon 04) | C'est un chemin d'états |

Voici l'évaluation de cet exercice, pas une règle : une autre équipe, avec d'autres données, peut les ordonner
autrement. Ici, les quatre font beaucoup de dégâts, donc c'est la probabilité qui départage : ce que l'histoire change
est ce qui a le plus de chances de casser. Les étapes 2 à 4 vont par outil pour que tu ne sautes pas de fichier en
fichier ; si une journée ne suffisait pas, CA-2 et CA-1 passeraient en premier.

Remarque la colonne « Outil ». **Le navigateur n'apparaît qu'une seule fois**, pour la seule chose qu'on ne peut pas
voir autrement. C'est la règle de la leçon 11, et elle coïncide avec ce que propose Ham Vocke dans « The Practical Test
Pyramid » : beaucoup de petits tests rapides, et très peu de bout en bout. Comme premier calcul, le blog de tests de
Google suggère 70 % de tests unitaires, 20 % de tests d'intégration et 10 % de tests de bout en bout ; c'est une
suggestion de cette équipe, pas une proportion obligatoire.

---

## Étape 2 · Les scénarios

Dans `~/practica`, crée le fichier :

```bash
nano lunes.feature
```

Écris les scénarios de CA-1 et CA-3. Utilise seulement des phrases du catalogue, les mêmes que dans les leçons 02 à 04.
Voici ceux qui ont été mesurés ; les tiens peuvent être autres, pourvu qu'ils couvrent les bords :

```gherkin
# language: fr
Fonctionnalité: Acheter avec un coupon et annuler à temps

  Règle: La livraison est gratuite à partir de $999.00, mesurée après le coupon

    Scénario: Sans coupon, exactement $999.00 · pas de frais de livraison
      Soit Marta n'a aucun coupon appliqué
      Et elle a dans son panier des produits pour $999.00
      Quand elle passe au paiement
      Alors la livraison que lui montre la boutique est de $0.00

    Scénario: Avec coupon, $1,110.00 tombe exactement à $999.00 · pas de frais de livraison
      Soit le coupon BIENVENIDA10 est en vigueur
      Et Marta n'a jamais utilisé le coupon BIENVENIDA10
      Et elle a dans son panier des produits pour $1,110.00
      Quand elle applique le coupon BIENVENIDA10
      Alors la boutique lui montre une réduction de $111.00
      Et la livraison que lui montre la boutique est de $0.00

  Règle: On annule tant que la commande n'est pas sortie de l'entrepôt

    Scénario: À l'entrepôt · c'est encore possible
      Soit Marta a une commande à l'entrepôt
      Quand elle annule la commande
      Alors la commande devient annulée
      Et on lui rembourse $432.00 sur sa carte

    Scénario: Expédiée · ce n'est plus possible
      Soit Marta a une commande expédiée
      Quand elle annule la commande
      Alors la boutique lui dit que la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée
      Et la commande reste expédiée
```

**Prédis avant de continuer :** pourquoi le deuxième scénario utilise-t-il $1,110.00 et non $999.00 ?

behave lit des scénarios écrits en langage naturel, qu'une personne qui ne programme pas peut lire, et il les exécute
contre la boutique. Jusqu'ici, tes scénarios étaient exécutés par le `verifica`. Aujourd'hui, tu les exécutes toi-même,
parce qu'en mode lundi tu auras besoin de les voir rouges de tes propres yeux. behave cherche les phrases dans un
dossier `steps` ; crées-en un avec une seule ligne, qui apporte le catalogue de phrases de la boutique :

```bash
mkdir -p steps
echo "from pasos_tienda import *" > steps/tienda.py
```

Le `>` crée le fichier, et s'il existait déjà, il le remplace. Si tu refais la leçon et que tu as déjà
`steps/tienda.py`, saute cette ligne.

Et exécute-les :

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

À la fin, dans le résumé, ces lignes doivent apparaître :

```text
2 rules passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
18 steps passed, 0 failed, 0 skipped
```

Le résumé sort en anglais même si ta boutique est dans une autre langue : c'est behave qui l'imprime, pas la boutique.

Si une phrase sort comme `undefined`, elle n'est pas dans le catalogue : copie-la telle quelle depuis les leçons 02 à 04.

---

## Étape 3 · La collection

Tu as déjà les requêtes : la collection de la leçon 07 teste la livraison de trois t-shirts, et celle de la 08 teste
qu'une autre cliente ne voit pas la commande de Marta. Pour le lundi, réunis-les en une seule collection :

```bash
jq -s '{info: {name: "lunes", schema: .[0].info.schema}, item: (.[0].item + .[1].item)}' \
  tienda.postman_collection.json permisos.postman_collection.json > lunes.postman_collection.json
```

Cette commande est une recette pour réunir les deux collections : ce n'est pas ce qu'apprend cette leçon, alors
colle-la telle quelle. Ce que fait chaque morceau, si tu veux le savoir :

| Morceau | Ce qu'il fait |
|---|---|
| `jq -s` | Lit les deux fichiers et les met dans une liste : `.[0]` est celui de la 07 et `.[1]` celui de la 08 |
| `info: {…}` | Donne un nom à la nouvelle collection et copie le format de la 07 |
| `item: (.[0].item + .[1].item)` | Met les requêtes de la 07 et, derrière, celles de la 08 |
| `> lunes.postman_collection.json` | Enregistre le résultat dans `lunes.postman_collection.json` ; les deux originaux ne sont pas touchés. Si ce fichier existait déjà, il le remplace |

newman est le programme qui exécute des collections Postman depuis le terminal. Vérifie que les douze requêtes y sont
et exécute-la avec l'environnement de la leçon 08 :

```bash
jq '.item | length' lunes.postman_collection.json
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

La première commande dit `12` : les trois de la leçon 07 et les neuf de la 08. Dans le résumé de newman, les deux lignes
qui comptent :

```text
│                requests │              12 │               0 │
│              assertions │              19 │               0 │
```

Douze requêtes, dix-neuf vérifications, zéro échec.

---

## Étape 4 · Le test de navigateur

Pour CA-2, tu as déjà le test : ton `compra.py` de la leçon 11 entre en tant que Marta, achète un t-shirt depuis la page
et vérifie dans « Mes commandes » qu'il est resté payé. C'est ce que demande la documentation de Playwright : que le
test vérifie que la page fonctionne pour la personne qui l'utilise, pas comment elle est faite à l'intérieur. Copie-le
avec le nom du lundi :

```bash
cp -n compra.py lunes.py
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

Le `-n` dit à `cp` de ne pas remplacer `lunes.py` s'il existe déjà : si tu refais la leçon, tu ne perds pas ta version.

Il se termine par `código de salida: 0`.

**Tu as maintenant les trois pièces au vert avec la boutique propre.** À la leçon 13, tu as appris que cela ne dit pas
encore si elles servent à quelque chose. Pour le savoir, il faut le lundi.

---

## Étape 5 · Le lundi

Active le mode lundi :

```bash
tienda lunes
```

La boutique te répond :

```text
🌙 Mode lundi activé : la boutique a des erreurs cachées. Elle ne dit pas lesquelles ; trouve-les avec tes tests.
   Tant qu’il dure, « tienda error » ne change rien. Quand tu as fini : tienda lunes fin
```

Si tu essaies de le découvrir, la boutique ne te le dit pas :

```bash
tienda error estado
```

```text
🌙 Mode lundi : il y a des erreurs cachées et la boutique ne dit pas lesquelles. Termine avec : tienda lunes fin
```

Elle ne dit ni lesquelles ni combien. Et comme elle l'a annoncé en s'activant, tant que dure le lundi
« tienda error » ne change rien : tu ne peux pas éteindre une erreur pour voir si c'était celle-là.

Maintenant, exécute tes trois pièces, une par une, avec `tienda reiniciar` avant chacune. Redémarrer n'éteint pas le
lundi, et la boutique te le rappelle à chaque fois :

```text
✅ la boutique est revenue à son état d'ouverture
🌙 Le mode lundi est toujours activé : redémarrer ne le désactive pas. Termine avec : tienda lunes fin
```

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

Avec les erreurs de l'histoire activées, les scénarios disent ceci (les lignes qui comptent) :

```text
      Alors la livraison que lui montre la boutique est de $0.00 ... failed in 0.000s
ASSERT FAILED: la boutique a affiché une livraison de $99.00, pas de $0.00
      Et la livraison que lui montre la boutique est de $0.00 ... failed in 0.000s
ASSERT FAILED: la boutique a affiché une livraison de $99.00, pas de $0.00
      Alors la boutique lui dit que la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée ... failed in 0.000s
ASSERT FAILED: la boutique a dit « (rien : elle l'a accepté) », pas « la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée »
1 scenario passed, 3 failed, 0 skipped
```

```bash
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

À la fin, le tableau des échecs de newman :

```text
 1.  AssertionError  livraison gratuite
 2.  AssertionError  commande d’autrui : code 404
 3.  AssertionError  sans produits
```

```bash
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

Il se termine par `código de salida: 1`, et avant le code viennent les lignes de Playwright que tu connais déjà de la
leçon 11 :

```text
  - waiting for locator("#lista-pedidos .pedido .estado").first
    13 × locator resolved to <span class="estado" data-estado="creado">créée</span>
       - unexpected value "creado"
```

Le nombre de tentatives (`13 ×`) peut sortir différent chez toi : il dépend de la vitesse de ton ordinateur.

**Maintenant, interprète les rouges :** tu n'as pas besoin de savoir quel interrupteur
a été activé ; identifie la règle cassée et le critère touché :

| Rouge | Quelle règle s'est cassée | Critère |
|---|---|---|
| Livraison de $99.00 à $999.00, sans coupon et avec coupon | La livraison gratuite ne commence pas à $999.00 juste | CA-1 |
| L'annulation d'une commande expédiée a été acceptée | On annule quelque chose qui est déjà sorti de l'entrepôt | CA-3 |
| L'autre cliente a reçu 200 et les produits | Une cliente voit la commande d'une autre | CA-4 |
| La commande payée depuis la page reste « créée » | Payer depuis la page ne paie pas | CA-2 |

Quatre trouvailles, une par critère. Remarque deux choses :

1. **Chaque outil a vu quelque chose de différent.** Le navigateur n'a vu que CA-2 ; la collection a vu CA-1 et CA-4 ;
   les scénarios ont vu CA-1 et CA-3. Aucune pièce seule n'aurait trouvé les quatre.
2. **CA-1 a été vu par deux pièces.** Ce n'est pas du gaspillage : c'est la même règle vue de deux côtés, et si un jour
   tu changes l'un des deux tests, l'autre continue de veiller sur toi.

**L'histoire sort-elle mercredi ?** Non. Avec quatre critères cassés, ta réponse est « elle ne sort pas », avec les
quatre trouvailles comme preuve.

---

## Étape 6 · Le rapport

Signale **un** des quatre, avec le format de la leçon 12. Choisis celui que tu peux reproduire avec le moins d'étapes.
Celui de la livraison se reproduit avec deux commandes : crée `~/practica/reporte.md` avec ces sections.

```markdown
# La livraison est facturée sur un panier d'exactement $999.00

**Gravité :** haute — elle prélève trop à la cliente.
**Priorité :** moyenne — d'après les mesures, cela n'arrive qu'à un panier d'exactement $999.00 ; je propose le travail planifié.

## Étapes
```

et, dans « Étapes », le bloc qu'on colle :

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Ensuite, « Résultat attendu », « Résultat obtenu » et « Preuves », comme dans la leçon 12. Gravité haute parce qu'il
prélève trop ; priorité moyenne parce que, dans ce que tu as mesuré, cela n'arrive qu'à un panier d'exactement
$999.00 (la même réponse que l'exercice 1 de la leçon 12). Les sorties mesurées :

| Boutique | Ce qu'elle affiche |
|---|---|
| Propre | `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}` |
| Le lundi | `{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}` |

Deux règles de la leçon 12 qui pèsent plus aujourd'hui :

- **Le rapport ne nomme pas l'erreur et ne l'active pas.** N'écris pas `tienda lunes` ni `tienda error` dans les
  étapes : la personne qui le corrige ne connaît pas les interrupteurs du cours. N'écris pas « E1 » non plus : tu ne sais
  pas quel numéro c'est ; tu sais quelle règle s'est cassée.
- **Les faits à part des soupçons.** Ce que tu as vu, c'est « $99.00 à $999.00 ». Que « la comparaison utilise plus grand
  que au lieu de plus grand ou égal » soit un soupçon : si tu le mets, marque-le comme tel.

Quand tu as fini, ferme le lundi :

```bash
tienda lunes fin
```

```text
✅ Mode lundi terminé : les 4 erreurs qu’il avait sont désactivées. Les autres sont restées comme avant le lundi.
```

Jusqu'ici tu ne savais pas combien il y en avait. Maintenant tu le sais, et tu peux comparer : ta suite a-t-elle vu
quatre rouges différents ?

**Ce que ta suite du lundi ne couvre pas.** La boutique a huit erreurs et ta suite en voit quatre. Les quatre autres ont
besoin de conditions que tu n'as pas créées aujourd'hui : deux paiements en même temps (leçon 09), une passerelle qui
tarde (leçons 08 et 10) ou une horloge à des heures indues (leçon 09). C'est l'idée de la leçon 13 appliquée à une
vraie journée : un vert dit que ce que tu as testé fonctionne, pas que la boutique fonctionne. Dire ce que tu **n'as pas**
testé fait partie du rapport d'une journée de QA.

---

## Étape 7 · Où tu te situes face à l'examen ISTQB

Un examen d'entrée connu en QA est l'**ISTQB Certified Tester Foundation Level (CTFL)**, version 4.0 ; la page
officielle propose le programme 4.0.1. Ce cours **te situe par rapport à** ce programme : il montre quelles parties
tu as déjà touchées et lesquelles restent en dehors. Voici comment ils se croisent, chapitre par chapitre :

| Chapitre du programme CTFL | Ce que tu as touché dans ce cours | Ce qui te manque |
|---|---|---|
| 1 · Fondamentaux des tests | D'une défaillance on remonte à son défaut ; tout tester n'est pas possible (00) ; un vert ne prouve pas qu'il n'y a pas d'erreurs (13) | Les sept principes complets, comme les énonce le programme ; activités, produits de test (*testware*) et rôles ; compétences et bonnes pratiques de qui teste |
| 2 · Les tests tout au long du cycle de vie du développement logiciel | Tests d'API et de navigateur (07, 11) ; tests qui se répètent après un changement (07, 13) | Niveaux de test (unitaire, intégration, système, acceptation) et types de test, avec leur nom ; tests de maintenance |
| 3 · Tests statiques | — | Revues et inspections de documents et de code, sans rien exécuter |
| 4 · Analyse et conception des tests | Scénarios à partir d'une histoire (01), partitions et bords (02), tables de décision (03), transition d'états (04), combinaisons (05) | Techniques boîte blanche ; techniques fondées sur l'expérience, comme le test exploratoire ; approches fondées sur la collaboration |
| 5 · Gestion des activités de test | Tests basés sur les risques (14) ; rapport de défauts (12) | Planification des tests ; suivi, contrôle et clôture ; gestion de configuration ; le cycle complet de gestion des défauts |
| 6 · Outils de test | behave, newman et Playwright (02, 07, 11) ; tests écrits par une IA (13) | Avantages et risques de l'automatisation, comme le programme les présente |

Les chapitres et leurs sections viennent de la page officielle de l'ISTQB, ouverte le 22 et le 25 nov. 2026. Le tableau
est un guide pour te situer, pas le programme complet : pour l'examen, c'est le programme qui fait foi. Le chapitre où
il te manque le plus est le 3 : les tests statiques se font **sans** rien exécuter, et ce cours ne les a pas enseignés
comme technique. Le plus près que tu en as été, c'était à la leçon 13, quand tu as lu un test contre sa règle avant de
l'exécuter.

---

## Comment on vérifie

Avant de lancer le `verifica`, vérifie :

- [ ] Avec la boutique propre, les trois pièces sortent au vert : les scénarios sans phrases `undefined`, la collection
      sans échecs et `lunes.py` qui se termine par 0.
- [ ] `lunes.py` et la collection ne contiennent écrits à la main ni l'adresse de la boutique, ni Marta, ni Luis, ni
      leurs mots de passe (cherche-les avec
      `grep -n -i -e localhost -e marta -e luis -e practica lunes.py lunes.postman_collection.json` ; il ne doit rien
      afficher).
- [ ] Le lundi, chaque critère de l'histoire a au moins une pièce au rouge, et tu as noté à côté de chaque critère le
      nom du test rouge qui l'a vu.
- [ ] Dans le rapport, « Résultat attendu » nomme la règle (« à partir de $999.00 ») et $0.00 ; « Résultat obtenu »
      nomme $99.00 et $1,098.00 ; « Preuves » copie une sortie avec ces valeurs.
- [ ] `reporte.md` a les sections de la leçon 12 et un seul bloc `bash` dans « Étapes », sans `tienda error`,
      `tienda lunes` ni `/control/`.
- [ ] Les étapes du rapport, collées dans une boutique propre, affichent autre chose que le lundi.
- [ ] Tu as fermé le lundi avec `tienda lunes fin`.

Deux cases de cette liste ne sont pas vérifiées par le `verifica` : celle de noter quel test rouge a vu chaque critère et
celle de ce que tu as écrit dans « Résultat attendu », « Résultat obtenu » et « Preuves ». C'est comme à la leçon 12 : le
`verifica` vérifie ce que tes étapes font à la boutique, pas ce que tu as écrit. **Ces deux-là, c'est toi qui les
vérifies.** Un rapport avec les bonnes étapes et ces sections vides sort au vert et ne sert à personne.

Ensuite, dans le terminal de la boutique :

```bash
verifica 14
```

**Ce que fait le `verifica 14` :** il n'utilise pas le mode lundi. Il active **chaque** erreur de l'histoire séparément
et, avec chacune, exige qu'au moins une de tes trois pièces sorte au rouge. Ensuite il exécute les étapes de ton rapport
propres et avec chaque erreur, et exige qu'avec au moins une la sortie change.

Le `verifica` ne te dit pas non plus lesquelles sont les erreurs : il les compte comme « erreur 1 sur 4 », « erreur 2 sur
4 », et ainsi de suite.

Avec tout en place, le `verifica 14` ressemble à ceci :

```text
Vérification de la leçon 14…

✅ Ton fichier lunes.feature est dans ~/practica
✅ Ton fichier lunes.postman_collection.json est dans ~/practica
✅ Ton fichier local.postman_environment.json est dans ~/practica
✅ Ton fichier lunes.py est dans ~/practica
✅ Ton fichier reporte.md est dans ~/practica
✅ Ton local.postman_environment.json contient base, cliente, contrasena, otra_cliente et otra_contrasena, comme celui de la leçon 08
✅ Ton lunes.py et ta collection n’ont pas écrits à la main l’adresse de la boutique, ni Marta, ni Luis, ni leurs mots de passe
✅ Ton reporte.md contient les quatre sections : Étapes, Résultat attendu, Résultat obtenu et Preuves
✅ La section «Étapes» contient un seul bloc de commandes bash
✅ Tes étapes n'activent pas d'erreurs et ne touchent pas au contrôle de la boutique
✅ Chaque étape de lunes.feature est une phrase du catalogue de la boutique
✅ Avec la boutique propre, tes scénarios sortent en vert (4)
✅ Avec la boutique propre, ta lunes.postman_collection.json passe au vert
✅ Avec la boutique propre, ton lunes.py termine en 0
✅ Avec l’erreur 1 sur 4 du lundi activée seule, ton lunes.feature passe au rouge
✅ Avec l’erreur 2 sur 4 du lundi activée seule, ton lunes.feature passe au rouge
✅ Avec l’erreur 3 sur 4 du lundi activée seule, ton lunes.postman_collection.json passe au rouge
✅ Avec l’erreur 4 sur 4 du lundi activée seule, ton lunes.py passe au rouge
✅ Avec la boutique propre, les étapes de ton rapport affichent la même chose les deux fois
✅ Le lundi, les étapes de ton rapport affichent autre chose qu’avec la boutique propre : elles reproduisent une erreur de l’histoire

🎉 Leçon terminée !
```

Si tu le lances avec la boutique propre, à la fin il laisse les huit erreurs éteintes, comme il les a trouvées.

---

## Tes exercices

1. **Une pièce de moins.** Relance le lundi, mais sans `lunes.py`. Quel critère reste sans aucun rouge ? Que dirais-tu
   au produit sur ce critère, si le navigateur n'existait pas ?
2. **Un autre rapport.** Signale la trouvaille de CA-4 (l'autre cliente voit la commande de Marta) dans
   `~/practica/reporte-ajeno.md`. Utilise deux sessions dans les étapes, comme dans la collection de la leçon 08.
   Essaie-le propre et le lundi avant de le donner pour bon.
3. **Sur papier, sans la boutique.** Une nouvelle histoire : « En tant que cliente, je veux que mon panier soit
   conservé si je ferme la page ». Écris ses critères d'acceptation et, pour chacun, quel outil du cours tu
   utiliserais et pourquoi, avec un tableau comme celui de l'étape 1. Résous-le sans IA pour exercer ton jugement.

---

## Pour conclure

Tu as commencé le cours avec une histoire et une question : quels scénarios trouvent des erreurs ? Aujourd'hui, tu as
reçu une nouvelle histoire, décidé quoi tester en premier, écrit trois types de test, trouvé quatre erreurs que
personne ne t'avait dites et signalé l'une d'elles pour qu'on la corrige. Cela, c'est une journée de QA.

**Révision :**

1. Pourquoi le navigateur n'apparaît-il qu'une seule fois dans le tableau de l'étape 1 ?
2. Deux pièces ont vu CA-1. Est-ce du gaspillage ? Pourquoi ?
3. Que manque-t-il à ton rapport si tu dis « E1 » au lieu de la règle qui s'est cassée ?
4. Nomme une condition que ta suite du lundi n'a pas créée, et une erreur qu'elle ne pouvait pas voir pour cette raison.
5. Quel chapitre du programme CTFL ce cours n'a-t-il pas touché, et pourquoi ?

---

## Compare tes réponses

**La prédiction de l'étape 2.** Avec le coupon de 10 %, $1,110.00 tombe à $999.00 exactement après la réduction :
$1,110.00 moins $111.00. C'est le bord de CA-1 mesuré **après** le coupon. Avec $999.00 avant le coupon, la cliente paie
$899.10 et la livraison lui est bien facturée : c'est un autre scénario, celui de la colonne 8a de la leçon 03.

**Exercice 1.** CA-2 reste sans aucun rouge : seul le navigateur le voyait. Sans navigateur, tu dirais au produit que
CA-2 n'est pas testé : dans la mesure, la collection et les scénarios sont restés verts avec cette erreur, et la page
est ce que personne n'a vérifié. Le dire fait partie du rapport.

**Exercice 2.** Les étapes ont besoin de deux `TOKEN` : celui de Marta crée la commande et celui de Luis la consulte.
Propre, la consultation de Luis donne 404 ; le lundi, 200 avec les produits de Marta.

**Exercice 3.** Il n'y a pas une seule réponse. Un bon tableau a un critère par ligne, l'impact et la probabilité avec
leur pourquoi, un outil par critère, et des critères qu'on peut observer. Un exemple de deux lignes : « en fermant la
page et en la rouvrant, le panier conserve le produit et la quantité » va au **navigateur**, parce que fermer et
rouvrir la page fait partie du parcours ; « le panier enregistré n'appartient qu'à celle qui l'a composé » va à la
**collection**, parce que c'est une permission qui se teste avec deux sessions. Si le navigateur apparaît sur plus
d'une ligne, vérifie si l'une d'elles peut se voir par l'API.

**Révision.**

1. Parce que seul CA-2 se voit uniquement depuis la page. Les tests de navigateur sont plus lents (environ 1,3 fois la
   collection dans la leçon 11) et peuvent sortir rouges sans que la boutique ait une erreur (l'exercice 3 de la leçon
   11) ; on les garde pour ce qui ne se voit pas autrement.
2. Non. C'est la même règle vue par deux tests différents : si l'un change ou se casse, l'autre continue de veiller sur
   la règle.
3. La personne qui le corrige ne sait pas ce qu'est « E1 ». Le rapport dit quelle règle s'est cassée et comment la voir,
   pas l'interrupteur du cours.
4. Par exemple, deux paiements en même temps : sans eux, le coupon utilisé deux fois (leçon 09) n'apparaît pas.
5. Le 3, tests statiques : tout dans le cours a été testé en exécutant la boutique, et les tests statiques passent en
   revue des documents et du code sans les exécuter.

---

## Sources de la leçon

Consultées le 22 novembre 2026.

1. ISTQB, « Certified Tester Foundation Level (CTFL) v4.0 » (chapitres et sections du programme ; programme en vigueur
   v4.0.1). https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
2. ISTQB Glossary, *risk-based testing*, *exploratory testing* et *test basis*. https://glossary.istqb.org/
3. Ham Vocke, « The Practical Test Pyramid », sur martinfowler.com.
   https://martinfowler.com/articles/practical-test-pyramid.html
4. Mike Wacker, « Just Say No to More End-to-End Tests », Google Testing Blog.
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
5. Playwright, « Best Practices ». https://playwright.dev/docs/best-practices
6. behave, « Behavior Driven Development ». https://behave.readthedocs.io/en/stable/philosophy/
7. Postman, « Run collections using Newman ». https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
8. Mozilla, « Bug Writing Guidelines ». https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
