# Lição 02 — Grupos e bordas

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, cinco palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Grupo:** um conjunto de valores que o sistema deveria tratar do mesmo jeito. «Qualquer quantidade de 1 a 10 peças»
  é um grupo. Nos livros se chama *partição de equivalência*.
- **Grupo inválido:** os valores que o sistema tem de rejeitar. «0 peça» e «a palavra *dois*» estão em grupos
  inválidos.
- **Borda:** o menor ou o maior valor de um grupo. Em «de 1 a 10», as bordas são 1 e 10. Nos livros se chama *valor
  limite*.
- **Vizinho:** o valor que está colado a uma borda, do outro lado ou do mesmo lado. O vizinho de 10 para fora é 11;
  para dentro, 9.
- **Precisão:** o menor passo que faz sentido em um dado. Em peças é 1; nos pesos deste curso, um centavo.

**O que fica com você:** você recebe uma regra e, antes de mexer no sistema, divide os dados dela em grupos (inclusive
os que têm de ser rejeitados); escolhe um valor por grupo; encontra as bordas de cada grupo e escolhe os valores de
teste delas com **dois** ou com **três** valores por borda; e os escreve em uma única tabela de Gherkin.

**Ideia nova desta lição (a única que se avalia):** os erros se juntam nas **bordas** das regras. Um limite mal
colocado aparece justamente na borda; um valor do meio quase sempre o deixa passar.

**Em que ordem vai:** você divide uma regra em grupos (passo 1), encontra as bordas dela (passo 2), decide quando vale a
pena um terceiro valor (passo 3), aprende por que a borda do dinheiro se mede em centavos (passo 4) e escreve tudo em
uma tabela de cenários (passo 5). No fim, você faz sozinho o mesmo com duas regras novas e compara as suas respostas.

---

## A cena

*Cenário inventado.*

Segunda-feira, 9:40. Sofía, a estagiária de QA da lição 01, já aprendeu a perguntar. O novo cartão dela diz:

> **Como** cliente, **quero** que o frete seja grátis em compras grandes, **para** não pagar a mais.

Desta vez ela pergunta antes de testar, e a pessoa de produto responde com uma regra clara: **«frete grátis em compras a
partir de $999.00 (pesos mexicanos); abaixo disso, o frete custa $99.00»**.

Sofía escreve dois cenários: um com um carrinho de $1,500.00 (frete grátis ✅) e outro com um de $300.00 (frete de
$99.00 ✅). Os dois passam. Ela escreve no cartão: «Testado: acima e abaixo de $999.00».

Na sexta-feira chega uma reclamação: uma cliente montou um carrinho de **exatamente $999.00** e cobraram $99.00 de
frete. A regra dizia «a partir de $999.00», então o frete devia ser grátis.

O programador abre o código e vê em um segundo: escreveu `subtotal > 999` («mais de 999») onde a regra dizia
`subtotal >= 999` («a partir de 999»). Um único caractere. E nenhum dos dois cenários de Sofía podia ver isso: $1,500.00
e $300.00 caem longe da borda, onde os dois códigos, o certo e o errado, dão o mesmo resultado.

Sofía testou um valor de cada lado. Faltou testar **bem na borda**. É disso que trata esta lição.

---

## Antes de começar

**Você não precisa do computador para os passos 1 a 4.** Precisa de papel ou de uma folha em branco, e de uma régua de
30 cm ou de uma linha desenhada: você vai desenhar retas com números.

**Faça a primeira tentativa sem IA.** Como na lição 01: o que se mede é se você encontra os grupos e as bordas. Com a
sua lista na mão, depois você poderá ver o que falta à de uma IA.

