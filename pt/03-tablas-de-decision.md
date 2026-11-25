# Lição 03 — Tabelas de decisão

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Condição:** uma pergunta que o sistema se faz e que se responde com sim ou não. «O cliente aplicou o cupom?»
  é uma condição.
- **Ação:** o que o sistema faz conforme as respostas: descontar, cobrar o frete, mostrar um aviso.
- **Tabela de decisão:** uma tabela com as condições e as ações nas linhas, e em cada coluna uma
  combinação de respostas com o que o sistema deve fazer.
- **Combinação:** as respostas de todas as condições juntas. Com três condições de sim ou não são oito.

**O que fica com você:** quando várias regras decidem juntas, você monta a tabela de decisão delas, torna visíveis as
combinações que ninguém definiu e as transforma em perguntas para o negócio; depois escreve um cenário para cada
coluna, e sabe qual deles pega o erro que uma regra sozinha não deixa ver.

**Ideia nova desta lição (a única que se avalia):** quando várias condições decidem juntas, uma tabela
mostra a regra que ninguém escreveu.

**Em que ordem vai:** você encontra as condições e as ações (passo 1), preenche todas as combinações (passo 2),
tira as impossíveis e junta as que dão igual (passo 3), procura a coluna que ninguém definiu e a transforma em pergunta
(passo 4), e escreve um cenário para cada coluna (passo 5).

---

## A cena

*Cenário inventado; os valores e as mensagens da loja são reais.*

Terça-feira, 17:30. Ramiro, de marketing, manda para a equipe a promoção de fim de mês:

> «Cupom BIENVENIDA10: 10% em compras a partir de $500 (pesos mexicanos). E frete grátis a partir de $999. As duas
> podem ser usadas juntas!»

A programação implementa isso à noite. O QA testa o cupom com um carrinho de $1,200: desconto de $120, frete grátis.
Testa o frete com um carrinho de $999 sem cupom: frete grátis. As duas regras funcionam. Sai na quarta-feira.

Na quinta-feira, uma cliente escreve irritada. Montou um carrinho de $999 justamente para não pagar frete, colocou o
cupom, o total baixou para $899.10… e cobraram $99 de frete. Uma hora depois escreve outra: carrinho de $1,050, cupom,
$99 de frete. As duas citam o anúncio: «frete grátis a partir de $999».

Ninguém errou ao testar cada regra. O problema está **onde as duas regras se cruzam**: os $999 do frete grátis
são contados antes ou depois do cupom? Ramiro não escreveu isso, a programação escolheu uma forma, e ninguém
perguntou porque ninguém olhou as duas regras **ao mesmo tempo**.

Esta lição é para olhá-las ao mesmo tempo. E para que essa pergunta apareça na terça-feira, na mesa, e não na quinta
no atendimento ao cliente.

---

## Antes de começar

**Sem computador nos passos 1 a 4.** Papel, ou uma planilha se você preferir: uma tabela de decisão é
literalmente uma tabela. Para o passo 5 você precisa do seu editor, como nas lições 01 e 02.

**Faça a primeira tentativa sem IA.** O que se avalia é se **você** encontra a coluna que ninguém definiu. Uma IA
pode preencher a tabela bem rápido, e o mais fácil é ela escolher uma resposta para a casela que ninguém definiu e
escrevê-la como se fosse regra, que é o mesmo que a programação fez com Ramiro. Com a sua tabela na
mão, depois sim você pode comparar.

**O que você já sabe e vai usar:** da lição 01, que um cenário sai de uma regra e que o que ninguém sabe se
escreve como pergunta; da 02, as bordas, sobretudo a de $999.00.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Encontre as condições e as ações

Leia de novo o e-mail de Ramiro e separe em duas listas: **o que o sistema pergunta** e **o que o sistema
faz**.

O que pergunta, cada coisa como pergunta de sim ou não:

| # | Condição |
|---|---|
| C1 | O cliente tenta aplicar o cupom `BIENVENIDA10`? |
| C2 | O subtotal é de $500.00 ou mais? |
| C3 | O subtotal é de $999.00 ou mais? |

O que faz:

