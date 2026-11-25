# Leçon 13 — Ton test sert-il à quelque chose ?

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

**Avant de lire, trois mots.** Une ligne chacun ; les autres arrivent à l'étape où ils servent.

- **Semer une erreur :** la mettre exprès pour voir si tes tests la remarquent. Dans la boutique, tu le fais avec
  `tienda error EX on`.
- **Survivre :** une erreur survit quand tu la sèmes et que tous tes tests restent verts.
- **Bénir une erreur :** un test la bénit quand il passe au vert **parce qu'**il attend le mauvais résultat.

**Ce que tu en retires :** un tableau qui dit quelles erreurs de la boutique tes tests voient et lesquelles ils ne
voient pas, et un script de tests hérités dans lequel tu as trouvé et corrigé le test qui protégeait une erreur.

**Idée de QA nouvelle de cette leçon (la seule) :** un test ne sert que s'il passe au rouge quand l'erreur est là. Tant
que tu ne l'as pas vu rouge, un test ne t'a pas encore donné la preuve qu'il détecte cette erreur.

**Dans quel ordre :** tu vois pourquoi un vert ne suffit pas (étape 1) ; tu sèmes les huit erreurs dans tes
collections (étape 2) ; tu comprends pourquoi presque toutes survivent (étape 3) ; tu trouves le test qui bénit une
erreur (étape 4) ; et tu appliques la même règle à des tests écrits par une IA (étape 5).

---

## La scène

*Scénario inventé ; les réponses, les tests et les erreurs de la boutique, eux, sont réels.*

Une équipe hérite de la boutique d'une autre. Avec le code arrive un script de cinq tests du panier, et les cinq
passent au vert. « Au moins le panier est testé », dit quelqu'un, et personne ne le rouvre.

Trois mois plus tard, une cliente se plaint : elle a monté un panier d'exactement $999.00 et on lui a facturé $99.00 de
livraison. C'est l'erreur de la leçon 02. Quand l'équipe la corrige, le script de tests passe au **rouge**. L'un des
cinq tests attendait les $99.00. Il était vert depuis trois mois parce que l'erreur était là.

---

## Avant de commencer

**Il te faut la boutique levée.** Comme dans les leçons 06 à 12 : `./practicar` sur ton ordinateur et, dans une autre
fenêtre, le terminal de la boutique. Tout se fait **à l'intérieur**, dans ton dossier `~/practica`.

> **Cette leçon utilise la boutique de la leçon 11**, avec les huit erreurs, de E1 à E8. Si `tienda error estado` t'en
> montre moins, mets ta boutique à jour avant de continuer.

**Il te faut tes collections** de la leçon 07 (`tienda.postman_collection.json`) et de la 08
(`permisos.postman_collection.json`), avec ton environnement `local.postman_environment.json` **comme tu l'as laissé à
la leçon 08**, avec `otra_cliente` et `otra_contrasena`. Si tu y as changé quelque chose ensuite, remets-les comme
elles étaient quand elles ont passé leur `verifica`.

**Ce que tu sais déjà et que tu vas utiliser :** de la leçon 02, la règle de la livraison gratuite à partir de
$999.00 ; de la 03, qu'avec un coupon la livraison gratuite se mesure **après** la remise ; de la 07, `newman run` ;
de la 09, le code de sortie (0 est vert), `$(…)` et les fonctions de bash ; de la 11, les variables de
l'environnement avec `export` ; et des leçons 04, 08, 09, 10 et 11, quelle erreur chacune a trouvée.

**Fais l'exercice 2 sans IA.** Ainsi tu t'entraînes à vérifier l'attendu avec ton propre jugement, ce qui est
justement ce que cet exercice entraîne.

**Commence propre :**

```bash
tienda reiniciar
tienda error estado
```

Les huit erreurs doivent dire « désactivée ».

---

## Étape 1 · Un vert qui n'a jamais été rouge

Quand un test passe au vert, il y a deux explications possibles : la boutique fonctionne, ou le test ne regarde pas ce
que tu crois. De l'extérieur, elles se ressemblent. La seule façon de les distinguer, c'est de **mettre l'erreur
exprès** et de voir si le test passe au rouge.

