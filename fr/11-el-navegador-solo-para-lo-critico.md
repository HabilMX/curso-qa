# Leçon 11 — Le navigateur, seulement pour ce qui est critique

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Test de navigateur :** un programme qui ouvre la page, écrit, clique et lit l'écran, comme le ferait Marta.
- **Sans fenêtre :** le navigateur tourne en entier, mais il ne dessine rien sur ton écran. En anglais on dit *headless*.
- **Sélecteur :** la façon de dire au test sur quel élément de la page agir, par exemple « le bouton Payer ».

**Ce que tu en retires :** un script, `compra.py`, qui se connecte comme Marta, achète un t-shirt et vérifie dans « Mes
commandes » que la commande est bien payée. Il sort vert avec la boutique propre et rouge avec une erreur qu'aucune de
tes collections ne voit.

**Idée de QA nouvelle de cette leçon (la seule) :** le test de navigateur est le plus cher : on le réserve au parcours
qui ne peut pas échouer. Les outils, eux, sont nouveaux (Python et Playwright), mais tu n'as pas à les apprendre en
entier : tu copies un script et tu le comprends ligne par ligne.

**Dans quel ordre :** tu achètes à la main et tu trouves une erreur que l'API ne voit pas (étape 1) ; tu écris le test
(étape 2) ; tu le lances vert et rouge (étape 3) ; tu vois les deux façons dont il peut te tromper (étape 4) ; et tu
mesures ce qu'il coûte (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Un mardi matin, une nouvelle version de la page de la boutique sort. Avant de la publier, l'équipe a lancé toutes ses
collections : celle de la leçon 07, celle des permissions, celle de la passerelle. Tout est vert.

L'après-midi, l'entrepôt demande pourquoi il n'y a rien à emballer. Depuis le matin, Marta et plusieurs autres clientes
ont vu sur la page « Commande 7 payée. Merci pour ton achat ! ». Aucune n'a été débitée, et aucune commande n'est
passée à payée. L'API était parfaite : personne ne lui a demandé de prélever.

---

## Avant de commencer

**Il te faut la boutique démarrée.** Comme dans les leçons 07 à 10 : `TIENDA_IDIOMA=fr ./practicar` sur ton ordinateur
et, dans une autre fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.
Cette fois, tu vas aussi utiliser le navigateur de ton ordinateur, à l'adresse que le terminal t'affiche à l'entrée
(`http://localhost:8080`).

> **Cette leçon utilise la boutique de la leçon 11.** Elle apporte l'erreur E8. Si `tienda error E8 on` te dit que cette
> erreur n'existe pas, mets ta boutique à jour avant de continuer : avec une version plus ancienne, tes sorties ne vont
> pas coïncider.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 07, ne pas écrire à la main l'adresse ni Marta dans tes
tests ; de la 09, le **code de sortie** (0 est vert, tout autre nombre est rouge) et vérifier **l'effet**, pas ce que
dit la réponse ; de la 10, vérifier que l'état de la commande concorde.

**Ce qui est nouveau :** Python et Playwright, l'outil qui pilote le navigateur. Les deux sont déjà dans la boutique :
tu n'installes rien.

**Fais l'exercice 2 sans IA.** Ce que tu entraînes là, c'est décider où va chaque test, et cela relève de ton propre
jugement.

**Repars de zéro :**

```bash
tienda reiniciar
```

```text
✅ la boutique est revenue à son état d'ouverture
```

**Combien de temps :** environ 60 minutes (estimation ; nous l'ajusterons avec la première promotion d'élèves).

---

## Étape 1 · Un achat que l'API ne voit pas

Achète d'abord à la main, comme Marta. Dans le navigateur de ton ordinateur, ouvre `http://localhost:8080` :

1. Écris le mot de passe de Marta (`marta-practica` ; le nom est déjà rempli) et clique sur **Entrer**.
2. Sur « T-shirt bleu », clique sur **Ajouter au panier**. Le panier en haut passe à 1.
3. Dans le panier, clique sur **Payer**. La carte de test est déjà remplie.
4. En bas apparaît « Commande 1 payée. Merci pour ton achat ! ». Clique sur **Mes commandes** : la commande 1 indique
   **payée**.