| # | Ação |
|---|---|
| A1 | Desconta 10% do subtotal |
| A2 | Avisa: «o cupom é para compras de $500.00 ou mais» |
| A3 | Frete grátis |
| A4 | Frete de $99.00 |

Dois detalhes que não são óbvios:

- **C1 diz «tenta».** Tentar aplicar o cupom e ele ficar aplicado não são a mesma coisa: com menos de $500.00 o
  cliente tenta e a loja o rejeita com um aviso. Essa diferença é justamente a coluna 5.
- **C2 e C3 se escrevem com o «ou mais».** É a borda da lição 02: $500.00 exatos contam, $999.00
  exatos também. Se a regra não diz se a borda entra, isso já é uma pergunta (lição 01).
- **«O subtotal» é o que os produtos somam, sem desconto e sem frete.** Escrevemos assim de propósito. No
  passo 4 você vai ver que essa é justamente a palavra que esconde o problema.

---

## Passo 2 · Preencha todas as combinações

Uma **tabela de decisão completa** tem uma coluna para cada combinação de respostas. Com três condições de sim
ou não são 2 × 2 × 2 = **8 colunas**.

Para não pular nenhuma, preencha-as com um padrão: a última condição muda a cada coluna, a do meio a cada
duas, a primeira a cada quatro.

O programa do ISTQB escreve T/F nas condições e permite outras notações; aqui usamos **S** (sim) e **N** (não). Nas
ações, como no programa, **X** se a ação acontece e vazio se não.

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| C1 Tenta aplicar o cupom? | N | N | N | N | S | S | S | S |
| C2 Subtotal a partir de $500? | N | N | S | S | N | N | S | S |
| C3 Subtotal a partir de $999? | N | S | N | S | N | S | N | S |

Agora, antes de preencher as ações, **preveja**: existe alguma coluna que não possa existir? Escreva e siga em frente.

---

## Passo 3 · Tire o impossível, junte o que dá igual

**O impossível.** As colunas 2 e 6 pedem um subtotal **menor** que $500 e **de $999 ou mais** ao mesmo tempo. Nenhum
carrinho cumpre isso. O programa do ISTQB as chama de combinações **impossíveis** (*infeasible*) e se marcam **N/A**:
não se testam, porque não há dado que as produza.

Sobram seis colunas possíveis. Preencha as ações delas com o que diz o e-mail de Ramiro:

| | 1 | 3 | 4 | 5 | 7 | 8 |
|---|---|---|---|---|---|---|
| C1 Tenta aplicar o cupom? | N | N | N | S | S | S |
| C2 Subtotal a partir de $500? | N | S | S | N | S | S |
| C3 Subtotal a partir de $999? | N | N | S | N | N | S |
| A1 Desconta 10% | | | | | X | X |
| A2 Aviso do mínimo | | | | X | | |
| A3 Frete grátis | | | X | | | **?** |
| A4 Frete de $99.00 | X | X | | X | X | **?** |
| **Um carrinho de exemplo** | $480.00 | $998.99 | $999.00 | $499.99 | $998.00 | ??? |

**O que dá igual.** Olhe as colunas 1 e 3: sem cupom, a resposta de C2 não muda nada; as duas cobram frete.
Quando uma condição não afeta o resultado, as colunas podem ser **juntadas** em uma só, e nessa condição se
escreve **–** («não importa»). Assim a tabela fica mais curta e você tem um cenário a menos para escrever. Juntar é
opcional; o importante é não juntar duas colunas cujas ações **são** diferentes.

---

## Passo 4 · A coluna que ninguém definiu

Olhe a coluna 8: cupom aplicado e um subtotal de $999 ou mais. Há desconto, claro. E o frete?

O e-mail de Ramiro diz «frete grátis a partir de $999» e «as duas podem ser usadas juntas». Com um subtotal de $999.00 e
o cupom, o cliente paga $899.10 pelos produtos. Já não chega a $999? Depende de uma palavra que o e-mail não
diz: **os $999 se medem antes ou depois do desconto?**

