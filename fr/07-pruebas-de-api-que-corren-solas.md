# Leçon 07 — Des tests d'API qui tournent tout seuls

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Collection :** un fichier qui garde tes requêtes à l'API, dans l'ordre, chacune avec ses tests.
- **Test (dans une collection) :** une ligne qui vérifie une partie de la réponse et dit « réussi » ou « échoué ».
- **newman :** le programme qui lit ta collection, envoie ses requêtes à la boutique et te dit quels tests ont réussi.
- **Environnement :** un fichier à part avec les données qui changent d'une machine à l'autre : l'adresse de la
  boutique, la cliente et son mot de passe.

**Ce que tu en retires :** une collection qui teste un achat de la boutique avec une seule commande, qui sort verte
quand la boutique va bien et rouge quand elle a l'erreur de la livraison, et qui tourne pareil avec une autre cliente
sans y toucher.

**Idée nouvelle de cette leçon (la seule) :** un test gardé, que l'on répète avec une commande, se relance à chaque
fois sans dépendre de quelqu'un qui s'en souvienne.

**Dans quel ordre :** tu gardes ta première requête avec un test et tu la lances (étape 1), tu lui demandes de vérifier
les trois parties de la réponse (étape 2), tu lui apprends à se connecter et à retenir le jeton (étape 3), tu lui fais
attraper l'erreur de la livraison (étape 4) et tu sors les données de la collection vers un environnement pour la
lancer avec une autre cliente (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et l'erreur de la boutique, eux, sont réels.*

Mardi, après la plainte sur la livraison, QA a bien fait les choses : il a envoyé la requête du panier avec `curl`, il a
lu le code, les en-têtes et le corps, et il a trouvé les $99.00 (pesos mexicains). L'équipe a corrigé le mercredi. QA a
répété la requête, a lu le corps et a vu $0.00.

Trois semaines plus tard, quelqu'un change le calcul des réductions. Personne ne touche à la livraison, ou c'est ce
qu'on croit. Personne ne répète la requête du mardi, parce qu'elle était dans un terminal désormais fermé et dans la
mémoire d'une personne qui, ce jour-là, était occupée ailleurs.

La cliente écrit de nouveau.

Ce que QA a fait le mardi était un **test manuel**, et bien fait. Sa limite, c'est qu'il n'a pas été gardé : pour le
répéter, il fallait que quelqu'un s'en souvienne et le remonte. Un **test automatisé** est ce même test gardé dans un
fichier, que n'importe qui relance avec une commande, quand il veut, et qui dit tout seul si tout va toujours bien.
Cette leçon transforme tes requêtes de la leçon 06 en tests automatisés.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans la leçon 00 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur et, dans
une autre fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans le terminal de la boutique, qui te
place déjà dans ton dossier `~/practica`. Ce que tu y gardes y reste même si tu éteins la boutique.

**Tu n'installes rien.** newman est déjà dans la boutique. Vérifie :

```bash
newman --version
```

Elle doit te répondre `6.2.3`.

**Pour écrire les fichiers**, tu utilises `nano`, l'éditeur qui est aussi dans la boutique : `nano nom-du-fichier` l'ouvre
(ou le crée), tu écris ou tu colles, tu enregistres avec `Ctrl+O` et Entrée, et tu sors avec `Ctrl+X`.

**Fais l'étape 3 sans IA.** Ce que tu entraînes là, c'est prédire le code de la connexion, avec sa raison, avant de le
lancer : c'est ce qui te permet ensuite de savoir ce que chaque test doit vérifier et pourquoi.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 06, les trois parties d'une réponse, le 201 à la connexion,
le jeton et le panier de $999.00 avec E1 ; de la 00, `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur ; de la 06,
`tienda reiniciar` pour repartir de zéro et `tienda error E1 on|off` pour activer et désactiver E1 depuis le terminal de
la boutique.

**Repars de zéro avant chaque lancement.** La collection suppose une boutique tout juste ouverte : si ton panier contient
des produits de tout à l'heure, les montants ne collent pas. Avant chaque `newman run`, lance :

```bash
tienda reiniciar
```

Tu n'as pas besoin de te connecter à la main : à partir de l'étape 3, la collection le fait toute seule.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Ta première requête gardée

Dans la leçon 06, tu as demandé le t-shirt bleu avec `curl -i` et tu as lu la réponse. Maintenant, tu vas garder cette
même requête dans un fichier, avec un test qui vérifie le code à ta place.

Une collection est un fichier texte dans un format qui s'appelle **JSON** : des accolades `{ }`, des noms entre
guillemets et des valeurs. newman comprend le format des collections de Postman, un outil très utilisé pour tester des
API. Tu n'as pas à l'apprendre par cœur : tu vas copier le squelette et ne changer que l'intérieur.

Crée le fichier :

```bash
nano tienda.postman_collection.json
```

Et écris ceci :

```json
{
 "info": {
  "name": "Boutique",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "Le t-shirt bleu existe",
   "request": {
    "method": "GET",
    "url": "http://localhost:8080/api/productos/playera-azul"
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));"
      ]
     }
    }
   ]
  }
 ]
}
```

Lis-le de haut en bas :

| Partie | Ce qu'elle dit |
|---|---|
| `info` | Le nom de la collection et le format. Dans cette leçon, le `schema` se copie tel quel |
| `item` | La liste des requêtes, dans l'ordre où elles vont être envoyées. Aujourd'hui, elle en a une |
| `request` | La requête : la méthode et l'adresse. C'est la même chose que ce que tu disais à `curl` |
| `event` → `test` | Ce qui se lance **après** l'arrivée de la réponse : tes tests |
| `pm.test('code 200', …)` | Un test. Entre guillemets, son nom ; après la flèche, ce qu'il vérifie |

La ligne du test se lit ainsi : « un test qui s'appelle *code 200* et qui attend que la réponse ait le code 200 ». `pm`
est la boîte à outils que newman prête à tes tests ; `pm.response` est la réponse qui est arrivée.

Enregistre, sors, et lance-la :

```bash
newman run tienda.postman_collection.json
```

Tu verras quelque chose comme ceci (tes tailles et tes durées changent ; le reste doit coïncider) :

```text
newman

