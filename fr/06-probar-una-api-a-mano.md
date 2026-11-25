# Leçon 06 — Tester une API à la main

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **API :** la porte par laquelle un programme demande des choses à la boutique, sans écran entre les deux. La page que
  tu as utilisée dans les leçons précédentes passe aussi par là.
- **Requête :** ce que tu envoies : ce que tu veux faire, à quelle route et, parfois, quelques données.
- **Réponse :** ce que la boutique répond. Elle a trois parties : code, en-têtes et corps.
- **Code :** un nombre à trois chiffres au début de la réponse qui dit comment s'est passée ta requête : 200, 404, 422…

**Ce que tu en retires :** tu parles à l'API de la boutique avec `curl`, tu lis les trois parties de chaque réponse et
tu prédis le code d'une requête invalide avant de l'envoyer.

**Idée nouvelle de cette leçon (la seule) :** une API répond avec un code, un corps et des en-têtes, et on vérifie les
trois.

**Dans quel ordre :** tu fais ton premier appel et tu sépares ses trois parties (étape 1), tu apprends à lire le code
(étape 2), tu fais un achat complet par l'API (étape 3), tu découvres pourquoi le code seul ne suffit pas (étape 4), tu
vérifies les en-têtes (étape 5) et tu prédis cinq erreurs avant de les provoquer (étape 6).

---

## La scène

*Scénario inventé ; les codes, les messages et l'erreur de la boutique, eux, sont réels.*

Lundi, 10:00. L'avis arrive : « La livraison gratuite avec coupon est corrigée, tu peux la tester ? ». QA ouvre le
terminal, envoie la requête qui applique le coupon à un panier de $1,110.00 (pesos mexicains) et voit sur la première
ligne :

```text
HTTP/1.1 200 OK
```

« Deux cents. Ça marche. » Il le marque comme testé et passe à la suite.

Le mardi, la même cliente de la leçon 05 écrit de nouveau : on lui a encore prélevé $99.00 de livraison.

QA retourne à son terminal. La réponse de lundi est toujours là, complète. Sous le 200, dans le corps, il y avait
`"envio":{"texto":"$99.00"…}`. Il ne l'a jamais lu.

Le 200 disait seulement que la boutique avait **compris et répondu**. Il ne disait pas qu'elle avait répondu
**correctement**. Cette leçon sert à lire toute la réponse, pas seulement sa première ligne.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans la leçon 00 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur et, dans
une autre fenêtre, le terminal de la boutique. Toutes les commandes de cette leçon se tapent **à l'intérieur**, dans le
terminal de la boutique.

**Fais l'étape 6 sans IA.** Ce que l'on évalue, c'est si **toi**, tu prédis le code avant de voir la réponse. Une IA
peut te donner le code de chaque requête, mais ce que tu entraînes ici, c'est le réflexe d'attendre quelque chose avant
de lancer.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 00, `curl http://localhost:8080/api/salud` et le panneau
réseau du navigateur, où tu as vu le code de chaque requête ; de la 03, le coupon BIENVENIDA10 et son minimum de
$500.00 ; de la 04, qu'une commande payée ne peut plus être payée ; de la 05, la cliente du panier de $1,110.00.

**Repars de zéro quand la leçon le dit.** La boutique garde ce que tu as fait dans les leçons précédentes : tes
commandes, ton panier et tes sessions. Les montants de cette leçon supposent une boutique tout juste ouverte ; donc,
quand une étape dit « repars de zéro », fais deux choses dans le terminal de la boutique :

1. Lance `tienda reiniciar`. C'est la même chose que `./practicar reiniciar` de la leçon 00, mais de l'intérieur. Cela
   efface commandes, paniers et **sessions** ; les erreurs activées restent comme elles étaient.
2. Reconnecte-toi avec la commande « Présente-toi » de l'étape 3 et garde le **nouveau** jeton dans `TOKEN`. L'ancien
   ne sert plus : avec lui, la boutique te répond 401.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Ton premier appel, en trois parties