`tienda reiniciar` efface les sessions. Si tu redémarres avec la page ouverte, la page te ramène à l'entrée avec l'avis
« Ta session n'existe plus (par exemple, parce que la boutique a redémarré). Reconnecte-toi. » : reconnecte-toi comme
Marta.

Maintenant, active l'erreur de cette leçon, dans le terminal de la boutique :

```bash
tienda reiniciar
tienda error E8 on
```

```text
✅ la boutique est revenue à son état d'ouverture
  E1  ⚪ désactivée
  E2  ⚪ désactivée
  E3  ⚪ désactivée
  E4  ⚪ désactivée
  E5  ⚪ désactivée
  E6  ⚪ désactivée
  E7  ⚪ désactivée
  E8  🔴 activée

⚠️ erreur E8 activée
```

Recharge la page, reconnecte-toi comme Marta et répète l'achat. Le message est le même : « Commande 1 payée. Merci pour
ton achat ! ». Mais dans **Mes commandes**, la commande 1 indique **créée**. Marta croit avoir acheté, et la boutique ne
l'a pas débitée.

**Prédis avant de lancer :** avec E8 activée, ta collection de la leçon 07 sort-elle verte ou rouge ?

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Elle sort **verte** : les mêmes sept coches que dans la leçon 07. Celle de la leçon 10, celle de la passerelle, aussi :
six sur six (mesuré avec E8 activée). Ce n'est pas un oubli de tes collections. E8 ne touche que **le paiement qui arrive depuis la page** : quand
Marta clique sur « Payer », la boutique répond que oui, la page écrit le message de paiement, et la commande n'est pas
prélevée. Si le paiement arrive directement par l'API, comme dans ta collection, il est bien prélevé. Un test qui parle
à l'API, aussi bon soit-il, ne passe pas par ce bouton et ne peut pas le voir.

Pour trouver cette erreur, il faut faire ce que fait Marta : ouvrir la page, cliquer et regarder.

**Désactive E8** avant de continuer :

```bash
tienda error E8 off
```

---

## Étape 2 · L'achat, écrit comme un test

Un test de navigateur fait la même chose que tu as faite à l'étape 1, mais tout seul et sans fenêtre. Dans `~/practica`,
crée le fichier :

```bash
nano compra.py
```

et écris ceci. Tu n'as pas besoin de savoir Python : copie le bloc entier, tel quel, puis lis-le avec le tableau
ci-dessous. Quatre choses de Python que tu vas voir : `import` apporte un outil ; `NOM = valeur` garde une donnée sous
un nom ; `pagina.quelquechose(…)` demande une action à la page ; et les quatre espaces au début d'une ligne la placent à
l'intérieur du bloc du dessus.

```python
"""L'achat critique, dans le navigateur : la cliente se connecte, achète un t-shirt et sa commande finit payée."""
import os

from playwright.sync_api import expect, sync_playwright

TIENDA_URL = os.environ["TIENDA_URL"]
CLIENTE = os.environ["CLIENTE"]
CONTRASENA = os.environ["CONTRASENA"]

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page()
    pagina.goto(TIENDA_URL)

    pagina.fill("#cliente", CLIENTE)
    pagina.fill("#contrasena", CONTRASENA)
    pagina.click("#form-entrada button")

    pagina.get_by_test_id("agregar-playera-azul").click()
    expect(pagina.locator("#piezas")).to_have_text("1")

    pagina.click("#pagar")
    expect(pagina.locator("#piezas")).to_have_text("0")

    pagina.click("#ver-pedidos")
    estado = pagina.locator("#lista-pedidos .pedido .estado").first
    expect(estado).to_have_attribute("data-estado", "pagado")

    navegador.close()

print("✅ la cliente a acheté et sa commande est payée")
```