Boutique

→ Le t-shirt bleu existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  code 200
```

Et en dessous, un tableau de résumé. La ligne qui compte est `assertions`, les vérifications : `1` exécutée et `0` échouée.

Cette coche `✓` est ce que tu vas chercher désormais. Ce que dans la leçon 06 tu lisais toi-même, newman le vérifie
maintenant.

> **Si newman se plaint d'une virgule ou d'une accolade :** le JSON est strict. Chaque `{` se ferme avec son `}`, chaque
> `[` avec son `]`, et entre deux éléments d'une liste il y a une virgule, mais **pas après le dernier**. Presque toutes
> les erreurs du premier jour sont une virgule en trop ou en moins. Avant de lancer, vérifie avec `jq`, qui est aussi
> dans la boutique :
>
> ```bash
> jq empty tienda.postman_collection.json
> ```
>
> S'il n'affiche rien, le JSON est bien écrit. Si quelque chose échoue, il te dit la ligne et la colonne où il s'est
> perdu.

---

## Étape 2 · Qu'il vérifie les trois parties

Un test qui ne regarde que le code a le même problème que QA le lundi de la leçon 06 : un 200 dit que la boutique a
répondu, pas qu'elle a bien répondu. Ajoute deux tests de plus à la même requête, un pour le corps et un pour un
en-tête.

Rouvre le fichier et laisse la liste `exec` ainsi :

```json
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.test('il s’appelle T-shirt bleu', () => pm.expect(pm.response.json().nombre).to.eql('T-shirt bleu'));",
       "pm.test('répond en JSON', () => pm.expect(pm.response.headers.get('content-type')).to.include('application/json'));"
      ]
```

Chaque test est une ligne entre guillemets, séparée de la suivante par une virgule. Les deux nouveaux :

| Test | Quelle partie il vérifie | Comment on le lit |
|---|---|---|
| `il s’appelle T-shirt bleu` | Le **corps** | Lit le corps comme du JSON, prend son `nombre` et attend qu'il soit égal à `'T-shirt bleu'` |
| `répond en JSON` | Un **en-tête** | Prend l'en-tête `content-type` et attend qu'il **inclue** `application/json` |

`pm.expect(quelque chose).to.eql(autre chose)` est la forme générale : « j'attends que *quelque chose* soit égal à
*autre chose* ». Avec elle, tu vérifies n'importe quelle donnée du corps.

Lance de nouveau :

```bash
newman run tienda.postman_collection.json
```

```text
→ Le t-shirt bleu existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 262B, 12ms]
  ✓  code 200
  ✓  il s’appelle T-shirt bleu
  ✓  répond en JSON
