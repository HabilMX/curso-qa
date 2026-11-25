# Leçon 09 — En même temps et à des heures indues

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **En parallèle :** deux requêtes qui partent ensemble, sans que l'une attende que l'autre se termine.
- **Situation de concurrence :** une erreur qui n'apparaît que lorsque deux choses se passent presque en même temps et
  que l'une se glisse au milieu de l'autre.
- **Fuseau horaire :** la différence entre l'heure d'un lieu et l'heure UTC, l'heure de référence du monde. La boutique
  d'entraînement écrit la sienne à la fin de chaque heure : `-06:00`, six heures derrière UTC.

**Ce que tu en retires :** un script de terminal qui paie deux commandes en même temps et une collection qui vérifie la
date d'une commande contre l'heure de la boutique. Les deux sortent verts quand la boutique va bien et rouges quand le
coupon est utilisé deux fois ou quand la commande se retrouve avec le mauvais jour, le mauvais mois ou la mauvaise année.

**Idée nouvelle de cette leçon (la seule) :** ce qu'une personne fait une chose à la fois, le système le reçoit en
parallèle et à n'importe quelle heure.

**Dans quel ordre :** tu paies deux commandes avec le même coupon, l'une après l'autre (étape 1) et en même temps
(étape 2) ; tu répètes le script pour voir que le résultat ne change pas (étape 3) ; tu déplaces l'horloge de la boutique
(étape 4) et tu testes la date d'une commande à midi et à des heures indues (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Le 1er janvier au matin, l'équipe de la boutique examine deux choses bizarres.

La première : une cliente a utilisé le coupon BIENVENIDA10 sur **deux** commandes. Le coupon est à usage unique, et le
test de l'équipe le confirmait : il payait une commande avec le coupon, puis l'autre, et la seconde sortait refusée. La
cliente n'avait rien fait d'étrange. Elle avait la boutique ouverte sur son téléphone et sur son ordinateur, et elle
avait appuyé sur « Payer » sur les deux presque en même temps.

La seconde : le rapport des ventes de décembre ne tombe pas juste. Les commandes de la nuit du 31, à partir de six heures
du soir, apparaissent comme des ventes de **janvier de l'année suivante**.

Les tests de l'équipe étaient verts. Tous lançaient une requête à la fois, et tous tournaient à midi.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans les leçons 07 et 08 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur
et, dans une autre fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.

> **Cette leçon utilise la boutique de la leçon 09.** Elle apporte l'erreur E2 « coupon deux fois » et l'erreur E6
> « date en UTC ». Si `tienda error E6 on` te dit que cette erreur n'existe pas, mets ta boutique à jour avant de
> continuer : avec une version plus ancienne, tes sorties ne vont pas coïncider.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 06, `curl` avec `-X`, `-H` et `-d`, et le jeton dans une
variable ; de la 07, `newman run`, `jq empty` et l'environnement `local` ; de la 08, `pm.collectionVariables` et comparer
une valeur contre une autre de la boutique elle-même ; de la 01, la règle R4 : le coupon expire le 31 décembre à 23:59,
heure de Mexico.

**Fais l'étape 1 sans IA.** Ce que tu entraînes là, c'est prédire ce qui se passe avec une erreur que tu ne vois pas
encore.

**Repars de zéro avant chaque lancement :**

```bash
tienda reiniciar
```

```text
✅ la boutique est revenue à son état d'ouverture
```

`tienda reiniciar` remet aussi l'horloge de la boutique à l'heure réelle. Si, à l'étape 4 ou 5, tu veux une autre heure,
tu la règles **après** avoir redémarré.

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Deux commandes avec le même coupon, l'une après l'autre

BIENVENIDA10 est à usage unique par cliente. La boutique ne le vérifie pas seulement quand on l'applique au panier : elle
le vérifie de nouveau au moment de **payer**, parce qu'une cliente peut avoir le coupon sur deux commandes qu'elle n'a
pas encore payées.

