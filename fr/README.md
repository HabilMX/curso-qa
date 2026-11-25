[Español](../es/README.md) · [English](../en/README.md) · **Français** · [Português](../pt/README.md) · [Български](../bg/README.md)

# QA depuis zéro : des scénarios qui trouvent les erreurs

**Par Dorian Chávez, fondateur de Hábil et architecte d'intégration.**

Un cours ouvert et gratuit pour apprendre à tester un logiciel en **trouvant de vraies erreurs**. Tu t'entraînes sur
une boutique en ligne inventée qui contient huit erreurs plantées exprès, et ton travail est d'écrire les tests qui les
trouvent : des scénarios, des tests d'API qui tournent tout seuls, un test de navigateur et des rapports qu'une autre
personne peut reproduire.

> Le cours existe en cinq langues : espagnol (la source), anglais, français, portugais du Brésil et bulgare.

## Pour qui

Pour celles et ceux qui débutent en QA, ou qui programment et veulent mieux tester : stagiaires, étudiants et
développeurs. Tu n'as besoin d'aucune expérience préalable en tests ; en revanche, tu dois être à l'aise dans le
terminal. Si tu ne l'as jamais utilisé, commence par le cours « Le terminal depuis zéro ».

## Ce qu'il te faut

- Un ordinateur avec **Docker**. La boutique et tout ce que tu utilises pour la tester (behave, curl, newman et un
  navigateur sans fenêtre) sont fournis à l'intérieur : tu n'installes rien d'autre.
- **Git**, pour télécharger ce dépôt.
- Un terminal. Chaque leçon te dit quoi taper.

Mesuré sous Linux x86_64 avec Docker 29 : l'image pèse environ 1.3 Go, elle se construit en 2 minutes environ la
première fois, la boutique démarre en 2 secondes et, au repos, elle utilise environ 56 Mo de mémoire. Sous macOS et sous
Windows avec WSL2, ce n'est pas encore mesuré.

## Comment démarrer la boutique

```bash
git clone <dirección de este repositorio>
cd <carpeta del repositorio>
./practicar
```

La première fois, la commande construit l'image, puis te laisse dans le terminal de la boutique. La page est à
l'adresse **http://localhost:8080**. De là, tu suis la leçon 00, qui t'apprend à vérifier que tout fonctionne et à
utiliser `verifica 00`, la commande qui contrôle ton travail à la fin de chaque leçon.

## Les 15 leçons

| # | Leçon | Ce que tu en retires |
|---|---|---|
| 00 | [Ta boutique d'entraînement](00-tu-tienda-de-practica.md) | La boutique qui tourne sur ton ordinateur, et le moyen de vérifier que l'API et la page répondent |
| 01 | [De l'histoire au scénario](01-de-la-historia-al-escenario.md) | Séparer une histoire d'utilisateur en règles, exemples et scénarios avant de toucher au système |
| 02 | [Groupes et bords](02-grupos-y-orillas.md) | Découper les données d'une règle en groupes et tester juste à leurs bords, là où se cachent les erreurs |
| 03 | [Tables de décision](03-tablas-de-decision.md) | Une table qui montre toutes les combinaisons quand plusieurs règles décident ensemble |
| 04 | [États et ordre](04-estados-y-orden.md) | Les états d'une commande, sa table, et les cases vides auxquelles personne n'a pensé |
| 05 | [Combiner sans tout tester](05-combinar-sin-probar-todo.md) | Une table de combinaisons qui couvre chaque paire de valeurs avec peu de tests |
| 06 | [Tester une API à la main](06-probar-una-api-a-mano.md) | Parler à l'API avec `curl`, lire chaque réponse et prédire ce qu'elle va répondre |
| 07 | [Des tests d'API qui tournent tout seuls](07-pruebas-de-api-que-corren-solas.md) | Une collection qui teste un achat avec une seule commande et passe au rouge quand il y a une erreur |
| 08 | [Permissions et nouveaux essais](08-permisos-y-reintentos.md) | Tester sans session, avec une autre cliente, et rejouer un paiement avec la même clé sans payer deux fois |
| 09 | [En même temps et à des heures indues](09-al-mismo-tiempo-y-a-deshoras.md) | Des paiements qui arrivent en même temps et des dates qui changent de jour selon l'heure |
| 10 | [Quand l'autre système tombe en panne](10-cuando-el-otro-sistema-falla.md) | Vérifier que l'état d'une commande et l'argent concordent quand la passerelle de paiement est lente |
| 11 | [Le navigateur, seulement pour ce qui est critique](11-el-navegador-solo-para-lo-critico.md) | Un test de navigateur pour ce qui ne se voit que sur la page, et pourquoi on s'en sert peu |
| 12 | [Signaler pour qu'on le corrige](12-reportar-para-que-lo-arreglen.md) | Un rapport avec des étapes que n'importe qui peut coller et reproduire, avec gravité et priorité |
| 13 | [Ton test sert-il à quelque chose ?](13-tu-prueba-sirve.md) | Planter des erreurs pour savoir lesquelles tes tests voient, et trouver le test qui protège une erreur |
| 14 | Rassemble tout : l'histoire du lundi | Une histoire complète, testée par risque avec tout ce qui précède, et ta place par rapport à l'examen ISTQB CTFL |

Chaque leçon se termine par son `verifica`, qui exécute ton travail contre la boutique propre et contre la boutique
avec l'erreur de la leçon activée, et te dit ce qui manque.

## Jusqu'où il va

La leçon 14 te situe par rapport au programme ISTQB CTFL : ce que tu as abordé et ce qui reste en dehors. Le cours n'est
ni un examen ni un certificat. Les tests de charge, d'accessibilité et de sécurité approfondie restent volontairement
de côté : chacun mérite son propre cours.

## Qui fait ce cours

Hábil construit et teste des systèmes qui ne peuvent pas tomber en panne : backend, intégrations, web et applications.
Si ton équipe veut de l'aide pour ses tests, la première conversation est sans frais : [habil.mx](https://www.habil.mx).

---

Tu maintiens le cours ou la boutique ? Les commandes de `./practicar` et comment lancer les tests sont dans [MANTENIMIENTO.md](../MANTENIMIENTO.md) (en espagnol).