Dans la leçon 00, tu as demandé à la boutique si elle était démarrée. Maintenant, demande-lui un produit, et ajoute
`-i` :

```bash
curl -i http://localhost:8080/api/productos/playera-azul
```

`-i` demande à `curl` de te montrer aussi les **en-têtes** de la réponse, pas seulement le corps. Tu verras quelque
chose comme ceci (j'ai retiré la date et le nom du serveur, qui changent) :

```text
HTTP/1.1 200 OK
content-length: 114
content-type: application/json
content-language: fr

{"id":"playera-azul","nombre":"T-shirt bleu","precio":{"texto":"$333.00","centavos":33300},"categoria":"T-shirts"}
```

Dans les réponses de l'API que tu verras dans cette leçon, les trois parties arrivent dans cet ordre :

| Partie | Où elle est | Ce qu'elle te dit ici |
|---|---|---|
| **Code** | La première ligne, après `HTTP/1.1` | `200 OK` : ça s'est bien passé |
| **En-têtes** | Les lignes `nom: valeur`, jusqu'à la ligne vide | Que le corps arrive en JSON et en français |
| **Corps** | Tout ce qui vient après la ligne vide | Le t-shirt : son nom, son prix et sa catégorie |

La ligne vide est la frontière : au-dessus, des données **sur** la réponse ; en dessous, la réponse elle-même.

**À toi :** demande un produit qui n'existe pas, `/api/productos/no-existe`, avec `-i`. Avant de le lancer, **prédis**
le code et le corps. Puis compare avec ce que tu vois :

```text
HTTP/1.1 404 Not Found
content-type: application/json
content-language: fr

{"mensaje":"ce produit n'existe pas"}
```

(À partir d'ici, je ne recopie plus `content-length` : il change avec chaque corps et ne t'apprend rien de nouveau.)

---

## Étape 2 · Comment on lit un code

Le code a trois chiffres, et **le premier te dit déjà presque tout**. La norme HTTP (RFC 9110) les regroupe ainsi :

| Commence par | Veut dire | Dans la boutique |
|---|---|---|
| **2** | Ça s'est bien passé | 200, 201 |
| **4** | Le problème est dans **ta requête** | 400, 401, 404, 409, 422 |
| **5** | Le problème est dans **le serveur** | 504, que tu verras à la leçon 08 |

Avant de lire le message, le premier chiffre te dit déjà de quel côté chercher. Un 4 dit « revois ce que tu as envoyé » ;
un 5 dit « la boutique est tombée en panne ».

Voici les codes que tu verras dans la boutique, avec ce que la norme dit de chacun et un exemple mesuré :

| Code | Ce que dit la norme | Quand la boutique le donne |
|---|---|---|
| **200 OK** | Ça s'est bien passé | Tu demandes un produit qui existe |
| **201 Created** | Ça s'est bien passé et quelque chose de nouveau a été **créé** | Tu te connectes ou tu crées une commande |
| **400 Bad Request** | La requête est mal formée | Tu envoies un JSON cassé, comme `{"cantidad:2` |
| **401 Unauthorized** | Il manque un justificatif valide | Tu demandes tes commandes sans t'être connecté |
| **404 Not Found** | Elle n'a pas trouvé ce que tu demandais, ou ne veut pas te dire si cela existe | Un produit ou une commande qui n'existe pas |
| **409 Conflict** | Cela entre en conflit avec l'état actuel de ce que tu demandes | Tu paies une commande déjà payée |
| **422 Unprocessable Content** | Elle a compris la requête, mais ne peut pas faire ce qu'elle demande | Tu demandes 0 pièce ou tu appliques le coupon à un petit panier |

Remarque la différence entre **400** et **422**, car c'est celle que l'on confond le plus. Dans cette boutique :

- **400 :** la boutique **n'a pas pu lire** ta requête. `{"cantidad:2` n'est pas du JSON : il manque un guillemet.
- **422 :** la boutique **l'a bien lue**, et ce que tu demandes ne peut pas se faire. `{"cantidad":0}` est du JSON
  parfait, mais personne n'achète zéro pièce.

La norme réserve le 422 à cela, une requête bien écrite qui ne peut pas être satisfaite. Le 400 est plus large : il
couvre toute requête que le serveur juge mal faite, et le JSON cassé n'en est qu'un exemple.

---

## Étape 3 · Un achat complet par l'API

Sur la page, acheter se résume à quelques clics. Par l'API, ce sont quatre requêtes, et chacune t'apprend quelque
chose sur `curl`.

**Repars de zéro :** lance `tienda reiniciar`. La première requête ci-dessous est justement la connexion.

**1. Présente-toi.** Pour presque tout, il faut se connecter :

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Trois choses nouvelles. Les lignes qui se terminent par `\` sont une seule commande coupée pour qu'elle se lise mieux :

| Option | Ce qu'elle fait |
|---|---|
| `-X POST` | Dit **ce que** tu veux faire : la méthode. Sans `-X`, `curl` utilise `GET`, qui ne fait que demander. Ici, `POST` ouvre une session ; sur d'autres routes, il crée une commande, applique un coupon ou paie |
| `-H '…'` | Ajoute un **en-tête** à ta requête. Celui-ci prévient la boutique que ce que tu envoies est du JSON |
| `-d '…'` | Les **données** que tu envoies : le corps de ta requête |

La boutique répond :

```text
HTTP/1.1 201 Created
content-type: application/json
content-language: fr

{"token":"OsnWdHMafjKUECEhtSIUQ-vU32wnHNDM","cliente":"Marta"}
```

**201**, pas 200 : quelque chose a été créé, ta session. Le `token` est ton laissez-passer ; le tien sera différent.
Garde-le dans une variable pour ne pas le recopier à chaque fois (colle le tien entre les guillemets) :

```bash
TOKEN='colle-ici-ton-token'
```

**2. Ajoute deux t-shirts au panier.** Le jeton voyage dans l'en-tête `Authorization` :

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":2}'
```

`PUT` laisse les choses comme tu le dis : « dans mon panier, je veux 2 de ce t-shirt ». Les guillemets sont ici
doubles, pour que le terminal mette ton jeton à la place de `$TOKEN`.

**3. Transforme le panier en commande :**

```bash
curl -i -X POST http://localhost:8080/api/pedidos \
  -H "Authorization: Bearer $TOKEN"
```

De nouveau **201**. Dans le corps, cherche `"id"` : c'est le numéro de ta commande, avec `"estado":"créée"` et un total
de $765.00 : deux t-shirts à $333.00 plus $99.00 de livraison. Si tu es reparti de zéro, c'est la 1. Garde-le, comme
le jeton (mets le tien) :

```bash
PEDIDO='1'
```

**4. Paie-la :**

```bash
curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}'
```

**200**, avec `"mensaje":"paiement approuvé"` et la commande en `"estado":"payée"`.

Tu viens de faire par l'API ce que tu as fait avec des clics dans la leçon 00. C'est ainsi que l'on teste les règles
sans dépendre de l'écran.

---

## Étape 4 · Pourquoi le code seul ne suffit pas

Retourne à la scène. Maintenant, tu vas voir de tes yeux ce que QA n'a pas lu.

**Repars de zéro** (`tienda reiniciar` et un nouveau jeton de Marta dans `TOKEN`). Ensuite, monte un panier de
$1,110.00 avec 10 casquettes à $111.00 :

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/gorra \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":10}'
```

Et applique le coupon :

```bash
curl -i -X POST http://localhost:8080/api/carrito/cupon \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"codigo":"BIENVENIDA10"}'
```

Avant de regarder, **prédis** : le code et ce que doit dire la livraison.

Avec la boutique propre, voici les parties du corps qui comptent :

```text
HTTP/1.1 200 OK
…
"subtotal":{"texto":"$1,110.00"…},"descuento":{"texto":"$111.00"…},"envio":{"texto":"$0.00"…},"total":{"texto":"$999.00"…}
```

Maintenant, active l'erreur E1, celle de la leçon 05 (l'encadré ci-dessous explique comment), **repars de zéro** à
nouveau et relance les deux requêtes. La réponse change ainsi :

```text
HTTP/1.1 200 OK
…
"envio":{"texto":"$99.00"…},"total":{"texto":"$1,098.00"…}
```

**Le même 200.** Le code n'a pas changé, et le client paierait $99.00 de trop. C'est pourquoi on vérifie les trois : le
code dit si la boutique a compris ; le corps dit **ce que** elle a répondu. Ici, le 200 ne révèle pas l'erreur : le
corps, si. Dans d'autres cas, une règle brisée change le code, le corps ou les deux.

> **Comment on active E1.** Dans le terminal de la boutique : `tienda error E1 on` ; pour la désactiver,
> `tienda error E1 off`. Depuis ton ordinateur, c'est la même chose avec `./practicar error E1 on` et `off`, comme dans
> la leçon 00. À la fin de cette étape, désactive-la.

---

## Étape 5 · Les en-têtes disent aussi des choses

Les en-têtes sont la partie que l'on regarde le moins, et c'est parfois justement celle qui échoue. Deux que portent
toutes les réponses de l'API dans cette leçon :

| En-tête | Ce qu'il dit | Pourquoi tu le vérifies |
|---|---|---|
| `content-type: application/json` | Dans quel format arrive le corps | Si un jour autre chose arrive, celui qui lit la réponse comme du JSON va planter |
| `content-language: fr` | Dans quelle langue arrive le corps | La boutique parle cinq langues ; il faut qu'elle dise dans laquelle elle t'a répondu |

Et un que **toi** tu envoies pour demander une autre langue, `Accept-Language` :

```bash
curl -i http://localhost:8080/api/pedidos -H 'Accept-Language: es'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
content-type: application/json
content-language: es

{"mensaje":"inicia sesión primero"}
```

Vérifie les trois parties ensemble : **401** parce que tu n'as pas envoyé ton jeton ; le corps en espagnol, et
`content-language: es`, qui le confirme. Et un nouvel en-tête, `www-authenticate: Bearer` : la norme HTTP demande que
tout 401 dise **comment** on se présente. Ici, il dit « avec un jeton Bearer », exactement ce que tu as fait à l'étape
3. Si le corps venait en espagnol et que l'en-tête disait `fr`, ce serait une erreur même si le code était le bon.

**À toi :** répète la requête avec `-H 'Accept-Language: en'` et vérifie que le corps et l'en-tête coïncident.

---

## Étape 6 · Prédis avant de lancer

Voici la compétence de la leçon : **savoir quel code tu attends avant de voir la réponse.** Si tu ne l'attendais pas, tu
ne sais pas si ce que tu vois est correct.

**Prépare la boutique :** repars de zéro et répète les quatre requêtes de l'achat de l'étape 3. Il te reste une commande
payée dans `$PEDIDO` et un panier vide.

Copie cette feuille. Pour chaque requête, écris **avant de la lancer** le code que tu attends et pourquoi. Ensuite,
lance-la et note ce qui est sorti : le code, ce que dit le corps et un en-tête que tu as vérifié.

| # | La requête | Ta prédiction | Pourquoi | Code et corps obtenus | Un en-tête que j'ai vérifié |
|---|---|---|---|---|---|
| 1 | Tes commandes, **sans** l'en-tête `Authorization` | | | | |
| 2 | Le produit `/api/productos/zapatos` | | | | |
| 3 | Ajouter des t-shirts avec `-d '{"cantidad":0}'` | | | | |
| 4 | Ajouter des t-shirts avec `-d '{"cantidad":2'` (il manque l'accolade de fin) | | | | |
| 5 | Payer **à nouveau** la commande que tu as payée | | | | |

Pour les requêtes 3 et 4, utilise la commande de l'étape 3, numéro 2, et change seulement ce qui va dans `-d`. Pour la
5, répète le numéro 4 tel quel.

Quand tu as fini, compare avec les réponses à la fin. Pour chaque erreur de prédiction, écris une ligne : ce que tu
croyais et ce que la réponse t'a appris. Ces lignes valent plus que les réussites.

---

## Comment on vérifie

**Ta feuille de prédictions** (étape 6) se vérifie avec « Compare tes réponses » : le code, et que ton « pourquoi »
nomme la bonne cause.

**Ta pratique avec `curl`** est vérifiée par le `verifica 06`. Lance-le **juste après avoir fini l'étape 6**, avant de
redémarrer la boutique :

```bash
verifica 06
```

Il vérifie trois choses dans la boutique : que Marta a une commande payée par l'API, que tu as provoqué les cinq
erreurs de la feuille et que E1 est restée désactivée. Peu importe l'ordre ou le nombre d'essais. La boutique se
souvient de tes requêtes depuis le dernier redémarrage : `tienda reiniciar` efface ce registre ; si tu as redémarré,
refais l'achat et les cinq erreurs (c'est rapide). De chaque requête, elle ne garde que qui l'a faite, sur quelle
route, quel code elle a répondu et à quelle heure ; jamais ce que tu as envoyé, ni ton mot de passe, ni ton jeton.

Une fois ta pratique faite, la sortie ressemble à ceci :

```text
Vérification de la leçon 06…

✅ La boutique a enregistré tes requêtes depuis le dernier redémarrage
✅ Marta a une commande payée, et tu l'as payée par l'API
✅ Tu as provoqué le 401 : tu as demandé GET /api/pedidos sans session
✅ Tu as provoqué le 404 : tu as demandé /api/productos/zapatos
✅ Tu as provoqué le 422 : tu as mis la quantité 0 dans le panier
✅ Tu as provoqué le 400 : tu as envoyé un JSON cassé au panier
✅ Tu as provoqué le 409 : tu as voulu payer à nouveau une commande déjà payée
✅ L'erreur E1 est restée désactivée

🎉 Leçon terminée !
```

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] Tu as fait les quatre requêtes de l'achat et ta commande est passée à `"estado":"payée"`.
- [ ] Tu as vu le même 200 avec E1 désactivée et activée, et dans chaque cas tu as repéré la livraison dans le corps.
- [ ] Tu as demandé une langue avec `Accept-Language` et le corps a coïncidé avec `content-language`.
- [ ] Tu as rempli la colonne « Ta prédiction » des cinq requêtes **avant** de les lancer.
- [ ] Tu as laissé E1 désactivée (`./practicar error estado` le confirme).
- [ ] Tu as lancé `verifica 06` avant de redémarrer et tu as obtenu 🎉.

---

## Tes exercices

1. **Cinq prédictions de plus** (sans IA). Continue avec la boutique comme l'a laissée l'étape 6 et lance-les **dans cet
   ordre**, car chacune dépend de l'état laissé par la précédente. Avant de lancer chacune, écris le code que tu attends
   et pourquoi : (a) te connecter comme Luis avec le mot de passe `incorrecta` ; (b) créer une commande avec le panier
   vide ; (c) mettre **un** t-shirt bleu dans le panier (`{"cantidad":1}`, pas besoin de le prédire) et lui appliquer
   BIENVENIDA10 ; (d) demander `/api/pedidos/uno` ; (e) annuler la commande que tu as payée. Prends 25 minutes comme
   limite. Les commandes, déjà montées :

   ```bash
   curl -i -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' -d '{"cliente":"Luis","contrasena":"incorrecta"}'
   curl -i -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN"
   curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"cantidad":1}'
   curl -i -X POST http://localhost:8080/api/carrito/cupon -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
   curl -i http://localhost:8080/api/pedidos/uno -H "Authorization: Bearer $TOKEN"
   curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion -H "Authorization: Bearer $TOKEN"
   ```

2. **La commande d'une autre personne.** Connecte-toi comme Luis (`luis-practica`), garde son jeton dans `TOKEN_LUIS`
   et demande la commande de Marta, celle que tu as dans `$PEDIDO`, avec le jeton de Luis :
   `curl -i http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN_LUIS"`. Prédis d'abord. La
   boutique répond **404**, pas « interdit ». Pourquoi crois-tu qu'une boutique préfère dire « elle n'existe pas »
   plutôt que « elle existe, mais elle n'est pas à toi » ? Réponds en trois lignes.