```

Trois coches, une pour chaque partie de la réponse : code, corps et en-tête.

---

## Étape 3 · Se connecter et retenir le jeton

Pour remplir un panier, il faut se connecter, comme dans la leçon 06. Là, tu copiais le jeton à la main et tu le gardais
dans `TOKEN`. Dans une collection, la requête de connexion le garde toute seule pour celles qui suivent.

**Avant de l'écrire, prédis** (sans IA, sans retourner à la leçon 06) : avec quel code la boutique répond-elle quand tu
te connectes correctement ? Écris-le sur un papier.

Maintenant, ajoute une deuxième requête à la liste `item`. Cherche l'accolade `}` qui ferme la première requête (c'est
celle qui est juste avant le `]` final), écris une **virgule** après elle et colle ceci :

```json
  {
   "name": "Connexion",
   "request": {
    "method": "POST",
    "url": "http://localhost:8080/api/sesiones",
    "header": [
     {"key": "Content-Type", "value": "application/json"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cliente\":\"Marta\",\"contrasena\":\"marta-practica\"}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.collectionVariables.set('token', pm.response.json().token);"
      ]
     }
    }
   ]
  }
```

Ce qu'il y a de nouveau :

- **`header`** est ce que, avec `curl`, tu écrivais avec `-H`, et **`body`** ce que tu écrivais avec `-d`. Les guillemets
  de l'intérieur portent une barre oblique inversée (`\"`) parce que le corps va dans un autre texte entre guillemets.
- **`pm.collectionVariables.set('token', …)`** garde le jeton de la réponse dans une variable de la collection qui
  s'appelle `token`. Toute requête qui vient après peut l'utiliser en écrivant `{{token}}`.

Le test dit 200 exprès, pour comparer une prédiction avec la preuve. Avant de lancer, regarde ton papier.
`tienda reiniciar` et lance :

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Connexion
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 4ms]
  1. code 200
```

Là où il y avait une coche, il y a un numéro : le test a échoué. Tout en bas, newman explique l'échec 1 :

```text
 1.  AssertionError  code 200
                     expected response to have status code 200 but got 201
```

« J'attendais 200 et 201 est arrivé. » Si sur ton papier tu avais écrit 201, tu as bien deviné : se connecter **crée** une
session, et la norme HTTP dit que 201 veut dire « c'est fait et quelque chose de nouveau a été créé » (leçon 06,
étape 3). Si tu avais écrit 200, tu sais maintenant pourquoi on prédit avant : sans ton papier, ce rouge se serait lu
comme « la boutique est en panne », et ce qui était faux, c'était le test.

Corrige le test à 201 :

```json
       "pm.test('code 201', () => pm.response.to.have.status(201));",
```

Relance-la après `tienda reiniciar`. Cette fois, il sort `✓  code 201`.

> **Un rouge n'est pas toujours une erreur de la boutique.** Avant de le signaler, demande-toi qui a raison : la boutique
> ou ton test. C'est à cela que sert d'avoir prédit avec une raison, et pas seulement avec un nombre.

---

## Étape 4 · Qu'il attrape l'erreur de la livraison

Maintenant, la requête qui compte : trois t-shirts à $333.00, un panier de $999.00, qui d'après la règle a la livraison
gratuite. Ajoute une troisième requête comme la deuxième : une virgule après l'`}` qui ferme la connexion, et ceci :

```json
  {
   "name": "Panier de $999.00",
   "request": {
    "method": "PUT",
    "url": "http://localhost:8080/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cantidad\":3}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('code 200', () => pm.response.to.have.status(200));",
       "pm.test('sous-total $999.00', () => pm.expect(pm.response.json().subtotal.texto).to.eql('$999.00'));",
       "pm.test('livraison gratuite', () => pm.expect(pm.response.json().envio.texto).to.eql('$0.00'));"
      ]
     }
    }
   ]
  }
