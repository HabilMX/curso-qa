# Leçon 10 — Quand l'autre système tombe en panne

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Dépendance :** un autre système dont ton système a besoin pour finir son travail. La boutique ne prélève pas toute
  seule : elle demande le paiement à la **passerelle de paiement**, qui vit ailleurs.
- **Délai d'attente :** combien de temps un système attend la réponse d'un autre avant d'abandonner. La
  boutique d'entraînement attend **5 secondes** la passerelle.
- **Concilier :** comparer ce que dit la commande avec ce qui s'est passé avec l'argent, et corriger la différence.

**Ce que tu en retires :** une collection qui paie une commande puis vérifie que **l'état et l'argent concordent**. Elle
sort verte avec la passerelle qui approuve, qui refuse, qui ne répond pas ou qui tarde, et rouge quand un paiement
arrive en retard et que personne ne le concilie.

**Idée nouvelle de cette leçon (la seule) :** une dépendance lente est plus dangereuse qu'une dépendance en panne.

**Dans quel ordre :** tu montes une collection qui paie (étape 1) ; tu regardes comment la commande se retrouve quand la
passerelle dit non (étape 2) et quand elle ne répond pas (étape 3) ; tu la fais tarder et tu attends ce qu'elle met
(étape 4) ; et tu trouves la commande à moitié faite (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Un vendredi soir, la passerelle de paiement traverse un mauvais moment : parfois elle répond en une seconde et parfois
elle en met sept.

Le lundi, Marta écrit, fâchée. Le vendredi, elle a voulu acheter un t-shirt, la page lui a dit « nous ne savons pas si le
paiement a été prélevé », et elle a laissé tomber. Le lundi, elle a vu dans sa banque un prélèvement de $432.00. Dans la
boutique, sa commande est toujours « creado » : personne ne l'a emballée, parce que, pour la boutique, elle n'a jamais
été payée.

Les tests de l'équipe étaient verts. Ils testaient la passerelle qui approuve et la passerelle qui refuse, et dans les
deux la commande se retrouvait bien. Ils ne l'ont jamais testée **lente**.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans les leçons 07 à 09 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur
et, dans une autre fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.

> **Cette leçon utilise la boutique de la leçon 10.** Elle apporte l'erreur E7. Si `tienda error E7 on` te dit que cette
> erreur n'existe pas, mets ta boutique à jour avant de continuer : avec une version plus ancienne, tes sorties ne vont
> pas coïncider.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 07, `newman run`, `jq empty` et l'environnement `local`
(avec `base`, `cliente` et `contrasena`) ; de la 08, la clé d'idempotence, le 504 et `tienda pasarela` ; de la 09,
vérifier **l'effet** et pas seulement le code.

**Fais l'étape 3 sans IA.** Ce que tu entraînes là, c'est prédire ce qui arrive à une commande quand l'autre système ne
répond pas.

**Repars de zéro avant chaque lancement, et dans cet ordre :**

```bash
tienda reiniciar
tienda pasarela aprueba
```

```text
✅ la boutique est revenue à son état d'ouverture
💳 La passerelle approuve
```

`tienda reiniciar` remet la passerelle sur « approuve ». C'est pourquoi le mode de la passerelle se règle toujours
**après** le redémarrage ; dans l'autre sens, le redémarrage l'efface et le lancement sort avec la passerelle qui
approuve sans que tu t'en rendes compte.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Une collection qui paie

La passerelle d'entraînement a quatre modes, et la boutique a une commande pour chacun :

| Commande | Ce que fait la passerelle |
|---|---|
| `tienda pasarela aprueba` | Prélève et répond tout de suite |
| `tienda pasarela rechaza` | Répond tout de suite qu'elle n'a pas prélevé |
| `tienda pasarela no-contesta` | Ne répond pas pendant toute la durée de l'entraînement, et ne prélève pas |
| `tienda pasarela tarda 7` | Prélève, mais répond au bout de 7 secondes |

Pour tester les quatre, il te faut une collection qui paie. C'est un fichier nouveau ; celles des leçons 07 à 09 ne sont
pas touchées :

```bash
nano pasarela.postman_collection.json
```

```json
{
 "info": {
  "name": "Passerelle",
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
  },
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
    "pm.test('approuvé, refusé ou sans réponse', () => pm.expect(pm.response.code).to.be.oneOf([200, 402, 504]));"
   ]}}]
  }
 ]
}
```

Les trois premières requêtes sont celles de la leçon 08 : la cliente se connecte, met un t-shirt dans le panier et passe
sa commande, et on garde le numéro de la commande et une nouvelle clé d'idempotence. La nouveauté est dans « Elle paie » :
elle accepte **trois** réponses, parce que les trois sont honnêtes.

| Code | Ce que ça veut dire ici |
|---|---|
| 200 | La passerelle a prélevé |
| 402 | La passerelle a dit non : elle n'a pas prélevé |
| 504 | La passerelle n'a pas répondu en 5 secondes : **la boutique ne sait pas** si elle a prélevé |

Le 402 n'a pas de sens fixe en HTTP : la norme le laisse « réservé pour un usage futur ». Certaines API de paiement
l'utilisent pour les erreurs de paiement, et **cette boutique** l'utilise quand la passerelle dit non.

Vérifie que le JSON est bien écrit et lance-la :

```bash
jq empty pasarela.postman_collection.json
tienda reiniciar
tienda pasarela aprueba
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ La cliente se connecte
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 16ms]
  ✓  code 201

→ Un t-shirt au panier
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ Elle passe sa commande
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 2ms]
  ✓  code 201

→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 969B, 3ms]
  ✓  approuvé, refusé ou sans réponse
```

Quatre sur quatre. Les tailles et les temps des sorties de cette leçon sont ceux de la mesure ; les tiens peuvent
changer. Les codes, les coches et les rouges, non.

Elle vérifie déjà que le paiement a reçu l'une des trois réponses prévues. Comme « Elle paie » sort verte avec
n'importe lequel des quatre modes, il reste à vérifier ce qui compte vraiment : **comment la commande s'est terminée**.

---

## Étape 2 · Quand la passerelle dit non

Ajoute une cinquième requête à la fin, après « Elle paie » (avec une virgule entre les deux) :

```json
  {
   "name": "Où en est la commande",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "const pedido = pm.response.json();",
    "pm.test('pas prélevé en trop', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
    "pm.test('payée si et seulement si prélevée', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
   ]}}]
  }
```

Ce sont deux tests, et ils ne vérifient pas un cas : ils vérifient une **règle qui vaut dans les quatre modes de la
passerelle**, juste après avoir essayé de payer. (Plus tard, quand la commande est expédiée ou annulée, son état n'est
plus « pagado » ni « creado », et la règle serait une autre.)

| Test | Ce qu'il compare |
|---|---|
| `pas prélevé en trop` | Ce qui a été prélevé (`cobrado`) ne dépasse pas le total de la commande |
| `payée si et seulement si prélevée` | Deux questions par oui ou par non : « la commande dit-elle payée ? » et « le total a-t-il été prélevé ? ». Les deux réponses doivent être **égales** : oui et oui, ou non et non |

`cobrado`, tu le connais de la leçon 08 : c'est ce que la passerelle a vraiment prélevé sur la carte, remboursements déjà
déduits. On compare les **centimes**, qui sont des nombres, et pas le texte `$432.00`, parce que « au plus » ne se
demande que d'un nombre.

Lance-la avec la passerelle qui approuve, puis qui refuse :

```bash
tienda reiniciar
tienda pasarela rechaza
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [402 Payment Required, 257B, 3ms]
  ✓  approuvé, refusé ou sans réponse

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  pas prélevé en trop
  ✓  payée si et seulement si prélevée
```

Six sur six avec la passerelle qui approuve, et six sur six qui refuse. Avec la passerelle qui approuve, la commande se
retrouve **payée et prélevée** : oui et oui. Avec celle qui refuse, elle se retrouve **créée et non prélevée** : non et
non. Les deux réponses sont différentes et toutes deux sont bonnes, et un seul test les accepte toutes les deux.

---

## Étape 3 · Quand la passerelle ne répond pas

**Fais cette étape sans IA.** Avant de lancer, prédis : avec la passerelle qui ne répond pas, quel code reçoit « Elle
paie », et comment se retrouve la commande ? Écris-le.

```bash
tienda reiniciar
tienda pasarela no-contesta
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé, refusé ou sans réponse

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  pas prélevé en trop
  ✓  payée si et seulement si prélevée
```

**504 au bout de 5 secondes.** C'est le délai d'attente de la boutique : elle a patienté 5 secondes et a abandonné. Un 504
veut dire exactement cela : le serveur, qui faisait l'intermédiaire, n'a pas reçu à temps la réponse de l'autre système
dont il avait besoin. Dans le corps, la boutique le dit avec ses mots : « la passerelle n'a pas répondu à temps ; nous ne
savons pas si le paiement a été prélevé. Réessaie avec la même clé d'idempotence ».

Et la commande s'est retrouvée **créée et non prélevée** : non et non, vert. Dans **ce mode d'entraînement**, la
passerelle qui ne répond pas ne prélève pas non plus, donc la commande ne ment pas. Mais Marta ne peut pas encore le
savoir : elle voit seulement un 504 qui dit « nous ne savons pas si le paiement a été prélevé ». C'est pourquoi la
boutique lui demande de réessayer **avec la même clé**, pas avec une nouvelle.

Regarde le « nous ne savons pas ». À la seconde 5, la boutique ne peut pas distinguer une passerelle qui ne répondra
jamais d'une qui répondra à la seconde 7. C'est pourquoi elle dit « nous ne savons pas » et pas « le paiement n'a pas été
prélevé ». Un délai d'attente écoulé ne te dit pas que rien ne s'est passé.

> Si tu réessaies avec la même clé pendant que la passerelle ne répond toujours pas, tu reçois de nouveau un 504 au bout
> de 5 secondes : la boutique attend toujours le **même** paiement, comme dans la leçon 08. Pour continuer la leçon,
> `tienda reiniciar`.

---

## Étape 4 · Quand la passerelle tarde

Maintenant la passerelle prélève **bien**, mais elle met 7 secondes à répondre. La boutique ne l'attend que 5.

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé, refusé ou sans réponse

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 675B, 2ms]
  ✓  pas prélevé en trop
  ✓  payée si et seulement si prélevée