Essa é a **regra que ninguém escreveu**. Neste exemplo o problema começa no requisito, antes do código:
há um buraco. A tabela o torna visível, porque obriga você a preencher uma casela que nem Ramiro nem a programação
preencheram.

O que você faz com uma casela assim é o mesmo que com um cartão vermelho da lição 01: **você a escreve como pergunta
e a leva a quem decide.** Ainda não a responda: assim a decisão fica nas mãos do negócio, e não do código
por acidente.

> **Pergunta para o negócio:** «Com o cupom aplicado, o frete grátis a partir de $999.00 se mede sobre o subtotal (antes
> do desconto) ou sobre o que o cliente paga pelos produtos (depois do desconto)?»

**O que a loja de prática decidiu.** Para esta loja, a resposta já existe: o frete grátis se mede
**depois** do cupom. É uma decisão de negócio, não a única correta; outra loja poderia decidir o contrário e
estaria bem, desde que a **escreva**.

Com essa resposta, a coluna 8 deixa de ser uma só. É preciso parti-la pelo que o cliente paga **depois** do
desconto. Para isso falta uma condição nova, C3': ela já não olha o subtotal, e sim o que o cliente paga pelos
produtos já com o desconto. Sem cupom, as duas dão o mesmo; com cupom, é preciso fazer a conta.

| | 8a | 8b |
|---|---|---|
| C1 Tenta aplicar o cupom? | S | S |
| C2 Subtotal a partir de $500? | S | S |
| C3' O que paga **já com o cupom** é a partir de $999? | N | S |
| A1 Desconta 10% | X | X |
| A3 Frete grátis | | X |
| A4 Frete de $99.00 | X | |
| **Um carrinho de exemplo** | $999.00 → paga $899.10 | $1,110.00 → paga $999.00 |

Repare no exemplo da 8b. Um subtotal de $1,110.00 com o cupom fica em **exatamente $999.00**: está bem
na borda da lição 02, mas agora a borda aparece **depois de uma conta**. Um cenário que
testa uma única regra não a procura aí. Para chegar lá, é preciso combinar o cupom com o frete e escolher o subtotal de
propósito.

> **De onde sai $1,110.00.** Se o que se paga depois dos 10% tem de ser $999.00, o subtotal é
> $999.00 ÷ 0.9 = $1,110.00. Na loja de prática, três Camisetas azuis ($333.00 cada uma) e um Boné
> ($111.00) somam isso.

**Olhe agora a coluna 7 com a C3'.** Um subtotal de $998.00 com cupom paga $898.20: C3' é «não», igual à
8a. Têm as mesmas respostas e as mesmas ações, então são **uma única coluna**, a 7 + 8a. O melhor
exemplo dela é o da 8a ($999.00), porque é o carrinho que antes do desconto chegava lá.

**A tabela final** tem seis colunas possíveis: 1, 3, 4, 5, 7 + 8a e 8b (ou cinco, se você juntou a 1 e a 3). Cada
uma é um cenário.

---

## Passo 5 · Um cenário por coluna

Na lição 01 você aprendeu que cada cenário testa uma regra. Aqui cada cenário testa **uma coluna**: uma
combinação completa de condições. Por isso o cenário tem de fixar **todas** as condições da coluna, não
só uma: o **Dado** põe o ponto de partida (o cupom vigente e sem uso, o que há no carrinho) e o
**Quando**, o que o cliente faz (aplicar o cupom ou ir pagar sem ele).

Use as frases do catálogo da loja que você já conhece. Um **E** continua o tipo do passo anterior, então
«E ela tem no carrinho…» depois de um Dado também é um Dado do catálogo. Assim fica a coluna 8b:

```gherkin
# language: pt
Funcionalidade: Cupom e frete grátis juntos

  Regra: Com cupom, o frete se mede sobre o que se paga depois do desconto

    Cenário: Coluna 8b · com cupom, já com desconto chega a $999.00
      Dado que o cupom BIENVENIDA10 está vigente
      E que Marta nunca usou o cupom BIENVENIDA10
      E ela tem no carrinho produtos no valor de $1,110.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela um desconto de $111.00
      E o frete que a loja mostra a ela é de $0.00
```