```

`Bearer {{token}}` est le jeton qu'a gardé la requête précédente. C'est pourquoi **l'ordre de la liste compte** : si
cette requête passait en premier, il n'y aurait pas encore de jeton et la boutique répondrait 401.

Pourquoi vérifier le sous-total et la livraison séparément ? Parce que si quelque chose sort rouge, tu veux savoir
**quoi**. Si tu ne vérifiais que le total, un rouge ne te dirait pas si c'est le prix, la quantité ou la livraison qui a
échoué.

**Avec E1 désactivée :**

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Panier de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 542B, 2ms]
  ✓  code 200
  ✓  sous-total $999.00
  ✓  livraison gratuite
```

Dans le tableau du résumé, `assertions` : 7 exécutées, 0 échouées.

**Maintenant, active E1** (sur ton ordinateur, `./practicar error E1 on` ; ou à l'intérieur, `tienda error E1 on`) et
lance pareil :

```bash
tienda error E1 on
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Panier de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 549B, 2ms]
  ✓  code 200
  ✓  sous-total $999.00
  1. livraison gratuite
```

Et en dessous :

```text
 1.  AssertionError  livraison gratuite
                     expected '$99.00' to deeply equal '$0.00'
```

C'est le même bord de $999.00 que dans la scène de la leçon 06 : là-bas, tu y arrivais avec le coupon ; ici, avec trois
t-shirts. Le code reste 200 et le sous-total est bon. La seule chose qui a changé, c'est la livraison, et ta collection
l'a signalée sans que personne lise le corps.

**Le oui ou non, pour une machine.** Juste après avoir lancé newman, écris :

```bash
echo $?
```

`$?` est le **code de sortie** du dernier programme : un nombre que tout programme laisse en terminant. Dans les
lancements de cette leçon, newman s'est terminé par **0** quand tous les tests ont réussi et par **1** quand l'un d'eux
a échoué. Avec E1 activée, il te répond `1` ; désactive-la, repars de zéro, lance de nouveau et il te répond `0`.

Ce nombre permet à **un autre programme** de lire le résultat sans que personne regarde l'écran. Un serveur qui lance les
tests chaque fois que quelqu'un change le code (dans l'industrie, cela s'appelle **intégration continue**) peut lancer ta
collection et regarder ce nombre. Ce qu'il fait d'un 1, chaque équipe le décide : marquer le changement comme échoué,
prévenir ou empêcher son intégration. Dans tous les cas, personne n'a à se souvenir de la requête du mardi.

Avant de continuer, désactive E1 :

```bash
tienda error E1 off
```

---

## Étape 5 · Sortir les données vers un environnement

Ta collection fonctionne, mais elle a écrit à la main trois choses qui ne sont pas du test mais **de ta machine** :
l'adresse `http://localhost:8080`, la cliente `Marta` et son mot de passe. Si quelqu'un la lance contre la boutique d'un
collègue, avec une autre adresse ou une autre cliente, il doit la modifier, et un test qu'il faut modifier pour le
lancer ne tourne plus tout seul.

La solution, c'est de séparer : **la collection dit ce que l'on teste ; l'environnement dit où et avec qui.**

**1. Crée l'environnement** `local.postman_environment.json` :

```bash
nano local.postman_environment.json
```

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"}
 ]
}
```

Trois variables : `base` (l'adresse de la boutique), `cliente` et `contrasena`.

**2. Change la collection pour qu'elle les utilise.** Dans les trois requêtes, remplace `http://localhost:8080` par
`{{base}}`. Dans le corps de la connexion, remplace `Marta` par `{{cliente}}` et `marta-practica` par
`{{contrasena}}` :

```json
    "url": "{{base}}/api/productos/playera-azul"
```

```json
    "url": "{{base}}/api/sesiones",
```

```json
     "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"
```

```json
    "url": "{{base}}/api/carrito/productos/playera-azul",
```

Les doubles accolades `{{ }}` disent à newman : « ici va la valeur de cette variable ». Quand tu lances, il la prend dans
l'environnement.

