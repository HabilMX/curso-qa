# Leçon 08 — Permissions et nouveaux essais

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Commande d'autrui :** une commande passée par une autre personne. Toi, tu ne devrais pas pouvoir la voir, même si
  tu connais son numéro.
- **Nouvel essai :** renvoyer une requête parce que la première n'a pas eu de réponse claire.
- **Clé d'idempotence :** un texte unique que tu envoies avec le paiement, dans l'en-tête `Idempotency-Key`, pour que la
  boutique sache qu'un nouvel essai est **le même** paiement et pas un nouveau.

**Ce que tu en retires :** une deuxième collection qui teste une commande de trois façons que la leçon 07 ne touchait
pas : sans session, avec une autre cliente et avec un paiement qui se répète. Elle sort verte quand la boutique va bien,
rouge quand elle laisse voir une commande d'autrui et rouge quand elle prélève deux fois.

**Idée nouvelle de cette leçon (la seule) :** chaque test important se répète avec une autre personne, et chaque requête
qui change quelque chose se répète deux fois.

**Dans quel ordre :** tu montes la collection avec une vraie commande (étape 1), tu demandes cette commande sans session
(étape 2) et avec une autre cliente (étape 3), tu paies et tu répètes le paiement avec la même clé (étape 4), et tu
répètes tout avec la passerelle lente, c'est là que le double prélèvement apparaît (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Un vendredi soir, deux messages arrivent au support à dix minutes d'écart.

Le premier est de Marta. Elle a payé sa commande, la page est restée à réfléchir, un avis « nous ne savons pas si le
paiement a été prélevé » est apparu et elle a payé de nouveau. Dans sa banque, il y a **deux** prélèvements de $432.00
(pesos mexicains). La commande, dans la boutique, n'est toujours pas payée.

Le second est de Luis, et il est pire. Il a ouvert sa commande, il a vu que l'adresse se terminait par `/api/pedidos/12`,
il a changé le 12 en 11 par curiosité et la boutique lui a montré la commande d'une autre personne, avec ses produits et
son total.

Les tests de l'équipe étaient verts. Ils testaient l'achat complet, avec une cliente, une fois. Aucun ne demandait ce qui
se passe si **une autre** personne demande la même commande, ni ce qui se passe si le paiement **se répète**. Les deux
choses que les gens font vraiment.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans la leçon 07 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur et, dans
une autre fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`, où tu as
déjà les environnements de la leçon 07.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 07, la collection, `pm.test`,
`pm.collectionVariables.set`, les environnements `local` et `luis`, `newman run` et `jq empty` ; de la 06, le 401 sans
jeton et l'en-tête `www-authenticate: Bearer` ; de la 04, que répéter un paiement avec la même clé n'est pas un nouveau
paiement ; de la 00, que la page envoie la clé d'idempotence quand tu paies.

**Fais l'étape 3 sans IA.** Ce que tu entraînes là, c'est prédire quel code la boutique doit répondre quand une autre
cliente demande ta commande, avec sa raison, avant de le lancer.

**Repars de zéro avant chaque lancement,** comme dans la 07 :

```bash
tienda reiniciar
```

> **Cette leçon utilise la boutique de la leçon 08.** Elle apporte l'erreur E5, la carte coupée (`•••• 4242`) et un
> `tienda reiniciar` qui écarte les paiements que la passerelle avait en route. Si `tienda error E5 on` te dit que cette
> erreur n'existe pas, mets ta boutique à jour avant de continuer : avec une version plus ancienne, tes sorties ne vont
> pas coïncider.

Attention à un détail : `tienda reiniciar` remet aussi la passerelle de paiement à la normale. Si, à l'étape 5, tu veux
la passerelle lente, tu la règles **après** avoir redémarré.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Une nouvelle collection, avec une vraie commande

Pour tester qui peut voir une commande, il te faut d'abord une commande. Cette collection la fait toute seule : la cliente
se connecte, met un t-shirt dans le panier et passe sa commande. De cette réponse, elle garde deux choses pour plus tard :
le **numéro de la commande** et une **clé d'idempotence** neuve.

**D'abord, l'autre cliente dans tes environnements.** Pour tester « avec une autre cliente » sans écrire son nom dans la
collection, chaque environnement dit qui est l'autre. Ouvre le tien :

```bash
nano local.postman_environment.json
```

et laisse-le comme ça (les trois premières clés sont celles de la leçon 07 ; les deux dernières sont nouvelles) :

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"},
  {"key": "otra_cliente", "value": "Luis"},
  {"key": "otra_contrasena", "value": "luis-practica"}
 ]
}
```