| Partie | Ce qu'elle fait |
|---|---|
| `os.environ["TIENDA_URL"]` | Lit l'adresse de la boutique **dans l'environnement**, comme `{{base}}` dans ta collection de la leçon 07. Pareil pour `CLIENTE` et `CONTRASENA`. Ainsi le test n'a rien d'écrit à la main et sert pour une autre boutique ou une autre cliente |
| `with sync_playwright() as p:` | Démarre Playwright. Les lignes du dessous qui commencent par quatre espaces vont **dans** ce bloc et peuvent l'utiliser ; quand le bloc se termine, Playwright s'éteint |
| `p.chromium.launch()` | Ouvre Chromium, le navigateur. Playwright l'ouvre **sans fenêtre** si tu ne lui demandes pas autre chose |
| `pagina.goto(TIENDA_URL)` | Ouvre la boutique, comme quand tu as écrit l'adresse dans ton navigateur |
| `pagina.fill("#cliente", CLIENTE)` | Écrit dans le champ dont l'`id` est `cliente`. Le `#` veut dire « l'élément avec cet id » |
| `pagina.click("#form-entrada button")` | Clique sur le bouton du formulaire d'entrée : « Entrer » |
| `get_by_test_id("agregar-playera-azul")` | Trouve le bouton **Ajouter au panier** du t-shirt bleu par son **test id**, une marque que la page met seulement pour les tests |
| `expect(…).to_have_text("1")` | **Vérifie** : le compteur du panier doit afficher 1. S'il ne l'affiche pas encore, il attend et regarde de nouveau, jusqu'à 5 secondes |
| `expect(pagina.locator("#piezas")).to_have_text("0")` | Après le paiement, attend que le panier se redessine à 0. La page le redessine **à la fin**, quand cette tentative de paiement est terminée ; ainsi le test ne demande pas « Mes commandes » trop tôt. Que le panier tombe à 0 ne dit pas que c'est payé : c'est la vérification du dessous qui s'en charge |
| `.first` et `to_have_attribute("data-estado", "pagado")` | Dans « Mes commandes », prend la commande tout en haut (la plus récente) et vérifie que son état est `pagado` |
| `print(…)` | Ne s'affiche que si toutes les vérifications ont réussi |

**Pourquoi ces sélecteurs et pas le texte des boutons.** La documentation de Playwright recommande de chercher par ce
que l'utilisateur voit, comme le texte d'un bouton. Ici cela ne marche pas : ta boutique parle cinq langues, et
« Ajouter au panier » est « Add to cart » en anglais et « Добави в количката » en bulgare. L'`id` et le test id ne
changent pas avec la langue. C'est pourquoi le bouton **Ajouter au panier** porte `data-testid="agregar-playera-azul"` :
c'est une marque que la page met pour les tests, et Playwright la considère comme la façon la plus résistante de
trouver un élément.

**Pourquoi le test dit « la cliente » et pas « Marta ».** Le `verifica` cherche Marta écrite à la main dans tout ce qui
n'est pas un commentaire, et le texte entre `"""` au début et celui du `print` ne sont pas des commentaires : ils
comptent. Un commentaire commence par `#`.

**Pourquoi l'état et pas le message.** Le message de la page, c'est ce que dit la page. L'état dans « Mes commandes »,
c'est ce que la boutique a enregistré. À l'étape 1, tu as vu qu'avec E8 ce n'est pas la même chose.

**Si quelque chose échoue, Python se termine avec un nombre différent de 0**, comme ton script de la leçon 09. Une
vérification `expect` qui n'est pas remplie en 5 secondes arrête le script sur place, et le `print` de la fin ne
s'exécute pas.

---

## Étape 3 · Vert, puis rouge

Le test lit l'adresse, la cliente et le mot de passe dans l'environnement. Donne-les-lui une fois dans le terminal de la
boutique :