Tu vas écrire un script : un fichier avec des commandes de terminal qui s'exécutent dans l'ordre, comme si tu les tapais
une par une. Ainsi tu peux le répéter avec une seule commande.

```bash
nano al-mismo-tiempo.sh
```

```bash
#!/bin/bash
# Deux commandes avec le même coupon, payées en même temps. Se termine par 0 si le coupon a été utilisé une fois et par 1 s'il l'a été deux.
BASE=http://localhost:8080
CLIENTE=Marta
CONTRASENA=marta-practica

TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)

pedido_con_cupon() {
  curl -s -o /dev/null -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"cantidad":2}'
  curl -s -o /dev/null -X POST $BASE/api/carrito/cupon -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
  curl -s -X POST $BASE/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r 'select(.cupon == "BIENVENIDA10") | .id'
}

pagar() {
  curl -s -o /dev/null -w "paiement de la commande $1 : %{http_code}\n" -X POST $BASE/api/pedidos/$1/pago \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: al-mismo-tiempo-$1-$$" -d '{"tarjeta":"4242 4242 4242 4242"}'
}

UNO=$(pedido_con_cupon)
DOS=$(pedido_con_cupon)
if [ -z "$UNO" ] || [ -z "$DOS" ]; then
  echo "Je n'ai pas pu passer les deux commandes avec le coupon. Lance tienda reiniciar et réessaie."
  exit 2
fi

pagar $UNO
pagar $DOS

PAGADOS=0
for P in $UNO $DOS; do
  ESTADO=$(curl -s $BASE/api/pedidos/$P -H "Authorization: Bearer $TOKEN" | jq -r .estado)
  echo "commande $P : $ESTADO"
  if [ "$ESTADO" = "pagado" ]; then PAGADOS=$((PAGADOS + 1)); fi
done

if [ $PAGADOS -eq 2 ]; then
  echo "ROUGE : le coupon a été utilisé deux fois"
  exit 1
fi
if [ $PAGADOS -ne 1 ]; then
  echo "Je n'ai pas pu le vérifier : aucune commande n'est restée payée. La boutique est-elle démarrée ?"
  exit 2
fi
echo "VERT : le coupon n'a été utilisé qu'une seule fois"
```

Ça a l'air long, mais ce sont les mêmes requêtes que dans la leçon 06, avec trois choses nouvelles :

| Partie | Ce qu'elle fait |
|---|---|
| `TOKEN=$(curl … \| jq -r .token)` | Se connecte et garde le jeton, sans que tu aies à le copier à la main. `jq -r .token` sort le champ `token` de la réponse |
| `pedido_con_cupon() { … }` et `pagar() { … }` | Ce sont des **fonctions** : un groupe de commandes avec un nom. `pedido_con_cupon` met deux t-shirts dans le panier, applique le coupon, passe la commande et écrit son numéro seulement si la commande porte bien le coupon. `pagar 1` paie la commande 1 et écrit le code que la boutique a répondu |
| `exit 0`, `exit 1`, `exit 2` | Le **code de sortie** du script, comme celui de newman dans la leçon 07 : 0 si le coupon a été utilisé une fois, 1 s'il l'a été deux fois, et 2 s'il n'a pas pu vérifier (il n'a pas passé les commandes, ou aucune n'est restée payée). Ainsi un problème de connexion ne sort jamais comme vert. À la fin, pas besoin de `exit 0` : un script qui arrive au bout sans erreur se termine par 0 |

La clé d'idempotence porte `$$`, le numéro du processus qui exécute le script : il change à chaque lancement, donc chaque
paiement a sa propre clé, comme le demande la leçon 08.

Enregistre et vérifie que bash peut le lire :

```bash
bash -n al-mismo-tiempo.sh
```

S'il n'affiche rien, le fichier est bien écrit. S'il affiche une ligne, elle te donne le numéro de la ligne qui pose
problème : ouvre-le dans nano et relis-la ; c'est presque toujours un guillemet ou une accolade qui manque.

Donne-lui la permission de s'exécuter (une seule fois) et lance-le :

