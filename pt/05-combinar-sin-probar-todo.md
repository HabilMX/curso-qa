# Lição 05 — Combinar sem testar tudo

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Variável:** algo da compra que pode mudar de um teste para outro: o valor do carrinho, o cupom, o cliente, o
  idioma.
- **Valor:** cada opção que uma variável assume. O cupom tem três: sem cupom, primeira vez, já usado.
- **Combinação:** um valor de cada variável, juntos. Uma combinação é um teste.
- **Par:** dois valores de duas variáveis diferentes, juntos. «Valor $1,110.00 (pesos mexicanos) com cupom pela primeira vez» é um par.

**O que fica com você:** você monta à mão uma tabela de combinações para quatro variáveis, confere que ela cobre cada par
e decide onde vale a pena subir para combinações de três.

**Ideia nova desta lição (a única):** com poucas combinações bem escolhidas se cobre cada par de valores. Com ela você
pratica também uma decisão: onde vale a pena revisar combinações de três.

**Em que ordem vai:** você conta as combinações (passo 1), conta os pares (passo 2), monta a tabela (passo 3),
confere que ela cobre cada par (passo 4), põe nela resultados e cenários (passo 5) e decide onde subir para três
(passo 6).

---

## A cena

*Cenário inventado; os valores, as mensagens e o erro da loja são reais.*

Sexta-feira, 16:00. A loja entra no ar na segunda e o QA tem só uma tarde. Ele tem quatro coisas para mexer no resumo da
compra: o valor do carrinho, o cupom, o cliente e o idioma da loja. Testar tudo são 36 combinações, e não dá tempo.

Ele faz o que parece razoável: que **cada valor apareça pelo menos uma vez**. Três testes, e neles aparecem os três
valores, os três casos do cupom, os dois clientes e os dois idiomas. Os três saem verdes. Entra no ar na segunda.

Na terça, uma cliente escreve: montou um carrinho de $1,110.00, aplicou o cupom, o total ficou em exatos $999.00…
e cobraram $99.00 de frete. Desde a lição 02 você sabe que a partir de $999.00 o frete é grátis.

Cada valor foi testado. O que ninguém testou foi **esse par**: $1,110.00 **com** o cupom pela primeira vez. Nenhum dos
três testes os tinha juntos.

Esta lição é para escolher poucos testes sem deixar nenhum par de fora.

---

## Antes de começar

**Sem computador nos passos 1 a 4.** Papel e lápis, ou uma planilha: você vai montar uma tabela e riscar pares. Para o
passo 5 você precisa do seu editor, como nas lições anteriores.

**Faça a primeira tentativa sem IA.** O que se avalia é se **você** monta uma tabela que cobre cada par e sabe conferi-la.
Uma IA pode te dar uma tabela em segundos; a folha de pares do passo 4 é a que te diz se falta algum.

**O que você já sabe e vai usar:** da lição 04, que cada célula de uma tabela pode virar um cenário; aqui
cada linha da tabela junta quatro valores e é um cenário. E também, da lição 02, os grupos e as bordas do valor ($999.00 do frete e $3,000.00
das parcelas sem juros); da 03, o cupom BIENVENIDA10 e o mínimo dele de $500.00, e que o frete se mede depois
do desconto.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · As variáveis, os valores delas e quantas combinações são

Estas são as quatro variáveis do resumo da compra e os valores que vamos usar:

| Variável | Valores | Quantos |
|---|---|---|
| Valor do carrinho | $600.00 · $1,110.00 · $3,330.00 | 3 |
| Cupom BIENVENIDA10 | sem cupom · primeira vez · já usado | 3 |
| Cliente | Marta · Luis | 2 |
| Idioma da loja | espanhol · inglês | 2 |

Os três valores saem dos grupos da lição 02: um abaixo de $999.00, um entre $999.00 e $3,000.00 e um a partir de
$3,000.00. Os três estão acima de $500.00, para que o cupom possa entrar; o que acontece abaixo do mínimo você já
testou na lição 03.

O idioma desta tabela é um dado da loja: o idioma em que a loja fala com o cliente. Não é o idioma em que você lê esta
lição, por isso os valores dele são espanhol e inglês em todas as versões do curso.

Antes de seguir, **preveja**: quantas combinações são se você testar todas?

