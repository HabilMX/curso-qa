# Lição 01 — Da história ao cenário

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, cinco palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **História de usuário:** uma frase curta que diz quem precisa de algo, o que precisa e para quê. É o pedido que chega
  até você para testar.
- **Regra:** algo que o negócio decidiu e que o sistema tem de respeitar. «O cupom só vale a partir de $500 (pesos mexicanos)» é uma
  regra.
- **Exemplo:** um caso concreto, com dados, que mostra uma regra funcionando. «Marta compra $500.00 e o cupom vale para
  ela» é um exemplo.
- **Cenário:** um exemplo escrito de forma que qualquer pessoa possa repeti-lo e conferi-lo: de onde se parte, o que se
  faz e o que tem de acontecer.
- **Caminho feliz:** o cenário em que tudo dá certo. É o primeiro que ocorre a todo mundo, e quase nunca é onde estão os
  erros.

**O que fica com você:** você recebe uma história de usuário e, antes de mexer no sistema, a separa em regras, exemplos
e perguntas; escreve cada exemplo como cenário, com dados concretos, na forma **Dado / Quando / Então**; e reconhece se
um cenário é o caminho feliz ou um dos outros dez tipos em que os erros se escondem.

**Ideia nova desta lição (a única que se avalia):** um cenário nasce de uma **regra de negócio**, não de uma tela. Se
você não sabe que regra está testando, não sabe o que tem de acontecer.

**Em que ordem vai:** você lê a história e a separa em cartões coloridos (passo 1), transforma cada exemplo em cenário
(passo 2), você confere se os seus cenários dizem o que acontece e não quais teclas se apertam (passo 3) e coloca cada
cenário na sua família (passo 4). No fim, você faz sozinho o mesmo com outra história e compara as suas respostas.

---

## A cena

*Cenário inventado.*

Segunda-feira, 10:15. Sofía está há uma semana como estagiária de QA. Chega para ela o primeiro cartão no quadro:

> **Como** cliente da loja, **quero** aplicar um cupom de desconto ao pagar, **para que** a minha compra me custe
> menos.

Embaixo, alguém escreveu: «Testar o cupom. Urgente».

Sofía abre a loja, coloca duas camisetas no carrinho, digita o cupom `BIENVENIDA10`, vê o total baixar e escreve no
cartão: «Testado, funciona».

Na quinta-feira, a área de finanças pergunta por que há clientes que usaram o mesmo cupom quatro vezes. E por que
outros o usaram em uma compra de $80, se o cupom era «para compras a partir de $500».

Sofía não fez nada de errado: testou o que lhe pediram. O problema é que **ninguém lhe disse quais eram as regras**, e
ela também não perguntou. Testar a tela era um bom começo; faltava combinar as regras de negócio com as quais
compará-la.

Esta lição é para que você pergunte, e saiba o que perguntar.

---

## Antes de começar

**Você não precisa do computador para os passos 1 a 4.** Precisa de papel, ou de uma folha em branco no seu editor, e de
quatro cores: amarelo, azul, verde e vermelho. Se você não tem cartões coloridos, servem quatro marcadores, ou escrever
a palavra da cor entre colchetes, assim: `[azul]`.

**Faça a primeira tentativa sem IA.** O exercício desta lição mede se é você quem encontra as regras. Com a sua própria
lista na mão, depois você poderá comparar o que uma IA sugerir e notar o que faltou a ela. Na lição 13, você aprende a
revisar o que uma IA lhe propõe.