**Quanto tempo:** cerca de 60 minutos na primeira vez (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Divida a entrada em grupos

A técnica se chama **partição de equivalência**. A ideia, como a descreve o programa oficial do ISTQB (a organização
internacional cujo programa e cujo vocabulário de testes este curso usa como referência): se os valores de um grupo são
todos processados do mesmo jeito, e um valor do grupo encontra um erro, espera-se que qualquer outro valor do mesmo
grupo também o encontre. Por isso, em teoria, **basta um valor por grupo**: é uma forma eficiente de escolher, não uma
garantia.

Você vai praticar com uma regra da loja:

> **Regra:** no carrinho você pode pôr de **1 a 10 peças** de cada produto.

### 1a. O que pode chegar?

Antes de dividir, pergunte quais valores **podem chegar** ao sistema, não só quais são corretos. Na página, o campo de
quantidade tem setinhas que não descem abaixo de 1 nem sobem acima de 10. Mas isso não limita o que chega: alguém pode
mandar a requisição direto para a API (a porta pela qual outros programas falam com a loja; você a vê na lição 06), ou
modificar a página pelo navegador. O guia da MDN, a documentação de referência da web, diz sem rodeios: o que o
navegador valida **não serve como proteção**, e o servidor tem de conferir de novo.

Então, para esta regra, pode chegar:

- um número inteiro, positivo, zero ou negativo;
- um número com decimais, como `2.5`;
- algo que não é número, como `dois`;
- nada (o campo vazio).

### 1b. Divida em grupos

Desenhe uma reta com os inteiros e marque onde o comportamento muda:

```
   ... -1   0 │ 1   2   3   4   5   6   7   8   9  10 │ 11  12 ...
   ─────────────┼─────────────────────────────────────────┼─────────────
   inválido     │           válido: é aceito              │  inválido
   «menos de 1» │                                         │  «mais de 10»
```

E à parte, os grupos que não cabem na reta, porque não são inteiros:

| # | Grupo | Válido? | Um valor para testá-lo | O que tem de acontecer |
|---|---|---|---|---|
| G1 | Inteiros de 1 a 10 | Sim | 4 | É aceito; o carrinho mostra 4 peças |
| G2 | Inteiros de 0 ou menos | Não | −3 | É rejeitado com uma mensagem que diga o mínimo |
| G3 | Inteiros de 11 ou mais | Não | 25 | É rejeitado com uma mensagem que diga o máximo |
| G4 | Números que não são inteiros (2.5, −0.5) | Não | 2.5 | É rejeitado: não existem meias peças |
| G5 | Algo escrito que não se pode ler como número | Não | `dois` | É rejeitado |
| G6 | Campo vazio ou que não chegou | Não | (nada) | É rejeitado |

Repare como estão escritos: primeiro se separa o **tipo** (inteiro, número com decimais, texto, nada) e depois a faixa.
Assim −0.5 cai em um único grupo, G4, e não em dois. E se a loja trata de forma diferente «vazio» e «não chegou», são
dois grupos: escreva isso em um cartão vermelho.

Seis grupos, um válido e cinco inválidos. Repare em três coisas:

1. **Os grupos não se sobrepõem.** Cada valor cai em um só. Se um valor parece estar em dois, a sua divisão tem um
   buraco na regra: escreva isso em um cartão vermelho, como na lição 01.
2. **Nenhum grupo está vazio.** Se você não consegue dar um exemplo de um grupo, revise a regra: talvez esse grupo seja
   impossível, ou talvez falte defini-lo.
3. **Cada grupo inválido se testa separadamente** (regra do curso; abaixo diz por quê). Se você manda `−3` e `dois` na
   mesma requisição e a loja a rejeita, você não sabe qual dos dois a provocou. É a mesma ideia da lição 01, «um
   cenário, uma regra», aplicada aos dados: **um valor inválido de cada vez**.

Com seis valores (4, −3, 25, 2.5, `dois` e vazio) você já testou cada grupo uma vez. É isso que o ISTQB chama de cobrir
100% das partições que você identificou.

**É suficiente?** Para encontrar um grupo esquecido, sim. Para encontrar um limite mal colocado, não. Aí está Sofía: os
dois valores dela eram representantes perfeitos dos dois grupos dela, e mesmo assim o erro passou. Falta o passo 2.

---

## Passo 2 · Procure as bordas

A segunda técnica se chama **análise de valor limite**. O programa do ISTQB explica por que ela existe: nas bordas dos
grupos é **mais provável** que o programador se engane (o guia SWEBOK da IEEE Computer Society diz o mesmo: muitas
falhas se concentram perto dos valores extremos), e o erro típico é um limite deslocado um lugar para cima ou para
baixo, ou que falta por completo. O de Sofía é exatamente isso: o limite ficou deslocado um centavo.

Só funciona com grupos **ordenados e sem buracos**: todo valor entre dois valores do grupo tem de ser do mesmo grupo.
G1, G2 e G3 cumprem isso: são trechos da reta dos inteiros. G4 não: entre 0.5 e 1.5 está o 1, que é de outro grupo. G5
e G6 não têm ordem. Esses três ficam com o valor do passo 1.

### 2a. As bordas são valores, não riscos

É fácil confundir a borda com o risco; um artigo do ISTQB as separa assim: a borda **não é o risco** entre dois grupos;
é um **valor** que pertence a um grupo. Cada grupo tem as suas:

| Grupo | A sua menor borda | A sua maior borda |
|---|---|---|
| G2, menos de 1 | (não tem: segue para os negativos) | 0 |
| G1, de 1 a 10 | 1 | 10 |
| G3, mais de 10 | 11 | (não tem: segue para cima) |

Quatro bordas: **0, 1, 10 e 11**.

### 2b. Dois valores por borda

Na forma de **dois valores**, para cada borda você testa a própria borda e o vizinho mais próximo dela **do outro
lado**:

| Borda | A borda | O vizinho dela do outro lado |
|---|---|---|
| 0 | 0 | 1 |
| 1 | 1 | 0 |
| 10 | 10 | 11 |
| 11 | 11 | 10 |

Eles se repetem, porque o vizinho de uma borda é a borda do grupo ao lado. Junte os valores sem repetir: **{0, 1, 10,
11}**. Quatro testes cobrem as quatro bordas.

```
          0 │ 1                          10 │ 11
   ─────●───┼───●──────────────────────●────┼───●─────
```

### 2c. Leia a regra com lupa

As bordas saem das palavras da regra, e as palavras enganam. Antes de escolher valores, sublinhe na regra cada uma
destas expressões e pergunte o que significa exatamente:

| A regra diz… | Pergunta em vermelho antes de seguir |
|---|---|
| «a partir de 999», «desde 999» | O 999 entra? (Quase sempre sim, mas peça que lhe confirmem) |
| «mais de 999», «acima de 999» | O 999 entra? (Quase sempre não) |
| «até 10», «máximo 10» | O 10 entra? |
| «entre 1 e 10» | O 1 e o 10 entram? Aqui a resposta muda de uma pessoa para outra |
| «menos de», «pelo menos» | O mesmo: a borda entra ou não? |

O artigo do ISTQB sobre valores limite recomenda justamente isto: revisar a regra com uma lista antes de testar, porque
«pelo menos», «no máximo» e «entre» são mal interpretados. Na cena, a regra de Sofía dizia «a partir de $999.00» e o
código dizia «mais de 999». A pergunta em vermelho, «o $999.00 entra?», teria posto o erro na mesa antes de se escrever
uma linha de código.

---

## Passo 3 · Três valores quando um erro custa mais

Existe uma segunda forma, a de **três valores**: para cada borda você testa a borda e **os dois vizinhos dela**, o de
fora e o de dentro.

| Borda | Vizinho de um lado | A borda | Vizinho do outro lado |
|---|---|---|---|
| 0 | −1 | 0 | 1 |
| 1 | 0 | 1 | 2 |
| 10 | 9 | 10 | 11 |
| 11 | 10 | 11 | 12 |

Juntos e sem repetir: **{−1, 0, 1, 2, 9, 10, 11, 12}**. Oito testes em vez de quatro.

```
     -1   0 │ 1   2                  9   10 │ 11  12
   ──○────●─┼───●───○────────────────○────●─┼───●───○──
          ● = dois valores     ○ = o que três valores acrescentam
```

**Para que servem os quatro a mais?** O programa do ISTQB dá este exemplo: a regra diz «se x é **menor ou igual** a 10»
e o programador escreve «se x é **igual** a 10». Com dois valores você testa 10 e 11, e o código errado dá o mesmo
resultado que o certo nos dois. O 9, que só aparece com três valores, o denuncia: a regra diz que sim e o código diz
que não.

Que o erro seja um operador trocado (`>` por `>=`, `<=` por `=`) não é raro: é um caractere. O artigo do ISTQB faz a
conta completa para uma regra de comprimento mínimo: de **dez** formas de escrever mal a comparação, os dois valores
pegam **oito**; os três valores, as **dez**. O mesmo acontece com a regra da cena (você verá no passo 4).

**Então sempre três?** Não. Três valores pedem mais testes (aqui, de quatro a oito), e o ISTQB deixa a decisão ao risco:
os três são mais rigorosos, e o esforço a mais pode valer a pena ou não. Neste curso usamos esta **regra do curso**
(não é do ISTQB; é como decidimos aqui):

> **Dois valores por borda, exceto quando a regra move dinheiro ou decide quem pode fazer algo: aí, três.**

**Por quê:** nessas regras, o erro que escapa não é uma tela feia; é uma cobrança a mais, um desconto que não era
devido ou uma porta aberta. Quatro testes a mais custam minutos; o erro custa clientes.

---

## Passo 4 · A borda do dinheiro se mede em centavos

Volte à regra de Sofía: **«frete grátis a partir de $999.00»**.

Os grupos são dois, os dois válidos:

| Grupo | De… | Até… | Frete |
|---|---|---|---|
| E1 | $0.01 | $998.99 | $99.00 |
| E2 | $999.00 | (sem teto) | Grátis |

**Por que $998.99 e não $998?** Porque o vizinho de uma borda está a **um passo de precisão**, e neste curso os valores
são em pesos com centavos: o passo é $0.01 (em uma regra real, confirme). Se o seu vizinho fosse $998.00, você deixaria
sem testar 99 centavos entre ele e a borda, e um limite deslocado para $998.50 passaria sem que você visse. O artigo do
ISTQB diz isso para qualquer dado contínuo: primeiro se escolhe a precisão, e depois se procuram as bordas com essa
precisão.

**Os valores para a borda de $999.00**, com três valores porque é dinheiro:

| Borda | Os três valores |
|---|---|
| $998.99 (a maior de E1) | $998.98 · **$998.99** · $999.00 |
| $999.00 (a menor de E2) | $998.99 · **$999.00** · $999.01 |

Juntos e sem repetir: **$998.98, $998.99, $999.00 e $999.01**.

Atenção: E1 também tem uma borda embaixo, $0.01. Esta tabela cobre **só a borda de $999.00**, que é a que decide o
frete; a borda mínima do carrinho se testa com a sua própria regra, na sua própria tabela.

E agora sim, o erro da cena: com `subtotal > 999`, um carrinho de **$999.00** paga frete. O valor $999.00 está na lista
desde a forma de dois valores; Sofía o teria pego com um único teste a mais.

Fizemos a conta com dez formas de escrever mal esta comparação (cinco operadores errados contra $999.00 e cinco contra
$998.99; não são todos os erros possíveis, só os de um operador trocado): como no artigo do ISTQB, os dois valores pegam
**oito** e os três valores pegam as **dez**. Uma das duas que escapam com dois valores é «frete grátis somente se o
subtotal for **igual** a $999.00», que só cai com $999.01.

### Um aviso para quando você automatizar

Muitas linguagens guardam os decimais de forma aproximada: em Python, `0.1 + 0.1 + 0.1 == 0.3` dá **falso** (a
documentação oficial explica isso). Por isso o dinheiro se programa com tipos decimais ou em centavos inteiros, e
Martin Fowler adverte que, ao arredondar dinheiro, é fácil perder centavos. Você verá isso a fundo na lição 07. Para
hoje basta uma pergunta na sua lista: **a borda de $999.00 compara bem quando o subtotal vem da soma de três camisetas
de $333.00?** É a mesma borda, alcançada por outro caminho, e vale um teste.

---

## Passo 5 · Escreva em uma tabela de cenários

Com oito valores, escrever oito cenários quase iguais é cansativo, e ao copiar oito vezes é fácil que escape uma
diferença. O Gherkin, o formato que você usou na lição 01, tem uma forma para isto: **`Esquema do Cenário`** (em
inglês, *Scenario Outline*) com uma tabela de **`Exemplos`**. O Cucumber, o projeto que mantém o Gherkin, o descreve
assim: os passos do esquema são um modelo que não roda sozinho; roda **uma vez por cada linha** da tabela, sem contar a
linha de títulos.

```gherkin
# language: pt
Funcionalidade: Frete grátis em compras grandes

  Regra: O frete é grátis em compras a partir de $999.00; abaixo disso custa $99.00

    Esquema do Cenário: Frete conforme o subtotal
      Dado que Marta não tem nenhum cupom aplicado
      E ela tem no carrinho produtos no valor de <subtotal>
      Quando ela vai pagar
      Então o frete que a loja mostra a ela é de <frete>

      Exemplos:
        | subtotal | frete  |
        | $998.98  | $99.00 |
        | $998.99  | $99.00 |
        | $999.00  | $0.00  |
        | $999.01  | $0.00  |
```

Quatro linhas, quatro cenários. Se amanhã a regra mudar para «a partir de $1,499.00», você troca quatro números e não
quatro cenários.

Três cuidados que vêm da lição 01 e continuam valendo:

1. **Uma tabela, uma regra.** Todas as linhas testam «frete a partir de $999.00». Se você quiser testar a quantidade de
   peças, vai em outra tabela, sob a sua própria `Regra:`.
2. **O `Então` se vê de fora:** o frete que a loja mostra, não um campo no banco de dados.
3. **Nenhum outro dado decide o resultado.** Por isso o primeiro `Dado` diz que Marta não tem cupom: nesta loja o frete
   se mede com o cupom já aplicado, e os 10% da lição 01 moveriam o subtotal para baixo da borda.

E uma nova, regra do curso: **os grupos inválidos vão na sua própria tabela**, com a mensagem que tem de aparecer. Por
exemplo, para a regra de peças:

```gherkin
# language: pt
Funcionalidade: Peças por produto no carrinho

  Regra: Podem-se pôr de 1 a 10 peças de cada produto

    Esquema do Cenário: Quantidade que é aceita
      Dado que Marta tem a camiseta azul no carrinho
      Quando ela muda a quantidade para <peças>
      Então o carrinho dela mostra <peças> peças da camiseta azul

      Exemplos:
        | peças |
        | 1     |
        | 2     |
        | 9     |
        | 10    |

    Esquema do Cenário: Quantidade que é rejeitada
      Dado que Marta tem 1 peça da camiseta azul no carrinho
      Quando ela muda a quantidade para <peças>
      Então a loja diz a ela que <mensagem>
      E o carrinho dela continua com 1 peça da camiseta azul

      Exemplos:
        | peças | mensagem                                  |
        | -1    | o mínimo é 1 peça                         |
        | 0     | o mínimo é 1 peça                         |
        | 11    | o máximo é 10 peças                       |
        | 12    | o máximo é 10 peças                       |
        | 2.5   | a quantidade tem de ser um número inteiro |
        | dois  | a quantidade tem de ser um número         |

    Cenário: Quantidade vazia
      Dado que Marta tem 1 peça da camiseta azul no carrinho
      Quando ela deixa a quantidade vazia
      Então a loja diz a ela que a quantidade é obrigatória
      E o carrinho dela continua com 1 peça da camiseta azul
```

O grupo «vazio» vai em um cenário à parte, sem tabela, porque uma célula vazia se presta a confusão. Repare também que o
`Dado` fixa quantas peças havia (1): assim o último `Então` tem um valor que se pode conferir.

Aqui usamos três valores embora a regra não mova dinheiro, para que você veja a forma completa. Com a regra do curso,
bastariam 0, 1, 10 e 11, mais um valor para cada grupo sem ordem.

---

## Como se confere

**O que você faz sem máquina** (passos 1 a 4 e os seus exercícios) se compara com «Compare as respostas», no final. O
que tem de coincidir: os grupos (nem sobrepostos nem vazios), as bordas, e os valores de dois e de três.

**O seu arquivo de cenários** é revisado pelo `verifica 02`. Salve-o como `envio.feature` em `~/practica` e, no
terminal da loja, escreva:

```bash
verifica 02
```

Ele faz o que o curso promete desde o início: roda os seus cenários contra a loja **sem** erros, onde têm de sair em
verde, e contra a loja com **o limite deslocado** plantado de propósito (E1), onde **pelo menos um tem de sair em
vermelho**. Se os seus cenários saem verdes nas duas, não estavam olhando a borda. Antes de rodá-lo, a lista abaixo diz
se a forma está certa.

**Antes de salvar, revise o seu arquivo com esta lista:**

- [ ] A primeira linha é `# language: pt`, e há uma única `Funcionalidade:`.
- [ ] Cada `Esquema do Cenário:` tem embaixo uma tabela `Exemplos:` com linha de títulos.
- [ ] Cada `<nome>` dos passos é exatamente um título da tabela (com a mesma grafia).
- [ ] Estão os quatro valores: $998.98, $998.99, $999.00 e $999.01.
- [ ] Um `Dado` deixa o cupom de fora, para que nenhuma linha dependa de outra regra.
- [ ] Se o erro fosse `subtotal > 999`, pelo menos uma linha teria de sair diferente. Qual?

---

## Os exercícios

**Exercício 1, sem IA.** Regra da loja:

> O nome impresso em um cartão-presente tem de **2 a 30 caracteres**.

1. **O que pode chegar:** anote tudo o que poderia chegar ao campo, não só o correto.
2. **Grupos:** faça a tabela de grupos (válidos e inválidos) com um valor para cada um.
3. **Bordas:** escreva as bordas de cada grupo ordenado e os valores de **dois** valores por borda.
4. **Cartão vermelho:** escreva pelo menos uma pergunta que você faria antes de testar. (Dica: um espaço conta como
   caractere? E um emoji?)

**Exercício 2, sem IA.** Regra da loja:

> Você pode pagar em parcelas sem juros em compras **a partir de $3,000.00 e até $50,000.00**.

1. **Grupos:** quantos há e quais são.
2. **Valores de três para as duas bordas que decidem as parcelas** ($3,000.00 e $50,000.00), sem repetir. (A borda lá
   de baixo, o menor total possível, é decidida por outra regra.)
3. **Tabela:** escreva o esquema do cenário em um arquivo `meses.feature`, com `# language: pt`.
4. Escreva um erro de uma só linha (como o `>` de Sofía) que os seus **três** valores pegam e **dois** valores não.

**Revisão.** Você tem de acertar 7 de 8, e os que **não** pode errar são o 2, o 3 e o 8: são os da ideia da lição.

1. Regra «de 1 a 10 peças». De quantos valores você precisa para cobrir todos os grupos ordenados, um por grupo?
2. Mesma regra. Que valores saem com dois valores por borda?
3. Mesma regra. Que valores a forma de três valores acrescenta?
4. Regra «frete grátis a partir de $999.00». Qual é o vizinho de fora de $999.00, e por que não é $998.00?
5. As bordas são o risco entre dois grupos, ou valores que pertencem a um grupo?
6. Você manda `−3` e `dois` na mesma requisição, e a loja a rejeita. O que você não sabe?
7. A página não deixa você digitar 11 na quantidade. Já não é preciso testar o 11? Por quê?
8. Regra «se x é menor ou igual a 10», programada como «se x é igual a 10». Que valor a denuncia: o 10, o 11 ou o 9?

---

## Para fechar

Sofía não precisava de mais testes, e sim de **outro** teste: um bem em $999.00. Dois cenários longe da borda lhe
disseram que a regra existia; nenhum lhe disse se estava bem colocada.

O que você leva daqui:

- Primeiro, **o que pode chegar**, não só o que é correto.
- Divida em **grupos** que não se sobrepõem, válidos e inválidos, e teste os inválidos **um de cada vez**.
- Os erros se juntam nas **bordas**: teste a borda e o vizinho dela do outro lado (dois valores), ou a borda e os dois
  vizinhos dela (três valores).
- O vizinho está a **um passo de precisão**: uma peça, um centavo, um segundo.
- **Leia a regra com lupa:** «a partir de», «mais de» e «entre» se perguntam antes de testar.

Na lição 03 você monta uma tabela de decisão para uma promoção com várias condições: verá o que acontece quando o cupom
da lição 01 e o frete grátis decidem juntos o mesmo carrinho.

---

## Compare as respostas

**Exercício 1, nome de 2 a 30 caracteres.** O que se testa é o **comprimento** do nome, e um comprimento não pode ser
negativo. O artigo do ISTQB chama isso de *domínio*: os valores que são possíveis. Por isso não há −1.

| Grupo | Válido? | Um valor |
|---|---|---|
| Comprimento 0 (vazio) e 1 | Não | `A` (1 caractere) |
| Comprimento de 2 a 30 | Sim | `Lupita` (6) |
| Comprimento de 31 em diante | Não | um nome de 40 caracteres |

Bordas: **0 e 1** (as do grupo curto), **2 e 30** (as do válido) e **31** (a menor do longo). Com dois valores: **{0, 1,
2, 30, 31}**. O 0 não tem vizinho de fora: não existe um comprimento de −1. Se você separou «vazio» como grupo à parte,
também está bem: é um caso que muitos sistemas tratam de forma diferente («o nome é obrigatório» em vez de «é curto
demais»), e vale o cartão vermelho.

Perguntas vermelhas que valem a pena ter: os espaços no início e no fim contam? Um emoji conta como um ou como vários
caracteres? Aceitam-se acentos e o ñ? O que acontece com um nome feito só de espaços?

**Exercício 2, parcelas sem juros de $3,000.00 a $50,000.00.** Três grupos: abaixo de $3,000.00 (não vale), de
$3,000.00 a $50,000.00 (vale) e acima de $50,000.00 (não vale).

| Borda | Os três valores |
|---|---|
| $2,999.99 | $2,999.98 · $2,999.99 · $3,000.00 |
| $3,000.00 | $2,999.99 · $3,000.00 · $3,000.01 |
| $50,000.00 | $49,999.99 · $50,000.00 · $50,000.01 |
| $50,000.01 | $50,000.00 · $50,000.01 · $50,000.02 |

Sem repetir: **$2,999.98, $2,999.99, $3,000.00, $3,000.01, $49,999.99, $50,000.00, $50,000.01 e $50,000.02**. Oito.

Uma forma do arquivo:

```gherkin
# language: pt
Funcionalidade: Parcelas sem juros

  Regra: Pode-se pagar em parcelas sem juros em compras a partir de $3,000.00 e até $50,000.00

    Esquema do Cenário: Opção de parcelas conforme o total
      Dado que Marta tem no carrinho produtos no valor de <total>
      Quando ela escolhe como pagar
      Então a opção de parcelas sem juros <resultado>

      Exemplos:
        | total      | resultado   |
        | $2,999.98  | não aparece |
        | $2,999.99  | não aparece |
        | $3,000.00  | aparece     |
        | $3,000.01  | aparece     |
        | $49,999.99 | aparece     |
        | $50,000.00 | aparece     |
        | $50,000.01 | não aparece |
        | $50,000.02 | não aparece |
```

Um erro que três valores pegam e dois não: «parcelas somente se o total for **igual** a $3,000.00» em vez de «a partir
de $3,000.00». Com dois valores ($2,999.99 e $3,000.00), o código ruim se comporta igual ao bom; $3,000.01 o denuncia.
Outro: «parcelas se o total for **diferente** de $2,999.99», que aceita tudo menos esse valor; com dois valores passa, e
$2,999.98 o denuncia.

**Revisão:**

1. Três: um por grupo ordenado (por exemplo −3, 4 e 25).
2. {0, 1, 10, 11}.
3. −1, 2, 9 e 12.
4. $998.99, porque a precisão do dinheiro é um centavo. Com $998.00 ficam 99 centavos sem testar.
5. Valores que pertencem a um grupo. O risco não se pode testar; os valores, sim.
6. Qual dos dois provocou a rejeição. Os inválidos vão um de cada vez.
7. É preciso, sim: a página não é a única porta. A API pode receber um 11, e o servidor tem de rejeitá-lo.
8. O 9. Com «igual a 10», o 10 dá o mesmo que a regra (sim) e o 11 também (não); o 9 dá «não» onde a regra diz «sim».

Se você não acertou o 4 ou o 8, revise os passos 3 e 4: ali se juntam a precisão e os três valores.

---

## Fontes da lição

Abertas e lidas em 21/11/2026.

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 15 de setembro de 2024, §4.2.1 «Equivalence
   Partitioning» e §4.2.2 «Boundary Value Analysis». Os grupos não se sobrepõem e não são vazios; um valor por grupo;
   as bordas são o mínimo e o máximo de um grupo ordenado; os programadores erram mais nas bordas; as formas de dois e
   de três valores, e o exemplo de «x ≤ 10» escrito como «x = 10».
   https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Matthias Hamburg e Adam Roman, «Boundary Value Analysis According to the ISTQB® Foundation Level Syllabus», ISTQB,
   2025. As bordas não são o risco; os seis passos; o domínio de valores possíveis; as dez comparações mal escritas (dois
   valores pegam oito); a precisão em dados contínuos; revisar «pelo menos», «entre» e «no máximo».
   https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf
3. IEEE Computer Society, *SWEBOK Guide* v4.0a, capítulo 5 «Software Testing», §3.1.1 e §3.1.2. A partição inclui
   valores válidos e fora de faixa; muitas falhas se concentram perto dos valores extremos.
   https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf
4. Cucumber, «Gherkin Reference», seção *Scenario Outline* e *Examples*: o esquema é um modelo que roda uma vez por
   linha. https://cucumber.io/docs/gherkin/reference/
5. Cucumber, palavras-chave do Gherkin em português (`gherkin-languages.json`): «Esquema do Cenário» e «Exemplos».
   https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
6. MDN Web Docs, `<input type="number">`: a validação do navegador não serve como proteção; o servidor tem de conferir.
   https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/number
7. OWASP, *Input Validation Cheat Sheet*: para números se definem tipo, formato, mínimo e máximo, e se valida no
   servidor ainda que o navegador já confira o mesmo campo.
   https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
8. Python, «Floating-Point Arithmetic: Issues and Limitations»: `0.1 + 0.1 + 0.1 == 0.3` dá `False`.
   https://docs.python.org/3/tutorial/floatingpoint.html
9. Microsoft Learn, «Floating-point numeric types (C# reference)»: o tipo `decimal` é o indicado para quantias de
   dinheiro. https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/floating-point-numeric-types
10. Martin Fowler, «Money», *Patterns of Enterprise Application Architecture*, 2003: ao arredondar dinheiro, é fácil
    perder centavos. https://martinfowler.com/eaaCatalog/money.html

**Regras do curso** (sem duas fontes; dizem por que existem):

- «Dois valores por borda, exceto dinheiro ou permissões: três». Por quê: ali o erro que escapa custa clientes, e
  quatro testes a mais custam minutos.
- «Os inválidos, um de cada vez». Vem de «um cenário, uma regra» da lição 01: se duas coisas falham juntas, você não
  sabe qual falhou.
- «Os grupos inválidos vão na sua própria tabela». Por quê: cada tabela testa uma só coisa, e a mensagem esperada muda
  por grupo.