Les équipes qui le font sérieusement utilisent des outils qui sèment de petites erreurs dans le code, une par une, et
lancent les tests à chaque fois. On appelle ça le **test de mutation**. La documentation de PIT, un de ces outils,
l'explique en deux lignes : si tes tests échouent, la mutation est tuée ; s'ils passent, la mutation a survécu. Le
pourcentage de mutations que tes tests tuent est un signal utile de leur capacité à détecter les défauts. Google l'a
évalué dans sa revue de code, avec plus de 24 000 programmeurs.

Dans la boutique, tu n'as pas besoin d'outil : les huit erreurs sont déjà semées et tu les allumes avec une commande.
C'est la même idée, à la main.

**Attention à un chiffre qu'on confond avec celui-ci : la couverture**, le pourcentage du code que tes tests touchent.
Martin Fowler avertit qu'un chiffre de couverture élevé est trop facile à atteindre avec des tests de mauvaise
qualité. Toucher le code, ce n'est pas le vérifier : un test peut passer par le calcul de la livraison et ne jamais
comparer le résultat à quoi que ce soit.

---

## Étape 2 · Sème les huit erreurs

Tu vas allumer chaque erreur, seule, lancer tes deux collections et noter si elles sont passées au rouge. Huit erreurs
fois deux collections, cela fait seize lancements ; une boucle les fait pour toi.

**D'abord, sans aucune erreur.** Un rouge dans la boucle ne veut rien dire si la collection ne sort pas verte avec la
boutique propre. Si une collection échoue pour une autre raison (un fichier absent, un environnement sans
`otra_cliente`, la boutique éteinte), dans la boucle elle sortirait rouge avec toutes les erreurs et elle aurait l'air
de toutes les attraper.

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Les deux doivent se terminer sans aucune vérification échouée. Si l'une échoue, corrige-la avant de continuer : la
boucle cache la sortie de newman et tu ne verrais plus pourquoi.

Maintenant écris ceci dans un fichier, `~/practica/siembra.sh` :

```bash
for e in E1 E2 E3 E4 E5 E6 E7 E8; do
  tienda error $e on > /dev/null
  tienda reiniciar > /dev/null
  newman run tienda.postman_collection.json -e local.postman_environment.json > /dev/null && L07=vert || L07=rouge
  tienda reiniciar > /dev/null
  newman run permisos.postman_collection.json -e local.postman_environment.json > /dev/null && L08=vert || L08=rouge
  echo "$e  07: $L07  08: $L08"
  tienda error $e off > /dev/null
done
```

Ce qui est nouveau tient en une seule ligne : `&& L07=vert || L07=rouge`. Après `&&` vient ce qu'on fait **si la
commande d'avant s'est terminée par 0**, et après `||`, ce qu'on fait **sinon**. C'est le code de sortie de la leçon
09, utilisé pour décider. (Comme `L07=vert` n'échoue jamais, `L07=rouge` ne s'exécute que lorsque newman a échoué.) Le
reste, tu le connais : `> /dev/null` jette la sortie pour que tu ne voies que le résumé, et chaque tour allume
l'erreur, redémarre, lance et éteint.

Si tu interromps la boucle à mi-chemin (avec Ctrl+C), une erreur peut rester allumée : lance `tienda error estado` et
éteins celle qui dit « activée ».

**Prédis avant de lancer :** avec lesquelles des huit erreurs crois-tu que chaque collection passe au rouge ? Écris-le.

```bash
bash siembra.sh
```

```text
E1  07: rouge  08: vert
E2  07: vert  08: vert
E3  07: vert  08: vert
E4  07: vert  08: vert
E5  07: vert  08: rouge
E6  07: vert  08: vert
E7  07: vert  08: vert
E8  07: vert  08: vert
```

Voilà ce que ça a donné avec les collections d'exemple du cours, en huit secondes environ. Si tes collections ne sont
pas identiques à celles d'exemple, ton tableau peut sortir différent : ce qui compte, c'est le **tien**.

Reporte ton résultat dans un fichier, `~/practica/siembra.md`, avec cette forme :

```markdown
| Erreur | Une est-elle passée au rouge ? | Laquelle |
|---|---|---|
| E1 | oui | 07 |
| E2 | non | |
| E3 | non | |
| E4 | non | |
| E5 | oui | 08 |
| E6 | non | |
| E7 | non | |
| E8 | non | |
```