```bash
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

`export` laisse la variable en place tant que cette fenêtre reste ouverte. Si tu fermes le terminal, réécris les trois
lignes.

**Prédis :** avec la boutique propre, combien de temps met-il ? Plus ou moins que ta collection de la leçon 07 ?
Lance-le :

```bash
tienda reiniciar
python3 compra.py
echo "código de salida: $?"
```

```text
✅ la boutique est revenue à son état d'ouverture
✅ la cliente a acheté et sa commande est payée
código de salida: 0
```

Il met environ une seconde et demie (mesuré : entre 1.4 et 1.5 secondes en cinq lancements).

Tu n'as vu aucune fenêtre, mais un navigateur complet a ouvert la boutique, s'est connecté, a acheté et a vérifié. Dans
la page, sur ton ordinateur, connecte-toi comme Marta et ouvre **Mes commandes** (si la page t'a ramené à l'entrée,
reconnecte-toi) : la commande que ton test a faite est là.

Maintenant avec l'erreur :

```bash
tienda reiniciar
tienda error E8 on
python3 compra.py
echo "código de salida: $?"
```

```text
✅ la boutique est revenue à son état d'ouverture
  E1  ⚪ désactivée
  E2  ⚪ désactivée
  E3  ⚪ désactivée
  E4  ⚪ désactivée
  E5  ⚪ désactivée
  E6  ⚪ désactivée
  E7  ⚪ désactivée
  E8  🔴 activée