Et celui de Luis, à l'envers : pour lui, l'autre est Marta.

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"},
  {"key": "otra_cliente", "value": "Marta"},
  {"key": "otra_contrasena", "value": "marta-practica"}
 ]
}
```

**Maintenant, la collection.** C'est un nouveau fichier ; celui de la leçon 07 n'est pas touché :

```bash
nano permisos.postman_collection.json
```

```json
{
 "info": {
  "name": "Permissions",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "La cliente se connecte",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "Un t-shirt au panier",
   "request": {
    "method": "PUT",
    "url": "{{base}}/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"cantidad\":1}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Elle passe sa commande",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('pedido', pm.response.json().id);",
    "pm.collectionVariables.set('llave', pm.variables.replaceIn('{{$guid}}'));"
   ]}}]
  }
 ]
}
```

Tout cela, tu le connais déjà de la leçon 07, sauf les dernières lignes :

| Ligne | Ce qu'elle fait |
|---|---|
| `pm.collectionVariables.set('pedido', …id)` | Garde le numéro de la commande qu'elle vient de créer, pour la demander ensuite comme `{{pedido}}` |
| `pm.variables.replaceIn('{{$guid}}')` | `{{$guid}}` est une variable que Postman invente à chaque lancement : un texte unique, comme `611c2e81-2ccb-42d8-9ddc-2d0bfa65c1b4`. `replaceIn` le transforme en texte |
| `pm.collectionVariables.set('llave', …)` | Garde ce texte comme clé d'idempotence de **ce** paiement, pour l'utiliser deux fois à l'étape 4 |

Pourquoi la clé ne s'écrit-elle pas à la main, comme `compra-1` ? Parce que chaque paiement a besoin de la sienne. Si tu
l'écrivais fixe, la deuxième fois que tu lancerais la collection, la boutique verrait une clé déjà utilisée pour une
autre commande (tu l'essaies dans l'exercice 3).

Vérifie que le JSON est bien écrit et lance-la :

```bash
jq empty permisos.postman_collection.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ La cliente se connecte
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 14ms]
  ✓  code 201

→ Un t-shirt au panier
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ Elle passe sa commande
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  code 201
```

Trois sur trois. Les tailles et les temps des sorties de cette leçon sont ceux de la mesure ; les tiens peuvent changer.
Les codes, les coches et les rouges, non.

---

## Étape 2 · Sans session

La première question de permissions est la plus simple : quelqu'un qui **ne s'est pas connecté** peut-il voir la
commande ?

Ajoute une quatrième requête, comme dans la leçon 07 : une virgule après l'`}` qui ferme « Elle passe sa commande », et
ceci :

> **Comment coller dans `item`.** Chaque nouvelle requête va **avant le `]` qui ferme `item`**. Mets une virgule après
> l'`}` de la dernière requête que tu avais déjà. Si tu en colles deux ou trois d'un coup, il y a aussi une virgule entre
> chacune, mais **pas** après la dernière. À la fin, le fichier se termine par `]` et `}`, et `jq empty` n'affiche rien.

```json
  {
   "name": "Sans session, on ne voit rien",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('sans session : code 401', () => pm.response.to.have.status(401));",
    "pm.test('demande un jeton', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
   ]}}]
  }
```

Elle n'a pas d'en-tête `Authorization` : c'est justement le but. Les deux tests, tu les as déjà écrits dans l'exercice 1
de la leçon 07, pour la liste des commandes ; ici ils portent sur **une** commande, celle que la collection vient de créer.

`jq empty`, `tienda reiniciar` et lance. Les trois premières restent pareilles, et la nouvelle :

```text
→ Sans session, on ne voit rien
  GET http://localhost:8080/api/pedidos/1 [401 Unauthorized, 217B, 2ms]
  ✓  sans session : code 401
  ✓  demande un jeton
