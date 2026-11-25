# Lição 04 — Estados e ordem

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Estado:** onde algo está no seu caminho. Um pedido «pago» é um estado; «entregue» é outro.
- **Evento:** o que acontece e pode mover algo de um estado para outro: o cliente paga, o armazém despacha, o cliente
  cancela.
- **Transição:** a passagem de um estado para outro por um evento. «Pago → cancela → cancelado» é uma transição.
- **Tabela de estados:** uma tabela com os estados nas linhas e os eventos nas colunas; em cada célula, para
  onde esse evento leva a partir desse estado.

**O que fica com você:** você desenha os estados de um pedido, preenche a tabela de estados dele e sabe ler as células vazias;
depois escreve cenários que testam eventos fora de ordem, e sabe qual deles pega o erro que deixa
cancelar o que já foi entregue.

**Ideia nova desta lição (a única que se avalia):** cada célula vazia de uma tabela de estados é um cenário.

**Em que ordem vai:** você encontra os estados e os eventos (passo 1), desenha o caminho (passo 2), preenche a tabela
(passo 3), lê as células vazias (passo 4) e escreve um cenário para cada célula (passo 5).

---

## A cena

*Cenário inventado; os estados, os valores e as mensagens da loja são reais.*

Segunda-feira, 10:00. Sofía recebe o pacote dela: uma camiseta azul. Às 10:20 ela entra em «Meus pedidos», vê o botão «Cancelar»
ainda lá e o aperta. A loja responde «Pedido 17 cancelado» e reembolsa $432.00 (pesos mexicanos) no cartão dela.

Sofía fica com a camiseta **e** com o dinheiro. Ela não trapaceou: a loja deixou.

No QA ninguém testou isso, e não foi por descuido. Testaram que dava para cancelar um pedido pago: funcionou. Testaram que
um pedido avançava de pago até entregue: funcionou. Cada passo do caminho, **na sua ordem**, estava certo. O que ninguém
testou foi um evento **fora da sua vez**: cancelar quando o pedido já tinha chegado.

A regra estava escrita, desde a lição 01: «pode-se cancelar enquanto o pedido não tiver saído do armazém».
O que faltou foi uma forma de ver, de uma só olhada, **todas** as vezes que alguém pode apertar um botão no
momento errado. Essa forma é a tabela desta lição.

---

## Antes de começar

**Sem computador nos passos 1 a 4.** Papel e lápis: você vai desenhar círculos e setas, e depois uma tabela. Para
o passo 5 você precisa do seu editor, como nas lições 01 a 03.

**Faça a primeira tentativa sem IA.** O que se avalia é se **você** encontra as células vazias e as transforma em
cenários. Se uma IA preenche a tabela para você, é fácil que ela preencha também as células que deveriam ficar vazias, e essas
são justamente as que você procura. Com a sua tabela na mão, depois sim você pode comparar.

**O que você já sabe e vai usar:** da lição 01, a história de cancelar um pedido e as suas regras; da 03, que
uma tabela obriga você a olhar todas as combinações, e que uma casela que ninguém sabe preencher é uma pergunta.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Encontre os estados e os eventos

Abra a loja de prática, entre como Marta e olhe «Meus pedidos». Cada pedido mostra uma palavra ao lado do seu
número: esse é o estado dele. A loja usa seis:

| Estado | O que significa |
|---|---|
| criado | O cliente montou o pedido, mas ainda não pagou |
| pago | O gateway aprovou a cobrança |
| no armazém | O armazém está preparando o pedido |
| enviado | Já saiu com a transportadora |
| entregue | Chegou às mãos do cliente |
| cancelado | Foi cancelado; se tinha sido cobrado, o dinheiro foi devolvido |

E três eventos podem mover um pedido:

| Evento | Quem o provoca |
|---|---|
| **paga** | O cliente, com o cartão dele |
| **avança** | O armazém ou a transportadora: prepara, envia, entrega |
| **cancela** | O cliente, com o botão «Cancelar» |