```

Vert, et avec la **même** taille de réponse que lorsque la passerelle ne répondait pas : la commande était créée et non
prélevée. Mais cette fois la passerelle allait prélever. Quand ?

Fais le calcul avec la ligne de temps de ce lancement :

| Seconde | Ce qui se passe |
|---|---|
| 0 | « Elle paie » part vers la boutique, et la boutique demande le paiement à la passerelle |
| 5 | La boutique se lasse d'attendre et répond 504. Newman passe aussitôt à « Où en est la commande » |
| 5 | La commande est encore créée et non prélevée : le test sort vert |
| 7 | La passerelle termine : elle **prélève** $432.00 |

Ton test a vérifié la commande **deux secondes avant** que le paiement n'arrive. Il a vérifié à temps pour la boutique,
mais pas pour la passerelle.

Pour voir ce qui se passe à la seconde 7, le test doit **attendre ce que la passerelle met**. La passerelle met 7
secondes et la boutique a déjà attendu 5 : il en manque 2. On attend 5 : les 2 qui manquent et 3 de marge.

Dans « Où en est la commande », **remplace en entier** le `"event": [ … ]` que tu as collé à l'étape 2 par ce bloc. Il
contient les mêmes tests, et avant eux un nouvel événement qui s'exécute **avant** d'envoyer la requête (`prerequest`). Ne
laisse pas deux `"event"` dans la même requête. Les virgules ne changent pas : il y en a une entre « Elle paie » et « Où
en est la commande », et aucune après « Où en est la commande », parce que c'est la dernière :

```json
   "event": [
    {"listen": "prerequest", "script": {"exec": [
     "setTimeout(() => {}, 5000);"
    ]}},
    {"listen": "test", "script": {"exec": [
     "const pedido = pm.response.json();",
     "pm.test('pas prélevé en trop', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
     "pm.test('payée si et seulement si prélevée', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
    ]}}
   ]