```bash
chmod +x al-mismo-tiempo.sh
tienda reiniciar
./al-mismo-tiempo.sh
echo "sortie : $?"
```

```text
paiement de la commande 1 : 200
paiement de la commande 2 : 422
commande 1 : pagado
commande 2 : creado
VERT : le coupon n'a été utilisé qu'une seule fois
sortie : 0
```

Le premier paiement passe avec le coupon ; le second reçoit 422, « ce coupon a déjà été utilisé », et cette commande
reste impayée. La boutique va bien.

**Maintenant, prédis, sur papier :** tu vas activer E2, l'erreur « coupon deux fois », et lancer le même script. Vert ou
rouge ? Écris ta prédiction avant de continuer.

```bash
tienda error E2 on
tienda reiniciar
./al-mismo-tiempo.sh
echo "sortie : $?"
```

```text
paiement de la commande 1 : 200
paiement de la commande 2 : 422
commande 1 : pagado
commande 2 : creado
VERT : le coupon n'a été utilisé qu'une seule fois
sortie : 0
```

Vert, avec l'erreur activée. Si tu as prédit rouge, ton raisonnement tenait la route : l'erreur s'appelle « coupon deux
fois » et le script utilise le coupon deux fois. Mais les deux paiements vont **l'un après l'autre** : quand le second
arrive, le premier a déjà noté que le coupon a été utilisé, et la boutique le refuse. C'est ainsi qu'une personne teste, et
c'est ainsi que testait l'équipe de la scène. L'erreur est là et ce test ne la voit pas.

---

## Étape 2 · Les deux paiements en même temps

La cliente de la scène n'a pas payé l'un après l'autre : elle a appuyé sur « Payer » sur deux écrans presque en même
temps. Pour la boutique, ce sont deux requêtes **en parallèle**.

Dans le terminal, `&` à la fin d'une commande l'envoie **en arrière-plan** : le terminal n'attend pas qu'elle se termine
et passe tout de suite à la suivante. `wait` attend que se terminent toutes celles que tu as envoyées en arrière-plan.
Ouvre le script :

```bash
nano al-mismo-tiempo.sh
```

et remplace ces deux lignes :

```bash
pagar $UNO
pagar $DOS
```

par ces trois-ci :

```bash
pagar $UNO &
pagar $DOS &
wait
```

Rien de plus. Avec E2 toujours activée :

```bash
tienda reiniciar
./al-mismo-tiempo.sh
echo "sortie : $?"
```

```text
paiement de la commande 1 : 200
paiement de la commande 2 : 200
commande 1 : pagado
commande 2 : pagado
ROUGE : le coupon a été utilisé deux fois
sortie : 1
```

Voilà la scène : deux commandes payées avec le même coupon à usage unique.

**Que s'est-il passé à l'intérieur ?** Avec E2, la boutique **vérifie** si le coupon a déjà été utilisé et, un instant plus
tard, **note** qu'il l'a été, sans vérifier de nouveau. Entre vérifier et noter, il y a une **fenêtre**. Si le second
paiement vérifie dans cette fenêtre, le premier n'a encore rien noté : les deux voient le coupon libre et les deux passent
au prélèvement. L'un après l'autre, le second arrive toujours quand la fenêtre est déjà fermée ; en même temps, il tombe
dedans.

Désactive E2 et lance pareil, avec les paiements en parallèle :

```bash
tienda error E2 off
tienda reiniciar
./al-mismo-tiempo.sh
echo "sortie : $?"
```

```text
paiement de la commande 1 : 200
paiement de la commande 2 : 422
commande 1 : pagado
commande 2 : creado
VERT : le coupon n'a été utilisé qu'une seule fois
sortie : 0
```

Avec la boutique en bon état, même en même temps, un seul paiement emporte le coupon. Parfois le 200 revient à la
commande 2 et le 422 à la 1, et les deux lignes « paiement de la commande » sortent dans un autre ordre : les deux
paiements tournent en même temps et n'importe lequel peut finir en premier. Le résultat est le même.

