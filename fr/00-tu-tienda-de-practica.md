# Leçon 00 — Ta boutique d'entraînement

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, quatre mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **API :** la porte par laquelle un programme demande des choses à un autre. La page de la boutique ne garde ni les
  produits, ni le panier, ni les commandes : elle les demande à l'API de la boutique.
- **Requête et réponse :** chaque fois que la page a besoin de quelque chose, elle envoie une **requête** à l'API
  (« donne-moi le panier ») et l'API lui renvoie une **réponse** (« voilà : un t-shirt, $333.00 (pesos mexicains) »).
- **Code d'état :** le nombre à trois chiffres qui accompagne chaque réponse et dit comment s'est passée la requête.
  200 veut dire « ça s'est bien passé » ; 401, « je ne sais pas qui tu es ».
- **Défaillance :** ce que l'on voit mal tourner : un double prélèvement, une commande qui n'arrive pas. Le **défaut**
  est la cause, et il peut se trouver dans le code, dans une règle mal écrite, dans une donnée ou dans la
  configuration. En tant que QA, tu pars de la défaillance et tu cherches la cause.

**Ce que tu en retires :** ta boutique d'entraînement qui tourne sur ton ordinateur ; tu sais vérifier que l'API et la
page répondent ; tu parcours un achat complet à la main en notant quel écran tu vois et quelle requête la page envoie à
chaque étape ; et tu peux expliquer ce que coûte à une boutique une défaillance du paiement, du stock ou de la
livraison.

**Idée nouvelle de cette leçon (la seule qui est évaluée) :** avant de tester, on connaît le système : ce qu'il fait,
qui l'utilise et ce qui se passe s'il tombe en panne. Ainsi tu sais où regarder en premier.

**Dans quel ordre :** tu démarres la boutique (étape 1), tu vérifies que l'API et la page répondent (étape 2), tu fais
un achat en regardant ce qui se passe en dessous (étape 3), tu laisses `verifica` le contrôler (étape 4) et tu
réfléchis à ce que coûterait une défaillance de tout cela (étape 5).

**Combien de temps :** environ 60 minutes, plus le temps que prend l'image la première fois (estimation ; nous
l'ajusterons avec la première promotion d'élèves).

---

## La scène

*Scénario inventé ; les écrans et les réponses de la boutique qui apparaissent dans la leçon, eux, sont réels.*

Lundi, 9:05. Andrea commence aujourd'hui comme QA dans une boutique de vêtements en ligne. On lui donne un portable, un
accès et une phrase : « une nouvelle version est sortie vendredi ; vérifie que tout va bien ».

Elle ouvre la page. Elle voit des t-shirts, un panier et un bouton qui dit « Payer ». Elle clique à droite et à gauche.
Tout semble fonctionner.

À 11:40, un courriel arrive du service client. Une cliente a payé une seule fois et, sur son relevé, il y a **deux
prélèvements**. À 12:10, un autre. À 12:30, la cheffe d'Andrea demande ce qu'elle a testé.

Andrea a testé ce qu'on voyait. Mais le double prélèvement ne se voit pas à l'écran : il se produit **en dessous**,
dans la conversation entre la page et l'API, quand le paiement traîne et que la page le redemande. Pour le trouver, il
fallait d'abord savoir que cette conversation existe, ce qu'elles se disent, et pourquoi un double prélèvement coûte
plus cher qu'un bouton mal aligné.

Cette leçon te donne cela dans une boutique faite pour se tromper : la tienne, d'entraînement. Elle contient des
erreurs semées exprès, et l'une d'elles ressemble beaucoup à celle du lundi d'Andrea. Aujourd'hui, tu ne la cherches
pas encore : aujourd'hui, tu fais connaissance avec la boutique.

---

## Avant de commencer

**Ce dont tu as besoin :**

| | Quoi | Remarques |
|---|---|---|
| Cours précédent | « Le terminal depuis zéro », leçons 00 à 02, ou savoir te déplacer dans le terminal sans aide | Là, tu as installé Docker et appris à entrer dans un terminal d'entraînement et à en sortir |
| Docker | Installé et qui répond | Si tu ne l'as pas, plus bas on explique comment |
| Navigateur | Chrome ou Firefox, sur ton ordinateur | Pour voir la page et ce qu'elle envoie en dessous |
| Disque | Environ 1.3 Go pour l'image | Elle contient la boutique et tout ce que tu vas utiliser dans le cours pour la tester |
| Réseau | Pour télécharger l'image de base et les outils la première fois | Ensuite, la boutique tourne sans internet |

**Où cela a été testé, et où cela manque :**