**Quanto tempo:** cerca de 60 minutos na primeira vez (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Separe a história em cartões coloridos

A técnica se chama **mapeamento de exemplos** (em inglês, *Example Mapping*). Foi publicada por Matt Wynne, líder do
projeto Cucumber, em 2015, e é usada porque é rápida e deixa à vista o que ninguém sabe. Funciona com quatro cores:

| Cor | O que você escreve | Na mesa vai… |
|---|---|---|
| **Amarelo** | A história de usuário | No alto, uma só |
| **Azul** | Cada **regra** que você já conhece | Em fila, embaixo da história |
| **Verde** | Cada **exemplo** que ilustra uma regra | Embaixo da sua regra |
| **Vermelho** | Cada **pergunta** que ninguém na mesa sabe responder | Ao lado |

A ordem importa: primeiro a história, depois as regras, depois os exemplos de cada regra. Quando aparece algo que
ninguém sabe, **não se discute**: escreve-se em vermelho e segue-se em frente. Assim, uma dúvida que ninguém tinha visto
vira uma pergunta concreta que alguém pode ir responder.

### Faça com a história de Sofía

**1. Amarelo.** Copie a história:

```
[amarelo] Como cliente, quero aplicar um cupom de desconto ao pagar,
          para que a minha compra me custe menos.
```

**2. Azul.** Que regras você conhece? A história não diz nenhuma, então é preciso ir perguntar a quem a pediu. Neste
caso, a pessoa de produto responde:

```
[azul] R1. O cupom BIENVENIDA10 desconta 10% do subtotal (sem contar o frete).
[azul] R2. Só vale se o subtotal for de $500.00 ou mais.
[azul] R3. Cada cliente pode usá-lo uma única vez.
[azul] R4. Vence em 31 de dezembro às 23:59, horário da Cidade do México.
```

Repare: nenhuma dessas quatro regras aparece na tela de pagamento. Sofía não podia adivinhá-las olhando a loja.

**3. Verde.** Para cada regra, um ou mais exemplos com **dados concretos**. Não «uma compra grande», mas «uma compra de
$500.00»:

```
[azul] R2. Só vale se o subtotal for de $500.00 ou mais.
   [verde] Subtotal $500.00 → vale, paga $450.00
   [verde] Subtotal $499.99 → não vale, a loja diz a ele por quê
   [verde] Subtotal $1,200.00 → vale, paga $1,080.00

[azul] R3. Cada cliente pode usá-lo uma única vez.
   [verde] Marta o usa na primeira compra → vale
   [verde] Marta tenta usá-lo na segunda compra → não vale
```

Por que $499.99 e não $300? Porque a **borda** de uma regra é um lugar frequente para procurar erros: basta que alguém
escreva «maior que 500» onde devia dizer «maior ou igual a 500». Com $300 esse erro não aparece. Na lição 02 você
trabalha isso a fundo; por ora, nas regras com valores ordenados, como dinheiro ou quantidades, ponha um exemplo de cada
lado da borda.

**4. Vermelho.** Enquanto escrevia os exemplos, com certeza surgiram dúvidas. Escreva-as:

```
[vermelho] Se Marta cancelar o pedido em que usou o cupom, ela pode usá-lo de novo?
[vermelho] Os 10% são calculados antes ou depois do frete grátis?
[vermelho] O que acontece se o cupom é aplicado às 23:59 e o pagamento é confirmado às 00:01?
```

Nenhuma dessas três a história responde. Se ninguém perguntar, o programador decide por conta própria, e a QA testa o
que o programador decidiu, não o que o negócio queria.

### Como saber se a história está pronta

A regra prática do mapeamento de exemplos: em equipe, um grupo pequeno mapeia uma história bem entendida e de bom
tamanho **em uns 25 minutos**. Se leva muito mais, ou se os cartões vermelhos não param de aparecer, a história é grande
demais ou ainda tem dúvidas demais, e convém parti-la ou devolvê-la com as perguntas. Quando você faz sozinho, use esses
25 minutos como aviso de que faltam respostas, não como prova de velocidade.

Olhe a sua mesa: **muitos vermelhos** quer dizer que falta conversar com alguém. **Muitos azuis** quer dizer que a
história é grande e talvez sejam duas. **Um azul com muitos verdes** pode indicar uma regra complicada, ou várias regras
misturadas em um único cartão.

> **Por que não se começa pela tela?** Porque a tela mostra o que alguém já programou. Se o que foi programado está
> errado, a tela mostra o erro com toda a naturalidade, e você não tem com o que compará-lo. A regra é o seu ponto de
> comparação.

---

## Passo 2 · Transforme cada exemplo em cenário

Um cartão verde diz «Subtotal $499.99 → não vale». Isso serve para quem estava na mesa. Para que qualquer pessoa possa
repeti-lo e conferi-lo, é preciso mais precisão: de onde se parte, o que se faz e o que tem de acontecer exatamente.

Para isso se usa a forma **Dado / Quando / Então** (em inglês, *Given / When / Then*). Foi proposta por Dan North e
Chris Matts como parte de um jeito de trabalhar chamado desenvolvimento guiado por comportamento (BDD, sigla do inglês
*behavior-driven development*). Cada parte tem a sua tarefa:

| Parte | O que descreve | Pergunte-se |
|---|---|---|
| **Dado** | O ponto de partida: como está o sistema antes de começar. Quase sempre é algo que já aconteceu | O que tem de ser verdade antes? |
| **Quando** | A ação ou o evento: o que a pessoa faz, ou o que outro sistema faz | O que acontece? |
| **Então** | O resultado esperado, que se pode **ver de fora** | Como sei que deu certo? |

Se você precisa de duas coisas na mesma parte, a segunda vai com **E** («E o subtotal dela continua em $499.99»), ou com
**Mas** se for um contraste.

### Os seus dois primeiros cenários

Pegue os dois cartões verdes da borda de R2, mais um de R1, e escreva-os assim:

```gherkin
# language: pt
Funcionalidade: Aplicar um cupom de desconto

  Contexto:
    Dado que o cupom BIENVENIDA10 está vigente
    E Marta nunca usou o cupom BIENVENIDA10

  Regra: O cupom desconta 10% do subtotal, sem contar o frete

    Cenário: O desconto é de 10% do subtotal
      Dado que Marta tem no carrinho produtos no valor de $1,200.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela um desconto de $120.00

  Regra: O cupom só vale se o subtotal for de $500.00 ou mais

    Cenário: Subtotal exatamente no mínimo
      Dado que Marta tem no carrinho produtos no valor de $500.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela que o cupom foi aplicado

    Cenário: Subtotal um centavo abaixo do mínimo
      Dado que Marta tem no carrinho produtos no valor de $499.99
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja diz a ela que o cupom é para compras de $500.00 ou mais
      E o subtotal dela continua em $499.99
```

Leia o bloco com calma. Quatro coisas que vale a pena notar:

1. **`# language: pt`** na primeira linha diz à ferramenta que as palavras-chave estão em português. O formato se chama
   **Gherkin**, e aceita `Funcionalidade`, `Regra`, `Cenário`, `Dado`, `Quando`, `Então`, `E` e `Mas`. Você vai
   executá-lo de verdade contra a loja de prática; por ora, o importante é a forma.
2. **A regra vem escrita acima dos seus cenários** (`Regra:`). Quem ler o arquivo sabe o que está sendo testado e por
   que cada cenário existe. É o seu cartão azul, passado a limpo.
3. **`Contexto` não está sobrando.** O que está ali vale antes de cada cenário do arquivo: o cupom está vigente (R4) e
   Marta não o usou (R3). Sem essas duas linhas, um cenário de R2 poderia falhar porque o cupom venceu ou porque Marta
   já o tinha usado, e você leria isso como um erro do mínimo. Um bom **Dado** deixa de fora as outras regras, para que
   só uma decida o resultado.
4. **Cada Então olha só a sua regra.** O de R1 confere o valor do desconto; os de R2 só conferem se o cupom foi aplicado
   ou não. Se o cenário do mínimo conferisse também «paga $450.00», um erro nos 10% (R1) o faria falhar, e você pensaria
   que o problema está no mínimo.

### Agora você: mais dois

Escreva os cenários de R3 (os dois cartões verdes de Marta) em um arquivo novo, com o seu `# language: pt` e a sua
`Funcionalidade:`. Cuide para que o **Dado** diga claramente se Marta já usou o cupom ou não, que o subtotal esteja
acima de $500.00 para que R2 não atrapalhe, e que o **Então** diga o que se vê. Compare com a seção «Compare as
respostas», no final.

---

## Passo 3 · Que diga o que acontece, não quais teclas se apertam

Olhe este cenário. Ele testa a mesma regra que o segundo do passo 2. *É um fragmento para comparar, não o copie como
arquivo:*

```gherkin
    Cenário: Cupom no mínimo
      Dado que eu abro a página da loja
      E clico em «Camisetas»
      E clico em «Adicionar ao carrinho» duas vezes
      E clico no ícone do carrinho
      E digito "BIENVENIDA10" na caixa de texto com id "cupon"
      Quando clico no botão azul «Aplicar»
      Então vejo "$450.00" no canto inferior direito
```

Tem mais linhas e diz menos. Quanto custam as duas camisetas? Não diz: se amanhã o preço mudar, o cenário pode falhar
sem que a regra tenha mudado. Que regra testa? É preciso adivinhar. E se alguém mudar o botão de lugar ou trocar a cor
dele, também pode falhar.

A esse modo de escrever se chama **imperativo**: descreve os passos mecânicos da tela. O do passo 2 é **declarativo**:
descreve o que faz o negócio. O guia do Cucumber recomenda o declarativo porque quebra menos e se lê como documentação
do sistema; o imperativo tem o seu lugar, mas costuma dar mais trabalho de manter, porque quando a tela muda muitas
vezes é preciso corrigi-lo.

**O teste rápido:** leia o seu cenário em voz alta para alguém do negócio. Se a pessoa entende o que se testa e por que
importa, é declarativo. Se ela pergunta «e isso serve para quê?», tem tela demais.

Mais uma coisa sobre o **Então**: o que se confere tem de **sair do sistema**, algo que uma pessoa ou outro sistema
possam ver: uma mensagem, um total, um e-mail, ou a resposta que um sistema dá a outro (uma **API**; você a conhece a
fundo na lição 06). «Grava-se um registro na tabela de cupons» não serve como **Então**, porque isso ninguém vê de fora.
A pergunta certa é: o que o cliente notaria?

---

## Passo 4 · Coloque cada cenário na sua família

Até aqui, todos os seus cenários saíram de regras. Falta a última pergunta: **que tipos de cenário estão faltando?**

No artigo [«Além do caminho feliz»](https://www.habil.mx/pt/blog/cenarios-de-teste-alem-do-caminho-feliz/) agrupamos os cenários em famílias. Cada família é uma pergunta diferente
que você faz ao sistema:

| Família | A pergunta |
|---|---|
| **Caminho feliz** | Funciona quando tudo dá certo? |
| **Limites** | O que acontece bem na borda de uma regra? |
| **Negativos** | Rejeita bem o que deve rejeitar? |
| **Concorrência** | O que acontece se duas coisas ocorrem ao mesmo tempo? |
| **Estado e ordem** | Respeita a sequência? O que acontece se um passo é pulado? |
| **Tempo e fuso horário** | O que acontece na virada de dia, mês, ano ou horário? |
| **Dados sujos** | Aguenta o que as pessoas realmente digitam? |
| **Integrações fora do ar** | O que acontece se o outro sistema demora ou não responde? |
| **Permissões** | Cada pessoa vê e faz somente o que é dela? |
| **Idempotência e novas tentativas** | Repetir a mesma requisição produz o efeito uma só vez? (*Idempotência* é isso: repetir sem repetir o efeito) |
| **Qualidade de uso e operação** | Continua utilizável, acessível (também para quem usa só o teclado ou um leitor de tela) e rápido com a carga esperada? |

São onze: o caminho feliz e **dez mais**. Sofía só testou a primeira.

Agora arrume os cartões do cupom:

- «Subtotal $1,200.00 → desconto de $120.00» é **caminho feliz**.
- «Subtotal $500.00» e «$499.99» são **limites**.
- «Marta tenta usá-lo na segunda compra» é **negativo**: a loja tem de rejeitá-lo.
- O cartão vermelho das 23:59 e das 00:01 é **tempo e fuso horário**.

E as famílias que não aparecem? Aí estão os erros da quinta-feira de Sofía. O que acontece se Marta aperta «Aplicar
cupom» duas vezes bem rápido (idempotência)? Se ela abre duas abas e paga nas duas ao mesmo tempo (concorrência)? Se ela
digita `bienvenida10` em minúsculas ou com um espaço no final (dados sujos)?

Nem todas as famílias se aplicam a todas as histórias. Mas, neste curso, **cada família que você descarta, você a
descarta de propósito**, não porque esqueceu. A pergunta deste passo é essa: qual você descartou, e por quê?

---

## Como se confere

Esta lição tem duas partes que se conferem de forma diferente.

**O que você faz sem máquina** (passos 1 a 4 e os seus exercícios) se compara com «Compare as respostas», no final. Não
há uma única resposta correta para as regras e as perguntas; o que tem de coincidir é que **cada cenário aponte para uma
só regra** e que o seu **Então** se veja de fora.

**O seu arquivo de cenários** será revisado pelo `verifica 01` quando ele existir: ele conferirá
que o arquivo tenha a forma do Gherkin e que rode contra a loja.

> ⚠️ **Nota para esta versão do curso:** a loja de prática já existe (foi levantada na lição 00); o `verifica 01`
> ainda não. Hoje a **forma** se confere com a lista abaixo, que continua sendo a que vale; rodar contra a loja fica
> pendente para quando existir o `verifica 01`. Salve o arquivo como `cupon.feature`.

**Antes de salvar, revise o seu arquivo com esta lista:**

- [ ] A primeira linha é `# language: pt`.
- [ ] Há uma única `Funcionalidade:`, e ela vem antes de todo o resto.
- [ ] Cada `Regra:` tem pelo menos um `Cenário:` embaixo.
- [ ] Cada cenário tem pelo menos um `Dado`, um `Quando` e um `Então`, nessa ordem.
- [ ] Cada `Então` nomeia algo que se vê: uma mensagem, um valor ou uma resposta.
- [ ] Se você tirar uma das outras regras, o resultado de cada cenário não muda.

---

## Os exercícios

**História nova** (sem IA):

> **Como** cliente, **quero** cancelar um pedido a partir da minha conta, **para** não pagar por algo de que já não
> preciso.

A pessoa de produto lhe dá estas regras:

- Pode-se cancelar enquanto o pedido não tiver saído do armazém.
- Se já foi cobrado, o reembolso vai para o mesmo cartão em no máximo 5 dias úteis (dias de trabalho).
- Só quem fez o pedido pode cancelá-lo.

1. **Mapeamento:** monte a história em cartões: um amarelo, três azuis, verdes e todos os vermelhos que surgirem. Como
   consigna deste exercício (não da técnica), ponha pelo menos dois verdes em cada regra que tenha borda ou exceção; se
   uma regra lhe parecer óbvia, anote por que não tem exemplo. Use 25 minutos como limite.
2. **Cenários:** escreva quatro em Dado / Quando / Então, em um arquivo `cancelar.feature` com `# language: pt`. Pelo
   menos um de cada regra, e pelo menos um que **não** seja caminho feliz.
3. **Famílias:** ao lado de cada um dos seus quatro cenários, escreva a que família pertence. Depois anote **duas
   famílias que você não usou** e uma linha sobre o porquê (porque não se aplicam, ou porque estão faltando).

**Revisão** (escolha a **família principal** de cada cenário; um pode tocar mais de uma, e você precisa acertar 9 de
11):

1. Cancelar um pedido que já saiu do armazém.
2. Cancelar um pedido em 31 de dezembro às 23:59:59.
3. Um cliente troca o número do pedido no endereço da página e cancela o pedido de outra pessoa.
4. O cliente aperta «Cancelar» duas vezes e o sistema faz dois reembolsos.
5. Cancelar um pedido recém-feito, ainda no armazém. É cancelado e o cliente é avisado.
6. O banco demora 40 segundos para responder ao reembolso.
7. O cliente escreve o motivo do cancelamento com emojis e aspas.
8. Duas pessoas da área de atendimento cancelam o mesmo pedido no mesmo segundo.
9. Tentar cancelar um pedido que não existe.
10. Uma pessoa que usa só o teclado não consegue chegar ao botão «Cancelar».
11. O pedido é marcado como «saiu do armazém» às 10:00:00, e o cliente aperta «Cancelar» às 09:59:59 e às 10:00:01.

---

## Para fechar

Sofía não precisava testar mais rápido, e sim perguntar antes. Uma conversa breve com quatro cartões azuis e três
vermelhos teria deixado visíveis o cupom de $80 e o cupom usado quatro vezes **antes** de programar, e não na quinta-feira
em finanças.

O que você leva daqui:

- Um cenário sai de uma **regra**. Se não há regra, primeiro se pergunta.
- **Dado** deixa de fora as demais regras, **Quando** é uma única ação e **Então** se vê de fora.
- Escreve-se o que faz o negócio, não as teclas.
- O caminho feliz é uma de onze famílias. As outras dez se descartam de propósito, nunca por esquecimento.

Na lição 02 você fica na borda das regras: como dividir os dados em grupos e escolher os poucos valores que encontram
quase todos os erros de limite.

---

## Compare as respostas

**Passo 2, cenários de R3.** Uma forma de escrevê-los:

```gherkin
# language: pt
Funcionalidade: Usar o cupom uma única vez

  Contexto:
    Dado que o cupom BIENVENIDA10 está vigente

  Regra: Cada cliente pode usar o cupom uma única vez

    Cenário: Primeira vez que ela usa
      Dado que Marta nunca usou o cupom BIENVENIDA10
      E tem no carrinho produtos no valor de $600.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela que o cupom foi aplicado

    Cenário: Segunda vez que ela tenta
      Dado que Marta já usou o cupom BIENVENIDA10 em uma compra anterior
      E tem no carrinho produtos no valor de $600.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja diz a ela que já usou este cupom
      E o subtotal dela continua em $600.00
```

Repare nos $600.00 dos dois: está acima do mínimo de R2, para que **só R3** decida o resultado. Se você usou $300, o seu
segundo cenário não vale por duas razões ao mesmo tempo e você não sabe qual das duas está funcionando.

**Exercício, mapeamento.** Perguntas vermelhas que valem a pena ter (não precisam sair iguais às suas):

- «Sair do armazém» é marcado por alguém à mão ou por um sistema? O que acontece no minuto em que muda?
- O reembolso pode ser cancelado se o banco já o processou?
- Alguém da área de atendimento pode cancelar pelo cliente? (Bate de frente com a terceira regra.)
- Os «5 dias úteis» contam os feriados?

**Revisão:** 1 estado e ordem · 2 tempo e fuso horário · 3 permissões · 4 idempotência e novas tentativas · 5 caminho
feliz · 6 integrações fora do ar · 7 dados sujos · 8 concorrência · 9 negativos · 10 qualidade de uso e operação ·
11 limites.

Por que esses quatro, se você ficou em dúvida: o **1** também é um negativo, mas o que o decide é a **sequência** (já
saiu do armazém). O **2** também é uma borda, mas o que o torna perigoso é a **virada de ano**. O **10** também é uma
rejeição, mas o que falha é que se possa **usar**. E o **11** é uma borda de tempo dentro da mesma manhã, sem virada de
dia: por isso é **limites**.

Se você confundiu 4 com 8: o 4 é **a mesma pessoa repetindo** a requisição (idempotência); o 8 são **duas pessoas
diferentes** ao mesmo tempo (concorrência).

---

## Fontes da lição

Abertas e lidas em 21/11/2026.

1. Matt Wynne, «Introducing Example Mapping», blog do Cucumber, 8 de dezembro de 2015. As quatro cores, a ordem, a
   pergunta em vermelho e os 25 minutos. https://cucumber.io/blog/bdd/example-mapping-introduction/
2. Cucumber, «Gherkin Reference». O que cada passo descreve: o **Given** é o contexto, quase sempre algo que já
   aconteceu; o **When** é a ação ou o evento; o **Then** é um resultado observável, não um registro no banco de dados.
   https://cucumber.io/docs/gherkin/reference/
3. Cucumber, palavras-chave do Gherkin em português (`gherkin-languages.json`): Funcionalidade, Regra, Contexto,
   Cenário, Dado, Quando, Então, E, Mas. https://github.com/cucumber/gherkin/blob/main/gherkin-languages.json
4. Cucumber, «Writing better Gherkin». O estilo declarativo em comparação com o imperativo.
   https://cucumber.io/docs/bdd/better-gherkin/
5. Cucumber, «Behaviour-Driven Development». As três práticas: descoberta, formulação e automação. Esta lição cobre as
   duas primeiras. https://cucumber.io/docs/bdd/
6. Martin Fowler, «GivenWhenThen», 21 de agosto de 2013. Origem da forma, com Dan North e Chris Matts, e a semelhança
   dela com o padrão de teste em quatro fases. https://martinfowler.com/bliki/GivenWhenThen.html
7. Dan North, «Introducing BDD». A forma original: «Given some initial context, When an event occurs, Then ensure
   some outcomes». https://dannorth.net/blog/introducing-bdd/
8. Ron Jeffries, «Essential XP: Card, Conversation, Confirmation». O cartão é um lembrete; o requisito se conta na
   conversa e se confirma com o teste de aceitação.
   https://ronjeffries.com/xprog/articles/expcardconversationconfirmation/
9. Bill Wake, «INVEST in Good Stories, and SMART Tasks». Uma boa história é testável: quem a escreve promete que a
   entende o suficiente para escrever um teste para ela.
   https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/
10. Mike Cohn, «User Stories», Mountain Goat Software. O modelo «Como… quero… para…» e a frase como lembrete de uma
    conversa. https://www.mountaingoatsoftware.com/agile/user-stories
11. Gojko Adzic, *Specification by Example*, Manning, 2011. Estudos de mais de 50 projetos que combinam o comportamento
    com exemplos concretos. https://gojko.net/books/specification-by-example/

Do curso e da Hábil: as onze famílias vêm do artigo [«Além do caminho feliz»](https://www.habil.mx/pt/blog/cenarios-de-teste-alem-do-caminho-feliz/) (Hábil, 2026). São **regras do
curso**, sem fonte externa:

- «Um **Dado** deixa de fora as demais regras, e cada **Então** olha só a sua regra»: existe para que, quando um
  cenário falhar, você saiba qual regra falhou.
- «Cada família que você descarta, descarta de propósito»: existe para que o risco que se aceita fique à vista.