```

---

## Étape 3 · Avec une autre cliente

Maintenant, la question de la scène : Luis a une session, connaît le numéro de la commande de Marta et la demande. Que
doit répondre la boutique ?

**Avant d'écrire le test, prédis sur papier :** le code, et une raison d'une ligne. Ne continue pas à lire avant de
l'avoir.

Tu as trois candidats raisonnables, et les trois ont du sens :

| Code | Ce que dirait la boutique |
|---|---|
| 401 | « Je ne sais pas qui tu es » |
| 403 | « Je sais qui tu es et je ne te laisse pas faire » |
| 404 | « Cette commande n'existe pas » |

401, ce n'est pas ça : Luis s'est bien connecté, la boutique sait qui il est. Entre 403 et 404, cette boutique a choisi
**404**, et elle a une règle écrite pour ça : une commande d'autrui **n'existe pas** pour qui ne l'a pas passée. La raison
est qu'un 403 dit déjà à Luis quelque chose qu'il ne devrait pas savoir : que la commande 11 existe. Avec 404, la réponse
ne le lui confirme pas ; c'est ce que la leçon 06 appelait « elle ne veut pas te dire si elle existe ». D'autres API
choisissent 403, et c'est bien aussi : l'indispensable, c'est que Luis ne voie ni ne touche la commande. Si tu as prédit
403 avec cette raison, ton raisonnement était bon ; la différence est une décision de la boutique, et le test vérifie
**ce que la boutique a décidé**.

Ajoute deux requêtes de plus, avec une virgule entre les deux. La première se connecte avec l'autre cliente et garde
**son** jeton à part ; la seconde demande la commande avec ce jeton :

```json
  {
   "name": "L’autre cliente se connecte",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{otra_cliente}}\",\"contrasena\":\"{{otra_contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token_otra', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "L’autre cliente ne la voit pas",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token_otra}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('commande d’autrui : code 404', () => pm.response.to.have.status(404));",
    "pm.test('sans produits', () => pm.expect(pm.response.json()).to.not.have.property('productos'));"
   ]}}]
  }
```

| Test | Pourquoi il est là |
|---|---|
| `commande d’autrui : code 404` | La règle de la boutique |
| `sans produits` | Au cas où, un jour, la boutique répondrait un autre code **et enverrait quand même** la commande. Ce qui compte, c'est que Luis ne voie pas les produits de Marta, pas seulement le numéro de la réponse |

Lance à nouveau. Les deux nouvelles :

```text
→ L’autre cliente se connecte
  POST http://localhost:8080/api/sesiones [201 Created, 213B, 2ms]
  ✓  code 201

→ L’autre cliente ne la voit pas
  GET http://localhost:8080/api/pedidos/1 [404 Not Found, 195B, 2ms]
  ✓  commande d’autrui : code 404
  ✓  sans produits
```

**Maintenant, active l'erreur de la scène.** E5 fait que la boutique montre la commande à n'importe qui qui a une session :

```bash
tienda error E5 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ L’autre cliente ne la voit pas
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  1. commande d’autrui : code 404
  2. sans produits
```

Et en dessous :

```text
 1.  AssertionError  commande d’autrui : code 404
                     expected response to have status code 404 but got 200
 2.  AssertionError  sans produits
                     expected { id: 1, estado: 'creado', …(11) } to not have property 'productos'