| Système | État | Ce qui a été lancé |
|---|---|---|
| Linux x86_64, Docker 29 | Testé le 21 nov. 2026 par la personne qui a construit la boutique | Construire l'image, démarrer la boutique, `verifica 00` au rouge sans achat et au vert avec un achat payé |
| Mac (Apple silicon ou Intel) | Pas encore testé | Le script `practicar` distingue le Mac quand il explique les erreurs de Docker |
| Windows avec WSL 2 | Pas encore testé | Tout se lance dans le terminal du Linux de WSL, pas dans PowerShell |

Si tu l'essaies sur l'un de ceux qui manquent, raconte-nous comment ça s'est passé.

**Les chiffres de cette leçon, et comment ils ont été mesurés :**

| Chiffre | Comment il a été mesuré |
|---|---|
| Image : environ 1.3 Go | Linux x86_64, 21 nov. 2026, une exécution, par la personne qui a construit la boutique (c'est ce que rapporte le README du cours) |
| Construire l'image la première fois : environ 2 minutes | La même exécution ; cela dépend de ton réseau et de ton ordinateur |
| Démarrer la boutique déjà construite : environ 2 secondes | La même exécution |
| Panier d'un t-shirt bleu : $333.00 + $99.00 de livraison = $432.00 | En lançant la boutique du cours le 21 nov. 2026 |

**Si tu n'as pas Docker.** Si tu as suivi « Le terminal depuis zéro », tu l'as déjà : passe à l'étape 1. Sinon, sa
[leçon 00](https://www.habil.mx/fr/cours/terminal/00-tu-terminal-de-practica/) explique comment l'installer sous
Linux, Mac et Windows, et la [leçon 1 du cours Docker](https://www.habil.mx/fr/cours/docker/01-instalacion/) le fait
pas à pas sous Linux. Pour savoir s'il répond, lance dans le terminal de ton ordinateur :

```bash
docker version
```

Tout va bien si tu vois deux blocs, `Client` et `Server`, chacun avec sa version.

---

## Étape 1 · Démarre la boutique et entre

**Prédis d'abord.** Écris sur une feuille : quand tu lanceras la commande, où la boutique va-t-elle se retrouver ? Dans
une nouvelle fenêtre ? Sur internet ? Ailleurs ?

Dans le terminal de ton ordinateur, entre dans le dossier du cours (celui que tu as téléchargé depuis son dépôt ; avec
`ls` tu dois voir le fichier `practicar`) et lance :

```bash
TIENDA_IDIOMA=fr ./practicar
```

Cette variable, `TIENDA_IDIOMA=fr`, met la boutique dans ta langue (la page a aussi un sélecteur de langue en haut à
droite). `practicar` est un script du cours, comme celui du terminal. La première fois, il construit l'image : il
télécharge Python et y installe la boutique, avec les outils que tu utiliseras plus tard (behave, curl, newman et un
navigateur sans fenêtre). Il te prévient avant de commencer :

```text
Construction de l'image « curso-qa-tienda ». La première fois, elle télécharge Python, Node et un navigateur sans fenêtre :
cela peut prendre plusieurs minutes. Ce qui était déjà construit est réutilisé.
```

Tu verras défiler beaucoup de texte et, à la fin, ceci :

```text
✅ Image prête.
✅ La boutique est démarrée : http://localhost:8080
Entrée dans le terminal de la boutique. Pour sortir, tape  exit  (ou Ctrl+D).
🛒 Tienda de práctica: http://localhost:8080  ·  ayuda: tienda --help  ·  tu avance: verifica NN
```

Cette dernière ligne du bloc sort en espagnol quelle que soit la langue choisie : l'image l'imprime ainsi pour tout le
monde.

Lis les lignes dans l'ordre. La deuxième est celle qui compte aujourd'hui : **la boutique est démarrée**, à une adresse
de ton propre ordinateur. `localhost` veut dire « cet ordinateur-ci », et `8080` est le **port**, le numéro de la porte
par laquelle on entre dans la boutique. Compare avec ta prédiction : elle ne s'est pas retrouvée sur internet. Le
script ne la publie que pour ton ordinateur ; la documentation de Docker l'explique ainsi : si, en publiant un port, on
inclut l'adresse `127.0.0.1`, seul ton propre ordinateur peut y accéder.

La dernière ligne est déjà celle de **l'intérieur** : tu es dans le terminal de la boutique, un conteneur avec tout ce
qu'il faut pour le cours. Là, tu travailles en tant qu'`alumno`, dans ton dossier `~/practica`, qui est conservé même
quand tu sors.

Lance ta première commande à l'intérieur :

```bash
verifica 00
```

Cela doit donner ceci :

```text
Vérification de la leçon 00…

✅ L'API de la boutique répond sur /api/salud
✅ La page de la boutique se charge
❌ Marta a une commande payée
   → Va sur la page en tant que Marta (mot de passe : marta-practica), ajoute quelque chose au panier et paie.

Il manque encore quelque chose : corrige-le et relance  verifica 00
```

Deux verts et un rouge. Le rouge est normal : c'est l'achat que tu fais à l'étape 3. Remarque une chose que tu verras
tout au long du cours : `verifica` **interroge la boutique**. Pour savoir si tu as acheté, il regarde si la commande
existe et si elle est payée. Ainsi, toi et le cours, vous regardez la même preuve.

**Ça le prouve** (objectif 0.1, première moitié) : les deux marques vertes.

---

## Étape 2 · Vérifie que l'API et la page répondent

`verifica` t'a déjà dit que oui. Maintenant, vérifie-le toi-même, parce qu'en QA tu le feras des centaines de fois :
avant de chercher une erreur, tu t'assures que le système est démarré. S'il ne l'est pas, tout test échoue, et pas à
cause de l'erreur que tu cherchais.

**L'API, de l'intérieur.** Dans le terminal de la boutique :

```bash
curl http://localhost:8080/api/salud
```

`curl` est un programme qui envoie une requête et te montre la réponse telle quelle. Tu la verras de près à la leçon
06 ; aujourd'hui, il suffit de la lire :

```json
{"estado":"arriba","hora_de_la_tienda":"2026-11-21T20:27:25-06:00"}
```

Deux informations : la boutique dit qu'elle est **en marche** (`arriba`) et quelle heure il est chez elle. La tienne
sera celle de ton moment. Cette heure, tu pourras la déplacer plus tard pour tester des choses comme un coupon qui
expire à minuit, et c'est pour cela que la boutique te la donne.

**La page, depuis ton ordinateur.** Ouvre ton navigateur sur <http://localhost:8080>. Tu dois voir en haut « Boutique
d'entraînement », une ligne qui dit que la boutique est inventée et contient des erreurs exprès, un sélecteur de langue
à droite et, au milieu, un cadre « Entre dans la boutique » avec deux champs : **Client** (il dit déjà Marta) et **Mot
de passe**. Si en haut à droite tu vois déjà le panier et « Mes commandes », commence quand même par le cadre : ces
boutons ne servent qu'une fois que tu es entrée.

**La carte de l'API.** Ouvre aussi <http://localhost:8080/docs>. C'est la documentation de l'API, que la boutique
construit toute seule à partir de son code : chaque route, ce qu'elle reçoit et ce qu'elle renvoie. La boutique est
faite avec FastAPI, un outil pour construire des API qui génère cette page `/docs` si on ne lui indique pas autre
chose. Tu n'as pas à la lire en entier : regarde les titres des groupes (session, catalogue, panier, commandes) et
reviens ici. C'est une carte que tu vas consulter souvent.

> **Si tu utilises un autre port.** Si, en démarrant la boutique, tu as utilisé
> `TIENDA_IDIOMA=fr TIENDA_PUERTO=8081 ./practicar` (plus bas, dans « Ça ne marche pas ? », on dit quand), dans ton
> navigateur remplace `8080` par `8081`. À l'intérieur du terminal de la boutique, l'adresse reste
> `http://localhost:8080` : le port qui change est la porte de ton ordinateur, pas celle de l'intérieur.

**Ça le prouve** (objectif 0.1, seconde moitié) : la réponse de `/api/salud` et la page ouverte dans ton navigateur.

---

## Étape 3 · Fais un achat en regardant ce qui se passe en dessous

Voici le cœur de la leçon. Tu vas acheter en tant que Marta, la cliente de test, et à chaque écran tu vas noter **ce
que tu as vu** et **quelle requête la page a envoyée**. C'est ce qui a manqué à Andrea.

### Ouvre la fenêtre qui montre la conversation

Les navigateurs ont des outils pour développeurs, et l'un d'eux enregistre chaque requête que la page envoie.

- **Chrome :** appuie sur Ctrl+Shift+J (sur Mac, Command+Option+J). La console s'ouvre ; clique sur l'onglet
  **Network** (Réseau).
- **Firefox :** appuie sur Ctrl+Shift+E (sur Mac, Cmd+Opt+E). Le **Moniteur réseau** s'ouvre.

Cette fenêtre ne note que ce qui se passe **pendant qu'elle est ouverte** ; ouvre-la donc, puis **recharge la page**.
Dans la zone de filtre, écris `/api/` : ainsi tu ne vois que les requêtes à l'API et pas celles du style ou des
dessins de la page.

Chaque ligne de cette fenêtre est une requête, et **un seul clic peut en produire plusieurs**. Sur ta feuille, note-les
toutes sur la même ligne, séparées par des points-virgules. Regarde trois colonnes : la **route** (le nom), la
**méthode** et le **code d'état** (dans Chrome, *Status*). La méthode dit quel genre de chose la page demande :

| Méthode | Ce qu'elle demande | Exemple dans la boutique |
|---|---|---|
| GET | Qu'on lui **donne** quelque chose, sans rien changer | Le panier, les produits |
| POST | **Créer** quelque chose ou faire en sorte que quelque chose se passe | Une session, une commande, un paiement |
| PUT | **Remplacer** quelque chose par ce qu'elle envoie | Les pièces d'un produit dans le panier |
| DELETE | **Retirer** quelque chose | Un produit du panier |

### La feuille de suivi

Recopie ce tableau dans ton cahier ou dans un fichier. Tu vas le remplir pendant que tu achètes ; celui d'en bas, dans
« Compare tes réponses », est pour après, pas avant.

| # | Ce que tu fais | Ce que tu vois à l'écran | Requêtes (méthode et route, toutes) | Codes | Ce qui a changé dans la boutique |
|---|---|---|---|---|---|
| 1 | Tu recharges la page | | | | |
| 2 | Tu entres comme Marta avec un mot de passe **erroné** | | | | |
| 3 | Tu entres comme Marta avec `marta-practica` | | | | |
| 4 | Tu ajoutes un T-shirt bleu au panier | | | | |
| 5 | Tu paies | | | | |
| 6 | Tu ouvres « Mes commandes » | | | | |

**Prédis avant chaque ligne.** Avant de cliquer, écris ce que tu crois qu'il va se passer. Par exemple, pour la 2 :
quel code crois-tu que l'API renvoie quand le mot de passe est faux ? Ensuite, compare.

### Fais l'achat

1. **Recharge la page** avec la fenêtre réseau ouverte. Note quelle requête apparaît.
2. **Entre avec un mot de passe erroné.** Écris `incorrecta` dans *Mot de passe* et appuie sur *Entrer*. La page te
   dit que quelque chose s'est mal passé. Quel code est venu de l'API ? Cette ligne, tu la fais exprès : un QA regarde
   aussi ce qui se passe quand les choses tournent mal, et ici c'est sans danger.
3. **Entre correctement :** mot de passe `marta-practica`. La page change : « Salut, Marta » apparaît, avec le
   catalogue et ton panier. Regarde combien de requêtes sont parties d'**un seul** clic. Il n'y en a pas une seule.
4. **Ajoute un T-shirt bleu.** Cherche le t-shirt dans le catalogue et appuie sur *Ajouter au panier*. Regarde le
   panier : sous-total, réduction, livraison et total. Écris les quatre nombres.
5. **Paie.** La carte de test est déjà écrite (`4242 4242 4242 4242`) et le mode de paiement est « Paiement en une
   fois ». Appuie sur *Payer*. Ouvre la ligne de la requête de paiement et cherche parmi ses en-têtes (*Headers*) un
   qui s'appelle `Idempotency-Key`. Pour l'instant, repère-le simplement et note qu'il est là ; à l'étape 5 tu verras à
   quoi il sert, et à la leçon 08 tu le testeras.
6. **Ouvre « Mes commandes »** (bouton du haut). Ta commande y est, avec son numéro, son état et son total.

> **Uniquement des données de test.** La carte `4242 4242 4242 4242` n'est à personne, et la passerelle de paiement de
> cette boutique est simulée : elle ne parle à aucune banque et ne prélève rien pour de vrai. Dans une boutique
> d'entraînement, n'écris jamais une vraie carte, un mot de passe que tu utilises ailleurs ni des données personnelles.

**Pour regarder à tête reposée :** à l'étape 3 tu as vu que la page demande le panier **avant** d'ajouter le t-shirt et
le redemande **après**. Pourquoi crois-tu qu'elle le fait ? Il n'y a pas une seule bonne réponse ; celle que donne le
code de la boutique se trouve dans « Compare tes réponses ».

**Ça le prouve** (objectif 0.2) : ta feuille de suivi, comparée à celle de « Compare tes réponses ». `verifica` ne peut
confirmer que la partie qui laisse une trace dans la boutique, c'est-à-dire que ta commande existe et est payée ; la
feuille, tu la révises toi-même avec cette liste :

- [ ] Les six lignes contiennent ce que tu as vu à l'écran.
- [ ] Chaque ligne a **toutes** ses requêtes à `/api/`, avec méthode, route et code.
- [ ] À la ligne 5, tu as noté l'en-tête `Idempotency-Key`.
- [ ] Chaque ligne dit ce qui a changé dans la boutique, ou « rien ».

---

## Étape 4 · Laisse `verifica` le contrôler

Retourne dans le terminal de la boutique et relance :

```bash
verifica 00
```

Maintenant, cela doit donner quelque chose comme ceci. Ton numéro de commande peut ne pas être 1 (si tu avais déjà
acheté, ou si c'est ton deuxième tour) ; avec un t-shirt bleu, le total est $432.00 :

```text
Vérification de la leçon 00…

✅ L'API de la boutique répond sur /api/salud
✅ La page de la boutique se charge
✅ Marta a une commande payée (la 1, de $432.00)

🎉 Leçon terminée !
```

Trois verts. `verifica` a trouvé ta commande en interrogeant la boutique, exactement comme tu l'as vue dans « Mes
commandes ». Si Marta a plusieurs commandes payées, il nomme la première qu'il trouve. C'est la règle que le cours va
utiliser tout le temps : **la preuve, c'est ce que la boutique a fait**, et on peut la répéter.

S'il sort en rouge avec « Marta a N commande(s), mais aucune n'est payée », la commande a été créée mais le paiement
n'est pas passé. La même ligne te dit quoi faire : termine l'achat avec *Payer* et, si la passerelle a refusé le
paiement, lance `tienda pasarela aprueba` dans le terminal et paie à nouveau.

---

## Étape 5 · Que coûterait une défaillance ?

Tu as parcouru l'achat. Maintenant, regarde-le comme le regarde le commerce : toutes les défaillances ne coûtent pas la
même chose. Un texte mal aligné gêne ; un double prélèvement coûte à la boutique un remboursement, un appel de la
cliente et, peut-être, la cliente. Choisir quoi tester en premier commence ici. Le programme de l'ISTQB, l'examen
de tests qui sert de repère au cours, le dit ainsi : tout tester n'est pas possible, et l'effort se
concentre, entre autres, selon le risque.

**Un mot nouveau : parcours critique.** C'est le chemin qui, s'il se casse, coûte de l'argent ou des clients au
commerce. Celui que tu as fait à l'étape 3 (entrer, remplir le panier, payer, voir la commande) est le parcours
critique de cette boutique.

Trois parties de ce parcours où une défaillance coûte cher. Les données viennent de sources qui mesurent d'autres
choses que cette boutique : elles servent à raisonner sur le risque, ce ne sont pas une mesure de celle-ci.

**Le paiement.** C'est là que se rejoignent l'argent du client et sa confiance. Baymard Institute, qui étudie comment
les gens achètent en ligne, a demandé à des acheteurs des États-Unis pourquoi ils avaient abandonné un panier sans
acheter (en laissant de côté ceux qui ne faisaient que regarder). Parmi les raisons données : **19 %** n'ont pas
confié leur carte au site, **17 %** ont dit que le site avait eu des erreurs ou était tombé en panne, et **10 %**, que
leur carte avait été refusée. C'est une enquête dans un autre pays, pas un décompte de ventes perdues ; elle dit
pourtant où l'acheteur a mal. Et le paiement a une défaillance qui fait plus mal que ne pas encaisser : **encaisser
deux fois**. C'est pour cela que la **clé d'idempotence** existe, l'en-tête que tu as repéré à l'étape 3. Stripe, une
passerelle de paiement très utilisée, l'explique ainsi : si la connexion est coupée, la page peut répéter la requête
avec la même clé sans risquer de faire deux fois la même opération.

**Le stock.** Si la boutique vend quelque chose qu'elle n'a pas, elle a encaissé pour une promesse qu'elle ne peut pas
tenir. Au Mexique, la Ley Federal de Protección al Consumidor (la loi mexicaine de protection du consommateur) oblige
la boutique à respecter ce qu'elle a offert et convenu avec le client, entre autres les quantités, les délais et les
dates, pour la livraison. Ce qui suit est déjà un raisonnement du cours, pas le texte de la loi : vendre ce qu'on n'a
pas oblige presque toujours à annuler, à rembourser et à s'expliquer auprès du client. Cette boutique d'entraînement
ne gère pas de stock, mais elle gère le chemin de la commande après le paiement (à l'entrepôt, expédiée, livrée), et
celui-là, tu le parcours à la leçon 04.

**La livraison.** Le client a déjà payé ; maintenant il attend. Dans la même enquête de Baymard, **20 %** ont dit
avoir abandonné un panier parce que la livraison était trop lente : le délai pèse dans la décision dès avant de payer.
Et la même loi exige que le montant total à payer soit indiqué de façon bien visible : une livraison qui apparaît par
surprise à la fin n'est pas seulement une mauvaise expérience. C'est pourquoi ta feuille de suivi a noté la livraison
($99.00) à côté du total.

**Ce que cela dit à un QA :** si un jour tu n'as le temps que pour un test, il va dans le parcours critique. Le cours
s'en sert à la leçon 11, où un test de navigateur parcourt justement ce chemin.

**Ça le prouve** (objectif 0.3) : la révision de « Pour conclure », 4 sur 5.

---

## Trois remarques sur ta boutique d'entraînement

1. **Les erreurs sont là, mais éteintes.** La boutique contient quatre erreurs semées qui s'allument une par leçon.
   Aujourd'hui elles sont toutes éteintes, et tu peux le vérifier depuis le terminal de ton ordinateur avec
   `./practicar error estado`. Ne les allume pas encore : chaque leçon te dit laquelle et quand. Si l'une reste
   allumée, `./practicar` te prévient quand tu entres.
2. **Ton travail est conservé.** `./practicar apagar` arrête la boutique ; tes commandes et ton dossier `~/practica`
   seront toujours là la prochaine fois. `./practicar reiniciar` remet la boutique comme à son ouverture, sans
   commandes. `./practicar desde-cero` efface aussi ton dossier, et c'est pourquoi il te demande de confirmer.
3. **La boutique n'est publiée que pour ton ordinateur.** Le script ouvre son port sur `127.0.0.1`, donc personne
   d'autre ne peut ouvrir ta boutique par ce port, et la passerelle de paiement est simulée. C'est fait pour que tu te
   trompes sans conséquences : entre avec de mauvais mots de passe, change des quantités bizarres, ouvre et ferme.
   Utilise toujours les données de test de la leçon.

---

## Tes exercices

1. **Achète comme Luis.** Sors de la boutique (bouton *Quitter*), entre comme Luis (`luis-practica`) et fais un autre
   achat avec un produit différent. Remplis une nouvelle feuille de suivi. Les requêtes ont-elles été les mêmes ?
   Qu'est-ce qui a changé ? Ensuite, lance `verifica 00` : ce qu'il dit a-t-il changé ? Pourquoi ?
2. **Interroge l'API sans te présenter.** Dans le terminal de la boutique, prédis ce qu'elle répond, puis lance :
   ```bash
   curl http://localhost:8080/api/pedidos
   ```
   Compare la réponse avec la ligne 2 de ta feuille. Qu'ont-elles en commun ?
3. **Trois défaillances, trois coûts.** Sans regarder l'étape 5, écris une défaillance possible dans le paiement, une
   dans le stock et une dans la livraison de cette boutique, et pour chacune : qui la remarque en premier (le client, la
   boutique, la banque) et ce qu'elle coûte à la boutique. Ensuite, compare avec l'étape 5.

---

## Ça ne marche pas ?

| Ce que tu vois | Ce qui se passe | Quoi faire |
|---|---|---|
| `no such file or directory: ./practicar` (ou `No such file or directory`) | Tu n'es pas dans le dossier du cours | Entre dans le dossier où tu as téléchargé le cours, lance `ls` et vérifie que `practicar` apparaît |
| `❌ Je ne trouve pas la commande « docker » sur cet ordinateur.` | Docker n'est pas installé | « Si tu n'as pas Docker », dans « Avant de commencer » |
| `❌ Docker est installé, mais je n'ai pas pu lui parler.` | Sur Mac, le programme de Docker est fermé. Sous Linux, le service est arrêté ou ton utilisateur n'est pas dans le groupe `docker` | Le même message dit quoi vérifier sur ton système. Si ce n'est pas cela, lance `docker info` et suis l'erreur exacte |
| `❌ Je n'ai pas pu démarrer la boutique.` avec `port is already allocated` | Un autre programme utilise le port 8080 | Ferme-le, ou démarre la boutique sur un autre port : `TIENDA_IDIOMA=fr TIENDA_PUERTO=8081 ./practicar` |
| `❌ ./practicar ouvre un terminal interactif…` | Tu l'as lancé avec un tube (`|`) ou une redirection | Lance-le directement dans ton terminal |
| La page ne se charge pas dans le navigateur | La boutique est arrêtée, ou tu utilises un autre port | Relance `./practicar` ; si tu as utilisé `TIENDA_PUERTO`, change le numéro dans l'adresse |
| `verifica 00` : « aucune n'est payée » | La passerelle a refusé le paiement ou tu n'as pas terminé l'achat | À l'intérieur : `tienda pasarela aprueba`, et paie à nouveau |

---

## Pour conclure

Andrea a révisé ce qu'on voyait. Toi, tu sais déjà que sous chaque clic il y a une conversation (requête, réponse et
code d'état), que tu peux la regarder, et que toutes les défaillances ne coûtent pas la même chose. C'est cela,
connaître le système avant de le tester.

À la leçon 01, tu cesses de regarder la boutique en acheteuse et tu commences à la lire en QA : tu reçois un récit
utilisateur, tu le sépares en règles et tu écris tes premiers scénarios sur papier et dans un fichier. Les lancer
contre cette même boutique viendra quand son `verifica 01` existera ; en attendant, la leçon te donne une liste pour
réviser leur forme.

**Révision (4 sur 5).** Pour chaque cas, écris trois choses : (1) quelle partie du parcours critique il touche
(paiement, stock ou livraison), (2) qui le remarque en premier et (3) la chaîne complète : **défaillance → ce qui arrive
au client ou à l'exploitation → ce que cela coûte à la boutique**. Nommer seulement la partie ne compte pas comme une
réponse.

1. Lucía voit $333.00 à chaque écran du parcours ; une fois ses données saisies, la dernière étape affiche $432.00.
2. La connexion internet de Pedro est coupée juste au moment où il appuie sur *Payer* ; la page réessaie toute seule,
   et sur son relevé apparaissent deux opérations de $432.00.
3. La boutique confirme dix commandes de la tasse le même jour ; le vendredi, quelqu'un découvre qu'il n'y en avait que
   six.
4. Une cliente a payé le lundi ; le vendredi, sa commande dit la même chose que le mardi et personne ne lui a écrit.
5. Pendant une heure, tous les achats se terminent par « la passerelle a refusé le paiement », alors que les gens
   utilisent des cartes qui fonctionnent dans d'autres boutiques.

---

## Compare tes réponses

**Ta feuille de suivi.** Voici ce qu'elle est devenue en faisant l'achat contre la boutique du cours. Tes heures et ton
numéro de commande peuvent être différents (ici, c'est le 1) ; les routes, les méthodes et les codes doivent être les
mêmes.

| # | Ce que tu fais | Ce que tu vois | Requêtes à `/api/` | Codes | Ce qui a changé |
|---|---|---|---|---|---|
| 1 | Tu recharges | « Entre dans la boutique » | `GET /api/textos` | 200 | Rien : la page a demandé ses textes dans ta langue |
| 2 | Mot de passe erroné | « client ou mot de passe incorrect » | `POST /api/sesiones` | 401 | Rien |
| 3 | Tu entres comme Marta | « Salut, Marta », catalogue et panier vide | `POST /api/sesiones`, `GET /api/productos`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Une session de Marta s'est ouverte |
| 4 | Tu ajoutes un T-shirt bleu | « Ajouté au panier » ; sous-total $333.00, réduction $0.00, livraison $99.00, total $432.00 | `GET /api/carrito`, `PUT /api/carrito/productos/playera-azul`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 200, 200, 200, 200 | Le panier de Marta contient 1 pièce |
| 5 | Tu paies | « Commande 1 payée. Merci pour ton achat ! » et le panier vide | `POST /api/pedidos`, `POST /api/pedidos/1/pago` (avec `Idempotency-Key`), `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | La commande 1 existe, payée, avec un prélèvement de $432.00 |
| 6 | « Mes commandes » | « Commande 1 · payée · $432.00 » | `GET /api/pedidos` | 200 | Rien |

Trois choses qui valent la peine d'être remarquées :

- **La ligne 3 :** un clic, quatre requêtes. L'écran te montre une chose ; l'API en reçoit plusieurs. Beaucoup
  d'erreurs vivent entre l'une et l'autre.
- **La ligne 5 :** payer, ce sont **deux** requêtes, une qui crée la commande et une autre qui l'encaisse. Entre les
  deux, la commande existe sans être payée. C'est pourquoi `verifica` distingue « tu as une commande » de « tu as une
  commande payée ».
- **Le GET avant d'ajouter (question de l'étape 3) :** la page demande combien de pièces de ce produit tu as déjà, en
  ajoute une et envoie le total avec `PUT`, parce que `PUT` remplace la quantité, il ne l'additionne pas. Ensuite elle
  redemande le panier pour afficher les nombres calculés par la boutique, pas ceux calculés par la page.

**Exercice 1 :** les requêtes sont les mêmes ; ce qui change, c'est la route du produit dans le `PUT` et les montants.
`verifica 00` ne change pas ce qu'il dit, parce qu'il vérifie les commandes de **Marta**, pas celles de Luis : il mesure
ce que la leçon a demandé.

**Exercice 2 :** l'API répond `{"mensaje":"connecte-toi d'abord"}` avec le code 401, le même code que la ligne 2. Dans
les deux cas, l'API ne sait pas qui tu es. Dans une requête sans te présenter, tu n'as même pas essayé.

**Exercice 3 :** toute défaillance bien pensée est valable. Ce qui compte, c'est que tu aies écrit qui la remarque en
premier et ce qu'elle coûte. Exemples : paiement → la banque refuse des cartes valables, le client le remarque, cela
coûte la vente ; stock → on vend ce qu'on n'a pas, l'entrepôt le remarque, cela coûte une annulation et un
remboursement ; livraison → la commande reste bloquée sans avertissement, le client le remarque, cela coûte sa
confiance et une réclamation.

**Révision.** Compte comme correcte la réponse qui contient les trois parties ; les chaînes ci-dessous sont des
exemples, et la tienne peut être différente si elle se tient :

1. **Paiement ou livraison, les deux valent.** Lucía le remarque à la dernière étape. Cela touche au paiement parce que
   cela change ce qu'elle paie, et à la livraison parce que la différence est la livraison ($99.00), que l'étape 5
   traite là. Le total n'a pas été indiqué de façon visible dès le début → Lucía se sent surprise et abandonne ou paie
   de mauvaise humeur → la boutique perd la vente ou gagne une réclamation, et la loi demande de montrer le total.
2. **Paiement.** Pedro le remarque, ou sa banque. Le paiement a été répété sans une clé qui l'identifie comme la même
   tentative → deux prélèvements pour un achat → remboursement, appel au service client et un client qui se méfie.
3. **Stock.** Celui qui prépare les commandes le remarque. On a encaissé ce qu'on n'avait pas → quatre clients sans leur
   tasse → quatre annulations avec remboursement et quatre explications.
4. **Livraison.** La cliente le remarque. La commande n'avance pas et personne ne prévient → elle ne sait pas si son
   argent est en sécurité → réclamation, et probablement elle ne rachète plus.
5. **Paiement.** Les clients le remarquent. La passerelle refuse de bons paiements → ils ne peuvent pas acheter → chaque
   achat de cette heure est perdu ou part vers une autre boutique (c'est la raison donnée par les 10 % dans l'enquête de
   Baymard).

**Si tu n'as pas eu 4,** retourne à l'étape 5 : chaque cas sort de l'une de ses trois parties.

---

## Sources de la leçon

Toutes ont été ouvertes le 21 nov. 2026 et recoupées phrase par phrase. Le détail, avec la phrase de chacune, se
trouve dans le research de la leçon.

1. Docker, « Port publishing and mapping ». Un port publié avec `127.0.0.1` n'est accessible que depuis l'ordinateur
   lui-même. https://docs.docker.com/engine/network/port-publishing/
2. MDN (Mozilla), « HTTP request methods ». Ce que font GET, POST, PUT et DELETE.
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
3. MDN (Mozilla), « HTTP response status codes ». 200 (la requête s'est bien passée) et 201 (quelque chose de nouveau a
   été créé). https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
4. Chrome for Developers, « Inspect network activity ». Comment s'ouvre le panneau Network, qu'il ne note que tant qu'il
   est ouvert, et la zone de filtre. https://developer.chrome.com/docs/devtools/network
5. Firefox Source Docs (Mozilla), « Network Monitor ». Ce qu'il montre et son raccourci clavier.
   https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/
6. FastAPI, « First Steps ». La documentation interactive de l'API sur `/docs`.
   https://fastapi.tiangolo.com/tutorial/first-steps/
7. Stripe, « Idempotent requests ». La clé d'idempotence pour répéter une requête sans faire l'opération deux fois.
   https://docs.stripe.com/api/idempotent_requests
8. Baymard Institute, « Cart Abandonment Rate: 50 Statistics & Why People Abandon (2026) », 28 oct. 2026. Raisons
   d'abandonner un panier : 19 % n'ont pas confié leur carte, 17 % erreurs du site, 10 % carte refusée, 20 % livraison
   lente. https://baymard.com/lists/cart-abandonment-rate
9. Ley Federal de Protección al Consumidor, Cámara de Diputados, dernière réforme DOF 12-12-2025, articles 7 et 7 BIS.
   Respecter ce qui a été offert et convenu pour la livraison, et indiquer de façon bien visible le montant total.
   https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf
10. ISTQB, Certified Tester Foundation Level Syllabus v4.0.1, 2024-09-15, §1.2 et §1.3. Des erreurs naissent les défauts,
    et des défauts, les défaillances ; tout tester n'est pas possible et l'effort se concentre selon le risque
    (principe 2). https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/

Du cours et de Hábil : la boutique d'entraînement, son `practicar` et son `verifica` sont du cours, dans son dépôt.
C'est une **règle du cours**, sans source externe : « si tu n'as le temps que pour un test, il va dans le parcours
critique » ; elle existe pour que le premier test que tu écris protège ce qui coûte le plus.