As regras que decidem qual evento move qual estado são três. A de cancelar vem da lição 01; as outras
duas são desta loja:

- O pedido segue esta ordem: criado → pago → no armazém → enviado → entregue. Só o pagamento o leva de «criado»
  para «pago».
- Pode-se cancelar enquanto o pedido não tiver saído do armazém. Se já foi cobrado, reembolsa-se no mesmo cartão;
  na regra da lição 01, o dinheiro chega em no máximo 5 dias úteis. A loja de prática registra o
  reembolso na hora.
- Um pedido se paga uma única vez.

---

## Passo 2 · Desenhe o caminho

Desenhe um círculo por estado e uma seta por cada evento que **sim** move o pedido. Sobre cada seta escreva o
evento; se além disso a loja faz algo, acrescente depois de uma barra. O programa do ISTQB usa essa mesma forma:
«evento / ação».

Assim fica (no papel fica melhor; aqui vai em texto):

```text
 criado ──paga──▶ pago ──avança──▶ no armazém ──avança──▶ enviado ──avança──▶ entregue
   │                │                    │
 cancela          cancela / reembolsa  cancela / reembolsa
   │                │                    │
   └────────────────┴────────────────────┴──────────▶ cancelado
```

Conte as setas: são **sete**. Cada uma é uma **transição válida**: um evento que, a partir desse estado, a loja
aceita.

Agora olhe o que o desenho **não** tem. Não há seta de «enviado» para «cancelado». Também não há de «entregue» para lugar
nenhum, nem de «cancelado» para lugar nenhum. No desenho, o que não se pode fazer **não se vê**: simplesmente não há
seta. E o que não se vê é muito fácil de não testar.

---

## Passo 3 · Preencha a tabela de estados

A tabela de estados diz o mesmo que o desenho, mas com uma diferença que importa: tem uma **célula para cada
estado e cada evento**, também para os que não devem acontecer. O programa do ISTQB explica assim: diferentemente do
diagrama, a tabela mostra explicitamente as transições inválidas, e as representa com células vazias.

Linhas: os seis estados. Colunas: os três eventos. Em cada célula, para qual estado esse evento leva a partir desse
estado, e a ação, se houver. Se o evento não deve mover o pedido, a célula fica **vazia**.

Antes de continuar, **preveja**: com seis estados e três eventos, quantas células tem a tabela, e quantas ficam
vazias? Escreva.

| Estado \ Evento | paga | avança | cancela |
|---|---|---|---|
| criado | pago | | cancelado |
| pago | | no armazém | cancelado / reembolsa |
| no armazém | | enviado | cancelado / reembolsa |
| enviado | | entregue | |
| entregue | | | |
| cancelado | | | |

São 6 × 3 = **18 células**. Sete estão preenchidas: são as sete setas do desenho. **Onze estão vazias.**

> **Um detalhe de «criado → cancela».** Cancelar um pedido que não foi pago não devolve nada, porque nada foi
> cobrado. A célula diz só «cancelado», sem «reembolsa».

> **Esta tabela é a das regras**, não uma foto da loja. Se a loja faz outra coisa em uma célula, a tabela
> ajuda você a notar. Confira com a ferramenta com a qual o armazém avança pedidos na loja de prática:
> `tienda pedido 1 avanzar` sobre um pedido «criado» responde «este pedido não está pago: o armazém só move pedidos
> pagos», e o pedido não se move. É a célula criado × avança, vazia: só o pagamento leva a «pago».

> **E um detalhe de «paga».** Se o cliente repete o pagamento com a **mesma** chave de idempotência (a da lição
> 00), não é outro pagamento: a loja repete a resposta anterior e não cobra de novo. A coluna «paga» desta
> tabela é um pagamento novo. As novas tentativas chegam na lição 08.

---

## Passo 4 · Leia as células vazias