Leia o **Então**: ele confere as duas ações da coluna, o desconto e o frete. Se você conferisse só o desconto,
o cenário sairia verde mesmo com o frete errado, e a coluna não ficaria testada.

**Agora você:** em um arquivo `promocion.feature`, copie a 8b e escreva um cenário para cada uma das colunas
3, 4, 5 e 8a. Use o carrinho de exemplo de cada uma. Agrupe-os com `Regra:` como na lição 01: uma regra para «sem
cupom» e outra para «com cupom».

**Quantos cenários bastam.** O programa do ISTQB mede a cobertura desta técnica como as colunas
possíveis que você testou divididas pelo total de colunas possíveis. Com a 1 e a 3 juntas, a tabela final tem cinco
colunas, e os seus cinco cenários (3, 4, 5, 8a e 8b) cobrem as cinco. O cenário da 3 testa a coluna 1 + 3
com um carrinho que também cumpre a C2. Uma ressalva honesta: na coluna 5 você só pode olhar o aviso. A loja
rejeita o cupom e nessa resposta não devolve o carrinho, então o frete dessa coluna fica sem ser observado.
Por isso dizemos «cinco colunas cobertas, uma com uma ação sem olhar», e não 100% limpos. Se um dia uma tabela tem
colunas demais, testam-se primeiro as de maior risco; para isso serve o que você viu na lição 00 sobre o
percurso crítico.

---

## Como se confere

**A tabela** (passos 1 a 4 e o exercício 1) se compara com «Compare as respostas». O que tem de coincidir:
que não falte nenhuma combinação possível, que as impossíveis estejam marcadas, e que você tenha escrito a pergunta da
coluna 8 **antes** de ler a resposta da loja.

**O seu arquivo `promocion.feature`** é revisado pelo `verifica 03`. No terminal da loja, escreva:

```bash
verifica 03
```

Ele roda os seus cenários duas vezes: com a loja limpa têm de sair **verdes**, e com o erro desta lição ligado,
**pelo menos um tem de sair vermelho**. Se saem verdes nas duas vezes, ele diz: «os seus testes não olham onde está o
erro». Antes de rodá-lo, a lista abaixo diz se a forma está certa. Os cenários de «Compare as respostas» foram rodados
contra a loja antes de publicar esta lição, junto com o que você copia do passo 5: verdes com a loja limpa, e dois em
vermelho com o erro ligado.

**Antes de salvar, revise o seu arquivo com esta lista:**

- [ ] A primeira linha é `# language: pt`.
- [ ] Há um cenário para cada coluna pedida, e o título diz qual coluna é.
- [ ] Entre o **Dado** e o **Quando**, cada cenário fixa **todas** as condições da sua coluna: o subtotal, e se
  aplica o cupom ou não.
- [ ] O **Então** confere **todas** as ações da sua coluna que a loja deixa você ver.
- [ ] Nenhum subtotal está «perto» de uma borda por acaso: se é uma borda, você a escolheu de propósito.

---

## Os exercícios

1. **A promoção de parcelas** (sem IA). Ramiro manda outra: «Parcelas sem juros a partir de $3,000. E com o cupom
   BIENVENIDA10, também». Na loja, as parcelas sem juros vão de $3,000.00 até $50,000.00.
   - Escreva as condições e as ações.
   - Preencha a tabela completa, marque as impossíveis e junte as que dão igual.
   - Encontre **pelo menos uma** coluna sem ação definida e escreva-a como pergunta para Ramiro. Dica: o total
     de uma compra tem mais de uma parte.
   Use 25 minutos como limite.
2. **Cenários** (sem IA). Escreva os cenários das colunas 3, 4, 5 e 8a do passo 5, se você não os escreveu lá.
3. **Qual pega o erro?** A loja traz um erro plantado: com ele ligado, o frete grátis é dado só **acima**
   de $999.00, não **a partir de** $999.00. Sem rodar nada, escreva quais dos seus cinco cenários ficam vermelhos com
   esse erro, e por que os demais continuam verdes.

**Revisão** (quantas colunas tem a tabela completa, sem tirar nada? Tente resolver pelo menos 4 de 5; é prática
do passo 2, não a avaliação da lição):