Deux erreurs éliminées, six survivantes. Et les deux collections sortent vertes avec la boutique propre, donc
jusqu'à aujourd'hui tu les voyais aussi bonnes l'une que l'autre.

À la fin, vérifie que tout est éteint :

```bash
tienda error estado
```

---

## Étape 3 · Pourquoi elles survivent

Six erreurs survivent, et ce n'est pas parce que tes collections sont mal faites. Chaque erreur vit à un endroit de la
boutique, et un test ne l'élimine que s'il **passe par cet endroit, avec la condition qui la réveille**.

| Erreur | Ce qu'elle fait | Ce qu'il faut pour la voir | Où tu l'as vue |
|---|---|---|---|
| E2 | Coupon deux fois | Deux commandes de la même cliente avec le coupon, payées **en même temps** | Leçon 09, `al-mismo-tiempo.sh` |
| E3 | Annule ce qui est livré | Une commande qui **avance** jusqu'à expédiée ou livrée | Leçons 04 et 12 |
| E4 | Prélève deux fois au nouvel essai | Une passerelle **lente** et un nouvel essai avec la même clé | Leçon 08 |
| E6 | Date en UTC | L'horloge de la boutique **à des heures indues**, comme la nuit du 31 décembre | Leçon 09, `tienda reloj` |
| E7 | Le paiement tardif n'est pas concilié | Une passerelle qui **met** 7 secondes | Leçon 10 |
| E8 | La page ne laisse pas payer | Payer **depuis la page**, avec le bouton | Leçon 11, `compra.py` |

Dans la boucle, tes collections de la 07 et de la 08 tournent avec la passerelle qui approuve instantanément,
l'horloge à l'heure réelle, un paiement à la fois, sans faire avancer de commandes et sans ouvrir la page. Aucune de
ces conditions ne réveille ces six-là.

Regarde E4 : à la leçon 08, ta collection de permissions **l'a bien** attrapée, mais avec la passerelle qui mettait 7
secondes. C'est la même collection ; ce qui a changé, c'est la condition. C'est pourquoi un tableau de semis vaut pour
les conditions avec lesquelles tu as lancé, pas pour la collection dans l'abstrait.

Cela change ta façon de lire un « tout vert ». **Un vert dit que ce que tu as testé fonctionne, pas que la boutique
fonctionne.** Pour savoir ce que tu ne vois pas, tu sèmes et tu regardes ce qui survit. Chaque survivante est une
question : cette erreur m'importe-t-elle ? Si oui, il te faut le test qui la réveille.

---

## Étape 4 · Le test qui bénit

Maintenant, le cas de la scène. Copie ces tests hérités dans `~/practica/heredadas.sh` :

```bash
# Tests hérités du panier. Chacun affiche ✅ ou ❌ ; si l'un échoue, le script se termine par 1.
BASE=${TIENDA_URL:-http://localhost:8080}
FALLAS=0
revisa() {  # revisa "nom" "attendu" "obtenu"
  if [ "$2" = "$3" ]; then echo "✅ $1"; else echo "❌ $1 : attendu $2, obtenu $3"; FALLAS=1; fi
}
TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)
carrito() {  # carrito <nombre de t-shirts bleus>
  curl -s -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d "{\"cantidad\":$1}"
}
revisa "un t-shirt : sous-total" '$333.00' "$(carrito 1 | jq -r .subtotal.texto)"
revisa "un t-shirt : paie la livraison" '$99.00' "$(carrito 1 | jq -r .envio.texto)"
revisa "trois t-shirts : sous-total" '$999.00' "$(carrito 3 | jq -r .subtotal.texto)"
revisa "trois t-shirts : livraison" '$99.00' "$(carrito 3 | jq -r .envio.texto)"
revisa "deux t-shirts : paie la livraison" '$99.00' "$(carrito 2 | jq -r .envio.texto)"
exit $FALLAS
```

Comment on le lit :