Uma célula vazia diz: **«a partir daqui, este evento não deve mover o pedido»**. Não diz que o evento não possa acontecer.
Sofía sim apertou «Cancelar» com o pedido entregue; o botão estava lá. A célula vazia diz o que a loja **deveria** fazer
quando isso acontece: não mover o pedido, e dizer por quê.

Por isso **cada célula vazia é um cenário**. São onze, e cada uma é um evento fora da sua vez:

| Célula vazia | O que alguém tenta | O que deve acontecer |
|---|---|---|
| pago × paga | Pagar de novo o que já foi pago | Nada se cobra; o pedido continua «pago» |
| enviado × cancela | Cancelar o que já saiu | Não se cancela; a loja diz por quê |
| entregue × cancela | Cancelar o que já chegou (Sofía) | Não se cancela; a loja diz por quê |
| cancelado × paga | Pagar um pedido cancelado | Não se cobra |
| entregue × avança | Avançar o que já chegou | Não se move |
| … | (as outras seis, na sua folha) | |

Na loja de prática, nessas células vazias o pedido não se move e a loja responde com uma mensagem
(`<estado>` é o estado do pedido). Medido em 21/11/2026:

| Tentativa | O que a loja responde |
|---|---|
| Cancelar um pedido «enviado» ou «entregue» | «o pedido já saiu do armazém; não pode mais ser cancelado» |
| Cancelar um pedido «cancelado» | «o pedido já estava cancelado» |
| Pagar um pedido «pago», «enviado» ou «cancelado» | «este pedido não pode mais ser pago: está «`<estado>`»» |
| Avançar um pedido «entregue» ou «cancelado» | «um pedido «`<estado>`» não avança mais» |

**Uma célula vazia por cenário.** Se um cenário tenta dois eventos fora de vez seguidos e o primeiro falha
como deve, você nunca vai saber o que o segundo fez: a primeira falha tapa a outra. O programa do ISTQB chama isso de
**mascaramento de defeitos** e recomenda testar uma única transição inválida por caso de teste.

> **E se uma célula vazia ninguém sabe como preencher, é uma pergunta**, como na lição 03. Aqui todas têm
> resposta porque as três regras do passo 1 a dão. No exercício 1 você vai encontrar uma que não.

---

## Passo 5 · Um cenário por célula

Para escrever cenários de pedidos há seis frases do catálogo da sua loja que você ainda não usou: são as que
rodaram os exemplos desta lição antes de publicá-la. Escreva o seu `pedidos.feature` com elas. As frases:

| Tipo | Frase |
|---|---|
| Dado | que Marta tem um pedido `<estado>` |
| Quando | ela cancela o pedido |
| Quando | ela tenta pagar o pedido |
| Quando | o armazém avança o pedido |
| Então | o pedido fica `<estado>` / o pedido continua `<estado>` |
| Então | devolvem `<valor>` ao cartão dela |
| Então | a loja diz a ela que `<mensagem>` (a mesma das lições 01 a 03) |

O pedido dessas frases é sempre o mesmo: uma Camiseta azul, $432.00 com o frete. E o **Dado** não faz
o pedido aparecer no seu estado: ele o cria, o paga e o avança pelo caminho real até deixá-lo ali.

O **Dado** põe o pedido no estado da linha, o **Quando** dispara o evento da coluna, e o
**Então** confere o que diz a célula. Assim fica a célula de Sofía, entregue × cancela:

```gherkin
# language: pt
Funcionalidade: O caminho do pedido

  Regra: Cancela-se enquanto o pedido não sair do armazém

    Cenário: Entregue × cancela · não se cancela o que já chegou
      Dado que Marta tem um pedido entregue
      Quando ela cancela o pedido
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado
      E o pedido continua entregue
```

Leia o **Então**: ele confere as duas coisas que a célula vazia diz, a mensagem e que o pedido não se moveu. Se você só
conferisse a mensagem, uma loja que dissesse «não pode» mas cancelasse mesmo assim passaria no seu teste.