3. **Vérifie les trois.** Avec E1 activée, écris, pour la requête du coupon de l'étape 4, ce que tu vérifierais dans
   chaque partie : une ligne pour le code, une pour un en-tête et une pour le corps. Laquelle des trois attrape
   l'erreur ?

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape 2) :

1. Quelles sont les trois parties d'une réponse, et qu'est-ce qui les sépare ?
2. Une réponse commence par 4. De quel côté cherches-tu le problème ?
3. Quelle différence y a-t-il entre un 400 et un 422 ?
4. Pourquoi la connexion répond-elle 201 et pas 200 ?
5. Une réponse dit 200 OK. Peux-tu déjà dire que la règle fonctionne ? Pourquoi ?

---

## Pour conclure

Le test de lundi est resté à moitié fait : le 200 était correct, et le corps montrait déjà la mauvaise livraison,
complète, sous la ligne que l'on avait bien lue. Lire les trois parties, c'est ce qui complète le test.

Ce que tu en retires :

- Toute réponse a **trois parties** : code, en-têtes et corps, avec une ligne vide avant le corps.
- Le **premier chiffre** du code te dit de quel côté chercher : 2, ça s'est bien passé ; 4, c'est ta requête ; 5, c'est
  le serveur.
- **400**, c'est « je ne t'ai pas compris » ; **422**, c'est « je t'ai compris, et ça ne se peut pas ».
- Avec `curl` : `-i` pour voir les en-têtes, `-X` pour dire ce que tu fais, `-H` pour tes en-têtes et `-d` pour tes
  données.