| Partie | Ce qu'elle fait |
|---|---|
| `BASE=${TIENDA_URL:-http://localhost:8080}` | L'adresse de la boutique : celle de `TIENDA_URL` si tu l'as définie (leçon 11), et sinon `http://localhost:8080` |
| `FALLAS=0` | Commence sans échecs ; chaque test rouge la met à 1 |
| `revisa() { … }` | Une fonction, comme celles de la leçon 09. Elle compare l'attendu avec l'obtenu et affiche ✅ ou ❌ |
| `carrito() { … }` | Une autre fonction : met N t-shirts bleus dans le panier et renvoie le panier |
| `$1`, `$2`, `$3` | Ce que tu passes à la fonction, dans l'ordre. Dans `revisa`, le nom, l'attendu et l'obtenu |
| Les cinq lignes `revisa …` | Les cinq tests |
| `exit $FALLAS` | Se termine par 0 si tous ont passé et par 1 si l'un a échoué |

Le script lit la cliente et son mot de passe dans l'environnement, comme ton `compra.py` de la leçon 11 :

```bash
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

**D'abord, comme était la boutique dont l'équipe a hérité :** avec E1 allumée.

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ un t-shirt : sous-total
✅ un t-shirt : paie la livraison
✅ trois t-shirts : sous-total
✅ trois t-shirts : livraison
✅ deux t-shirts : paie la livraison
0
```

Cinq verts. C'est ce qu'on voyait depuis trois mois.

**Lequel bénit l'erreur ?** Il y a deux façons de le trouver, et il convient d'utiliser les deux.

**La première est de lire chaque attendu contre la règle.** La valeur attendue d'un test ne vient pas de ce que la
boutique répond : elle vient de la règle. Le glossaire de l'ISTQB le dit ainsi : le résultat attendu est le
comportement qui est prédit **à partir de la base du test**, c'est-à-dire de l'histoire, de la règle ou de
l'exigence. Prends chaque ligne et pose-lui la règle de la leçon 02, « livraison gratuite à partir de $999.00 » :

| # | Test | Attendu | Que dit la règle ? |
|---|---|---|---|
| 1 | un t-shirt : sous-total | $333.00 | Le prix du t-shirt : $333.00 ✔ |
| 2 | un t-shirt : paie la livraison | $99.00 | $333.00 est moins que $999.00 : il paie $99.00 ✔ |
| 3 | trois t-shirts : sous-total | $999.00 | 3 × $333.00 ✔ |
| 4 | trois t-shirts : livraison | $99.00 | $999.00 est « à partir de $999.00 » : livraison **gratuite**. La règle dit $0.00 ✘ |
| 5 | deux t-shirts : paie la livraison | $99.00 | $666.00 est moins que $999.00 : il paie $99.00 ✔ |

**La seconde est d'enlever l'erreur et de voir ce qui passe au rouge.** Dans une équipe, cela revient à lancer les
tests contre la version corrigée. Ici, c'est éteindre E1 :

```bash
tienda reiniciar
tienda error E1 off
bash heredadas.sh; echo $?
```

```text
✅ un t-shirt : sous-total
✅ un t-shirt : paie la livraison
✅ trois t-shirts : sous-total
❌ trois t-shirts : livraison : attendu $99.00, obtenu $0.00
✅ deux t-shirts : paie la livraison
1
```

Les deux façons désignent le **4**. Son attendu ne vient pas de la règle : tout indique qu'il a été pris dans ce que
répondait la boutique, qui avec E1 donnait $99.00. Ainsi, le test est devenu le garde du corps de l'erreur : avec
l'erreur, vert ; le jour où quelqu'un la corrige, rouge, et la première chose que pense celui qui le voit, c'est que
la correction a cassé quelque chose.

**Corrige-le.** Dans `heredadas.sh`, change l'attendu du test 4 de `'$99.00'` en `'$0.00'`. Maintenant il doit faire
le contraire de tout à l'heure :

```bash
tienda reiniciar
bash heredadas.sh; echo $?
```