**Agora você:** em um arquivo `pedidos.feature`, copie o cenário de Sofía e escreva um para cada uma destas
células. São duas preenchidas, para ter o caminho permitido à vista, e mais duas vazias, para procurar eventos fora de
vez; cada cenário testa uma única célula:

1. pago × cancela (preenchida: fica cancelado e devolvem $432.00).
2. no armazém × cancela (preenchida: fica cancelado e devolvem $432.00).
3. enviado × cancela (vazia).
4. cancelado × paga (vazia).

Agrupe-os com `Regra:`, uma por regra do passo 1.

**Quanto você testou.** O programa do ISTQB mede esta técnica de três formas, e esclarece que um caso de teste
normalmente cobre várias transições. Aqui isso acontece no **Dado**: para deixar um pedido «enviado», ele percorre
criado → pago → no armazém → enviado. Essas transições também contam, porque foram executadas:

- **Todos os estados:** os estados pelos quais algum pedido passou, entre os seis.
- **Transições válidas:** as células preenchidas que foram executadas (no Dado ou no Quando), entre as sete.
- **Todas as transições:** as preenchidas que foram executadas e as vazias que você tentou, entre as dezoito.

Com os seus cinco cenários, faça as três contas. Você as compara no exercício 2.

---

## Como se confere

**O desenho e a tabela** (passos 2 e 3, e o exercício 1) se comparam com «Compare as respostas». O que tem
de coincidir: seis estados, sete setas, dezoito células, e as onze vazias **vazias**, não preenchidas com um
estado inventado.

**O seu arquivo `pedidos.feature`** é revisado pelo `verifica 04`. No terminal da loja, escreva:

```bash
verifica 04
```

Ele roda os seus cenários com a loja limpa, onde têm de sair **verdes**, e com o erro desta lição ligado, onde **pelo
menos um tem de sair vermelho**. Se saem verdes nas duas vezes, ele diz: «os seus testes não olham onde está o erro».
Antes de rodá-lo, a lista abaixo diz se a forma está certa. Os cenários de «Compare as respostas» foram rodados contra
a loja antes de publicar esta lição, junto com o que você copia do passo 5: verdes com a loja limpa, e dois em vermelho
com o erro ligado.

**Antes de salvar, revise o seu arquivo com esta lista:**

- [ ] A primeira linha é `# language: pt`.
- [ ] Há um cenário para cada célula que pediram, e o título diz qual célula é (estado × evento).
- [ ] O **Dado** põe o estado da linha e o **Quando** dispara o evento da coluna.
- [ ] Em cada célula vazia, o **Então** confere a mensagem **e** que o pedido continua no seu estado.
- [ ] Cada cenário tenta **uma única** célula vazia.

---

## Os exercícios

1. **As devoluções** (sem IA). A pessoa de produto passa a você estas regras para devolver um pedido entregue:
   - O cliente pede a devolução: a solicitação fica «solicitada».
   - O atendimento ao cliente a aceita ou a rejeita: fica «aceita» ou «rejeitada».
   - O cliente pode cancelar a sua solicitação enquanto não a tiverem aceitado: fica «cancelada».
   - Quando chega ao armazém o pacote de uma solicitação aceita, fica «recebida».
   - O que foi recebido é reembolsado: fica «reembolsada».

   Desenhe os estados, preencha a tabela de estados e encontre **pelo menos uma** célula vazia que as regras não
   resolvem: um evento que pode acontecer na vida real e sobre o qual ninguém disse o que fazer. Escreva-a como pergunta
   para produto. Dica: os pacotes chegam quando chegam. Use 25 minutos como limite.
2. **As suas contas.** Com os seus cinco cenários do passo 5, que porcentagem de cada cobertura você tem? Quantos
   cenários a mais você precisa para os 100% de todas as transições?