```

| Ligne | Ce qu'elle fait |
|---|---|
| `"listen": "prerequest"` | Ce script s'exécute avant d'envoyer la requête ; celui de `"test"` s'exécute après avoir reçu la réponse |
| `setTimeout(() => {}, 5000)` | Programme « ne rien faire » pour 5000 millisecondes. Newman n'envoie pas la requête avant que cela se termine, donc il attend 5 secondes |

Ces 5 secondes **ne sont pas un nombre magique**, et ce ne sont pas les 7 de la passerelle : l'attente commence quand la
boutique a déjà attendu 5. Elles couvrent les 2 secondes qu'il manque à la passerelle, plus 3 de marge. Si la
passerelle mettait 12, tu referais le calcul à partir de la seconde 5. Une attente sans raison donne un test lent dont tu
ne sais même pas s'il suffit.

Lance-la de nouveau, avec la passerelle qui tarde :

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé, refusé ou sans réponse

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 880B, 5ms]
  ✓  pas prélevé en trop
  ✓  payée si et seulement si prélevée
```

Vert de nouveau, mais maintenant la réponse est plus grosse : 880B. La commande porte un mouvement, le prélèvement de
$432.00, et dit **pagado**. Quand le paiement est arrivé à la seconde 7, la boutique l'a **concilié** : elle a vu que le
prélèvement appartenait à une commande créée et l'a fait passer à payée. Oui et oui.