```text
✅ un t-shirt : sous-total
✅ un t-shirt : paie la livraison
✅ trois t-shirts : sous-total
✅ trois t-shirts : livraison
✅ deux t-shirts : paie la livraison
0
```

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ un t-shirt : sous-total
✅ un t-shirt : paie la livraison
✅ trois t-shirts : sous-total
❌ trois t-shirts : livraison : attendu $0.00, obtenu $99.00
✅ deux t-shirts : paie la livraison
1
```

Vert sans l'erreur, rouge avec elle. **Maintenant tu l'as bien vu rouge pour la bonne raison**, et c'est cela qui la
fait servir. Éteins E1 :

```bash
tienda error E1 off
```

---

## Étape 5 · Des tests écrits par une IA

Aujourd'hui, il est courant de demander à une IA d'écrire des tests. Elle en écrit beaucoup, vite, et ils sortent
souvent verts. Ce dernier point est justement ce qu'il faut vérifier.

Meta a publié comment fonctionne son outil de génération de tests avec l'IA. Quand un
test généré échoue, l'outil ne peut pas savoir s'il a trouvé une erreur ou s'il porte simplement une comparaison
incorrecte, et ils disent que la seconde hypothèse est la plus probable. C'est pourquoi, dans son flux automatique, il
**écarte tout test qui ne passe pas à sa première exécution**. Pour eux, cela a du sens : leur outil ajoute des tests
à ceux qui existent déjà, et il ne peut pas savoir seul quel attendu est le bon.

Pense à ce que cela signifie dans une boutique qui a une erreur : un test qui passe du premier coup décrit ce que la
boutique **fait**, pas ce qu'elle **doit** faire. Si la boutique fait quelque chose de faux, ce test la bénit, comme
le test 4. L'OWASP, dans sa liste des risques des applications d'IA, le dit sans détour : ce que génère un modèle,
une personne le relit.

La règle est la même que pour n'importe quel test, d'où qu'il vienne :

1. **D'où vient l'attendu ?** De la règle ou de l'histoire, pas de ce que la boutique répond aujourd'hui.
2. **L'as-tu vu rouge ?** Sème l'erreur qu'il devrait attraper et vérifie qu'il passe au rouge.
3. **Avec quoi compare-t-il ?** Un test qui compare la boutique avec elle-même (il demande deux fois la même donnée et
   compare les deux réponses) ne vérifie aucune règle : il reste vert avec n'importe quelle erreur. Fowler cite comme
   cas le plus absurde les tests qui ne vérifient rien ; celui-ci leur ressemble beaucoup.

---

## Comment on vérifie

**Ton travail** est vérifié par le `verifica 13`. Dans `~/practica`, il lui faut trois fichiers :

- `siembra.md`, ton tableau de l'étape 2 ;
- `bendice.txt`, avec **seulement le numéro** du test qui bénissait l'erreur ;
- `heredadas.sh`, avec ce test corrigé.

Dans le terminal de la boutique, écris :

```bash
verifica 13
```

Le `verifica` :

1. lance tes collections de la 07 et de la 08, avec ton environnement, avec chaque erreur allumée seule, et compare ce
   qui s'est passé avec ton `siembra.md`, ligne par ligne (il accepte « oui » et « non », avec ou sans majuscules) ;
2. dans ce même lancement, au minimum ta collection de la 07 doit sortir rouge avec E1 et celle de la 08 avec E5,
   comme dans leurs leçons. Si elles attrapent plus d'erreurs, tant mieux ;
3. vérifie que `bendice.txt` dit le bon numéro ;
4. lance ton `heredadas.sh` avec la boutique propre : il doit se terminer par 0, avec **cinq** ✅, et le quatrième
   test doit attendre `$0.00` ;
5. le lance avec E1 allumée : il ne doit **pas** se terminer par 0.

Le point 2 existe à cause de l'exercice 3 : si tu laisses ta collection avec l'attendu changé, le tableau
sortirait honnête, mais ta collection n'attraperait plus E1. Le point 4 demande cinq ✅ pour que le test soit
corrigé, pas supprimé : sans le test 4, le script sort vert avec E1 et le point 5 le rejette. Il passe au script
l'adresse, la cliente et le mot de passe par l'environnement. Il allume et éteint les erreurs tout seul et redémarre
la boutique, donc il **efface tes commandes, ton panier et ta session**.

Quand tout est en place, le `verifica 13` donne ceci :

```text
Vérification de la leçon 13…