```

Voilà la commande de Marta dans les mains de Luis, et ta collection l'a attrapé. Remarque une chose : **tous les autres
tests sont restés verts.** Avec Marta seule, la boutique avec E5 a l'air parfaite. L'erreur n'apparaît que quand une
autre personne demande.

Désactive-la avant de continuer :

```bash
tienda error E5 off
```

---

## Étape 4 · Payer, et répéter le paiement avec la même clé

Payer est une requête qui **change quelque chose** : elle déplace de l'argent. Ces requêtes ont une question de plus :
que se passe-t-il si elles arrivent deux fois ?

Elles peuvent arriver deux fois : la page reste à réfléchir et la personne appuie de nouveau sur « Payer », ou le réseau
se coupe et le programme réessaie tout seul. C'est pourquoi la boutique accepte l'en-tête `Idempotency-Key` : si deux
paiements arrivent avec la **même** clé, l'un **après** l'autre, elle ne prélève qu'une fois. Si le premier a déjà eu une
réponse, elle répond la même chose au second ; si le premier est resté sans réponse (un 504, à l'étape 5), le second
attend que ce même paiement se termine. Si deux arrivaient exactement en même temps, cette boutique répond 409 au second
pendant que le premier est encore en cours ; c'est un sujet de la leçon 09.

Ajoute les trois dernières requêtes, avec une virgule entre chacune. Les deux premières sont **le même paiement**, avec la
même clé ; la troisième vérifie
où en est la commande :

```json
  {
   "name": "Elle paie",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('approuvé ou sans réponse', () => pm.expect(pm.response.code).to.be.oneOf([200, 504]));"
   ]}}]
  },
  {
   "name": "Elle réessaie avec la même clé",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('nouvel essai : code 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Où en est la commande",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('commande payée', () => pm.expect(pm.response.json().estado).to.eql('pagado'));",
    "pm.test('prélevé égal au total', () => pm.expect(pm.response.json().cobrado.texto).to.eql(pm.response.json().total.texto));"
   ]}}]
  }
```

Trois choses nouvelles :

- **`to.be.oneOf([200, 504])` :** le premier paiement accepte deux réponses. 200, c'est « approuvé » ; 504, c'est « la
  passerelle n'a pas répondu à temps et je ne sais pas si c'est prélevé ». Les deux sont honnêtes, et ce qui compte vient
  après. Pourquoi le 504 est nécessaire, tu le vois à l'étape 5.
- **`cobrado` et `total` :** la commande apporte les deux. `total` est ce que la cliente doit ; `cobrado` est ce que la
  passerelle a vraiment prélevé sur sa carte. S'ils sont différents, quelqu'un a prélevé de trop ou de moins. Le test
  compare l'un à l'autre, donc il ne dépend pas du montant : il sert pareil pour une commande de $432.00 que pour une de
  $999.00.
- **La carte** `4242 4242 4242 4242` est celle d'entraînement de la leçon 00, qui n'est à personne. Dans les réponses de
  la boutique, elle sort coupée, `•••• 4242` : dans une réponse, on ne montre pas le numéro complet d'une carte.

Lance :

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 969B, 3ms]
  ✓  approuvé ou sans réponse

→ Elle réessaie avec la même clé
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 969B, 2ms]
  ✓  nouvel essai : code 200

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 2ms]
  ✓  commande payée
  ✓  prélevé égal au total
```

Douze sur douze. Le deuxième paiement a répondu la même chose que le premier et n'a pas prélevé de nouveau.

**Maintenant, active E4**, l'erreur du double prélèvement, et lance pareil :

```bash
tienda error E4 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Douze sur douze **encore**. E4 ne fait rien ? Si, elle fait quelque chose, mais seulement quand le premier paiement reste
sans réponse. Avec la passerelle qui répond vite, la boutique a gardé la réponse du premier paiement et l'a rendue telle
quelle au nouvel essai, sans arriver à la partie que E4 casse. Pour voir l'erreur, tu dois provoquer ce qui est arrivé à
Marta : que la passerelle tarde.

---

## Étape 5 · Quand la passerelle tarde

La boutique attend la passerelle **5 secondes**. Si, dans ce délai, elle ne répond pas, la boutique dit à la cliente
**504** : « la passerelle n'a pas répondu à temps ; nous ne savons pas si le paiement a été prélevé. Réessaie avec la même
clé d'idempotence ». Mais la passerelle continue de travailler, et le paiement peut se terminer plus tard.

C'est le moment dangereux : la cliente ne sait pas si c'est prélevé et elle paie de nouveau. Avec la même clé, la
boutique reconnaît que c'est le même paiement : elle attend que le premier se termine et répond 200, sans prélever de
nouveau. Avec une clé différente, ou avec une boutique qui ne respecte pas la clé, ce sont deux prélèvements.

Fais en sorte que la passerelle tarde 7 secondes (après avoir redémarré, parce que redémarrer la remet à la normale), avec
E4 toujours activée :

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Le lancement dure une dizaine de secondes. Les trois dernières requêtes :

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé ou sans réponse

→ Elle réessaie avec la même clé
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  1. nouvel essai : code 200

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 5ms]
  2. commande payée
  ✓  prélevé égal au total
```