São 3 × 3 × 2 × 2 = **36**. Com quatro variáveis pequenas já não dá a tarde. E a loja do curso tem cinco idiomas:
com os cinco seriam 90.

---

## Passo 2 · Conte os pares

Um par junta dois valores de duas variáveis diferentes. Para contá-los, pegue as variáveis duas a duas e multiplique
os valores delas:

| As duas variáveis | Pares |
|---|---|
| Valor e cupom | 3 × 3 = 9 |
| Valor e cliente | 3 × 2 = 6 |
| Valor e idioma | 3 × 2 = 6 |
| Cupom e cliente | 3 × 2 = 6 |
| Cupom e idioma | 3 × 2 = 6 |
| Cliente e idioma | 2 × 2 = 4 |
| **Total** | **37** |

Repare em uma coisa: uma única combinação cobre **seis pares** de uma vez, um por cada linha desta tabela. Por isso
bastam menos combinações do que as 36.

O programa avançado do ISTQB para analistas de teste chama isso de **testes por pares** (*pairwise testing*):
testar cada par de valores de cada duas variáveis pelo menos uma vez, sem testar todas as combinações. Ele o usa quando
há mais combinações do que cabem no tempo, como na tarde da sexta-feira.

---

## Passo 3 · Monte a tabela à mão

Antes de seguir, **preveja**: quantas linhas você precisa no mínimo? Dica: olhe a linha maior do passo 2.

O valor e o cupom sozinhos já têm 9 pares, e cada linha cobre só um deles. Então **9 linhas é o mínimo**.
O bom é que com 9 dá para tudo, se você preencher bem as outras duas variáveis.

**1. A base.** Escreva as 9 combinações do valor e do cupom, uma por linha. Você já cobre os 9 pares deles.

**2. O cliente.** Cada valor tem de sair com Marta e com Luis, e cada caso do cupom também. Ponha Luis uma vez
em cada grupo de valor, e cada vez com um cupom diferente (linhas 2, 4 e 9). Nas demais, Marta.

**3. O idioma.** O mesmo: inglês uma vez em cada grupo de valor, cada vez com um cupom diferente (linhas 2, 6 e 7).
Nas demais, espanhol.

**4. Confira o último cruzamento.** Cliente e idioma são 4 pares: Luis-inglês (linha 2), Luis-espanhol (linhas 4 e 9),
Marta-inglês (linhas 6 e 7) e Marta-espanhol (as demais). Estão os quatro.

| # | Valor | Cupom | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sem cupom | Marta | espanhol |
| 2 | $600.00 | primeira vez | Luis | inglês |
| 3 | $600.00 | já usado | Marta | espanhol |
| 4 | $1,110.00 | sem cupom | Luis | espanhol |
| 5 | $1,110.00 | primeira vez | Marta | espanhol |
| 6 | $1,110.00 | já usado | Marta | inglês |
| 7 | $3,330.00 | sem cupom | Marta | inglês |
| 8 | $3,330.00 | primeira vez | Marta | espanhol |
| 9 | $3,330.00 | já usado | Luis | espanhol |

De 36 combinações para 9. Há ferramentas que montam essas tabelas sozinhas quando as variáveis são muitas; aqui você a monta
à mão para entender o que elas te entregam.

**Guarde-a.** Copie a tabela em um arquivo `pares.md` dentro de `~/practica`, em Markdown e com as suas quatro
colunas (a de `#` é opcional). O `verifica 05` a lê de lá. Assim começam as duas primeiras linhas:

```markdown
| # | Valor | Cupom | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sem cupom | Marta | espanhol |
| 2 | $600.00 | primeira vez | Luis | inglês |
```

Os valores se escrevem como na tabela: `primeira vez`, não «primeira»; `$1,110.00`, com vírgula e centavos.

---

## Passo 4 · Confira que cobre cada par

Antes de confiar em uma tabela, confira-a par por par. Copie esta folha e risque cada par que encontrar na tabela
do passo 3, e escreva junto à casela em que linha ele está. Assim começa: «$600 · primeira ☑ linha 2». Com o número da
linha, se algo falha você sabe qual linha mudar:

| As duas variáveis | Pares que têm de aparecer |
|---|---|
| Valor e cupom | $600 · sem ☐ · primeira ☐ · usado ☐ — $1,110 · sem ☐ · primeira ☐ · usado ☐ — $3,330 · sem ☐ · primeira ☐ · usado ☐ |
| Valor e cliente | $600 · Marta ☐ · Luis ☐ — $1,110 · Marta ☐ · Luis ☐ — $3,330 · Marta ☐ · Luis ☐ |
| Valor e idioma | $600 · espanhol ☐ · inglês ☐ — $1,110 · espanhol ☐ · inglês ☐ — $3,330 · espanhol ☐ · inglês ☐ |
| Cupom e cliente | sem · Marta ☐ · Luis ☐ — primeira · Marta ☐ · Luis ☐ — usado · Marta ☐ · Luis ☐ |
| Cupom e idioma | sem · espanhol ☐ · inglês ☐ — primeira · espanhol ☐ · inglês ☐ — usado · espanhol ☐ · inglês ☐ |
| Cliente e idioma | Marta · espanhol ☐ · inglês ☐ — Luis · espanhol ☐ · inglês ☐ |

Se sobrar uma casela sem riscar, a sua tabela não tem esse par: mude um valor de uma linha ou acrescente uma.

**Faça a prova ao contrário.** Apague a linha 9 e risque de novo. Sobram três caselas sem riscar: $3,330 com já
usado, $3,330 com Luis, e já usado com Luis. Cada linha carrega pares que nenhuma outra tem.

**E compare com a tabela da cena.** Os três testes de «cada valor uma vez» foram estes:

| # | Valor | Cupom | Cliente | Idioma |
|---|---|---|---|---|
| A | $600.00 | sem cupom | Marta | espanhol |
| B | $1,110.00 | já usado | Marta | inglês |
| C | $3,330.00 | primeira vez | Luis | espanhol |

Risque os pares deles em uma folha nova: cobrem **18 de 37**. E o par da cliente, $1,110.00 com cupom pela primeira vez,
não está.

---

## Passo 5 · Resultados esperados e cenários

A tabela diz **o que** testar, não o que tem de acontecer. Quando uma ferramenta monta as combinações, o programa do
ISTQB indica que quem testa põe nelas o resultado esperado. Em uma tabela à mão acontece o mesmo: você decide o que deve
acontecer em cada linha. Estes são os da loja, medidos em 21/11/2026:

| # | O que tem de acontecer |
|---|---|
| 1 | Frete $99.00, total $699.00, sem parcelas sem juros |
| 2 | Desconto $60.00, frete $99.00, total $639.00 |
| 3 | O cupom não entra: «ya usó este cupón»; total $699.00 |
| 4 | Frete $0.00, total $1,110.00 |
| 5 | Desconto $111.00, o total fica em $999.00 e o frete é $0.00 |
| 6 | O cupom não entra: «this coupon was already used»; total $1,110.00 |
| 7 | Total $3,330.00, aparecem as parcelas sem juros |
| 8 | Desconto $333.00, total $2,997.00: **as parcelas sem juros já não aparecem** |
| 9 | O cupom não entra; o total continua em $3,330.00 e as parcelas sem juros aparecem |

Olhe a linha 8. Com $3,330.00 há parcelas sem juros, e o cupom pela primeira vez funciona; mas **juntos**, o
desconto baixa o total de $3,000.00 e a opção desaparece. É o que diz a regra da lição 02, e mesmo assim
surpreende quem não viu vir. Esse tipo de surpresa vive nos pares.

Cada linha vira um cenário, com frases do catálogo. A linha 5, a da cliente:

```gherkin
# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00
```

As linhas em inglês vão em um arquivo à parte, `pares-en.feature`, com `# language: en`, porque o idioma da loja é o
arquivo que define.
Assim fica a linha 7:

```gherkin
# language: en
Feature: The purchase summary, by pairs

  Scenario: Row 7 · $3,330.00, no coupon, Marta, English
    Given Marta has no coupon applied
    And she has products worth $3,330.00 in her cart
    When she chooses how to pay
    Then the interest-free installments option appears
```

> **Um limite do catálogo.** Depois de «elige cómo pagar» dá para conferir se aparecem as parcelas sem juros,
> mas já não o frete nem o desconto. Se o cupom entrou, depois de aplicá-lo você pode conferir desconto, frete e
> parcelas. Se o cupom não entrou, a loja só responde com a mensagem dela; para ver o que aconteceu com a conta, escolha
> como pagar e confira as parcelas. Por isso cada cenário confere o mais importante da sua linha, não tudo o que está na
> tabela de resultados.