**3. Lance-la avec l'environnement**, avec `-e` :

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Les mêmes sept coches qu'à l'étape 4. Rien n'a changé dans ce que l'on teste ; ce qui a changé, c'est d'où sortent les
données.

**4. La preuve que tu l'as bien séparée.** Fais un deuxième environnement avec l'autre cliente d'entraînement, Luis :

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"}
 ]
}
```

Et lance **la même collection, sans y toucher** :

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e luis.postman_environment.json
```

Sept coches de nouveau, maintenant en tant que Luis. C'est le signe que ta collection est bien séparée : pour changer de
cliente, tu n'as changé que le fichier d'environnement. Les deux environnements pointent vers la même boutique ; pour
lancer la collection contre la boutique d'une autre machine, tu ferais un environnement avec **sa** `base`, et la
collection ne serait pas touchée non plus.

> **L'environnement sépare les données ; il ne les protège pas.** Le mot de passe va dans l'environnement parce qu'il
> change d'une personne à l'autre, pas parce qu'il y serait à l'abri : l'environnement est aussi un fichier texte que
> l'on peut partager. Ici, les mots de passe sont d'entraînement. Dans un vrai travail, un mot de passe ne s'écrit ni dans
> la collection ni dans un environnement partagé : il se garde dans le coffre à secrets qu'utilise ton équipe.

---

## Comment on vérifie

**Ta collection et ton environnement** sont contrôlés par `verifica 07`. Enregistre-les dans `~/practica` sous les
noms `tienda.postman_collection.json` et `local.postman_environment.json` et, dans le terminal de la boutique,
écris :

```bash
verifica 07
```

Le `verifica` :

1. lance ta collection avec ton environnement et la boutique propre : elle doit sortir **verte** ;
2. la lance avec E1 activée : **au moins un test doit sortir rouge** ; s'il sort vert, ta collection ne regardait pas
   la livraison ;
3. la lance avec un environnement qu'il monte lui-même, avec Luis, et vérifie que ta collection s'est connectée
   **en tant que Luis** ;
4. vérifie qu'aucune requête n'a écrit à la main l'adresse, `Marta` ou son mot de passe.

S'il manque quelque chose, il te dit quelle requête et quoi corriger. Avant de l'exécuter, la liste ci-dessous te dit
si la forme est bonne.

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] Ta collection a trois requêtes dans cet ordre : le produit, la connexion et le panier.
- [ ] Avec E1 désactivée, `newman run … -e local.postman_environment.json` se termine avec 0 échouée et `echo $?` donne
      `0`.
- [ ] Avec E1 activée, « livraison gratuite » échoue et `echo $?` donne `1`.
- [ ] Avec `-e luis.postman_environment.json`, elle sort verte sans que tu aies touché à la collection.
- [ ] Dans ta collection n'apparaissent ni `localhost`, ni `Marta`, ni `marta-practica` (cherche-les avec
      `grep -n -e localhost -e Marta -e marta-practica tienda.postman_collection.json` ; il ne doit rien afficher.
      S'il n'affiche rien, il a trouvé ce qu'on attendait : ici son `echo $?` donne 1, ce qui, pour `grep`, veut dire
      « sans correspondance »).
- [ ] Tu as laissé E1 désactivée (`./practicar error estado` le confirme).

---

## Tes exercices

1. **Une requête qui doit échouer.** Ajoute à la fin de la collection, comme à l'étape 3 (une virgule après l'`}` de la
   dernière requête), une quatrième requête qui demande tes commandes **sans** jeton : `GET {{base}}/api/pedidos`, sans
   en-tête `Authorization`. Avant de la lancer, prédis le code et écris deux tests : un pour le code et un pour l'en-tête
   qui, d'après la leçon 06, doit l'accompagner. Une requête qui attend une erreur est aussi un test : si un jour la
   boutique laisse voir les commandes sans session, ce test devient rouge.
2. **Le coupon sur le panier de $999.00.** Ajoute, de la même façon, une cinquième requête qui applique BIENVENIDA10 au
   panier de l'étape 4 (`POST {{base}}/api/carrito/cupon`, avec le jeton et le corps `{"codigo":"BIENVENIDA10"}`). Avant
   d'écrire les tests, prédis avec E1 **désactivée** : quelle réduction ? quelle livraison ? pourquoi ? Écris un test
   pour la réduction et un autre pour la livraison, et lance-la. Si ta prédiction de la livraison ne coïncide pas avec ce
   qui arrive, retourne à la règle de la livraison de la leçon 02 et décide qui a raison avant de rien corriger.