⚠️ erreur E8 activée
Traceback (most recent call last):
  File "/home/alumno/practica/compra.py", line 27, in <module>
    expect(estado).to_have_attribute("data-estado", "pagado")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.15/site-packages/playwright/sync_api/_generated.py", line 15155, in to_have_attribute
    self._sync(
    ~~~~~~~~~~^
        self._impl_obj.to_have_attribute(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        )
        ^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_sync_base.py", line 124, in _sync
    return task.result()
           ~~~~~~~~~~~^^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 357, in to_have_attribute
    await self._expect_impl(
    ...<7 lines>...
    )
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 122, in _expect_impl
    _record_soft_or_raise(
    ~~~~~~~~~~~~~~~~~~~~~^
        AssertionError(
        ^^^^^^^^^^^^^^^
    ...<2 lines>...
        self._is_soft,
        ^^^^^^^^^^^^^^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_assertions.py", line 50, in _record_soft_or_raise
    raise error
AssertionError: Locator expected to have attribute 'pagado'
Actual value: creado 
Call log:
  - Expect "to_have_attribute" locator("#lista-pedidos .pedido .estado").first with timeout 5000ms
  - waiting for locator("#lista-pedidos .pedido .estado").first
    14 × locator resolved to <span class="estado" data-estado="creado">créée</span>
       - unexpected value "creado"

Aria snapshot:
- text: créée
código de salida: 1
```

C'est long, et presque tout est le chemin à l'intérieur de Playwright. Ce qui compte est à la fin : `Locator
expected to have attribute 'pagado'`, `Actual value: creado` et `código de salida: 1`.

Le test sort **rouge**. Il arrive à « Mes commandes », attend 5 secondes que la commande indique `pagado` et elle ne
l'indique pas : elle indique `creado`. Python affiche quelle vérification a échoué et se termine avec un code différent
de 0. C'est exactement ce que ta collection n'a pas vu à l'étape 1.

**Désactive E8 :**

```bash
tienda error E8 off
```

---

## Étape 4 · Deux verts qui ne suffisent pas

Un test de navigateur coûte plus cher à écrire et à lancer qu'un test d'API. Il ne vaut la peine que s'il voit ce que
l'API ne voit pas. Il y a deux façons courantes de sortir vert sans l'avoir vu.

**Regarder le message au lieu de l'état.** Si la dernière vérification était « le message de la page dit payée », avec
E8 le test sortirait vert : la page écrit le message même si rien n'a été payé. C'est la même erreur que dans la leçon
09 : croire ce qui se dit au lieu de vérifier ce qui s'est passé. Tu le vérifieras dans l'exercice 1.

**Parler à l'API au lieu d'utiliser la page.** Un `compra.py` qui, au lieu d'ouvrir le navigateur, se connecte, ajoute le
t-shirt et paie avec des appels directs à l'API, sort vert avec E8 : mesuré. Ce script achète bien, mais il ne passe pas
par le bouton « Payer », qui est justement ce qui échoue. C'est pourquoi le `verifica 11` lance ton test avec E8
activée et exige qu'il échoue : un achat direct par l'API reste vert avec E8, et là il le rejette. Le `verifica` ne lit
pas comment ton test est écrit ; il vérifie ce qu'il fait.

---

## Étape 5 · Ce que ça coûte

Lance ta collection de la leçon 07 et ton `compra.py`, avec la boutique propre, et mesure le temps de chacun avec
`time` :

```bash
tienda reiniciar
time newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
time python3 compra.py
```

`time` affiche à la fin combien de temps la commande a mis ; regarde la ligne `real`.

Mesuré dans l'image de la boutique, avec la boutique propre :

| Test | Ce qu'il vérifie | Temps (médiane de 5) |
|---|---|---|
| Collection de la leçon 07 | 3 requêtes à l'API, 7 vérifications | 1.1 s |
| `compra.py` | 1 parcours dans le navigateur | 1.5 s |

Dans une boutique aussi petite, `compra.py` met environ 1.3 fois ce que met ta collection : peu. Mais compare ce
que vérifie chacun : la collection fait sept vérifications ; `compra.py`, un seul parcours.

Le temps n'est pas le seul coût. Un test de navigateur :

- **est plus lent** : il démarre un navigateur, charge la page et attend que chaque chose apparaisse ;
- **casse plus facilement** : si quelqu'un change un `id`, un test id ou le chemin de l'achat, le test échoue même si la
  boutique fonctionne bien ;
- **en dit moins quand il échoue** : « la commande n'est pas payée » peut venir de la page, de l'API, de la passerelle
  ou de la base de données, et il faut chercher laquelle.

C'est pourquoi les équipes dessinent leurs tests en **pyramide** : en bas, beaucoup de petits tests rapides ; au milieu,
des tests d'API comme tes collections ; en haut, **peu** de tests de navigateur. Mike Cohn, qui l'a fait connaître dans
un livre de 2009, place les tests d'interface tout en haut parce qu'on veut en avoir le moins possible. Martin Fowler le
dit ainsi : les tests qui passent par l'interface sont fragiles, chers à écrire et longs à lancer. Et chez Google, même
avec beaucoup de tests des autres types, on recommande de garder un **petit** nombre de tests de bout en bout pour
vérifier le système complet.

**Règle pratique de ce cours** (ce n'est pas une loi : c'est comment nous l'appliquons à cette boutique) : les règles
qui vivent dans l'API se testent par l'API ; dans le navigateur va le parcours qui ne peut pas échouer et ce que seule
la page peut montrer.

**Qu'est-ce qui va en haut, alors, dans cette boutique.** Le parcours qui ne peut pas échouer, et ce qui ne se voit que
dans la page. Acheter, c'est les deux : si Marta ne peut pas acheter, la boutique ne sert à rien, et dans la scène les
collections étaient vertes. Que le coupon ne s'utilise qu'une fois, que Luis ne voie pas les commandes de Marta ou
qu'un paiement tardif soit concilié n'a pas besoin du navigateur : tes collections le vérifient plus vite et, quand
elles échouent, elles te disent où.

---

## Comment on vérifie

**Ton test** est contrôlé par `verifica 11`. Enregistre-le dans `~/practica` sous le nom `compra.py` et, dans le
terminal de la boutique, écris :

```bash
verifica 11
```

Le `verifica` :

1. vérifie que ton `compra.py` n'a pas écrit à la main l'adresse, `Marta` ni son mot de passe (les commentaires ne
   comptent pas) ;
2. le lance avec la boutique propre : il doit **se terminer par 0**, et la boutique doit avoir une commande **payée** de
   Marta ;
3. le lance avec E8 activée : il **ne doit pas se terminer par 0**. S'il se termine par 0, ton test ne vérifie pas ce que
   la boutique a enregistré, ou il n'utilise pas la page.

Il passe à ton test l'adresse, la cliente et le mot de passe par l'environnement ; tu n'as pas besoin de tes `export`
pour le lancer. Il active et désactive E8 tout seul. Il redémarre la boutique avant chaque lancement et à la fin, donc
il **efface tes commandes, ton panier et ta session** (la page te demande de te reconnecter) ; ce qui revient comme
c'était, ce sont les erreurs que tu avais activées. Il laisse à ton test jusqu'à 2 minutes par lancement.

```text
Vérification de la leçon 11…

✅ Ton fichier compra.py est dans ~/practica
✅ Ton compra.py n'écrit pas en dur l'adresse, Marta ni son mot de passe : tout vient de l'environnement
✅ Avec la boutique propre, ton compra.py se termine avec 0 et la boutique a la commande payée
✅ Avec l'erreur E8 activée, ton compra.py se termine avec 1 : ton test voit que la commande n'a pas été payée

🎉 Leçon terminée !
```

Il met environ 8 secondes.

**Avant de considérer la leçon comme terminée, vérifie :**

- [ ] `compra.py` est dans `~/practica`.
- [ ] Il lit `TIENDA_URL`, `CLIENTE` et `CONTRASENA` avec `os.environ`.
- [ ] Il trouve le bouton **Ajouter au panier** avec `get_by_test_id`.
- [ ] Après **Payer**, il attend que le panier tombe à 0.
- [ ] La dernière vérification regarde l'**état** dans « Mes commandes », pas le message.
- [ ] Avec la boutique propre il se termine par 0 ; avec E8, non.
- [ ] Dans ton test n'apparaissent ni `localhost`, ni `Marta`, ni le mot de passe (cherche-les avec
      `grep -n -i -e localhost -e marta -e practica compra.py` ; il ne doit rien afficher).
- [ ] Tu as laissé E8 désactivée (`tienda error estado`).

---

## Tes exercices

1. **Le test qui croit le message.** Fais une copie (`cp compra.py mensaje.py`) et, dans la copie, remplace les trois
   dernières vérifications (à partir de `pagina.click("#ver-pedidos")`) par une seule :

   ```python
   expect(pagina.locator("#mensaje")).to_contain_text("payée")
   ```

   Prédis : avec la boutique propre, vert ou rouge ? Et avec E8 ? Lance les deux. Quand tu as fini, désactive E8 et
   `rm mensaje.py`.
2. **API ou navigateur ?** (sans IA). Pour chaque scénario, décide si tu le testes avec une collection d'API ou avec le
   navigateur, et écris pourquoi en une ligne.

   | Scénario | API ou navigateur ? | Pourquoi |
   |---|---|---|
   | Le coupon BIENVENIDA10 ne peut s'utiliser qu'une fois (leçon 09) | | |
   | Luis ne peut pas voir les commandes de Marta (leçon 08) | | |
   | Le bouton « Payer » envoie le paiement (cette étape 1) | | |
   | Un paiement qui arrive en retard laisse la commande payée (leçon 10) | | |
   | Marta peut se connecter, acheter un t-shirt et le voir payé | | |
   | Le bouton « Ajouter au panier » de chacun des produits du catalogue fonctionne | | |

3. **Combien attendre.** Dans ton `compra.py`, enlève la ligne qui attend que le panier tombe à 0 après le paiement, et
   lance le test dix fois avec la boutique propre :

   ```bash
   for i in 1 2 3 4 5 6 7 8 9 10; do tienda reiniciar > /dev/null; python3 compra.py > /dev/null; echo $?; done
   ```

   Sortent-ils dix zéros ? Prédis avant de lancer. Quand tu as fini, remets la ligne.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Dans la scène, pourquoi les collections de l'équipe sont-elles sorties vertes ? (étape 1)
2. Pourquoi le bouton « Ajouter au panier » porte-t-il un test id et pourquoi le test ne le cherche-t-il pas par son
   texte ? (étape 2)
3. Pourquoi le test vérifie-t-il l'état dans « Mes commandes » et pas le message de la page ? (étapes 2 et 4)
4. Pourquoi un `compra.py` qui paie par l'API ne te sert-il à rien ici, même s'il achète pour de vrai ? (étape 4)
5. Si les tests de navigateur trouvent ce que ceux d'API ne voient pas, pourquoi ne pas tous les écrire ainsi ? (étape
   5)

---

## Pour conclure

Jusqu'à la leçon 10, tu as testé la boutique par l'API, qui est l'endroit où vit presque tout : les prix, les coupons,
les permissions, les paiements. Cette leçon a testé la seule chose que l'API ne peut pas voir : ce que la page fait
avec elle.

Ce que tu en retires :

- **Il y a des erreurs qui ne se voient que dans la page.** Avec E8, ta collection paie sans problème et Marta ne peut pas acheter
  depuis la page. Aucune collection ne le voit.
- **Un test de navigateur vérifie ce que la boutique a enregistré, pas ce que la page dit.** Le message de paiement
  sortait pareil avec E8 ; l'état de la commande, non.
- **Cherche les éléments par quelque chose qui ne change pas :** dans une page en cinq langues, le test id et pas le
  texte.
- **Le test de navigateur est le plus cher** : plus lent, plus fragile et plus difficile à lire quand il échoue. On le
  réserve au parcours qui ne peut pas échouer, et tout le reste se teste plus bas.

Dans la leçon 12, tu portes ce que tu as trouvé à celui qui doit le corriger : un rapport qui se comprend à la première
lecture.

---

## Compare tes réponses

**Étape 1, la prédiction.** **Vert**, les sept coches. Ta collection paie par l'API, et l'API fonctionne. E8 ne touche que
le paiement qui arrive depuis le bouton de la page, et ta collection ne passe jamais par lui.

**Étape 3, la prédiction.**

Il met un peu plus que ta collection : dans la mesure, 1.5 seconde contre 1.1 (médiane de cinq lancements chacun). Si
tu as prédit beaucoup plus, ce n'est pas étonnant : dans cette petite boutique la différence est faible, et l'étape 5
explique pourquoi le temps n'est pas le seul coût.

**Exercice 1.** Avec la boutique propre, **vert**. Avec E8, aussi **vert** : la page écrit « Commande 1 payée. Merci
pour ton achat ! » même si elle n'a pas envoyé le paiement, et le test ne regardait que cela. Il est passé par la page, a
fait les mêmes clics que Marta et n'a pourtant pas vu l'erreur, parce qu'il a vérifié ce que la page dit et non ce que la
boutique a enregistré.

Mesuré : les deux lancements affichent « ✅ la cliente a acheté et sa commande est payée » et se terminent par `0`.

**Exercice 2.**

| Scénario | API ou navigateur ? | Pourquoi |
|---|---|---|
| Le coupon ne s'utilise qu'une fois | API | La règle vit dans l'API ; ton script de la leçon 09 la vérifie en quelques secondes, même avec deux commandes en même temps |
| Luis ne voit pas les commandes de Marta | API | La permission, c'est l'API qui la décide ; une page qui cache un bouton ne protège rien si l'API répond |
| Le bouton « Payer » envoie le paiement | Navigateur | Cela ne se voit que dans la page : avec E8, le paiement que le bouton envoie n'est pas prélevé, et celui de ta collection l'est |
| Le paiement tardif laisse la commande payée | API | Cela se passe entre la boutique et la passerelle, après que la page a déjà répondu |
| Marta se connecte, achète et la voit payée | Navigateur | C'est le parcours qui ne peut pas échouer ; s'il échoue, la boutique ne vend pas |
| Le « Ajouter au panier » de chaque produit | Navigateur, mais **un seul**, pas tous | Chaque produit utilise le même bouton et le même appel ; en tester un dans le navigateur vérifie le bouton, et les prix de tous se vérifient plus vite par l'API |

La dernière ligne n'a pas une seule bonne réponse. Si tu as répondu « API », c'est bien si ta raison est que le panier se
vérifie par l'API ; si tu as répondu « navigateur pour tous », demande-toi combien de temps cela prendrait et ce que cela
trouverait qu'un seul produit ne trouve pas.

**Exercice 3.**

Presque toujours oui, et c'est bien le problème. Dans la mesure, nous avons lancé ta boucle de dix lancements deux fois
dans chacune des cinq langues : cent lancements. Quatre-vingt-dix-neuf sont sortis en `0` ; **un est sorti en `1`**,
avec la commande en `creado`. Sans l'attente, le test a cliqué sur « Mes commandes » avant que le paiement soit
terminé, et la commande n'est jamais passée à payée : il a attendu 5 secondes et elle est restée en `creado`. La
boutique répond en millisecondes, donc presque toujours le paiement gagne ; une fois sur cent, non. Dans une autre mesure, cent lancements de plus sont tous sortis en `0` : la
panne est rare, et c'est pour ça qu'elle est si difficile à voir. Un test comme
celui-là passe au rouge de temps en temps sans que la boutique ait la moindre erreur, et plus personne ne lui fait
confiance. C'est pourquoi on attend quelque chose qui change **seulement** quand l'action est terminée, comme le
panier à 0.

**Révision.**

1. Parce qu'elles testaient l'API, et l'API allait bien. L'erreur était dans la page : le bouton « Payer » ne demandait
   pas à l'API de prélever.
2. Parce que le texte change avec la langue : « Ajouter au panier », « Add to cart », « Добави в количката ». Le test id
   est le même dans les cinq, et Playwright le considère comme la façon la plus résistante de trouver un élément.
3. Parce que le message est ce que la page dit, et l'état est ce que la boutique a enregistré. Avec E8, le message dit
   payée et la commande reste créée.
4. Parce qu'il ne passe pas par le bouton « Payer », qui est ce qui échoue. Il sort vert avec E8, et le `verifica 11` le
   rejette pour cela.
5. Parce qu'ils coûtent plus cher : ils sont plus lents, ils cassent quand la page change même si la boutique
   fonctionne, et quand ils échouent ils ne te disent pas où est le problème. On les garde pour ce qui ne peut pas échouer
   et pour ce qui ne se voit que dans la page.

---

## Sources de la leçon

1. Martin Fowler, « TestPyramid » (consulté le 22 novembre 2026). « In short, tests that run end-to-end through
   the UI are: brittle, expensive to write, and time consuming to run. » ; « Most people know about the the Test Pyramid
   due to Mike Cohn, when he described it in his 2009 book Succeeding with Agile. »
   https://martinfowler.com/bliki/TestPyramid.html
2. Mike Cohn, « The Forgotten Layer of the Test Automation Pyramid », Mountain Goat Software (consulté le 22
   novembre 2026). « Automated user interface testing is placed at the top of the test automation pyramid because
   we want to do as little of it as possible. »
   https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid
3. Mike Wacker, « Just Say No to More End-to-End Tests », Google Testing Blog (2015 ; consulté le 22 novembre
   2026). « Even with both unit tests and integration tests, you probably still will want a small number of end-to-end
   tests to verify the system as a whole. »
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
4. Playwright pour Python, « Library » (consulté le 22 novembre 2026). « By default, Playwright runs the
   browsers in headless mode. »
   https://playwright.dev/python/docs/library
5. Playwright pour Python, « Locators » (consulté le 22 novembre 2026). « Testing by test ids is the most
   resilient way of testing as even if your text or role of the attribute changes, the test will still pass. »
   https://playwright.dev/python/docs/locators
6. Playwright, « Best Practices » (consulté le 22 novembre 2026). « The end user will see or interact with what
   is rendered on the page, so your test should typically only see/interact with the same rendered output. »
   https://playwright.dev/docs/best-practices
7. Playwright pour Python, « Assertions » (consulté le 22 novembre 2026). « By default, the timeout for
   assertions is 5 seconds. »
   https://playwright.dev/python/docs/test-assertions
8. Python, documentation de `os.environ` et de `sys.exit` (consulté le 22 novembre 2026). « A mapping object
   where keys and values are strings that represent the process environment. » ; « zero is considered “successful
   termination” and any nonzero value is considered “abnormal termination” by shells and the like. »
   https://docs.python.org/3/library/os.html · https://docs.python.org/3/library/sys.html