✅ Ton fichier tienda.postman_collection.json est dans ~/practica
✅ Ton fichier permisos.postman_collection.json est dans ~/practica
✅ Ton fichier local.postman_environment.json est dans ~/practica
✅ Ton fichier siembra.md est dans ~/practica
✅ Ton fichier bendice.txt est dans ~/practica
✅ Ton fichier heredadas.sh est dans ~/practica
✅ Ton local.postman_environment.json contient base, cliente, contrasena, otra_cliente et otra_contrasena, comme tu l'as laissé à la leçon 08
✅ Ton siembra.md a les huit lignes, de E1 à E8, avec « oui » ou « non »
✅ Ton bendice.txt dit 4 : le test qui bénissait l'erreur
✅ Le quatrième test de ton heredadas.sh attend $0.00, ce que dit la règle
✅ Avec la boutique propre, ta collection de la 07 sort en vert (3)
✅ Avec la boutique propre, ta collection de la 08 sort en vert (12)
✅ Ton siembra.md correspond à ce qui s'est passé, ligne par ligne
✅ Ta collection de la 07 passe au rouge avec E1 et celle de la 08 avec E5, comme dans leurs leçons
✅ Avec la boutique propre, ton heredadas.sh se termine par 0 avec cinq ✅
✅ Avec E1 allumée, ton heredadas.sh ne se termine pas par 0 : maintenant il attrape l'erreur