3. **Le piège de la cliente écrite à la main.** Fais une copie de ta collection (`cp tienda.postman_collection.json
   copia.json`), et dans la copie réécris `Marta` et `marta-practica` dans le corps de la connexion. Lance-la avec
   l'environnement de Luis. Prédis d'abord : verte ou rouge ? Ensuite, réponds en trois lignes : de qui est le panier qui
   s'est rempli ? pourquoi le résultat de newman ne te l'a-t-il pas dit ? et que devrait vérifier un test pour s'en
   rendre compte ? À la fin, supprime la copie avec `rm copia.json`.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Que manquait-il au test manuel du mardi pour se répéter sans dépendre de personne ? (scène)
2. Dans `pm.test('livraison gratuite', …)`, qu'est-ce que `'livraison gratuite'` et à quoi sert-il d'avoir un bon
   nom ? (étape 1)
3. Pourquoi la requête du panier doit-elle venir après la connexion ? (étape 4)
4. Quel code de sortie newman laisse-t-il quand un test échoue, et qui l'utilise ? (étape 4)
5. Qu'est-ce qui va dans la collection et qu'est-ce qui va dans l'environnement ? (étape 5)

---

## Pour conclure

Ce que QA a fait le mardi reste nécessaire : quelqu'un doit lire la réponse complète la première fois, comprendre la
règle et décider quoi vérifier. Ce qui change avec une collection, c'est que cette lecture se garde. La personne
suivante, ou le serveur d'intégration, la répète sans la reconstruire de mémoire.

Ce que tu en retires :

- Une **collection** garde des requêtes dans l'ordre, chacune avec ses **tests** ; `newman run` la lance.
- Chaque test vérifie **une** chose et porte un nom qui dit laquelle. Vérifie les trois parties : code, corps et
  en-têtes.
- `pm.collectionVariables.set` garde une donnée d'une réponse, comme le jeton, pour les requêtes suivantes ; c'est
  pourquoi l'ordre compte.
- Dans cette leçon, newman s'est terminé par **0** si tout a réussi et par **1** si quelque chose a échoué ; c'est ce
  nombre que peut lire l'intégration continue.
- **La collection dit ce que l'on teste ; l'environnement dit où et avec qui.** Si ta collection tourne avec un autre
  environnement sans y toucher, elle est bien séparée.
- Un rouge peut venir de la boutique ou de ton test : prédis avec une raison pour savoir lequel.

Dans la leçon 08, tu montes une deuxième collection avec les mêmes environnements : des tests avec une autre cliente,
sans session et avec un paiement qui se répète, pour voir ce qui se passe quand quelqu'un fait ce qu'il ne doit pas ou le fait deux fois.

---

## Compare tes réponses

**Étape 3, la prédiction.** 201. Se connecter crée une nouvelle session, et 201 veut dire « c'est fait et quelque chose
a été créé ». Si tu as écrit 200 avec la raison « ça s'est bien passé », la raison n'était pas fausse, mais il lui
manquait la distinction entre « ça s'est bien passé » et « ça s'est bien passé et quelque chose a été créé ».

**Exercice 1.** **401**, et l'en-tête `www-authenticate: Bearer`. Mesuré :

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer

{"mensaje":"connecte-toi d'abord"}
```

Des tests qui conviennent :

```json
       "pm.test('code 401', () => pm.response.to.have.status(401));",
       "pm.test('demande un jeton', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
```

Si en plus tu as vérifié le message du corps, tant mieux : c'est la troisième partie.

**Exercice 2.** Avec E1 désactivée : code 200, réduction **$99.90** (les 10 % de $999.00) et livraison **$99.00** ; total
$998.10. La livraison n'est **pas** gratuite parce que la livraison gratuite se calcule sur ce qui reste **après** la
réduction : $999.00 − $99.90 = $899.10, moins que $999.00. C'est la même règle que dans la leçon 05, où le panier de
$1,110.00 avec coupon tombait à $999.00 pile et avait bien la livraison gratuite. Si tu as prédit $0.00, la boutique avait
raison et pas ton test : c'est de nouveau le cas de l'étape 3.

```json
       "pm.test('réduction $99.90', () => pm.expect(pm.response.json().descuento.texto).to.eql('$99.90'));",
       "pm.test('livraison $99.00', () => pm.expect(pm.response.json().envio.texto).to.eql('$99.00'));"