Et en dessous :

```text
 1.  AssertionError  nouvel essai : code 200
                     expected response to have status code 200 but got 504
 2.  AssertionError  commande payée
                     expected 'creado' to deeply equal 'pagado'
```

Deux rouges : le nouvel essai n'a pas eu de réponse non plus et la commande reste « creado ». Et « prélevé égal au total »
en vert ? À cet instant, oui : un prélèvement de $432.00 était déjà entré. Le second prélèvement, celui que E4 a lancé
avec une autre clé en cachette, était encore en route. Ta collection l'a attrapé grâce aux deux autres tests, mais ce
second prélèvement, personne ne l'a encore vu.

**Regarde-le toi-même.** Sans redémarrer, attends quelques secondes et demande la commande à la main, comme dans la
leçon 06. Connecte-toi en tant que Marta :

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Garde le jeton qu'elle t'a répondu et demande la commande 1 :

```bash
TOKEN='pega-aquí-tu-token'
curl -i http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN"
```

Dans le corps, cherche `"estado"` et `"cobrado"` : la commande est toujours à `"creado"`, et ce qui a été prélevé dit
maintenant `"$864.00"`, le double du total. C'est la scène de Marta : deux prélèvements et la commande sans être payée.

La valeur d'`estado` est un code et reste en espagnol (`creado`, `pagado`) ; la page l'affiche dans ta langue
(créée, payée).

**Maintenant, désactive E4 et lance pareil, avec la passerelle lente :**

```bash
tienda error E4 off
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé ou sans réponse

→ Elle réessaie avec la même clé
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 969B, 1989ms]
  ✓  nouvel essai : code 200

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  commande payée
  ✓  prélevé égal au total
```

Douze sur douze. Le premier paiement a dit 504 ; le nouvel essai, avec la même clé, a attendu que la passerelle termine
(c'est pour ça qu'il a pris environ deux secondes) et a répondu 200. Un seul prélèvement. Maintenant, tu vois pourquoi le
premier paiement accepte 200 **ou** 504 : la même collection doit sortir verte avec la passerelle rapide et avec la
lente, parce que l'erreur ne se voit qu'avec la lente.