1. Duas condições de sim ou não.
2. Quatro condições de sim ou não.
3. Três condições de sim ou não, e uma delas se torna irrelevante quando outra é «não». (Sem juntar.)
4. Uma condição de sim ou não e outra com três respostas possíveis (por exemplo: menos de $500, de $500 a $998.99, e
   $999 ou mais).
5. Cinco condições de sim ou não.

---

## Para fechar

Ramiro não escreveu mal a promoção: escreveu duas regras que, cada uma por si, estavam certas. O que ninguém
escreveu foi o que acontece **quando elas se juntam**. Uma tabela de decisão não deixa você pular essa parte, porque tem
uma casela para cada combinação, e uma casela vazia se nota.

O que você leva daqui:

- Quando várias condições decidem juntas, **uma coluna por combinação**. Com *n* condições de sim ou não são
  2 × 2 × … (*n* vezes).
- As combinações **impossíveis** se marcam e não se testam; as que **dão igual** podem ser juntadas.
- Uma casela que ninguém sabe preencher é uma **pergunta para o negócio**, não uma decisão sua nem do código.
- Cada coluna é um cenário, e entre o seu **Dado** e o seu **Quando** eles fixam todas as condições da coluna.
- As bordas também aparecem **depois de uma conta**, e aí é fácil deixá-las passar.

Na lição 04 você muda de pergunta: já não é que combinação de dados chega, e sim **em que ordem** as coisas acontecem.
Um pedido criado, pago, enviado, entregue, cancelado… e o que acontece se alguém tenta um passo fora da sua vez.

---

## Compare as respostas

**Passo 2, previsão.** As colunas 2 e 6 não podem existir: um subtotal não pode ser menor que $500 e de $999 ou
mais ao mesmo tempo.

**Passo 3.** A tabela de seis colunas possíveis, como está no passo. **A tabela final** (depois do passo 4, com a
7 e a 8a já juntas), se você também juntou a 1 e a 3, fica assim:

| | 1 + 3 | 4 | 5 | 7 + 8a | 8b |
|---|---|---|---|---|---|
| C1 Tenta aplicar o cupom? | N | N | S | S | S |
| C2 Subtotal a partir de $500? | – | S | N | S | S |
| C3' A partir de $999 (sem cupom: o subtotal; com cupom: o que paga já com o cupom)? | N | S | N | N | S |
| A1 Desconta 10% | | | | X | X |
| A2 Aviso do mínimo | | | X | | |
| A3 Frete grátis | | X | | | X |
| A4 Frete de $99.00 | X | | X | X | |

**Passo 4, a pergunta.** Qualquer redação serve se perguntar o mesmo: com cupom, o frete grátis se mede antes ou
depois do desconto? Se você a escreveu como afirmação («se mede depois»), transforme-a agora em pergunta: assim a
decisão fica nas mãos do negócio.

**Passo 5, os cenários.** Estes são os que foram rodados contra a loja (a coluna 8b está no passo 5):

```gherkin
# language: pt
Funcionalidade: Cupom e frete grátis juntos

  Regra: Sem cupom, o frete é grátis a partir de $999.00

    Cenário: Coluna 4 · sem cupom, a partir de $999.00
      Dado que Marta não tem nenhum cupom aplicado
      E ela tem no carrinho produtos no valor de $999.00
      Quando ela vai pagar
      Então o frete que a loja mostra a ela é de $0.00

    Cenário: Coluna 3 · sem cupom, abaixo de $999.00
      Dado que Marta não tem nenhum cupom aplicado
      E ela tem no carrinho produtos no valor de $998.99
      Quando ela vai pagar
      Então o frete que a loja mostra a ela é de $99.00

  Regra: Com cupom, o frete se mede sobre o que se paga depois do desconto

    Cenário: Coluna 5 · com cupom, abaixo do mínimo do cupom
      Dado que o cupom BIENVENIDA10 está vigente
      E que Marta nunca usou o cupom BIENVENIDA10
      E ela tem no carrinho produtos no valor de $499.99
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja diz a ela que o cupom é para compras de $500.00 ou mais

    Cenário: Coluna 8a · com cupom, antes do desconto chegava e depois não
      Dado que o cupom BIENVENIDA10 está vigente
      E que Marta nunca usou o cupom BIENVENIDA10
      E ela tem no carrinho produtos no valor de $999.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela um desconto de $99.90
      E o frete que a loja mostra a ela é de $99.00
```