---

## Étape 3 · Le même résultat à chaque fois

Un test de quelque chose qui se passe « en même temps » a un risque : qu'il attrape parfois l'erreur et parfois non,
selon qui arrive le premier. Avec un test comme ça, un vert isolé ne suffit pas encore pour faire confiance. Avant de faire
confiance à ton script, lance-le plusieurs fois de suite.

Avec E2 activée, cinq fois :

```bash
tienda error E2 on
for i in 1 2 3 4 5; do tienda reiniciar > /dev/null; ./al-mismo-tiempo.sh > /dev/null; echo "sortie : $?"; done
```

```text
sortie : 1
sortie : 1
sortie : 1
sortie : 1
sortie : 1
```

| Partie | Ce qu'elle fait |
|---|---|
| `for i in 1 2 3 4 5; do …; done` | Répète ce qui est au milieu cinq fois |
| `> /dev/null` | Jette la sortie normale de cette commande, pour que tu ne voies que ce qui compte |

Cinq sur cinq en rouge. Maintenant avec E2 désactivée : il doit sortir cinq `sortie : 0`. Cette boutique est faite pour que
la course soit répétable : les deux paiements partent ensemble et tombent toujours dans la fenêtre. Dans une vraie
boutique, la fenêtre peut durer quelques millièmes de seconde, et là il peut te falloir beaucoup plus d'essais ; l'idée
est la même.

Désactive E2 :

```bash
tienda error E2 off
```

---

## Étape 4 · L'heure de la boutique

L'autre erreur de la scène ne dépend pas de **comment** les requêtes arrivent, mais de **quand**. Pour tester la nuit du 31
décembre, tu n'as pas à attendre le 31 décembre : la boutique a sa propre horloge et c'est toi qui la déplaces.

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
```

```text
🕒 Heure de la boutique : 2026-12-31T23:30:00-06:00
```

À partir de là, l'horloge continue de tourner, comme une vraie : une minute plus tard, elle dira 23:31.

L'heure s'écrit comme dans les réponses de la boutique : année-mois-jour, un `T` et l'heure. Le `-06:00` à la fin est le
**fuseau** : la boutique est six heures derrière UTC. La boutique te le dit aussi dans `GET /api/salud` :

```bash
curl -s http://localhost:8080/api/salud
```

```json
{"estado":"arriba","hora_de_la_tienda":"2026-12-31T23:30:00-06:00"}
```

Et elle la note sur chaque commande, dans le champ `creado`. C'est la date que ta collection va vérifier.

Pour revenir à l'heure réelle :

```bash
tienda reloj real
```

(`tienda reiniciar` la remet aussi.)

---

## Étape 5 · La date de la commande, à midi et à des heures indues

Le test qu'il te faut est simple à dire : **la commande doit se retrouver avec la date de la boutique**. Sans écrire
aucune date à la main : la collection demande l'heure à la boutique et compare.

C'est une nouvelle collection, avec ton environnement `local` de la leçon 07 :

```bash
nano deshoras.postman_collection.json
```

```json
{
 "info": {
  "name": "Heures indues",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "L'heure de la boutique",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/salud"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('code 200', () => pm.response.to.have.status(200));",
    "pm.collectionVariables.set('hoy', pm.response.json().hora_de_la_tienda.slice(0, 10));"
   ]}}]
  },
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
    "pm.test('même année que la boutique', () => pm.expect(pm.response.json().creado.slice(0, 4)).to.eql(pm.collectionVariables.get('hoy').slice(0, 4)));",
    "pm.test('même jour que la boutique', () => pm.expect(pm.response.json().creado.slice(0, 10)).to.eql(pm.collectionVariables.get('hoy')));"
   ]}}]
  }
 ]
}
```

Les trois dernières requêtes, tu les connais déjà de la leçon 08. Ce qui est nouveau :

| Ligne | Ce qu'elle fait |
|---|---|
| `hora_de_la_tienda.slice(0, 10)` | `slice(0, 10)` prend les dix premiers caractères d'un texte. De `2026-12-31T23:30:00-06:00`, il garde `2026-12-31` : la date, sans l'heure |
| `pm.collectionVariables.set('hoy', …)` | Garde cette date sous le nom `hoy`, pour la comparer ensuite |
| `creado.slice(0, 4)` contre `hoy.slice(0, 4)` | Compare seulement l'année : `2026` contre `2026` |
| `creado.slice(0, 10)` contre `hoy` | Compare la date complète : année, mois et jour |

Pourquoi deux tests, si celui du jour inclut déjà l'année ? Parce que, quand il échoue, le nom du test rouge te dit à quel
point c'est grave : une commande au mauvais jour, ou dans la mauvaise **année**, celle qui casse le rapport annuel.

Vérifie le JSON et lance-la à l'heure réelle :

```bash
jq empty deshoras.postman_collection.json
tienda reiniciar
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ L'heure de la boutique
  GET http://localhost:8080/api/salud [200 OK, 214B, 11ms]
  ✓  code 200