- **Un 200 ne prouve pas la règle.** Il dit que la boutique a compris ; si la règle a été respectée, c'est le corps et,
  parfois, le code qui le disent.
- Avant de lancer, **prédis** : sans réponse attendue, tu ne sais pas si celle qui est arrivée est correcte.

Dans la leçon 07, ces mêmes requêtes ne s'écrivent plus à la main : tu les gardes dans une collection qui tourne toute
seule et vérifie les trois parties à ta place.

---

## Compare tes réponses

**Étape 1, le produit qui n'existe pas.** `404 Not Found` et `{"mensaje":"ce produit n'existe pas"}`. Le 4 te disait
déjà que le problème était dans ta requête : tu as demandé quelque chose que la boutique n'a pas.

**Étape 4, la prédiction.** `200 OK` et livraison $0.00 : ce que l'on paie pour la marchandise après le coupon est de
$999.00 pile, et à partir de là la livraison est gratuite (leçon 02). Avec E1 activée, le code est le même et la
livraison sort à $99.00.

**Étape 6, la feuille.**

| # | Code | Pourquoi | Corps | Un en-tête |
|---|---|---|---|---|
| 1 | **401** | Sans jeton, la boutique ne sait pas qui tu es | `{"mensaje":"connecte-toi d'abord"}` | `www-authenticate: Bearer` |
| 2 | **404** | Ce produit n'existe pas | `{"mensaje":"ce produit n'existe pas"}` | `content-language: fr` |
| 3 | **422** | Le JSON est correct ; zéro pièce, ce n'est pas possible | `{"mensaje":"le minimum est de 1 pièce"}` | `content-type: application/json` |
| 4 | **400** | Ce n'est pas du JSON : la boutique n'a pas pu le lire | `{"mensaje":"la requête ne contient pas ce que cette route attend",…}` | `content-language: fr` |
| 5 | **409** | La commande est déjà payée : cela entre en conflit avec son état | `{"mensaje":"cette commande ne peut plus être payée : elle est « payée »"}` | `content-type: application/json` |