3. **Qual pega o erro?** A loja traz um erro plantado: com ele ligado, dá para cancelar um pedido
   enviado ou entregue, e a loja devolve o dinheiro. Sem rodar nada, escreva quais dos seus cinco cenários ficam
   vermelhos e por que os demais continuam verdes.

**Revisão** (tente resolver pelo menos 4 de 5; se algum não sair, volte ao passo 3):

1. Uma tabela com quatro estados e três eventos, quantas células tem?
2. Na tabela da loja, a célula pago × paga está preenchida ou vazia? Por quê?
3. Por que um cenário tenta uma única célula vazia e não duas?
4. Um pedido «no armazém» recebe «cancela». Para qual estado ele vai e o que a loja faz além disso?
5. Um pedido «enviado» recebe «avança». Para qual estado ele vai?

---

## Para fechar

Sofía não quebrou nada: apertou um botão que estava lá. O que faltava era um teste para o momento errado, e
esse teste não sai do desenho, porque no desenho o proibido não tem seta. Sai da tabela, porque na
tabela o proibido tem uma célula, e uma célula vazia se nota.

O que você leva daqui:

- Um fluxo com passos se desenha com **estados** e **eventos**; cada seta é uma transição válida.
- A **tabela de estados** tem uma célula por estado e evento; as vazias são o que não deve acontecer.
- **Cada célula vazia é um cenário**: o **Então** confere a mensagem e que o pedido não se moveu.
- **Uma célula vazia por cenário**, para que uma falha não tape a outra.
- Se ninguém sabe o que fazer em uma célula, é uma **pergunta para produto**.

Na lição 05 você muda de pergunta outra vez: já não é qual ordem, e sim o que fazer quando as combinações são tantas
que os testes não dão conta de todas.

---

## Compare as respostas

**Passo 3, previsão.** 6 × 3 = 18 células; 7 preenchidas e 11 vazias.

**Passo 4, as onze vazias.** pago × paga, no armazém × paga, enviado × paga, entregue × paga, cancelado × paga;
criado × avança, entregue × avança, cancelado × avança; enviado × cancela, entregue × cancela, cancelado × cancela.

**Passo 5, os cenários.** Estes são os que foram rodados contra a loja (o de Sofía está no passo 5):

```gherkin
# language: pt
Funcionalidade: O caminho do pedido

  Regra: Cancela-se enquanto o pedido não sair do armazém

    Cenário: Pago × cancela · cancela-se e devolve-se o que foi cobrado
      Dado que Marta tem um pedido pago
      Quando ela cancela o pedido
      Então o pedido fica cancelado
      E devolvem $432.00 ao cartão dela

    Cenário: No armazém × cancela · ainda dá
      Dado que Marta tem um pedido no armazém
      Quando ela cancela o pedido
      Então o pedido fica cancelado
      E devolvem $432.00 ao cartão dela

    Cenário: Enviado × cancela · já saiu do armazém
      Dado que Marta tem um pedido enviado
      Quando ela cancela o pedido
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado
      E o pedido continua enviado

  Regra: Um pedido se paga uma única vez

    Cenário: Cancelado × paga · não se cobra o que foi cancelado
      Dado que Marta tem um pedido cancelado
      Quando ela tenta pagar o pedido
      Então a loja diz a ela que este pedido não pode mais ser pago: está «cancelado»
      E o pedido continua cancelado
```

**Exercício 1.** Estados: sem solicitação (o pedido entregue), solicitada, aceita, rejeitada, cancelada,
recebida, reembolsada. Eventos: solicita devolução, aceita, rejeita, cancela, chega o pacote, reembolsa. Uma
pergunta que sai da tabela: «Se chega ao armazém o
pacote de uma solicitação **rejeitada** ou **cancelada**, o que fazemos com ele e com o cliente?». As regras só
dizem o que acontece quando chega o de uma aceita, mas o cliente pode ter mandado antes de saber a resposta. Se
você encontrou outra célula sem resposta que se sustenta (por exemplo, se dá para cancelar uma solicitação já
rejeitada), também vale.

