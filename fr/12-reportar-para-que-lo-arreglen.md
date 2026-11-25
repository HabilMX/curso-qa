# Leçon 12 — Signaler pour qu'on le corrige

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Rapport de défaut :** le texte que tu remets à la personne qui va corriger une erreur. Dans les équipes, on dit
  *bug report* ou *issue*.
- **Gravité :** combien de dégâts fait l'erreur.
- **Priorité :** à quelle vitesse il faut la corriger.

**Ce que tu en retires :** un fichier, `reporte.md`, avec l'erreur de la leçon 04 écrite de façon que n'importe qui la
reproduise en collant tes étapes dans son terminal. Tu apprends aussi à lui donner une gravité et une priorité, et à la
noter dans une matrice de tests et un rapport QA avec le format que nous utilisons chez Hábil.

**Idée de QA nouvelle de cette leçon :** une erreur qu'une autre personne ne peut pas reproduire n'est presque jamais
corrigée. La trouver, c'était la moitié du travail ; l'autre moitié, c'est que quelqu'un d'autre la voie comme toi. La
gravité, la priorité et le format de la maison accompagnent cette idée quand le rapport entre dans une équipe ; tu les
vois aux étapes 4 et 5.

**Dans quel ordre :** tu vois ce qui manquait à un rapport qui n'a pas servi (étape 1) ; tu écris les étapes comme des
commandes (étape 2) ; tu vérifies qu'elles fonctionnent dans la boutique d'un autre (étape 3) ; tu lui donnes une
gravité et une priorité (étape 4) ; et tu la notes dans le format de la maison (étape 5).

---

## La scène

*Scénario inventé ; les réponses et les erreurs de la boutique, elles, sont réelles.*

Tu te souviens de Sofía, celle de la leçon 04 ? Elle a reçu son t-shirt, elle a appuyé sur « Annuler » et la boutique
lui a rendu son argent. Cette fois, quelqu'un du QA l'a vu le premier et a écrit ce rapport :

> **On peut annuler des commandes qu'on ne devrait pas pouvoir annuler !!! URGENT**
>
> J'ai annulé une commande et la boutique m'a laissé l'annuler. C'est mal. Je crois que c'est à cause du changement de
> la semaine dernière.

Le programmeur l'a lu, il est entré dans sa boutique, il a passé une commande, l'a payée et l'a annulée. La boutique
l'a annulée et l'a remboursée. Il a répondu « ça marche comme il faut : une commande payée peut s'annuler » et il a
fermé le rapport.

Tous les deux avaient raison avec ce qu'ils savaient. Le rapport ne disait pas **dans quel état** était la commande, ni
**ce qui** aurait dû se passer, et il n'apportait **rien** qui le démontre. Et la phrase sur « le changement de la
semaine dernière » était un soupçon, pas un fait ; le programmeur a perdu un moment à la vérifier.

---

## Avant de commencer

**Il te faut la boutique levée.** Comme dans les leçons 06 à 11 : `./practicar` sur ton ordinateur et, dans une autre
fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.

**L'erreur de cette leçon est E3**, celle de la leçon 04 : une commande qui a déjà quitté l'entrepôt peut être annulée
et elle est remboursée. Tu vas l'allumer toi-même pour la voir, et tu vas la signaler **sans la nommer** : la personne
qui corrige la boutique ne sait pas qu'il existe un interrupteur appelé E3. Elle voit seulement ce que fait la
boutique.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 04, les états de la commande et la règle « on peut annuler
tant que la commande n'a pas quitté l'entrepôt » ; de la 06, `curl` et les codes de réponse ; de la 09, garder une
valeur avec `$(…)` et `jq -r` ; de la 10, le filtre de `jq` qui résume une commande en une ligne.

**Fais l'étape 4 et la révision sans IA.** Ce que tu y entraînes, c'est décider combien de dégâts fait une erreur et
son degré d'urgence, et ça, c'est ton jugement.

**Commence propre :**

```bash
tienda reiniciar
```

---

## Étape 1 · Ce qui manquait au rapport

Les grands projets de logiciel ont déjà écrit ce qu'ils attendent d'un rapport. Mozilla, l'équipe de Firefox, le dit en
une ligne : des étapes précises pour le reproduire, le résultat attendu et le résultat obtenu. Chromium, le projet
derrière Chrome, demande la même chose et ajoute des captures quand elles aident. Simon Tatham, dans son guide « How to
Report Bugs Effectively », résume à quoi sert tout cela : que le programmeur puisse reproduire le problème sans toi en
face de lui.