```

**Exercice 3.** **Vert** : les sept tests réussissent. Le panier qui s'est rempli est celui de **Marta** ; celui de Luis
est resté vide. newman ne l'a pas dit parce qu'aucun test ne vérifiait **de qui** était le panier : tous regardaient des
montants, et les montants sont les mêmes pour n'importe quelle cliente. Pour s'en rendre compte, un test devrait
vérifier quelque chose qui dépend de la cliente (par exemple, demander le panier avec la session de Luis et voir qu'il a
les trois t-shirts), ou bien examiner la collection et n'y trouver aucun nom. Le `verifica 07` fait les deux.

**Révision.**

1. Être gardé : un test automatisé vit dans un fichier, se répète avec une commande et dit tout seul si tout va toujours
   bien. Celui du mardi dépendait de quelqu'un qui s'en souvienne et le remonte.
2. C'est le nom du test. Quand il échoue, c'est la première chose que tu lis (« 1. livraison gratuite »), donc il doit te
   dire quelle règle s'est brisée sans que tu ouvres le fichier.
3. Parce qu'elle a besoin du jeton, et que le jeton, c'est la requête de connexion qui le garde. Si elle passait avant,
   `{{token}}` serait vide et la boutique répondrait 401.
4. 1, dans les lancements de cette leçon. N'importe quel programme qui lance ta collection peut le lire, par exemple le
   serveur d'intégration continue ; ce qu'il en fait, chaque équipe le décide.
5. Dans la collection, les requêtes et ce que chaque test attend ; dans l'environnement, l'adresse de la boutique, la
   cliente et son mot de passe.

---

## Sources de la leçon

1. Postman, *newman — the cli companion for postman*, README du dépôt postmanlabs/newman (consulté le 21 novembre
   2026). « Newman is a command-line collection runner for Postman. It allows you to effortlessly run and test a
   Postman collection directly from the command-line » ; « -e <source>, --environment <source>: Specify an
   environment file path or URL. Environments provide a set of variables that one can use within collections ».
   https://github.com/postmanlabs/newman
2. Postman, *Write post-response scripts to test API response data* (learning.postman.com, consulté le 21 novembre
   2026). « Define tests using the pm.test function » ; « Use Chai.js BDD syntax and pm.expect in your
   assertions to test the response detail » ; « Post-response scripts can use dynamic variables, carry out test
   assertions on response data, and pass data between requests ».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/test-scripts/
3. Postman, *Store and reuse values using variables* (learning.postman.com, consulté le 21 novembre 2026).
   « A variable is a symbolic representation of data that enables you to access a value without having to enter it
   manually wherever you need it » ; « Environment variables enable you to scope your work to different environments,
   such as local development versus testing or production environments » ; « Collection variables are available
   throughout the requests in a collection and are independent of environments ».
   https://learning.postman.com/docs/sending-requests/variables/variables/

Mesure propre : chaque sortie de cette leçon a été mesurée avec newman 6.2.2 contre la boutique du cours (HabilMX/curso-qa) le 21 novembre 2026, avec son API lancée sans Docker et redémarrée à chaque lancement : la collection
complète avec Marta et avec Luis (7 tests sur 7 verts, code de sortie 0), avec E1 activée (1 rouge, « livraison
gratuite », code de sortie 1), le test de la connexion écrit avec 200, et les trois exercices. L'image de la boutique
embarque newman 6.2.3.

Règles du cours, sans source externe :

- « Un test, une chose » : chaque `pm.test` vérifie une seule donnée, pour qu'un rouge dise ce qui s'est brisé.
- « Repars de zéro avant chaque lancement » : la collection suppose une boutique tout juste ouverte ; avec des données de
  tout à l'heure, les montants changent et le rouge ne dit rien de la règle.