Beaucoup de vrais systèmes fonctionnent de façon proche : la passerelle prévient après, quand le paiement se termine (par
exemple avec un *webhook*, un avis que la passerelle envoie à la boutique), et la boutique décide à ce moment ce qu'elle
fait de la commande. En production, une réponse qui n'est pas arrivée à temps est traitée comme incertaine jusqu'à ce
qu'on la concilie, qu'elle arrive en retard ou qu'elle ne réponde pas du tout.

Avant de continuer, vérifie que l'attente n'a pas cassé ce que tu avais : avec `aprueba`, `rechaza` et `no-contesta`, la
collection sort six sur six les trois fois. Maintenant chaque lancement met environ 5 secondes de plus, et 10 avec
`no-contesta`.

---

## Étape 5 · La commande à moitié faite

Active E7 et lance avec la passerelle qui tarde :

```bash
tienda reiniciar
tienda error E7 on
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle paie
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 359B, 5s]
  ✓  approuvé, refusé ou sans réponse

→ Où en est la commande
  GET http://localhost:8080/api/pedidos/1 [200 OK, 816B, 6ms]
  ✓  pas prélevé en trop
  1. payée si et seulement si prélevée
```

```text
  #  failure         detail

 1.  AssertionError  payée si et seulement si prélevée
                     expected false to deeply equal true
```

Un rouge. `expected false to deeply equal true` se lit à l'envers de la façon dont le test est écrit : « la commande
dit-elle payée ? » a donné **non** (`false`), et « le total a-t-il été prélevé ? » a donné **oui** (`true`). Ça ne
concorde pas.

Regarde la commande avec `curl`, comme dans la leçon 06 (avec la boutique toujours dans cet état, sans redémarrer) :

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