→ La cliente se connecte
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 5ms]
  ✓  code 201

→ Un t-shirt au panier
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 546B, 3ms]
  ✓  code 200

→ Elle passe sa commande
  POST http://localhost:8080/api/pedidos [201 Created, 680B, 3ms]
  ✓  code 201
  ✓  même année que la boutique
  ✓  même jour que la boutique
```

Six sur six. Les tailles et les temps des sorties de cette leçon sont ceux de la mesure ; les tiens peuvent changer. Les
codes, les coches et les rouges, non.

**Maintenant, active E6, l'erreur « date en UTC », et lance-la à midi :**

```bash
tienda error E6 on
tienda reiniciar
tienda reloj 2026-11-21T12:00:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

Six sur six **encore une fois**. Avec E6, la boutique convertit l'heure en UTC, six heures plus tard, et la note dans
`creado` sans fuseau, si bien que plus personne ne peut savoir de quel fuseau elle venait. À midi, cela donne 18:00 le même
jour : la date ne change pas et ton test n'y voit rien.

**Maintenant, à des heures indues.** La nuit du 31 décembre, après avoir redémarré :

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ Elle passe sa commande
  POST http://localhost:8080/api/pedidos [201 Created, 674B, 3ms]
  ✓  code 201
  1. même année que la boutique
  2. même jour que la boutique
```

Et en dessous :

```text
 1.  AssertionError  même année que la boutique
                     expected '2027' to deeply equal '2026'
 2.  AssertionError  même jour que la boutique
                     expected '2027-01-01' to deeply equal '2026-12-31'
```

Une commande du 31 décembre à 23:30 s'est retrouvée avec la date du 1er janvier 2027. C'est la seconde moitié de la scène.
Et il n'y a pas besoin de la fin de l'année : le dernier jour d'un mois, le soir, échoue aussi. Avec la boutique à 19:00 le
30 novembre :

```text
 1.  AssertionError  même jour que la boutique
                     expected '2026-12-01' to deeply equal '2026-11-30'