**Exercício 2.** Conte também o que cada **Dado** percorre. Todos os pedidos nascem «criados», e entre os cinco
passam pelos seis estados: **6 de 6**. As sete células preenchidas são executadas: criado × paga, pago × avança, no
armazém × avança e enviado × avança nos Dado que levam o pedido adiante; criado × cancela no Dado do pedido
cancelado; pago × cancela e no armazém × cancela nos Quando. **7 de 7** transições válidas. E das onze
vazias você tenta três (enviado × cancela, entregue × cancela, cancelado × paga): 7 + 3 = **10 de 18** de todas as
transições. Para os 100% faltam **oito cenários**, um para cada vazia que você não tentou: pago × paga, no
armazém × paga, enviado × paga, entregue × paga, criado × avança, entregue × avança, cancelado × avança e cancelado
× cancela.

**Exercício 3.** Ficam vermelhos o de Sofía (entregue × cancela) e o de enviado × cancela: com o erro, a
loja os cancela e devolve o dinheiro, então o pedido não «continua» onde estava e a mensagem não chega. É o que
aconteceu ao rodá-los: dois em vermelho. Os demais continuam verdes: cancelar um pedido pago ou no armazém já era permitido,
e pagar um cancelado não tem a ver com este erro.

Repare em uma coisa: com **7 de 7** transições válidas você já tem os 100% da cobertura que o programa do ISTQB chama de
a mais usada, e mesmo assim o erro vive **só** em células vazias. Um teste que percorre o caminho na sua ordem, de
criado até entregue, sai verde com o erro ligado. Quem o pega são as vazias que você tentou.

**Revisão.** 1, doze (4 × 3). 2, vazia: um pedido se paga uma única vez. 3, porque se a primeira falha como deve, tapa
o que a segunda faria. 4, para cancelado, e devolve o que foi cobrado ao mesmo cartão. 5, para entregue.

---

## Fontes da lição

1. ISTQB, *Certified Tester Foundation Level Syllabus* v4.0.1, 2024-09-15, §4.2.4 «State Transition Testing»
   (pp. 41–42). Estados, transições iniciadas por um evento e a forma «event [guard condition] / action»; a tabela
   de estados com os estados nas linhas e os eventos nas colunas; «the state table explicitly shows
   invalid transitions, which are represented by empty cells»; as três coberturas (todos os estados, transições
   válidas e todas as transições), com «One test case may, and usually will, cover several transitions between
   states» e «Valid transitions coverage is the most widely used coverage criterion»; e «Testing only one invalid transition in a single test case helps to avoid
   defect masking». https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf
2. Cucumber, «Gherkin Reference»: «Given steps are used to describe the initial context of the system»; «When
   steps are used to describe an event, or an action». Sustenta que o Dado põe o estado e o Quando dispara o
   evento. https://cucumber.io/docs/gherkin/reference/
3. Cucumber, «Behaviour-Driven Development»: «It may also reveal gaps in our understanding, where we need more
   information before we know what to do». Sustenta que uma célula sem resposta vira pergunta.
   https://cucumber.io/docs/bdd/

Medição própria: os estados, os eventos e as mensagens foram medidos contra a loja do curso (hb-curso-qa,
develop 0ddda22) em 21 de novembro de 2026, com a API dela no ar sem Docker. Os cinco cenários da lição foram
rodados com behave e uma versão de teste das frases de pedidos: 5 de 5 em verde com a loja limpa; com o
erro E3 ligado, 2 em vermelho (enviado e entregue).

Regras do curso, sem fonte externa:

- «Cada célula vazia é um cenário»: o programa do ISTQB pede tentar as transições inválidas para a cobertura
  de todas as transições; o curso transforma isso em hábito para que nenhuma célula vazia fique sem ser testada.
- «O Então de uma célula vazia confere a mensagem e que o pedido não se moveu»: existe porque uma loja pode
  dizer «não pode» e fazê-lo mesmo assim.