```text
{"estado":"creado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

Voilà la scène de Marta : **prélevée et créée**. Le paiement est arrivé à la seconde 7 et la boutique **l'a noté** (il est
là, dans `movimientos`), mais avec E7 elle ne le concilie pas : elle laisse la commande comme elle était, sans prévenir
personne. Et elle reste ainsi. Personne ne va l'emballer, parce que, pour l'entrepôt, elle n'a pas été payée.

Compare les trois passerelles qui n'ont pas répondu à temps :

| Passerelle | Ce que la cliente a vu | La commande |
|---|---|---|
| Ne répond pas | 504, « nous ne savons pas si le paiement a été prélevé » | Créée et non prélevée : elle n'a pas acheté, et elle n'a pas perdu d'argent |
| Tarde 7, boutique propre | 504, « nous ne savons pas si le paiement a été prélevé » | Payée et prélevée : elle a acheté |
| Tarde 7, avec E7 | 504, « nous ne savons pas si le paiement a été prélevé » | **Créée et prélevée** : elle a payé et n'a pas acheté |

La cliente a vu **la même chose** dans les trois cas. Ce qui change, c'est ce qui s'est passé après que la boutique a
cessé d'attendre. Dans cet entraînement, la passerelle en panne est la plus facile : elle ne prélève pas, et la commande
ne ment pas. La lente prélève quand plus personne ne l'attend, et quelqu'un doit se charger de ce paiement.

C'est pourquoi une dépendance lente est plus dangereuse qu'une dépendance en panne. Et pas seulement à cause de
l'argent : celui qui reste à attendre un système qui ne répond pas reste aussi occupé, et s'ils sont nombreux à attendre,
c'est celui qui attendait qui tombe.

Désactive E7 avant de continuer :

```bash
tienda error E7 off
tienda reiniciar
```

---

## Comment on vérifie

**Ta collection** est contrôlée par `verifica 10`. Enregistre-la dans `~/practica` sous le nom
`pasarela.postman_collection.json`, avec ton environnement `local.postman_environment.json`, et, dans le terminal de la
boutique, écris :

```bash
verifica 10
```

Le `verifica` :

1. lance ta collection avec la boutique propre quatre fois : avec la passerelle qui approuve, qui refuse, qui ne répond
   pas et qui tarde 7 secondes : les quatre fois, elle doit sortir **verte** ;
2. la lance avec E7 activée et la passerelle qui tarde 7 secondes : **au moins un test doit sortir rouge** ; s'il sort
   vert, ta collection ne compare pas l'état de la commande avec ce qui a été prélevé après avoir attendu la passerelle ;
3. vérifie que ta collection n'a pas écrit à la main l'adresse, `Marta` ni son mot de passe.

S'il manque quelque chose, il te dit quoi corriger. Il change la passerelle et active et désactive E7 tout seul. À la
fin, il laisse activées les erreurs que tu avais activées et la passerelle qui approuve, mais il réinitialise la
boutique : il efface tes commandes, ton panier et ta session. Il met moins d'une minute. Avant de l'exécuter, la liste
ci-dessous te dit si la forme est bonne.

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] Ta collection a cinq requêtes, dans l'ordre des étapes 1 et 2.
- [ ] « Elle paie » accepte 200, 402 et 504.
- [ ] « Où en est la commande » attend 5 secondes avant de s'envoyer et a les deux tests de l'étape 2.
- [ ] Avec la boutique propre, elle sort 6 sur 6 avec `aprueba`, `rechaza`, `no-contesta` et `tarda 7`.
- [ ] Avec E7 activée et `tarda 7`, « payée si et seulement si prélevée » échoue.
- [ ] Dans ta collection n'apparaissent ni `localhost`, ni `Marta`, ni le mot de passe (cherche-les avec
      `grep -n -e localhost -e Marta -e practica pasarela.postman_collection.json` ; il ne doit rien afficher).
- [ ] Tu as laissé E7 désactivée et la passerelle qui approuve (`tienda error estado` et `tienda pasarela aprueba`).

---

## Tes exercices

1. **Deux paiements, deux clés.** Fais une copie de ta collection
   (`cp pasarela.postman_collection.json dos-llaves.postman_collection.json`) et, dans la copie, duplique la requête
   « Elle paie » juste en dessous. Donne à la copie le nom « Elle paie à nouveau, avec une autre clé » et, dans son
   en-tête `Idempotency-Key`, remplace `{{llave}}` par `{{$guid}}` : ainsi chaque essai porte une clé neuve, comme
   l'exercice 2 de la leçon 08. Lance-la avec la passerelle qui tarde 7 secondes, d'abord avec la boutique propre puis
   avec E7. Prédis : verte ou rouge dans chaque cas ? Et dans la boutique propre, combien de mouvements a la commande ?
   Vérifie-le avec le `curl` de l'étape 5. À la fin, `rm dos-llaves.postman_collection.json`.
2. **Lente, mais à temps.** Avec la boutique propre et `tienda pasarela tarda 3`, quel code reçoit « Elle paie », et au
   bout de combien de secondes ? Comment se retrouve la commande ? Prédis et lance.
3. **Qui est au courant** (sans IA). Pour chaque ligne, écris ce que Marta voit sur la page et qui apprend qu'il y a un
   problème : Marta, la boutique ou personne.

   | Cas | Ce que Marta voit | Qui est au courant |
   |---|---|---|
   | La passerelle refuse | | |
   | La passerelle ne répond pas | | |
   | La passerelle tarde 7, boutique propre | | |
   | La passerelle tarde 7, avec E7 | | |

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Dans la scène, pourquoi les tests de l'équipe n'ont-ils pas vu le problème de Marta ? (scène)
2. Pourquoi « Elle paie » accepte-t-elle le 504 comme une bonne réponse ? (étapes 1 et 3)
3. Que veut dire que la commande sorte « non et non » dans le test « payée si et seulement si prélevée » ? (étape 2)
4. Pourquoi la collection attendait-elle 5 secondes et pas 1, ni 30 ? (étape 4)
5. Pourquoi une passerelle lente est-elle plus dangereuse qu'une passerelle en panne ? (étape 5)

---

## Pour conclure

Dans la leçon 08, tu as déjà utilisé la passerelle lente, pour qu'un nouvel essai ne prélève pas deux fois. Cette leçon
regarde l'autre moitié du problème : ce qui arrive à la commande **après** le 504, même si personne ne réessaie, quand la
boutique dépend d'**un autre système** et que ce système dit non, ne répond pas ou répond en retard.

Ce que tu en retires :

- **Un 504 ne te dit pas ce qui s'est passé.** Il te dit que quelqu'un a cessé d'attendre. Ce qui compte, c'est ce qui
  s'est passé après.
- **Un test vérifie que l'état et l'argent concordent, pas seulement le code.** Une seule règle, « payée si et seulement
  si prélevée », vaut avec la passerelle qui approuve, qui refuse, qui ne répond pas ou qui tarde.
- **L'attente d'un test a une raison :** ce que met l'autre système, plus une marge. Une attente plus courte laisse
  passer l'erreur : avec E7, ta collection sans attente sort verte.
- **Une dépendance lente est plus dangereuse qu'une dépendance en panne.** Dans cet entraînement, celle qui est en panne
  ne prélève pas ; la lente prélève quand plus personne ne l'attend, et quelqu'un doit concilier.

Dans la leçon 11, tu quittes le terminal et tu testes la page comme Marta l'utilise, dans un navigateur.

---

## Compare tes réponses

**Étape 3, la prédiction.** **504 au bout de 5 secondes**, et la commande **créée et non prélevée** : vert. Si tu as prédit
que la boutique allait attendre indéfiniment, c'est un bon raisonnement : elle attendrait, si elle n'avait pas de délai
d'attente. C'est son travail : abandonner à temps et dire « nous ne savons pas ».

**Exercice 1.** Avec la boutique propre, **vert**. Les deux paiements reçoivent 504, et les deux prélèvements arrivent :
la commande a **trois mouvements**, deux prélèvements et un remboursement, et dit payée avec $432.00. Mesuré :

```text
{"estado":"pagado","cobrado":"$432.00","movimientos":["cargo $432.00","cargo $432.00","reembolso $432.00"]}
```

Le premier prélèvement a payé la commande ; le second est arrivé sur une commande déjà payée, et la boutique l'a
remboursé toute seule. Pour le test, tout concorde, parce que `cobrado` déduit déjà le remboursement. Pour Marta, non :
dans sa banque, elle voit deux prélèvements et un remboursement. C'est pourquoi la clé se répète à chaque essai, comme
dans la leçon 08 : avec la même clé, il n'y a qu'un seul prélèvement.

Avec E7, **rouge** : « pas prélevé en trop » échoue, `expected 86400 to be at most 43200`. La commande reste créée avec
$864.00 et deux prélèvements, et personne ne rembourse rien. « Payée si et seulement si prélevée » sort verte, parce que
ce n'est pas **le total** qui a été prélevé : c'est le double. C'est pourquoi il y a deux tests et pas un.

**Exercice 2.** **200 au bout de 3 secondes**, et la commande payée avec $432.00 : six sur six. La passerelle a mis moins
que le délai d'attente de la boutique, donc la boutique a reçu la réponse. Lente n'est pas la même chose que hors délai :
le problème commence quand la passerelle met plus que ce que la boutique attend.

**Exercice 3.**

| Cas | Ce que Marta voit | Qui est au courant |
|---|---|---|
| La passerelle refuse | 402, « la passerelle a refusé le paiement » | Marta, sur le moment : elle sait qu'elle n'a pas payé |
| La passerelle ne répond pas | 504, « nous ne savons pas si le paiement a été prélevé » | Marta sait qu'elle n'a pas de confirmation. Dans ce mode d'entraînement, aucun prélèvement n'arrive, donc il n'y a rien à concilier |
| La passerelle tarde 7, boutique propre | 504, « nous ne savons pas si le paiement a été prélevé » | La boutique : elle concilie le paiement quand il arrive, et la commande suit son chemin |
| La passerelle tarde 7, avec E7 | 504, « nous ne savons pas si le paiement a été prélevé » | **Personne, de lui-même.** La boutique a noté le prélèvement, mais n'a pas fait passer la commande à payée ni prévenu personne. Marta le voit des jours après dans sa banque ; l'équipe le trouverait en conciliant les mouvements avec les commandes |

La dernière ligne, c'est la scène. La passerelle a terminé le paiement et la boutique l'a noté, mais l'erreur a cessé de
le relier à l'état de la commande : la donnée était là, et personne ne l'a regardée.

**Révision.**

1. Parce qu'ils testaient la passerelle qui approuve et qui refuse, qui répondent tout de suite. Ils ne l'ont jamais
   testée **lente**, c'est-à-dire quand le paiement arrive après que la boutique a cessé d'attendre.
2. Parce qu'un 504 est une réponse honnête : la boutique dit qu'elle ne sait pas. Le test de « Elle paie » ne décide pas
   si le paiement s'est bien passé ; c'est « Où en est la commande » qui le décide.
3. Que la commande ne dit pas payée **et** n'a pas été prélevée : la cliente n'a pas acheté et n'a pas perdu d'argent.
   C'est ce qui se passe quand la passerelle refuse ou ne répond pas, et c'est bien.
4. Parce que la passerelle met 7 secondes et que la boutique a déjà attendu 5 : il en manque 2, et les 3 autres sont de la
   marge. Avec 1, le test arriverait avant le paiement ; avec 30, il serait lent sans rien gagner.
5. Parce que, dans cet entraînement, celle qui est en panne ne prélève pas : la commande reste non payée et non prélevée,
   et elle ne ment pas. La lente prélève quand plus personne ne l'attend, et si personne ne concilie, la commande reste
   prélevée et non payée.

---

## Sources de la leçon

1. IETF, RFC 9110, *HTTP Semantics* (2022), §15.6.5 et §15.5.3 (consulté le 22 novembre 2026). « The 504
   (Gateway Timeout) status code indicates that the server, while acting as a gateway or proxy, did not receive a
   timely response from an upstream server it needed to access in order to complete the request. » ; « The 402 (Payment
   Required) status code is reserved for future use. »
   https://www.rfc-editor.org/rfc/rfc9110
2. Amazon, *Builders' Library*, « Timeouts, retries, and backoff with jitter » (consulté le 22 novembre 2026).
   « A timeout or failure doesn't necessarily mean that side effects haven't happened. » ; « In general, our view is that
   APIs with side effects aren't safe to retry unless they provide idempotency. »
   https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
3. Martin Fowler, « CircuitBreaker » (consulté le 22 novembre 2026). « remote calls can fail, or hang without a
   response until some timeout limit is reached » ; « if you have many callers on a unresponsive supplier, then you can
   run out of critical resources leading to cascading failures across multiple systems ».
   https://martinfowler.com/bliki/CircuitBreaker.html
4. Stripe, *API Reference*, « Idempotent requests » (consultée le 22 novembre 2026). « Retries with the same key
   return the saved response, including 500 errors. »
   https://docs.stripe.com/api/idempotent_requests
5. Stripe, « Verificar el estado de un PaymentIntent » (version en espagnol de Stripe ; consulté le 22 novembre 2026).
   « Stripe puede enviar
   eventos de webhook a tu servidor a fin de notificarte cuando cambie el estado de un PaymentIntent, que puedes usar
   para, por ejemplo, determinar cuándo entregar bienes y servicios. »
   https://docs.stripe.com/payments/payment-intents/verifying-status
6. Stripe, « Errores » (consulté le 22 novembre 2026). « 402 Error en la solicitud Los parámetros eran válidos,
   pero se produjo un error en la solicitud ».
   https://docs.stripe.com/error-low-level
7. Postman, `postman-sandbox`, CHANGELOG (consulté le 22 novembre 2026). « GH-106 Support for timers inside
   sandbox (not in browser) ».
   https://github.com/postmanlabs/postman-sandbox/blob/develop/CHANGELOG.yaml

Mesure propre : chaque sortie de cette leçon a été mesurée avec curl et newman 6.2.2 le 22 novembre 2026, avec l'API de
la boutique lancée sans Docker et redémarrée avant chaque lancement, contre la boutique du cours (HabilMX/curso-qa) : les quatre modes de la passerelle, E7, l'attente de 5 secondes (sans elle, la collection sort verte avec E7)
et les trois exercices.

Règles du cours, sans source externe :

- « Un test vérifie que l'état et l'argent concordent, pas seulement le code » : le 504 est le même avec la passerelle
  en panne et avec la lente ; ce qui change, c'est ce qui se passe après.
- « L'attente d'un test a une raison » : on attend ce que met l'autre système, avec une marge. Une attente plus courte
  laisse passer l'erreur (mesuré).
- « Une dépendance lente est plus dangereuse qu'une dépendance en panne » : celle qui est en panne ne prélève pas ; la
  lente prélève quand plus personne ne l'attend.