```

Un rouge : l'année est bonne, mais la commande est partie en décembre.

Désactive E6 en terminant :

```bash
tienda error E6 off
tienda reiniciar
```

---

## Comment on vérifie

**Ton script et ta collection** sont contrôlés par le `verifica 09`. Enregistre-les dans `~/practica` sous les noms
`al-mismo-tiempo.sh` et `deshoras.postman_collection.json`, avec ton environnement `local.postman_environment.json`, et
dans le terminal de la boutique, écris :

```bash
verifica 09
```

Le `verifica` :

1. lance ton script avec la boutique propre : il doit se terminer par **0** ;
2. le lance avec E2 activée : il doit se terminer par **1** ; s'il se termine par 0, tes paiements ne sont pas partis en
   même temps ;
3. lance ta collection avec la boutique propre, avec l'horloge à une heure normale, au 30 novembre à 23:30 et au 31
   décembre à 23:30 : les trois fois, elle doit sortir **verte** ;
4. la lance avec E6 activée à ces mêmes heures : **au moins un test doit sortir rouge** ;
5. vérifie que ta collection n'a aucune date écrite à la main.

S'il manque quelque chose, il te dit quoi corriger. Il déplace l'horloge et active ou désactive les erreurs tout seul.
À la fin, il laisse activées les erreurs que tu avais activées et l'horloge à l'heure réelle, mais il réinitialise la
boutique : il efface tes commandes, ton panier et ta session. Avant de l'exécuter, la liste ci-dessous te dit si la
forme est bonne.

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] Ton script paie les deux commandes avec `&` et `wait`, pas l'une après l'autre.
- [ ] Avec la boutique propre, il se termine par 0 ; avec E2 activée, par 1, cinq fois sur cinq.
- [ ] Ta collection a quatre requêtes et sort 6 sur 6 avec la boutique propre, à l'heure réelle et avec
      `tienda reloj 2026-12-31T23:30:00`.
- [ ] Avec E6 activée, à midi elle sort verte et le 31 décembre à 23:30 « même année que la boutique » et
      « même jour que la boutique » échouent.
- [ ] Aucune date n'apparaît dans ta collection (cherche-les avec `grep -nE '20[0-9]{2}-[0-9]{2}' deshoras.postman_collection.json` ; il ne
      doit rien afficher).
- [ ] Tu as laissé E2 et E6 désactivées et l'horloge à l'heure réelle (`tienda error estado` et `tienda reloj real`).

---

## Tes exercices

1. **L'heure exacte.** Avec E6 activée, à partir de quelle heure le 30 novembre ta collection commence-t-elle à échouer ?
   Prédis l'heure avec le fuseau de la boutique, puis vérifie-la avec deux lancements : une minute avant et exactement à
   cette heure. L'horloge de la boutique continue de tourner à partir de l'heure que tu lui donnes, alors écris les trois
   commandes sur une seule ligne, pour qu'il ne s'écoule pas de secondes entre l'une et l'autre :

   ```bash
   tienda reiniciar && tienda reloj 2026-11-30T17:59:00 && newman run deshoras.postman_collection.json -e local.postman_environment.json
   ```

   (et un autre identique avec l'heure que tu as prédite).
2. **Le coupon à minuit.** La règle R4 de la leçon 01 dit que le coupon expire le 31 décembre à 23:59. Avec `curl`, comme
   dans la leçon 06, et avec la boutique tout juste redémarrée : connecte-toi et mets deux t-shirts dans le panier. Une
   fois tout prêt, mets l'horloge à `2026-12-31T23:59:00` et applique le coupon ; puis mets-la à `2027-01-01T00:00:00` et
   applique-le de nouveau. Prédis les deux codes. On utilise une minute avant, pas une seconde, parce que l'horloge
   continue de tourner pendant que tu tapes le `curl`. (Si tu es déjà en 2027 ou après, utilise le 31 décembre de ton année
   en cours : le coupon expire le 31 décembre de l'année où la boutique est ouverte.)
3. **Le même paiement en même temps.** Copie ton script (`cp al-mismo-tiempo.sh misma-llave.sh`) et, dans la copie, fais
   deux changements : remplace `pagar $DOS &` par `pagar $UNO &`, ainsi les deux paiements vont à la même commande et
   portent la même clé (le numéro de la commande et `$$` sont identiques dans un même lancement) ; et, sur la ligne de
   `ESTADO=`, remplace `jq -r .estado` par
   `jq -r '.estado + " " + .cobrado.texto + " de " + .total.texto'`, pour voir combien a été prélevé. Avant de le lancer,
   prédis **combien de prélèvements** il y aura sur la commande 1. Lance-le cinq fois, avec `tienda reiniciar` avant
   chacune, et compare les codes des cinq lancements. La dernière ligne, « VERT… », ne signifie rien ici : la commande 2
   n'est jamais payée. À la fin, `rm misma-llave.sh`.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Dans la scène, qu'avaient en commun les deux erreurs que les tests de l'équipe n'ont pas vues ? (scène)
2. Pourquoi le script l'une-après-l'autre est-il sorti vert avec E2 activée ? (étape 1)
3. Que font `&` et `wait` ? (étape 2)
4. Pourquoi lancer cinq fois un test de quelque chose qui se passe en même temps ? (étape 3)
5. Pourquoi ta collection est-elle sortie verte à midi avec E6 activée ? (étape 5)

---

## Pour conclure

Les leçons 07 et 08 testaient une personne, ou deux, qui faisaient les choses l'une après l'autre et à l'heure où tu
lançais le test. Cette leçon retire les deux conforts : les requêtes arrivent **ensemble** et à **n'importe quelle heure**.

Ce que tu en retires :

- **Ce qu'une personne fait une chose à la fois, teste-le aussi en même temps.** Une règle qui tient en séquence peut se
  casser en parallèle, dans la fenêtre entre vérifier et noter.
- `&` envoie une commande en arrière-plan et `wait` attend toutes les commandes : avec cela, tu tires en parallèle depuis
  le terminal.
- **Un test de course se répète avant de lui faire confiance :** un vert isolé ne suffit pas encore.
- **Les dates se testent au bord, pas à midi :** fin de journée, de mois et d'année, dans le fuseau de la boutique.
- Compare contre l'heure de la boutique elle-même, pas contre une date écrite à la main.

Dans la leçon 10, le problème sort de la boutique : la passerelle de paiement, un autre système, tombe en panne ou devient
lente, et tu vois pourquoi une dépendance lente est plus dangereuse qu'une dépendance qui tombe.

---

## Compare tes réponses

**Étape 1, la prédiction.** Vert. En séquence, le second paiement arrive quand le premier a déjà noté l'usage du coupon,
et la boutique le refuse même avec E2 activée. Si tu as prédit rouge parce que le script « utilise le coupon deux fois »,
c'est un bon raisonnement : ce qui manque, c'est de penser à **quand** arrive chaque paiement.

**Exercice 1.** À **18:00:00**. La boutique est six heures derrière UTC : à 18:00 à Mexico, il est déjà 00:00 le lendemain
en UTC, et E6 note cette heure. Mesuré :

```text
2026-11-30T17:59:00 → 6 sur 6 en vert
2026-11-30T18:00:00 → 1. même jour que la boutique: expected '2026-12-01' to deeply equal '2026-11-30'
```

C'est pourquoi, dans la scène, les commandes « à partir de six heures du soir » partaient au jour suivant. Les bords d'une
date ne sont pas seulement le minuit de ton fuseau : c'est aussi le minuit d'UTC.

**Exercice 2.** **200** à 23:59 et **422** « le coupon a déjà expiré » à 00:00:00. C'est l'analyse des bords de la leçon 02
appliquée au temps : la dernière minute valide et le premier instant qui ne l'est plus. Mesuré : avec l'horloge à
23:59:00 et le `curl` 20 secondes plus tard, 200 ; avec l'horloge à 00:00:00, 422.

**Exercice 3.** **Un seul prélèvement**, dans les cinq lancements : `commande 1 : pagado $698.40 de $698.40`. Ce qui change
d'un lancement à l'autre, ce sont les codes. Presque toujours, il sort **200 et 200** : le second paiement arrive quand le
premier est déjà terminé et reçoit la réponse gardée, comme dans la leçon 08. Parfois il sort **200 et 409** « ce
paiement est toujours en cours ; attends et réessaie avec la même clé » : le second est arrivé pendant que le premier
était encore en cours. Mesuré sur 20 lancements : 17 fois 200 et 200, 3 fois 200 et 409, et les 20 avec un seul
prélèvement égal au total.

```text
paiement de la commande 1 : 200
paiement de la commande 1 : 200
commande 1 : pagado $698.40 de $698.40
commande 2 : creado $0.00 de $698.40
```

C'est pourquoi un test de quelque chose qui se passe en même temps vérifie **l'effet**, pas le code : le code dépend de
qui est arrivé le premier ; qu'il y ait eu un seul prélèvement, non.

**Révision.**

1. Les deux avaient besoin de quelque chose que les tests ne faisaient jamais : deux requêtes **en même temps**, ou un
   test **à des heures indues**. Tous lançaient une requête à la fois, à midi.
2. Parce que le second paiement est arrivé quand le premier avait déjà noté l'usage du coupon : la fenêtre était déjà
   fermée.
3. `&` envoie la commande en arrière-plan et le terminal continue sans l'attendre ; `wait` attend que se terminent toutes
   celles qui sont en arrière-plan.
4. Parce que celui qui arrive le premier peut changer d'un lancement à l'autre. Si le test attrape parfois l'erreur et
   parfois non, un vert ne te dit rien.
5. Parce qu'à midi, six heures de plus donnent 18:00 le même jour : la date ne change pas, et le test compare la date.

---

## Sources de la leçon

1. PortSwigger, *Web Security Academy*, « Race conditions » (consulté le 21 novembre 2026). Il inspire l'exemple de cette
   leçon : un code de réduction à usage unique, avec une fenêtre entre le vérifier et le noter.
   « consider an online store that lets you enter a promotional code during checkout to get a one-time discount on
   your order » ; « This introduces a small race window during which you can repeatedly claim the discount ».
   https://portswigger.net/web-security/race-conditions
2. MITRE, CWE-362, « Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition') »
   (consulté le 21 novembre 2026). « a timing window exists in which the shared resource can be modified by
   another code sequence operating concurrently ».
   https://cwe.mitre.org/data/definitions/362.html
3. MITRE, CWE-367, « Time-of-check Time-of-use (TOCTOU) Race Condition » (consulté le 21 novembre 2026). « The
   product checks the state of a resource before using that resource, but the resource's state can change between
   the check and the use in a way that invalidates the results of the check. »
   https://cwe.mitre.org/data/definitions/367.html
4. IETF, RFC 3339, *Date and Time on the Internet: Timestamps* (2002), §2 et §4.4. « Z … denotes a UTC offset of
   00:00 » ; « Since interpretation of an unqualified local time zone will fail in approximately 23/24 of the globe, the
   interoperability problems of unqualified local time are deemed unacceptable for the Internet ».
   https://www.rfc-editor.org/rfc/rfc3339
5. GNU, *Bash Reference Manual*, « Job Control Builtins » (consulté le 21 novembre 2026). « If no options or ids
   are supplied, wait waits for all running background jobs… ».
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
6. GNU, *Bash Reference Manual*, « Lists of Commands » (consulté le 22 novembre 2026). « If a command is
   terminated by the control operator ‘&’, the shell executes the command asynchronously in a subshell » ; « The shell
   does not wait for the command to finish ».
   https://www.gnu.org/software/bash/manual/html_node/Lists.html

Mesure propre : chaque sortie de cette leçon a été mesurée avec curl, bash et newman 6.2.2 les 21 et 22 novembre 2026, avec
l'API de la boutique lancée sans Docker et redémarrée avant chaque lancement : le coupon, l'horloge et le 409 contre la
boutique du cours (hb-curso-qa, develop 13cdb22) ; E2 « coupon deux fois » en parallèle (20 sur 20 activée, 0 sur 20
désactivée, 0 sur 20 en séquence) et E6 « date en UTC » contre un prototype dans une copie de la boutique, pendant que les
vrais se construisent.

Règles du cours, sans source externe :

- « Ce qu'une personne fait une chose à la fois, teste-le aussi en même temps » : l'erreur de course n'apparaît pas en
  séquence.
- « Un test de course se répète avant de lui faire confiance » : s'il attrape parfois l'erreur et parfois non, un vert
  isolé ne suffit pas. Dans cette boutique, la fenêtre est grande exprès, pour que le résultat se répète à l'identique.
- « Les dates se testent au bord, pas à midi » : à midi, l'erreur de fuseau ne change pas la date.