**Et avec l'autre personne.** L'idée de cette leçon vaut aussi à l'envers : lance la collection en tant que Luis, avec la
passerelle lente :

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e luis.postman_environment.json
```

Douze sur douze. Maintenant, la commande est celle de Luis, et c'est Marta qui essaie de la voir. Tu n'as pas touché à la
collection : seulement à l'environnement.

Laisse la passerelle normale en terminant :

```bash
tienda pasarela aprueba
```

---

## Comment on vérifie

**Ta collection et tes environnements** sont contrôlés par `verifica 08`. Enregistre-les dans `~/practica` sous les
noms `permisos.postman_collection.json`, `local.postman_environment.json` et `luis.postman_environment.json` et, dans
le terminal de la boutique, écris :

```bash
verifica 08
```

Le `verifica` :

1. lance ta collection avec la boutique propre trois fois : avec ton environnement `local`, avec `local` et la
   passerelle qui tarde 7 secondes, et avec ton environnement `luis` : les trois fois, elle doit sortir **verte** ;
2. la lance avec E5 activée : **au moins un test doit sortir rouge** ; s'il sort vert, ta collection n'a pas demandé à
   une autre cliente ;
3. la lance avec E4 activée et la passerelle qui tarde 7 secondes : **au moins un test doit sortir rouge** ; s'il sort
   vert, ta collection n'a pas vérifié le nouvel essai ;
4. vérifie qu'aucune requête n'a écrit à la main l'adresse, `Marta`, `Luis` ou leurs mots de passe.

S'il manque quelque chose, il te dit quoi corriger. Avec la passerelle lente, il met quelques minutes. Avant de
l'exécuter, la liste ci-dessous te dit si la forme est bonne.

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] Tes deux environnements ont `otra_cliente` et `otra_contrasena`, et dans chacun l'autre est l'autre personne.
- [ ] Ta collection a neuf requêtes, dans l'ordre des étapes 1 à 4.
- [ ] Avec la boutique propre, elle sort 12 sur 12, avec la passerelle normale et avec `tienda pasarela tarda 7`.
- [ ] Avec E5 activée, « commande d’autrui : code 404 » et « sans produits » échouent.
- [ ] Avec E4 activée et la passerelle lente, « nouvel essai : code 200 » et « commande payée » échouent.
- [ ] Avec `-e luis.postman_environment.json`, elle sort verte sans toucher à la collection.
- [ ] Dans ta collection n'apparaissent ni `localhost`, ni `Marta`, ni `Luis`, ni les mots de passe (cherche-les avec
      `grep -n -e localhost -e Marta -e Luis -e practica permisos.postman_collection.json` ; il ne doit rien afficher).
- [ ] Tu as laissé E4 et E5 désactivées et la passerelle normale (`tienda error estado` et `tienda pasarela aprueba`).

---

## Tes exercices

1. **Annuler celle d'autrui.** Ajoute une requête, après « L’autre cliente ne la voit pas », dans laquelle l'autre cliente
   essaie d'**annuler** la commande : `POST {{base}}/api/pedidos/{{pedido}}/cancelacion`, avec son jeton. Avant de la
   lancer, prédis le code et écris deux tests : un pour le code et un autre qui vérifie, dans la requête « Où en est la
   commande », que la commande **reste** « pagado ». Pourquoi le second test est-il nécessaire, si le premier vérifie
   déjà le code ?
2. **La clé neuve à chaque essai.** Fais une copie de ta collection (`cp permisos.postman_collection.json copia.json`).
   Dans la copie, dans « Elle réessaie avec la même clé », remplace `{{llave}}` par `{{$guid}}` : ainsi chaque essai porte
   une clé différente. Lance-la avec E4 **désactivée** et la passerelle lente. Prédis d'abord : verte ou rouge, et
   pourquoi ? Ensuite, trois secondes après la fin, demande la commande à la main avec `curl` et lis `cobrado` et `movimientos`. À la fin,
   `rm copia.json`.
3. **La même clé sur une autre commande.** Avec `curl`, comme dans la leçon 06, et avec la boutique tout juste
   redémarrée : (1) connecte-toi en tant que Marta et garde le jeton dans `TOKEN` ; (2) mets un t-shirt dans le panier et
   passe la commande 1 ; (3) paie-la avec la clé `prueba-1` ; (4) mets un autre t-shirt, passe la commande 2 et, **avant
   de lancer la dernière commande**, prédis son code et pourquoi la boutique ne peut pas simplement l'approuver :

   ```bash
   curl -i -X POST http://localhost:8080/api/pedidos/2/pago \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: prueba-1' \
     -d '{"tarjeta":"4242 4242 4242 4242"}'
   ```

   Pour le point 3, utilise la même commande avec `pedidos/1`. Les autres sont celles de la leçon 06.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Dans la scène, qu'avaient en commun les deux erreurs que les tests de l'équipe n'ont pas vues ? (scène)
2. Pourquoi cette boutique répond-elle 404, et pas 403, quand une autre cliente demande ta commande ? (étape 3)
3. Que compare le test « prélevé égal au total », et pourquoi n'est-il pas écrit avec un montant fixe ? (étape 4)
4. Avec E4 activée et la passerelle normale, la collection est sortie verte. Pourquoi ? (étape 4)
5. Pourquoi le premier paiement accepte-t-il 200 ou 504, mais le nouvel essai seulement 200 ? (étape 5)

---

## Pour conclure

Les tests de la leçon 07 répondaient à « est-ce que ça marche ? ». Ceux de cette leçon répondent à une autre question :
« est-ce que ça marche **aussi** quand quelqu'un fait ce qu'il ne doit pas, ou le fait deux fois ? ». Ni la commande
d'autrui ni le double prélèvement ne se voient avec une cliente qui achète une fois et s'en va ; les deux apparaissent
dès qu'arrive une deuxième personne ou un deuxième essai.

Ce que tu en retires :

- **Chaque test important, encore une fois avec une autre personne.** Sans session, il doit dire 401 ; avec une autre
  cliente, ce que la boutique a décidé pour ce qui n'est pas à elle (ici, 404), et sans montrer la donnée.
- L'autre personne sort de l'**environnement**, comme la première : la collection ne porte pas de noms.
- **Chaque requête qui change quelque chose, deux fois.** Un paiement répété avec la même clé d'idempotence prélève une
  fois et répond la même chose.
- Vérifie l'**effet**, pas seulement le code : `cobrado` contre `total` dit combien a vraiment été prélevé.
- Certaines erreurs ne sortent que lorsque quelque chose échoue d'abord. Pour tester un nouvel essai, fais en sorte que le
  premier essai reste sans réponse.

Dans la leçon 09, le problème n'est plus qui ni combien de fois, mais **quand** : deux requêtes qui arrivent en même
temps, et la boutique à une seconde du changement de jour, de mois ou d'année.

---

## Compare tes réponses

**Étape 3, la prédiction.** 404, parce que dans cette boutique une commande d'autrui n'existe pas pour qui ne l'a pas
passée, et ainsi Luis ne découvre pas que la commande existe. 403 avec la raison « je sais qui tu es et je ne te laisse
pas faire » est aussi un raisonnement correct ; ce qui n'est pas correct, c'est 401, parce que Luis s'est bien connecté.

**Exercice 1.** **404** « cette commande n'existe pas », le même que pour la consultation : pour l'autre cliente, la
commande n'existe pas, ni pour la voir ni pour l'annuler. Le second test est nécessaire parce que le code dit ce que la
boutique a **répondu**, pas ce qu'elle a **fait** : une boutique pourrait répondre 404 et annuler quand même. C'est la
règle de la leçon 04 avec les cellules vides : vérifie le message et que la commande n'a pas bougé.

```json
    "pm.test('annuler celle d’autrui : code 404', () => pm.response.to.have.status(404));"