Dans ce cours, un rapport a ces parties :

| Partie | Ce qu'elle contient | Ce qui manquait à celui de la scène |
|---|---|---|
| **Titre** | Ce qui échoue, en une ligne. Mozilla demande moins de 60 caractères qui disent le problème, pas ta solution | « On peut annuler des commandes qu'on ne devrait pas pouvoir annuler » ne dit pas lesquelles |
| **Gravité et priorité** | Les deux, séparément (étape 4) | Il disait seulement « URGENT » |
| **Étapes** | Ce que tu as fait, dans l'ordre, de façon qu'un autre le répète à l'identique | Il n'y avait pas d'étapes |
| **Résultat attendu** | Ce qui aurait dû se passer, et pourquoi : la règle qui le dit | Il ne disait pas que la commande était déjà livrée ni quelle règle elle enfreignait |
| **Résultat obtenu** | Ce qui s'est vraiment passé | « Il m'a laissé l'annuler », sans l'état ni l'argent |
| **Preuves** | La sortie qui le démontre, copiée telle quelle | Rien |

**Les faits à part des soupçons.** Tatham demande de bien distinguer ce qui est un fait (« j'étais devant l'ordinateur
et ceci s'est passé ») et ce qui est une spéculation (« je crois que le problème pourrait être ceci »). « Je crois que
c'est à cause du changement de la semaine dernière » peut figurer dans un rapport, mais marqué comme un soupçon et à la
fin, jamais mélangé à ce que tu as vu.

---

## Étape 2 · Les étapes, comme des commandes qu'on colle

Des étapes en prose (« connecte-toi comme Marta, achète, fais avancer la commande, annule ») laissent des choses non
dites : quel produit ? avec quelle carte ? jusqu'à quel état ? Dans cette boutique, tu peux faire mieux : écrire les
étapes **comme les commandes que tu as lancées**, pour que l'autre les colle dans son terminal et voie la même chose.

Écris ceci dans un fichier, `~/practica/pasos.sh` :

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":1}' > /dev/null
PEDIDO=$(curl -s -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: reporte-$PEDIDO" -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}' > /dev/null
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
curl -s -o /dev/null -w 'cancelar: HTTP %{http_code}\n' -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion \
  -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

Ligne par ligne :

| Ligne | Ce qu'elle fait |
|---|---|
| `TOKEN=$(…)` | Se connecte comme Marta et garde son jeton, comme dans la leçon 09 |
| `curl … -X PUT …/carrito/…` | Met un t-shirt bleu dans le panier. `> /dev/null` jette la réponse : elle ne fait pas partie des preuves |
| `PEDIDO=$(… \| jq -r .id)` | Crée la commande et **garde son numéro**. L'étape 3 explique pourquoi tu n'écris pas le numéro à la main |
| `curl … /pago …` | La paie avec la carte de test ; la clé porte le numéro de la commande pour ne pas se répéter |
| `tienda pedido $PEDIDO avanzar` ×3 | Fait ce que ferait l'entrepôt : à l'entrepôt, expédiée, livrée |
| `curl -s -o /dev/null -w '…'` | Essaie d'annuler. `-o /dev/null` jette le corps et `-w` n'imprime que le code de réponse |
| `curl … \| jq -c '{…}'` | Montre la commande sur une ligne : état, combien est resté facturé et les mouvements |

`-w` est nouveau : il dit à `curl` d'imprimer quelque chose après avoir fini, et `%{http_code}` est le code de la
réponse.

**Lance-le avec la boutique propre.** Prédis d'abord : quel code donne l'annulation ?

```bash
tienda reiniciar
bash pasos.sh
```

```text
📦 La commande 1 est maintenant « à l'entrepôt »
📦 La commande 1 est maintenant « expédiée »
📦 La commande 1 est maintenant « livrée »
cancelar: HTTP 409
{"estado":"entregado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

C'est correct : la commande a déjà quitté l'entrepôt, la boutique répond **409** et le débit reste. Si, au lieu de `-o
/dev/null`, tu laisses `curl` imprimer le corps, la boutique explique : « la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée ».

**Maintenant avec E3.**

```bash
tienda reiniciar
tienda error E3 on
bash pasos.sh
```

```text
📦 La commande 1 est maintenant « à l'entrepôt »
📦 La commande 1 est maintenant « expédiée »
📦 La commande 1 est maintenant « livrée »
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

La même séquence, une autre fin : **200**, la commande livrée finit annulée et les $432.00 reviennent. Cette
différence, copiée telle quelle, est ta preuve.

Remarque ce qui n'est **pas** dans `pasos.sh` : `tienda error E3 on`. Cette ligne, tu l'utilises pour voir l'erreur
dans ta pratique, mais dans une vraie équipe l'erreur est déjà dans la boutique ; personne ne l'allume. Si tes étapes
l'allument, elles ne testent que l'interrupteur d'entraînement ; elles ne montrent pas comment la boutique échoue
toute seule.

---

## Étape 3 · Des étapes qui fonctionnent dans la boutique d'un autre

Ta boutique vient de redémarrer, et c'est pour cela que ta commande est la 1. Celle du programmeur, non : elle contient
les commandes de ses propres tests. Que se passe-t-il si tes étapes disent `pedido 1` au lieu de `$PEDIDO` ?

Fais une copie avec le numéro écrit à la main. `sed` est un outil qui change du texte à l'intérieur d'un fichier ; tu
n'as pas besoin de comprendre cette ligne, copie-la telle quelle. Elle change `$PEDIDO` en `1` dans tout le fichier,
garde la création de la commande mais sans garder son numéro, et écrit le résultat dans `pasos-1.sh` :

```bash
sed -e 's/\$PEDIDO/1/g' -e 's/^PEDIDO=\$(\(.*\) | jq -r .id)$/\1 > \/dev\/null/' pasos.sh > pasos-1.sh
```

Maintenant, lance les deux versions **une seconde fois, sans redémarrer**, avec E3 toujours allumée. C'est ainsi qu'est
la boutique de quelqu'un qui a déjà fait des tests avant toi. Prédis d'abord.

```bash
bash pasos.sh
```

```text
📦 La commande 2 est maintenant « à l'entrepôt »
📦 La commande 2 est maintenant « expédiée »
📦 La commande 2 est maintenant « livrée »
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

```bash
bash pasos-1.sh
```

```text
❌ une commande « annulée » n'avance plus
❌ une commande « annulée » n'avance plus
❌ une commande « annulée » n'avance plus
cancelar: HTTP 409
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Avec `$PEDIDO`, l'erreur apparaît de nouveau, maintenant sur la commande 2. Avec le 1 écrit à la main, les étapes
déplacent une vieille commande qui était déjà annulée, l'annulation donne **409**, et qui le reçoit conclut que la
boutique va bien. C'est la même erreur que celle de la scène, cette fois avec des commandes : un rapport qui se
reproduit **seulement** dans ta boutique.

**Règle de ce cours : avant d'envoyer un rapport, lance-le deux fois sans redémarrer.** Si la seconde fois ne montre
pas l'erreur, tes étapes dépendent de quelque chose que seule ta boutique a. C'est pour cela que le `verifica 12`
laisse une commande préalable avant de lancer tes étapes.

Quand tu as fini, éteins E3 et supprime la copie :

```bash
tienda error E3 off
rm pasos-1.sh
```

---

## Étape 4 · Gravité et priorité

Le rapport de la scène disait « URGENT ». Urgent parce qu'il fait beaucoup de dégâts, ou parce qu'il faut le corriger
aujourd'hui ? Ce n'est pas pareil, et dans une équipe, ce sont des personnes différentes qui le décident.

- **La gravité** est le dommage. Le glossaire de l'ISTQB (International Software Testing Qualifications Board) la
  définit comme le degré d'impact qu'a un défaut sur le développement, les tests ou l'exploitation du système.
  Bugzilla, l'outil de rapports de Mozilla, l'explique de la même façon : à quel point le problème est grave, depuis
  « l'application est inutilisable » jusqu'à « un détail cosmétique ».
- **La priorité** est l'ordre dans lequel on corrige. Bugzilla dit qu'elle est utilisée par quelqu'un qui a l'autorité
  pour diriger le temps de l'équipe, comme la personne qui dirige le projet. WebKit, le moteur de Safari, dit à qui
  signale qu'elle est normalement fixée par quelqu'un du QA ou du développement.

La gravité change normalement moins que la priorité : l'erreur fait les mêmes dégâts aujourd'hui que dans un mois, sauf
si tu découvres un effet nouveau ; alors on la révise. La priorité, elle, change avec le calendrier, avec qui la subit
et avec ce qui va être publié. C'est pourquoi on les note séparément :

| | **Priorité haute** | **Priorité basse** |
|---|---|---|
| **Gravité haute** | La boutique rembourse des commandes déjà livrées, chaque fois que quelqu'un annule tard | Un rapport utilisé une fois par an additionne mal, et son prochain usage est dans 11 mois |
| **Gravité basse** | Une faute d'orthographe sur le bouton « Payer », un jour avant une campagne | Le logo apparaît coupé sur un téléphone que presque personne n'utilise |

**L'échelle de ce cours** utilise trois niveaux pour chacune. C'est une règle du cours, adaptée du tableau de gravité
que nous utilisons chez Hábil :

| Niveau | Gravité (le dommage) | Priorité (quand on corrige) |
|---|---|---|
| **haute** | Facture mal, fait perdre de l'argent, empêche d'acheter, expose les données de quelqu'un ou donne un chiffre faux sans prévenir | Avant la prochaine chose qui sera publiée |
| **moyenne** | Quelque chose échoue, mais il y a une autre façon de le faire, ou cela n'arrive qu'à très peu de gens | Dans le travail déjà prévu |
| **basse** | Cosmétique : ne change ni ce qui est facturé, ni ce qui est livré, ni ce qui est enregistré | Quand il y aura de la place |

Toi, comme QA, tu **proposes** les deux et tu écris pourquoi en une ligne. La gravité, c'est toi qui la défends, parce
que c'est toi qui as vu le dommage. La priorité peut être changée par la personne qui dirige le travail, parce qu'elle
sait des choses que tu ne sais pas : ce qui est publié demain ou quel client attend.

> **Chez Hábil, il y a un cas où la priorité ne se choisit pas.** Dans nos audits, chaque incident porte une tâche
> sur le tableau, et sa priorité découle directement de la gravité : haute devient urgente, moyenne devient haute et
> basse devient normale. C'est une règle de la maison pour les audits, où le délai de correction dépend du dommage. La
> différence que tu as apprise ici est celle de l'industrie, et c'est celle que tu utiliseras dans un rapport de
> produit.

**Pour E3 :** gravité **haute**, parce que la boutique perd l'argent d'une chose qu'elle a déjà livrée. Priorité
**haute** : dans toutes tes exécutions, chaque annulation d'une commande livrée a été remboursée, et cela peut arriver
à n'importe quelle cliente qui annule après avoir reçu.

---

## Étape 5 · Le format de la maison : matrice et rapport QA

Dans une équipe, ton rapport ne vit pas seul. Chez Hábil, chaque histoire porte une **matrice de tests**, qui dit ce
qui a été testé pour chaque critère, et un **rapport QA**, qui raconte chaque tour de révision. Ta trouvaille apparaît
dans les deux.

Ce qui suit est une **version d'entraînement** : elle contient les parties qu'un QA remplit au premier tour, avec
l'histoire d'annuler de la leçon 01. À la fin de l'étape, tu trouves ce qui lui manque pour être le format complet.

**La matrice de tests.** Son tableau principal place chaque critère d'acceptation (CA) à côté de son scénario. La
colonne **Type** dit ce qu'on examine : `Fonctionnel` est le chemin du métier (annuler, rembourser) et `Sécurité` est
un contrôle, comme qui peut faire quoi.

| CA | Scénario | Type | Preuve attendue | Résultat |
|---|---|---|---|---|
| CA-1 On peut annuler tant que la commande n'a pas quitté l'entrepôt | QA-001 Annuler une commande payée | Fonctionnel | `cancelación` 200, état annulé, remboursement | Réussi |
| CA-1 | QA-002 Annuler une commande livrée | Fonctionnel | `cancelación` 409, état livré, sans remboursement | Échoué |
| CA-2 Si c'est déjà débité, le remboursement va sur la même carte | QA-003 Remboursement d'une commande payée | Fonctionnel | Mouvement de remboursement sur `•••• 4242` | Réussi |
| CA-3 Seule la personne qui a passé la commande peut l'annuler | QA-004 Luis annule une commande de Marta | Sécurité | 404 « cette commande n'existe pas » | Réussi |

Sous le tableau, chaque scénario a son détail : ce qui est validé, comment, et une dernière ligne avec le résultat
final. Celui de QA-002 devient :

```markdown
### QA-002 — Annuler une commande livrée

Marta paie une commande, l'entrepôt la porte à livrée et Marta l'annule. On valide que la boutique répond 409 et que
la commande reste livrée et débitée. Étapes et preuves dans reporte.md.

Résultat final : échoué ; enregistré comme OBS-001
```

Le modèle de la maison dit « Résultat final : réussi » ou « échoué avec INC-001 ». Comme dans cet entraînement il n'y
a pas d'INC (plus bas tu vois pourquoi), la dernière ligne nomme l'observation.

Trois règles de la maison que l'on voit ici :

- un CA peut avoir **plus d'un scénario** : le CA-1 en a deux, un de chaque côté de la règle ;
- la colonne **Résultat** se remplit **après** avoir testé, jamais avant ;
- le détail **renvoie** au rapport ; il ne copie pas les étapes.

**Pourquoi OBS et pas INC ?** Chez Hábil, un incident (`INC-001`) n'existe que s'il a sa tâche sur le tableau de
l'équipe, avec son numéro. Sans tâche, le défaut est noté comme une **observation** (`OBS-001`) dans le tableau des
observations de la matrice. Dans cet entraînement, il n'y a pas de tableau, donc ta trouvaille est une observation :

| OBS | Sujet | État | Justification |
|---|---|---|---|
| OBS-001 | Une commande livrée peut être annulée, et elle est remboursée (reporte.md) | Ouvert | Sans tâche sur le tableau ; dans une équipe, on crée la tâche et elle devient INC-001 |

**Le rapport QA** grandit avec une section par tour de révision. Le tien est le premier :

```markdown
## Cycle 1 — Révision QA 1

| Champ | Valeur |
|---|---|
| Date | 2026-11-22 10:00 CDMX |
| Réviseur | (ton nom) |
| Résultat | Non approuvé |

### Constats de ce cycle

| Constat | Description | INC | État |
|---|---|---|---|
| H-001 | Une commande livrée peut être annulée, et elle est remboursée | — (OBS-001) | Ouvert |
```

Le rapport QA **ne copie pas** ton rapport : il le référence. Le détail vit à un seul endroit.

**Ce qui manque à la version d'entraînement pour être le format complet de la maison :** dans le cycle, le champ de
l'étiquette de la révision et le lien vers le document de cette révision ; dans la matrice, son en-tête de données, son
objectif et le tableau des incidents, qui a six colonnes et se remplit quand la tâche existe. Tu les verras quand tu
travailleras sur un vrai dossier.

---

## Comment on vérifie

**Ton rapport**, c'est le `verifica 12` qui le vérifie. Enregistre-le dans `~/practica` sous le nom `reporte.md`, avec
cette forme :

````markdown
# Une commande livrée peut être annulée, et elle est remboursée

**Gravité :** haute
**Priorité :** haute

## Étapes

```bash
(tes étapes vont ici : le contenu de pasos.sh)
```

## Résultat attendu

(ce qui aurait dû se passer et quelle règle le dit)

## Résultat obtenu

(ce qui s'est passé)

## Preuves

(la sortie qui le démontre, copiée telle quelle)
````

Dans le terminal de la boutique, écris :

```bash
verifica 12
```

Le `verifica` :

1. vérifie que les quatre sections sont là (les majuscules et les espaces en trop n'ont pas d'importance) et que
   « Étapes » contient **un** bloc de commandes `bash` ;
2. rejette les étapes qui allument une erreur (`tienda error`) ou qui touchent au contrôle de la boutique ;
3. avec la boutique propre, laisse une commande préalable de Marta et lance tes étapes : une commande doit arriver à
   expédiée ou livrée et **ne pas** finir annulée ;
4. avec E3 allumée, laisse de nouveau une commande préalable et lance tes étapes **deux fois de suite, sans
   redémarrer** : les deux fois, une commande doit finir annulée **après** être sortie de l'entrepôt. C'est la règle de
   l'étape 3 : un rapport qui ne marche que la première fois ne sert à rien.

Il ne lit pas ce que tu as écrit dans « Résultat attendu », « Résultat obtenu » ni « Preuves » : il vérifie ce que tes
étapes font à la boutique. **Ces trois sections, c'est toi qui les révises** avec la liste ci-dessous ; un rapport aux
bonnes étapes et à ces sections vides sort vert dans le `verifica` et ne sert à personne. Il allume et éteint E3 tout
seul et redémarre la boutique, donc il **efface tes commandes, ton panier et ta session**.

Avec un bon rapport, la sortie ressemble à ceci :

```text
Vérification de la leçon 12…

✅ Ton fichier reporte.md est dans ~/practica
✅ Ton reporte.md contient les quatre sections : Étapes, Résultat attendu, Résultat obtenu et Preuves
✅ La section «Étapes» contient un seul bloc de commandes bash
✅ Tes étapes n'activent pas d'erreurs et ne touchent pas au contrôle de la boutique
✅ Avec la boutique propre, tes étapes amènent une commande jusqu'à expédiée ou livrée et la boutique ne laisse pas l'annuler
✅ Avec l'erreur E3 activée, tes étapes annulent une commande qui avait déjà quitté l'entrepôt : le rapport reproduit l'erreur
✅ Relancées sans redémarrer, tes étapes reproduisent l'erreur sur une nouvelle commande

🎉 Leçon terminée !
```

Lors de la mesure, il a pris environ 4 secondes. À la fin, les erreurs restent comme elles étaient avant que tu le
lances : il n'en allume ni n'en éteint aucune pour toi. Si tes étapes ne se terminent pas en 60 secondes, il les arrête
et te dit :

```text
❌ Avec la boutique propre, tes étapes amènent une commande jusqu'à expédiée ou livrée et la boutique ne laisse pas l'annuler
   → Tes étapes n'ont pas fini en 60 secondes. Vérifie qu'aucune commande n'attend que tu tapes quelque chose.
```

**Avant de considérer la leçon terminée, vérifie :**

- [ ] `reporte.md` est dans `~/practica`.
- [ ] Le titre dit ce qui échoue en une ligne, sans « urgent » ni signes en trop.
- [ ] Il contient une gravité et une priorité, chacune avec son niveau.
- [ ] Les étapes utilisent `$PEDIDO`, pas un numéro écrit à la main.
- [ ] Les étapes ne contiennent pas `tienda error`.
- [ ] Tu as lancé tes étapes deux fois sans redémarrer, avec E3 allumée, et les deux fois tu as vu l'annulation avec 200.
- [ ] Les quatre sections ont du texte de toi : aucune n'est vide ni avec le texte d'exemple entre parenthèses.
- [ ] « Résultat attendu » dit le 409 et cite la règle (« on peut annuler tant que la commande n'a pas quitté
      l'entrepôt »).
- [ ] « Résultat obtenu » dit le 200, que la commande livrée a fini annulée et que $432.00 ont été remboursés.
- [ ] La preuve est la sortie d'une exécution avec E3, copiée telle quelle, et elle dit la même chose que « Résultat
      obtenu ».
- [ ] Si tu as écrit un soupçon, il est marqué comme soupçon et à la fin.
- [ ] Tu as laissé E3 éteinte (`tienda error estado`).

---

## Tes exercices

1. **Un autre rapport.** Allume E1 (`tienda error E1 on`) et écris dans `~/practica/reporte-envio.md` le rapport de la
   livraison facturée sur un panier d'exactement $999.00, avec les mêmes parties. Pour les étapes, commence par le
   `TOKEN=$(…)` de `pasos.sh` et ajoute un panier de **trois** t-shirts bleus qui imprime sous-total, livraison et
   total avec `jq`. Quelle règle de la leçon 02 enfreint-il ? Ce rapport n'est pas vérifié par le `verifica` :
   compare-le avec celui d'en bas. Quand tu as fini, éteins E1.
2. **Se reproduit-il dans la boutique d'un autre ?** Avec E3 allumée, lance tes étapes trois fois de suite sans
   redémarrer. Note le numéro de commande et le code de l'annulation de chaque exécution. Les trois donnent-elles 200 ?
3. **Ta matrice et ton cycle.** Avec la boutique propre puis avec E3, lance à la main les quatre scénarios de la
   matrice de l'étape 5 (QA-003 sort de la même annulation que QA-001 ; QA-004 a besoin du jeton de Luis, comme dans la
   leçon 06). Dans `~/practica/matriz.md`, remplis toi-même la colonne Résultat avec ce que tu as vu **avec E3
   allumée**, écris le détail de chaque scénario avec son « Résultat final », le tableau des observations et la
   section « Cycle 1 » de ton rapport QA.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape 4). Pour chaque cas,
propose une gravité et une priorité, chacune avec une ligne disant pourquoi :

1. La boutique rembourse les commandes déjà livrées quand quelqu'un les annule (E3).
2. Sur la page en bulgare, le bouton « Payer » a une faute d'orthographe, et demain commence une campagne en Bulgarie.
3. Le rapport annuel des ventes par catégorie additionne mal si un produit n'a pas de catégorie. Aujourd'hui tous en
   ont une, et le rapport est tiré de nouveau dans 11 mois.
4. Dans le catalogue, le filtre « Accessoires » n'affiche pas la tasse ; elle apparaît si tu la cherches par son nom.
5. Sur un téléphone qui représente moins de 1 visite sur 100, le logo apparaît coupé.

---

## Pour conclure

Jusqu'à la leçon 11, tu as appris à trouver des erreurs. Cette leçon t'a appris à les remettre, parce qu'une erreur qui
n'est pas comprise n'est pas corrigée.

Ce que tu en retires :

- **Un rapport sert si un autre reproduit l'erreur sans toi.** C'est pour cela qu'il contient des étapes, un résultat
  attendu, un résultat obtenu et des preuves.
- **Dans cette boutique, des étapes qu'on colle épargnent des doutes à qui corrige**, et elles ne doivent pas dépendre
  de ta boutique : garde le numéro de la commande, ne l'écris pas à la main, et lance-les deux fois avant de les envoyer.
- **Décris ce que fait le système**, pas comment tu l'as fait échouer, et sépare ce que tu as vu de ce que tu soupçonnes.
- **La gravité est le dommage ; la priorité, c'est quand on corrige.** Tu proposes les deux ; la priorité peut être
  déplacée par qui dirige le travail.
- **Dans une équipe, ta trouvaille vit à trois endroits** : le rapport avec le détail, la matrice avec le scénario
  échoué et le rapport QA avec le tour où elle est apparue. Les trois se renvoient l'un à l'autre ; aucun ne copie
  l'autre.

Dans la leçon 13, tu retournes la question : tes tests trouvent des erreurs, mais comment sais-tu qu'ils en
trouveraient une que tu ne connais pas encore ?

---

## Compare tes réponses

**Étape 2, la prédiction.** Avec la boutique propre, **409** : la commande a déjà quitté l'entrepôt. Avec E3, **200**.

**Étape 3, la prédiction.** `pasos.sh` montre l'erreur de nouveau sur la commande 2. `pasos-1.sh` non : il déplace la
commande 1, qui était déjà annulée, et l'annulation donne 409.

**Ton rapport**, un qui convient :

````markdown
# Une commande livrée peut être annulée, et elle est remboursée

**Gravité :** haute — la boutique rend l'argent d'une chose qu'elle a déjà livrée.
**Priorité :** haute — à chaque exécution, la commande livrée a été annulée et remboursée.

## Étapes

```bash
(le contenu de pasos.sh de l'étape 2)
```

## Résultat attendu

L'annulation répond 409, « la commande a déjà quitté l'entrepôt ; elle ne peut plus être annulée ». La commande reste
livrée et débitée : « on peut annuler tant que la commande n'a pas quitté l'entrepôt » (histoire d'annuler une
commande).

## Résultat obtenu

L'annulation répond 200. La commande livrée finit annulée et les $432.00 sont remboursés.

## Preuves

```text
📦 La commande 1 est maintenant « à l'entrepôt »
📦 La commande 1 est maintenant « expédiée »
📦 La commande 1 est maintenant « livrée »
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Il se reproduit aussi sur une commande expédiée, avant d'être livrée.
````

La dernière ligne est un fait que tu peux vérifier : fais avancer la commande deux fois au lieu de trois et annule. Si
tu ne l'as pas vérifié, ne l'écris pas.

**Exercice 1.** Les étapes, après le `TOKEN=$(…)` :

```bash
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Avec la boutique propre, il sort `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}` ; avec E1,
`{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}`. Il enfreint la règle de la livraison gratuite **à partir
de** $999.00 : à la limite, la livraison doit être $0.00. Gravité **haute** (il facture trop) et priorité **moyenne** :
dans ce que tu as mesuré, cela n'arrive qu'à un panier d'exactement $999.00, et cela se corrige dans le travail prévu.
Si tu as proposé une priorité haute parce que facturer trop est délicat, c'est valable aussi : écris cette raison.

**Exercice 2.** Trois fois 200. Si tu viens directement de l'étape 3 sans redémarrer, ce sont les commandes 4, 5 et 6
(`pasos-1.sh` en a aussi créé une, la 3). Le numéro change ; l'erreur, non.

**Exercice 3.** Avec E3 allumée, QA-001, QA-003 et QA-004 sortent comme le dit la matrice : Réussi. QA-002 sort Échoué.
Révise ton `matriz.md` avec cette liste :

- [ ] Chaque CA a au moins un scénario, et chaque scénario a son code QA-00N.
- [ ] Chaque ligne a un Type (`Fonctionnel` ou `Sécurité`) et une preuve attendue qu'on peut voir : un code, un état ou
      un mouvement.
- [ ] La colonne Résultat dit Réussi, Échoué, Réussi, Réussi.
- [ ] Chaque scénario a son détail sous le tableau. QA-002 se termine par « Résultat final : échoué ; enregistré comme
      OBS-001 » ; les autres, par « Résultat final : réussi ».
- [ ] Le tableau des observations a une ligne, OBS-001, qui nomme ton `reporte.md` et dit pourquoi ce n'est pas un INC.
- [ ] Tu n'as écrit aucun INC : il n'y a pas de tâche sur un tableau.
- [ ] La section « Cycle 1 » contient la date, le réviseur et le résultat « Non approuvé », et son tableau de constats
      relie H-001 à OBS-001.
- [ ] Ni la matrice ni le cycle ne copient les étapes : ils renvoient à `reporte.md`.

**Révision.** Voici les réponses guides ; compte combien coïncident avec les tiennes dans les deux colonnes. Il y a une
seule exception : au 4, la **priorité** peut être basse ou haute si ta raison apporte une donnée du métier qui change
l'urgence (par exemple, que cette semaine-là on promeut les tasses).

1. Gravité **haute** (perd de l'argent) ; priorité **haute** (cela arrive maintenant, à chaque annulation tardive).
2. Gravité **basse** (ne change pas ce qui est facturé) ; priorité **haute** (la campagne est demain).
3. Gravité **haute** (donne un chiffre faux sans prévenir) ; priorité **basse** (aujourd'hui cela n'arrive pas et le
   rapport est utilisé dans 11 mois).
4. Gravité **moyenne** (échoue, mais il y a une autre façon de trouver la tasse) ; priorité **moyenne** (va dans le
   travail prévu).
5. Gravité **basse** (cosmétique) ; priorité **basse** (presque personne ne le voit).

Si, au 2 ou au 3, tu as mis la même gravité que la priorité, retourne au tableau de l'étape 4 : ce sont les deux cas où
elles se séparent.

---

## Sources de la leçon

1. Simon Tatham, « How to Report Bugs Effectively » (consulté le 22 novembre 2026). « If you have to report a
   bug to a programmer who can't be present in person, the aim of the exercise is to enable them to reproduce the
   problem. » ; « In bug reports, try to make very clear what are actual facts ("I was at the computer and this
   happened") and what are speculations ("I think the problem might be this"). »
   https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
2. Mozilla, « Bug Writing Guidelines » (consulté le 22 novembre 2026). « Provide precise steps to reproduce,
   expected results and actual results » ; « How would you describe the bug in less than 60 characters? It should
   quickly and uniquely identify a bug report as well as explain the problem, not your suggested solution. »
   https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
3. The Chromium Projects, « Bug Life Cycle and Reporting Guidelines » (consulté le 22 novembre 2026).
   « Mention detailed steps to replicate the issue. Include the expected behavior. » ; « Include screenshots, if they
   might help. » https://www.chromium.org/for-testers/bug-reporting-guidelines/
4. ISTQB, « Glossary » : *severity*, *priority* et *defect report* (consulté le 22 novembre 2026). « The degree
   of impact that a defect has on the development, testing or operation of a component or system. »
   https://glossary.istqb.org/en_US/term/severity
5. Bugzilla, « Understanding a Bug » (consulté le 22 novembre 2026). « The Priority field is used to prioritize
   bugs, either by the assignee, or someone else with authority to direct their time such as a project manager. » ;
   « The Severity field indicates how severe the problem is—from blocker (“application unusable”) to trivial (“minor
   cosmetic issue”). » https://bugzilla.readthedocs.io/en/latest/using/understanding.html
6. WebKit, « Bug Report Guidelines » (consulté le 22 novembre 2026). « Good bug reports help developers and
   quality assurance (QA) people decide an appropriate priority and severity for a bug » ; « Normally a QA person or
   developer will set this ». https://webkit.org/bug-report-guidelines/
7. GitHub Docs, « Syntax for issue forms » (consulté le 22 novembre 2026). Le formulaire d'exemple pour signaler une
   erreur demande « What happened? » et « Also tell us, what did you expect to happen? », et demande de coller
   « any relevant log output ».
   https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
8. curl, « curl.1 the man page » (consulté le 22 novembre 2026). « -w, --write-out <format> Make curl display
   information on stdout after a completed transfer. » ; « http_code The numerical response code that was found in the
   last retrieved HTTP(S) or FTP(s) transfer. » https://curl.se/docs/manpage.html

**Format de la maison** (étape 5 et la règle d'audits de l'étape 4) : standards internes de Hábil de matrice de tests,
rapport QA et documentation des incidents. Ils ne sont pas publics ; la leçon montre seulement les parties qu'elle
utilise.