**Agora você:** em um arquivo `pares.feature`, copie o cenário da linha 5 de cima e escreva os das linhas 1, 4 e 9.
Para a 9, o **Então** confere que as parcelas sem juros continuam aparecendo: é a forma de comprovar que o cupom não
entrou.

---

## Passo 6 · Quando subir para três?

Por pares não é testar tudo. Se um erro precisa de **três** valores juntos para aparecer, a tabela de pares pode não
tê-los.

Com que frequência acontece? O NIST (o instituto de padrões dos Estados Unidos) resume estudos próprios e de outras
equipes, que eles mesmos chamam de não conclusivos: na maioria das falhas observadas bastou um único valor ou dois
valores juntos, e nos seis estudos resumidos chegou-se a precisar de 4 a 6. O programa do ISTQB cita um sobre dispositivos médicos: 66% das falhas com uma variável e 97% com uma
ou duas. E o NIST adverte que por pares pode deixar passar entre 10% e 40% ou mais dos erros de um sistema, então não
basta para software crítico.

Por isso se sobe para três **onde o risco pede**, não em tudo. Três perguntas ajudam a decidir:

1. **Ali se move dinheiro?** Um erro ali cobra a mais ou a menos de alguém.
2. **Essas variáveis se afetam entre si segundo as regras?** O valor, o cupom e as parcelas sem juros sim; o
   idioma quase não muda a conta.
3. **Quanto isso é usado?** Uma combinação que acontece em toda compra pesa mais do que uma rara.

Subir para três só para três variáveis custa: valor, cupom e cliente têm 3 × 3 × 2 = 18 ternas, e a tabela do
passo 3 cobre 9. Para ter todas você precisa de pelo menos 18 linhas.

---

## Como se confere

**A sua tabela** (passo 3 e exercício 1) se confere com a folha de pares do passo 4: **nenhuma casela sem riscar**.

**A sua tabela e o seu arquivo** são revisados pelo `verifica 05`. No terminal da loja, escreva:

```bash
verifica 05
```

Primeiro ele lê `~/practica/pares.md` e confere que a sua tabela cobre os 37 pares. Depois roda `pares.feature`, junto
com qualquer outro `pares*.feature` que você tenha (como `pares-en.feature`), com a loja limpa, onde têm de sair
**verdes**, e com o erro E1 ligado, onde **pelo menos um tem de sair vermelho**. Se saem verdes nas duas vezes, ele diz
que ainda falta um cenário que olhe o ponto onde está o erro.

Antes de rodá-lo, a folha de pares do passo 4 e a lista abaixo dizem se você vai bem. Os cenários das 9 linhas foram
rodados contra a loja antes de publicar esta lição: 9 verdes com a loja limpa; com o erro ligado, a linha 5 em
vermelho.

**Antes de salvar, revise o seu arquivo com esta lista:**

- [ ] Há um arquivo por idioma, e a primeira linha de cada um é o seu `# language:`.
- [ ] O título de cada cenário diz a sua linha e os seus quatro valores.
- [ ] O **Dado** põe o valor, o cupom e o cliente da linha.
- [ ] O **Então** confere um resultado da tabela do passo 5 para essa linha.
- [ ] Nenhum cenário mistura valores de duas linhas.

---

## Os seus exercícios

1. **Cinco idiomas** (sem IA). Mude a variável idioma para os cinco da loja: espanhol, inglês, francês,
   português e búlgaro. Quantas combinações são se você testar todas? Quantas linhas você precisa no mínimo para cobrir
   cada par? Monte a tabela e confira-a com uma folha de pares. Dica para montá-la: faça um bloco por valor e, em cada
   bloco, escreva uma linha por idioma; depois distribua o cupom e o cliente dentro dos blocos, como no passo 3,
   para que cada valor saia com cada outro. Use 25 minutos como limite.
2. **Qual pega o erro?** Com o erro E1 ligado, o frete deixa de ser grátis quando o que se paga pela
   mercadoria é exatamente $999.00. Sem rodar nada, diga quais linhas da tabela do passo 3 ficam vermelhas e por que
   os três testes da cena saem verdes.