```

et dans « Où en est la commande » tu as déjà `commande payée`, qui deviendrait rouge si quelqu'un l'avait annulée.

**Exercice 2.** **Rouge**, même avec E4 désactivée : « nouvel essai : code 200 » échoue. « commande payée » et « prélevé
égal au total » sortent en vert, et trois secondes plus tard `cobrado` dit toujours **$432.00**. Mais la commande a
maintenant **trois mouvements** : deux prélèvements et un remboursement. Mesuré :

```text
premier paiement : 504 · nouvel essai avec une autre clé : 504 · sur le moment : pagado, prélevé $432.00, 1 prélèvement · 3 s après : prélevé $432.00, mouvements : cargo, cargo, reembolso
```

Avec une autre clé, la boutique n'a aucun moyen de savoir que c'est le même paiement : pour elle, ce sont deux, et la
passerelle a prélevé deux fois. Cette boutique s'en rend compte après coup, parce que le second prélèvement arrive sur une
commande déjà payée, et elle le rembourse toute seule (tu le verras dans la leçon 10). Pour le test, tout colle ; pour
Marta, non : son relevé montre deux prélèvements et un remboursement. Avec E4 activée, c'est pire : personne ne rembourse
le second prélèvement. L'erreur peut être dans la boutique **ou** chez celui qui l'appelle ; c'est pour ça que la clé,
c'est le client qui la génère une fois par paiement, et la répète à chaque essai.

**Exercice 3.** **422** « cette clé d'idempotence a déjà été utilisée pour une autre commande ». La boutique ne peut pas
l'approuver parce que la clé dit « je suis le paiement de la commande 1 », et elle arrive avec la commande 2 : soit c'est
une erreur du programme qui l'envoie, soit quelqu'un réutilise une vieille clé. Cette boutique répond 422 parce qu'elle a
déjà associé cette clé à une autre commande. Le brouillon de l'IETF sur cet en-tête, qui n'est pas encore un standard,
propose 422 quand une clé est réutilisée avec un corps différent ; la boutique applique la même idée à sa façon.

**Révision.**

1. Les deux avaient besoin d'une seconde fois : une seconde personne (Luis demandant une commande d'autrui) ou un second
   essai (Marta payant de nouveau). Les tests de l'équipe faisaient tout avec une cliente, une fois.
2. Parce qu'un 403 confirme à celui qui demande que la commande existe, et le 404 non. C'est une décision de cette
   boutique (d'autres API choisissent 403), et le test vérifie ce que la boutique a décidé.
3. Il compare ce que la passerelle a prélevé (`cobrado`) à ce que la cliente doit (`total`). Avec un montant fixe, le test
   ne servirait que pour une commande de $432.00 ; ainsi, il sert pour n'importe laquelle.
4. Parce qu'avec la passerelle rapide le premier paiement a bien eu une réponse, et le nouvel essai a reçu cette même
   réponse gardée. E4 ne casse que le chemin du nouvel essai après un 504.
5. Le premier peut rester sans réponse sans que ce soit une erreur : la passerelle tarde. Le nouvel essai, avec la même
   clé, doit finir en 200 quand la passerelle a réglé le paiement, sans second prélèvement.

---

## Sources de la leçon

1. OWASP, *API Security Top 10 2023*, « API1:2023 Broken Object Level Authorization » (dépôt OWASP/API-Security,
   consulté le 21 novembre 2026). C'est le premier risque de la liste : demander un objet qui n'est pas à soi en changeant
   son numéro. « Every API endpoint that receives an ID of an object, and performs any action on the object, should
   implement object-level authorization checks » ; « Write tests to evaluate the vulnerability of the authorization
   mechanism. Do not deploy changes that make the tests fail. »
   https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
2. IETF, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-09 (brouillon du 21 novembre
   2026 ; pas encore un standard publié). « Per [RFC9110], the methods OPTIONS, HEAD, GET, PUT and
   DELETE are idempotent while methods POST and PATCH are not » ; « The client is left uncertain about the status of the
   resource » ; « If there is an attempt to reuse an idempotency key with a different request payload, the resource
   SHOULD reply with an HTTP 422 status code ».
   https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
3. Stripe, *Idempotent requests* (documentation de son API, consultée le 21 novembre 2026). « if a connection
   error occurs, you can safely repeat the request without risk of creating a second object or performing the update
   twice » ; « Retries with the same key return the saved response » ; « we suggest using V4 UUIDs ».
   https://docs.stripe.com/api/idempotent_requests
4. Postman, *Use dynamic variables to return randomly generated data* (learning.postman.com, consulté le 21 novembre
   2026). « To use dynamic variables in pre-request or post-response scripts, use
   pm.variables.replaceIn() » ; « $guid A uuid-v4 style guid ».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/variables-list/

Mesure propre : chaque sortie de cette leçon a été mesurée avec curl et newman 6.2.2 contre la boutique du cours
(HabilMX/curso-qa) le 21 novembre 2026, avec son API lancée sans Docker et redémarrée à chaque lancement : la
collection complète avec Marta et avec Luis, avec la passerelle normale et avec la passerelle qui tarde 7 secondes (12 sur
12), avec E4 et la passerelle lente (2 rouges), avec E4 et la passerelle normale (12 sur 12), et les trois exercices. E5 a
été mesurée avec un prototype dans une copie de la boutique, pendant que la vraie se construit.

Règles du cours, sans source externe :

- « Chaque test important, encore une fois avec une autre personne » : l'erreur de permissions ne se voit pas avec la
  propriétaire de la donnée ; elle n'apparaît que lorsque quelqu'un d'autre demande.
- « Pour tester un nouvel essai, fais en sorte que le premier essai reste sans réponse » : avec la passerelle rapide, le
  double prélèvement ne se voit pas.