🎉 Leçon terminée !
```

Lors de la mesure, il a pris environ 22 secondes. À la fin, il laisse les erreurs comme elles étaient avant que tu
le lances, et la boutique redémarrée : Marta sans commandes, avec son panier à $0.00 et aucune session ouverte.

**Avant de considérer la leçon terminée, vérifie :**

- [ ] Avant la boucle, tes deux collections sont sorties vertes avec la boutique propre.
- [ ] `siembra.md` a huit lignes, E1 à E8, avec « oui » ou « non ».
- [ ] Chaque « oui » dit quelle collection est passée au rouge.
- [ ] Avant de lancer la boucle, tu as écrit ta prédiction, et tu l'as comparée.
- [ ] Pour chaque survivante, tu sais quelle condition manque à tes collections (étape 3).
- [ ] `bendice.txt` ne contient qu'un seul numéro.
- [ ] Dans `heredadas.sh`, le test que tu as corrigé est toujours là, avec son attendu tiré de la règle.
- [ ] Tu as vu `heredadas.sh` vert avec la boutique propre et rouge avec E1.
- [ ] Tu as laissé toutes les erreurs éteintes (`tienda error estado`).

---

## Tes exercices

1. **Réveille une survivante.** Choisis E3. Avec tes étapes de la leçon 12 (`pasos.sh`), allume E3, lance-les et
   regarde si elles passent au « rouge » : quelle ligne te dit que l'erreur est là ? Éteins E3. Pourquoi tes étapes la
   voient-elles et pas ta collection de la 07 ?
2. **Des tests écrits par une IA** (sans IA). Une IA a écrit ces six tests pour le panier, avec la même fonction
   `revisa` de l'étape 4. Tous, sauf un, sortent verts dans la boutique qu'elle avait à ce moment-là. Pour chacun,
   décide s'il est **bon**, s'il **bénit une erreur**, s'il **ne vérifie aucune règle** ou s'il **est faux**, et écris
   pourquoi en une ligne. Utilise la règle de la livraison (leçon 02) et celle du coupon avec livraison (leçon 03).

   | # | Test |
   |---|---|
   | 1 | `revisa "un t-shirt : total" '$432.00' "$(carrito 1 \| jq -r .total.texto)"` |
   | 2 | `revisa "trois t-shirts : total" '$1,098.00' "$(carrito 3 \| jq -r .total.texto)"` |
   | 3 | `revisa "trois t-shirts avec coupon : livraison" '$99.00' "…"` (trois t-shirts et le coupon BIENVENIDA10) |
   | 4 | `revisa "trois t-shirts : livraison" "$(carrito 3 \| jq -r .envio.texto)" "$(carrito 3 \| jq -r .envio.texto)"` |
   | 5 | `revisa "un t-shirt avec coupon : remise" '$0.00' "…"` (un t-shirt, essaie le coupon BIENVENIDA10 puis lis le panier) |
   | 6 | `revisa "deux t-shirts : livraison" '$0.00' "$(carrito 2 \| jq -r .envio.texto)"` |

3. **Ta collection l'attrape-t-elle ?** Ouvre ta collection de la leçon 07 et cherche le test qui est passé au rouge
   avec E1. Change son attendu pour qu'il dise ce que la boutique répond **avec** E1. Prédis : que sort-il maintenant
   dans `siembra.sh` ? Lance-le puis remets le test comme il était.

**Révision** (essaie d'en réussir au moins 4 sur 5 ; si l'une ne sort pas, retourne à l'étape indiquée) :

1. Qu'est-ce que cela veut dire qu'une erreur « survit » ? (étape 1)
2. Ta collection de la leçon 07 est verte avec E3 allumée. Cela veut-il dire que E3 ne fait pas de mal ? (étape 3)
3. Quelles sont les deux façons de trouver le test qui bénit une erreur ? (étape 4)
4. D'où vient la valeur attendue d'un test ? (étape 4)
5. Une IA te remet vingt tests, tous verts du premier coup. Que fais-tu avant de les accepter ? (étape 5)

---

## Pour conclure

Jusqu'à la leçon 12, tu as écrit des tests pour trouver des erreurs. Cette leçon a mis tes tests à l'épreuve.

Ce que tu en retires :

- **Un test sert s'il passe au rouge quand l'erreur est là.** Tant que tu ne l'as pas vu rouge, il ne t'a pas encore
  donné la preuve qu'il la détecte.
- **Semer te dit ce que tu ne vois pas.** Avec la boutique, tu le fais avec une commande ; les grandes équipes le font
  avec des outils de test de mutation. Le résultat est le même : une liste de survivantes.
- **Une erreur survit quand tes tests ne passent pas par son endroit avec la condition qui la réveille.** Ce n'est pas
  que le test soit mauvais : c'est qu'il regarde autre chose.
- **L'attendu vient de la règle, pas de ce que la boutique répond aujourd'hui.** Un test qui copie la réponse du
  système bénit n'importe quelle erreur que le système a déjà.
- **La règle vaut aussi pour les tests écrits par une IA** : d'où vient l'attendu, si tu l'as vu rouge et s'il peut
  passer au rouge.

À la leçon 14, tu rassembles tout ce que tu as appris dans une nouvelle histoire, avec les erreurs semées de la
boutique.

---

## Compare tes réponses

**Étape 2, la prédiction.** La collection de la 07 passe au rouge seulement avec E1, parce qu'elle vérifie la
livraison d'un panier de $999.00. Celle de la 08, seulement avec E5, parce qu'elle vérifie que Luis ne voit pas la
commande de Marta. E8 ne les met pas au rouge non plus : aucune des deux n'ouvre la page. Si tu as prédit plus de
rouges, ne t'inquiète pas : c'est ce que presque tout le monde attend d'un « tout vert ». L'étape 3 explique pourquoi
non.

**Exercice 1.** Avec E3, l'annulation de tes étapes répond `cancelar: HTTP 200` et la commande reste annulée avec
remboursement ; sans E3, 409. Tes étapes la voient parce qu'elles mènent la commande jusqu'à livrée puis annulent :
elles passent par l'endroit de l'erreur avec la condition qui la réveille. Ta collection de la 07 ne fait jamais
avancer une commande et n'annule rien.

**Exercice 2.**

| # | Qu'est-ce que c'est ? | Pourquoi |
|---|---|---|
| 1 | Bon | $333.00 + $99.00 de livraison = $432.00, et c'est ce que dit la règle |
| 2 | Bénit une erreur | Trois t-shirts font $999.00 : livraison gratuite, total $999.00. $1,098.00 ne sort qu'avec E1. L'IA a copié ce que répondait la boutique |
| 3 | Bon | Avec un coupon, la livraison se mesure après la remise : $999.00 − $99.90 = $899.10, moins que $999.00, donc il paie $99.00 (leçon 03) |
| 4 | Ne vérifie aucune règle | Il compare la réponse de la boutique avec la même réponse. Il sort vert avec n'importe quelle erreur |
| 5 | Bon | Le coupon est pour les achats à partir de $500.00. Avec $333.00 la boutique le refuse (422, « le coupon est réservé aux achats de $500.00 ou plus ») et le panier reste avec une remise de $0.00. Attention : la réponse du 422 ne contient pas `descuento` ; c'est pourquoi le test lit le panier ensuite |
| 6 | Est faux | Deux t-shirts font $666.00 : il paie $99.00. C'est celui qui sortait rouge, avec la boutique saine |

Le 3 et le 6 sont les difficiles. Le 3 semble bénir quelque chose parce qu'il attend de la livraison avec $999.00,
mais la règle du coupon lui donne raison. Le 6 est rouge et il n'y a aucune erreur : selon Meta, quand un test généré
échoue, le plus probable est une vérification fausse. C'est pourquoi on ne l'écarte pas sans regarder : on le lit
contre la règle et ensuite on décide.

**Exercice 3.** Avec E1, la collection de la 07 sort **verte** : maintenant elle bénit E1. Et avec la boutique propre,
elle sort rouge. Dans `siembra.sh`, la ligne de E1 devient « 07: vert ». Tu as changé un nombre et le test a cessé de
servir : c'est aussi facile d'écrire un test qui bénit.

**Révision.**

1. Que tu la sèmes et que tous tes tests restent verts : aucun ne la remarque.
2. Non. Cela veut dire que ta collection ne passe pas par là : elle ne fait jamais avancer une commande ni ne
   l'annule. E3 rend l'argent des commandes livrées.
3. Lire chaque attendu contre la règle, et enlever l'erreur (ou lancer la version corrigée) pour voir lequel passe
   au rouge.
4. De la règle, de l'histoire ou de l'exigence. Ce que le système répond aujourd'hui est justement ce que tu vérifies :
   cela ne peut pas être aussi l'attendu.
5. Vérifier d'où vient chaque attendu, semer les erreurs qu'ils devraient attraper pour les voir rouges, et écarter
   ceux qui ne peuvent pas passer au rouge.

---

## Sources de la leçon

1. PIT, « What is mutation testing? » (consulté le 22 novembre 2026). « If your tests fail then the mutation is
   killed, if your tests pass then the mutation lived. » ; « The quality of your tests can be gauged from the percentage
   of mutations killed. » https://pitest.org/
2. Stryker Mutator, « Introduction » (consulté le 22 novembre 2026). « Bugs, or mutants, are automatically
   inserted into your production code. Your tests are run for each mutant. » ; « If your tests passed, the mutant
   survived. » https://stryker-mutator.io/docs/
3. Goran Petrović, Marko Ivanković, Gordon Fraser et René Just, « Practical Mutation Testing at Scale » (arXiv, 2021 ;
   consulté le 22 novembre 2026). « Mutation analysis assesses a test suite's adequacy by measuring its
   ability to detect small artificial faults, systematically seeded into the tested program. » ; « Evaluation in a
   code-review-based setting with more than 24,000 developers on more than 1,000 projects… »
   https://arxiv.org/abs/2102.11378
4. Martin Fowler, « TestCoverage » (consulté le 22 novembre 2026). « The trouble is that high coverage numbers
   are too easy to reach with low quality testing. » ; « At the most absurd level you have AssertionFreeTesting. »
   https://martinfowler.com/bliki/TestCoverage.html
5. ISTQB, « Glossary » : *expected result* et *test oracle* (consulté le 22 novembre 2026). « The observable
   predicted behavior of a test item under specified conditions based on its test basis. » ; « A source to determine an
   expected result. » https://glossary.istqb.org/en_US/term/expected-result
6. Nadia Alshahwan et autres, « Automated Unit Test Improvement using Large Language Models at Meta » (arXiv, 2024 ;
   consulté le 22 novembre 2026). « Any test that does not pass may reveal a fault. However, it is more likely
   that the test simply contains an incorrect assertion. » ; « Therefore, […] discards any test case that does
   not pass on first execution. » https://arxiv.org/abs/2402.09171
7. OWASP Gen AI Security Project, « LLM09:2025 Misinformation » (consulté le 25 novembre 2026).
   « Implement human oversight and fact-checking processes, especially for critical or sensitive information. »; « if
   trusted without verification, leads to security risks. »
   https://genai.owasp.org/llmrisk/llm092025-misinformation/
8. GNU Bash Reference Manual, « Lists of Commands » (consulté le 22 novembre 2026). « command2 is executed if,
   and only if, command1 returns an exit status of zero (success). » ; « command2 is executed if, and only if, command1
   returns a non-zero exit status. » https://www.gnu.org/software/bash/manual/html_node/Lists.html