**Exercício 1.** Uma forma da pergunta: «Com o cupom, os $3,000 se medem sobre o subtotal, sobre o que paga
pelos produtos já com o desconto, ou sobre o total com o frete incluído?». Na loja de prática, as parcelas
se medem sobre o **total**; um total de $3,000.00 exatos entra. Se você encontrou outra coluna sem definir que
se sustenta (por exemplo, o que acontece com um total acima de $50,000.00 e o cupom), também vale.

**Exercício 3.** Ficam vermelhos os cenários em que o que se paga pelos produtos fica em **exatamente**
$999.00: o da 4, com um carrinho de $999.00 sem cupom, e o da 8b, com $1,110.00 e cupom. É o que aconteceu ao
rodá-los: dois em vermelho. Os demais continuam verdes porque o erro só muda o que acontece em $999.00 exatos. O da 3,
com $998.99, é o vizinho imediato da borda (lição 02) e deve $99.00 com ou sem o erro.

Repare em uma coisa: a coluna 4 você já tinha desde a lição 02. A 8b é nova. As duas pegam o mesmo erro, mas
a 8b o pega **em uma combinação**, uma combinação que também pode acontecer com um cliente: com o cupom dele colocado.

**Revisão.** 1, quatro (2 × 2). 2, dezesseis (2 × 2 × 2 × 2). 3, oito: a tabela completa tem todas as
combinações mesmo que depois você junte algumas. 4, seis (2 × 3). 5, trinta e duas (2⁵).

**Se você não acertou 4,** volte ao passo 2: a conta é multiplicar quantas respostas tem cada condição.

---

## Fontes da lição

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.3 «Decision Table Testing» (p. 41).
   As condições e as ações são as linhas e cada coluna é uma combinação única; a notação T/F
   (aqui S/N), «–» para o que não importa, N/A para o impossível, X para a ação que acontece; a tabela completa, a
   que tira o impossível e a que junta colunas; a cobertura como colunas testadas divididas por colunas possíveis; e
   que a técnica ajuda a encontrar buracos e contradições nos requisitos.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. ISTQB, *Certified Tester Advanced Level Test Analyst Syllabus* v3.1.2, §3.2.3 «Decision Table Testing»: «the
   inputs of the test case might be different parameters than in the conditions of the decision table» e o
   exemplo de uma condição que «may require the tester to calculate». Sustenta a C3', que pede fazer a conta.
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTAL-TA_Syllabus_v3.1.2.pdf
3. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action»; «Then steps are used to describe an expected outcome, or
   result». Sustenta a divisão entre Dado, Quando e Então. https://cucumber.io/docs/gherkin/reference/
4. behave, «Tutorial»: «The “and” and “but” step types are renamed internally to take the preceding step’s keyword».
   Sustenta que um E continua o passo anterior. https://behave.readthedocs.io/en/stable/tutorial/
5. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». Sustenta transformar o buraco em pergunta. https://cucumber.io/docs/bdd/

Medição própria: os cenários das colunas 3, 4, 5, 8a e 8b foram rodados com behave contra a loja do curso
(HabilMX/curso-qa) em 21 de novembro de 2026. Com a loja limpa, 5 de 5 em verde; com o erro E1
ligado, 2 em vermelho (4 e 8b). Os valores ($111.00, $99.90, $899.10) e o aviso do mínimo saem dessa rodada.

Regras do curso, sem fonte externa:

- «Uma casela que ninguém sabe preencher é uma pergunta para o negócio»: existe para que o buraco do requisito seja fechado
  por quem decide, e não pelo código por acidente.
- «Entre o Dado e o Quando se fixam todas as condições da coluna»: existe para que, se o cenário falhar,
  você saiba qual combinação falhou.