Dans la colonne de l'en-tête, n'importe lequel convient, du moment que tu l'as lu. Dans la 1, celui qui dit quelque
chose de nouveau est `www-authenticate`.

Dans la 4, le corps contient en plus un `"detalle"` avec ce qui a échoué ; tu n'as pas besoin de le lire en entier.

**Exercice 1.** (a) **401**, « client ou mot de passe incorrect », avec `www-authenticate: Bearer`. (b) **422**, « le
panier est vide » : créer la commande de l'étape 6 l'a vidé. (c) **422**, « le coupon est réservé aux achats de $500.00
ou plus » : un t-shirt à $333.00 n'atteint pas le minimum. (d) **400** : `uno` n'est pas un nombre, et la route en
attend un. (e) **200** : une commande payée peut encore être annulée (leçon 04), et le corps contient le remboursement
de $765.00.

**Exercice 2.** **404**, « cette commande n'existe pas », exactement comme si tu en demandais une qui n'existe pas,
comme la 999. Une réponse défendable : si la boutique répondait « elle existe, mais elle n'est pas à toi », n'importe qui
pourrait essayer des numéros et découvrir combien de commandes il y a et lesquelles existent. La norme HTTP permet
justement cela : un 404 peut vouloir dire que le serveur ne veut pas révéler si quelque chose existe.