3. **Onde você sobe para três?** (sem IA). Com as três perguntas do passo 6, escolha **uma** terna de três variáveis desta
   lição onde você subiria para combinações de três e outra onde não. Justifique cada uma em duas linhas.

**Revisão** (tente resolver pelo menos 5 de 6; se algum não sair, volte ao passo 2):

1. Três variáveis de 4, 3 e 2 valores. Quantas combinações são todas?
2. Nessas mesmas três variáveis, quantos pares há?
3. Por que a tabela de pares desta lição não pode ter menos de 9 linhas?
4. O que te diz uma casela sem riscar na folha de pares?
5. Por que não basta que cada valor saia pelo menos uma vez?
6. Variáveis de 2, 2 e 3 valores, e uma tabela com 3 linhas. Ela pode cobrir cada par? Por quê?

---

## Para fechar

Ao QA não faltou cuidado na sexta: ele testou cada valor. Faltou testar os valores **juntos**, de dois em dois, e para
isso não faziam falta 36 testes: bastavam 9.

O que você leva daqui:

- Todas as combinações são a **multiplicação** dos valores; crescem muito rápido.
- Um **par** são dois valores de duas variáveis; uma combinação cobre vários pares de uma vez.
- A tabela **por pares** cobre cada par pelo menos uma vez, com muito menos linhas.
- Ela se **confere** com a folha de pares: nenhuma casela sem riscar.
- O resultado esperado de cada linha **quem põe é você**.
- Por pares não é tudo: se sobe para três **onde o risco pede**.

Na lição 06 você deixa a página e as frases do catálogo, e fala com a API diretamente, à mão.

---

## Compare as respostas

**Passo 1, previsão.** 3 × 3 × 2 × 2 = 36.

**Passo 3, previsão.** 9: valor e cupom sozinhos têm 9 pares, e cada linha cobre só um deles.

**Passo 3, o seu `pares.md`.** A tabela do passo 3, tal qual:

```markdown
| # | Valor | Cupom | Cliente | Idioma |
|---|---|---|---|---|
| 1 | $600.00 | sem cupom | Marta | espanhol |
| 2 | $600.00 | primeira vez | Luis | inglês |
| 3 | $600.00 | já usado | Marta | espanhol |
| 4 | $1,110.00 | sem cupom | Luis | espanhol |
| 5 | $1,110.00 | primeira vez | Marta | espanhol |
| 6 | $1,110.00 | já usado | Marta | inglês |
| 7 | $3,330.00 | sem cupom | Marta | inglês |
| 8 | $3,330.00 | primeira vez | Marta | espanhol |
| 9 | $3,330.00 | já usado | Luis | espanhol |
```

**Passo 5, o seu `pares.feature`.** As linhas 1, 4, 5 e 9, como foram rodadas contra a loja:

```gherkin
# language: es
Característica: El resumen de la compra, por pares

  Escenario: Fila 1 · $600.00, sin cupón, Marta, español
    Dado que Marta no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $600.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $99.00

  Escenario: Fila 4 · $1,110.00, sin cupón, Luis, español
    Dado que Luis no tiene ningún cupón aplicado
    Y tiene en su carrito productos por $1,110.00
    Cuando pasa a pagar
    Entonces el envío que le muestra la tienda es de $0.00

  Escenario: Fila 5 · $1,110.00, cupón por primera vez, Marta, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Marta no ha usado nunca el cupón BIENVENIDA10
    Y tiene en su carrito productos por $1,110.00
    Cuando aplica el cupón BIENVENIDA10
    Entonces la tienda le muestra un descuento de $111.00
    Y el envío que le muestra la tienda es de $0.00

  Escenario: Fila 9 · $3,330.00, cupón ya usado, Luis, español
    Dado que el cupón BIENVENIDA10 está vigente
    Y que Luis ya usó el cupón BIENVENIDA10 en una compra anterior
    Y tiene en su carrito productos por $3,330.00
    Cuando aplica el cupón BIENVENIDA10
    Y elige cómo pagar
    Entonces la opción de meses sin intereses aparece
```

**Exercício 1.** Todas: 3 × 3 × 2 × 5 = 90. O mínimo é dado pelo cruzamento maior, valor e idioma ou cupom e idioma:
3 × 5 = **15 linhas**. Uma forma de chegar, já conferida (61 de 61 pares): três blocos de cinco linhas, um por valor,
com os cinco idiomas na mesma ordem em cada bloco (espanhol, inglês, francês, português, búlgaro). O cupom, por
bloco: em $600, sem–primeira–usado–sem–primeira; em $1,110, primeira–usado–sem–primeira–usado; em $3,330,
usado–sem–primeira–usado–sem. O cliente: Marta–Luis–Marta–Luis–Marta nos blocos de $600 e $3,330, e
Luis–Marta–Luis–Marta–Luis no de $1,110. Se a sua folha de
pares não tem caselas sem riscar, a sua tabela vale ainda que não seja igual à de outra pessoa.

**Exercício 2.** Só a linha 5: $1,110.00 com o cupom pela primeira vez é a única em que o que se paga pela
mercadoria fica em exatos $999.00. É o que aconteceu ao rodá-las: com E1 ligado, a linha 5 em vermelho e as outras
oito em verde. Os três testes da cena saem verdes com E1 (também foram rodados) porque nenhum tem esse par:
o B tem $1,110.00 mas com o cupom já usado, que não entra, e o C tem o cupom mas com $3,330.00.

**Exercício 3.** Uma resposta defensável: **sim** para valor, cupom e cliente, porque ali se move dinheiro, as três
se afetam entre si (o cupom é de uma vez só por cliente e muda o total) e acontece em muitas compras. **Não** para
cliente, idioma e cupom juntos, porque o idioma muda os textos, não a conta. Se você escolheu outra e a justifica com
as três perguntas, também vale.

**Revisão.** 1, 4 × 3 × 2 = 24. 2, 4 × 3 + 4 × 2 + 3 × 2 = 26. 3, porque valor e cupom têm 9 pares e cada linha
cobre um. 4, que a sua tabela não tem esse par. 5, porque um erro pode precisar de **dois** valores juntos, e «cada
valor uma vez» não os junta. 6, não: as duas variáveis de 2 valores têm 2 × 2 = 4 pares entre elas, e cada linha
cobre só um; com 3 linhas sempre falta pelo menos um.

---

## Fontes da lição

1. ISTQB, *Certified Tester Advanced Level Test Analyst (CTAL-TA) Syllabus* v3.1.2 (errata de 2022-01-31), §3.2.6 «Pairwise
   Testing» (pp. 32–33). «Pairwise testing is used when testing software in which several input parameters, each with
   several possible values, must be tested in combination, giving rise to more combinations than are feasible to test
   in the time allowed»; «a table is constructed with test cases represented by rows and one column for each
   parameter»; «the Test Analyst must supply the expected results for each combination that is created by the
   tools»; «66% of failures were triggered by a single variable and 97% by either one variable or two variables
   interacting»; «There is a residual risk that pairwise testing may not detect systems failures where three or more
   variables interact»; «The 100% pairwise coverage requires every pair of values of any pair of parameters be
   included in at least one combination». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
2. D. Richard Kuhn, Raghu N. Kacker e Yu Lei, *Practical Combinatorial Testing*, NIST Special Publication 800-142,
   outubro de 2010. «the number of interactions involved in system failures is relatively low, with a maximum from 4
   to 6 in the six studies cited»; «pairwise testing may miss 10% to 40% or more of system bugs, and is thus not
   sufficient for mission-critical software». https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-142.pdf

Medição própria: as variáveis, os resultados esperados e as mensagens foram medidos contra a loja do curso
(hb-curso-qa, develop 0ddda22) em 21 de novembro de 2026, com a API dela no ar sem Docker. As 9 linhas foram rodadas
com behave e somente frases do catálogo: 9 de 9 em verde com a loja limpa; com o erro E1 ligado, a linha 5 em
vermelho. Os 3 testes de «cada valor uma vez» também foram rodados: verdes com E1 desligado e com E1 ligado. A
cobertura de pares de cada tabela foi contada com um script (37 de 37 e 18 de 37), e ao tirar a linha 9 ele marcou os três
pares que se perdem.

Regras do curso, sem fonte externa:

- «As três perguntas para subir para três» (dinheiro, regras que se cruzam, uso): são a forma como este curso aterrissa
  o «segundo o risco» do ISTQB nesta loja.