**Exercice 3.** Code : 200, celui qui est attendu, donc il n'attrape rien. En-tête : `content-type: application/json`,
celui qui est attendu. Corps : `"envio"` à $99.00 alors qu'il devait être à $0.00. **Seul le corps attrape l'erreur.**

**Révision.** 1, code, en-têtes et corps ; la ligne vide sépare les en-têtes du corps. 2, de ta requête. 3, le 400 est
une requête que la boutique n'a pas pu lire ; le 422, une requête qu'elle a bien lue et qui demande quelque chose qui ne
peut pas se faire. 4, parce que quelque chose de nouveau a été créé : ta session. 5, non : le code dit que la boutique a
compris et répondu ; si la règle a été respectée, c'est le corps qui le dit.

---

## Sources de la leçon

1. IETF, *RFC 9110: HTTP Semantics*, juin 2022, §15 « Status Codes » et §8.5 « Content-Language ».
   « The first digit of the status code defines the class of response » ; « 4xx (Client Error): The request contains bad
   syntax or cannot be fulfilled » ; « The 201 (Created) status code indicates that the request has been fulfilled and
   has resulted in one or more new resources being created » ; « The 404 (Not Found) status code indicates that the
   origin server did not find a current representation for the target resource or is not willing to disclose that
   one exists » ; « The server generating a 401 response MUST send a WWW-Authenticate header field » ; « The 409 (Conflict) status code indicates that the request could not be completed due to a conflict
   with the current state of the target resource » ; « the syntax of the request content is correct, but it was unable
   to process the contained instructions » (422) ; « The "Content-Language" header field describes the natural
   language(s) of the intended audience for the representation ». https://www.rfc-editor.org/rfc/rfc9110
2. curl, *curl.1 the man page* (curl.se/docs/manpage.html, consulté le 21 novembre 2026). `-i` : « Show
   response headers in the output » ; `-X` : « Change the method to use when starting the transfer » ; `-H` : « Extra header
   to include in information sent » ; `-d` : « Send the specified data to a server ».
   https://curl.se/docs/manpage.html

Mesure propre : chaque code, corps et en-tête de cette leçon a été mesuré avec `curl -i` contre la boutique du cours
(hb-curso-qa, commit db52e90) le 21 novembre 2026, avec son API lancée sans Docker, y compris les cinq requêtes de la
feuille, les cinq de l'exercice 1 et la commande de Marta vue par Luis. La requête du coupon de l'étape 4 a été lancée
avec E1 désactivée et activée : 200 les deux fois, avec une livraison de $0.00 et de $99.00.

Règles du cours, sans source externe :

- « Prédis avant de lancer » : c'est la façon dont ce cours entraîne l'oracle, la réponse attendue que l'ISTQB demande
  pour chaque cas de test ; sans elle, une réponse ne peut pas être jugée.
