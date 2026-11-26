# Lição 14 — Junte tudo: a história de segunda-feira

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Esta lição não traz nenhuma técnica nova.** Ela traz um dia de trabalho: uma história de usuário que chega na
segunda-feira, a loja com erros que ninguém conta para você, e tudo o que você aprendeu no curso para encontrá-los. A
única novidade é uma decisão: **o que testar primeiro**, de acordo com o risco.

**Antes de ler, três palavras.**

- **Modo segunda-feira:** um modo da loja que liga vários erros **sem dizer quais**. É como receber um sistema real: os
  erros já estão lá e ninguém passou a lista para você.
- **Impacto:** quanto estrago um critério faz se falhar.
- **Probabilidade:** quão provável é que ele falhe.

**O que fica com você:** quatro arquivos que cobrem uma história completa —cenários, uma coleção de API, um teste de
navegador e um relatório— e uma tabela que diz qual parte do ofício de QA este curso cobre e o que falta para você.

**Em que ordem vai:** você lê a história e decide o que testar primeiro (passo 1); escreve os cenários (passo 2), a
coleção (passo 3) e o teste de navegador (passo 4) contra a loja limpa; liga a segunda-feira e lê os vermelhos
(passo 5); reporta um (passo 6); e se situa diante do exame da indústria (passo 7).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são reais.*

Segunda-feira, 9:00. Chega ao quadro da equipe uma história de usuário nova, com quatro critérios de aceitação. A
programadora diz que já está pronta. O produto quer lançá-la na quarta. Cabe a você dizer se ela sai.

Ninguém diz onde estão os erros. Pode ser que não haja nenhum. Pode ser que haja vários. A única coisa que você tem é o
que aprendeu em treze lições: cenários, uma coleção que roda sozinha, um teste de navegador e um relatório que pode ser
reproduzido.

---

## Antes de começar

**Você precisa da loja de pé.** Como nas lições 06 a 13: `./practicar` no seu computador e, em outra janela, o terminal
da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`.

> **Esta lição usa a loja da lição 11**, com os oito erros, de E1 a E8.

**Você precisa de três coisas de lições anteriores**, em `~/practica`:

| Arquivo | Da lição |
|---|---|
| `tienda.postman_collection.json` | 07 |
| `permisos.postman_collection.json` e `local.postman_environment.json` (o que tem `otra_cliente`) | 08 |
| `compra.py` | 11 |

**Comece com a loja limpa:**

```bash
tienda reiniciar
tienda error estado
```

Os oito têm que dizer «desligado». Se algum estiver ligado, desligue-o com `tienda error EX off`.

---

## Passo 1 · A história, e o que testar primeiro

Esta é a história de segunda-feira:

> **Como cliente, quero comprar com meu cupom pela página, ver meu pedido e cancelá-lo enquanto ele não sair do
> armazém.**
>
> - **CA-1.** O frete é grátis a partir de $999.00, medido **depois** do cupom.
> - **CA-2.** Se eu pagar pela página, meu pedido fica pago.
> - **CA-3.** Posso cancelar meu pedido enquanto ele não sair do armazém; depois, não.
> - **CA-4.** Só eu vejo meus pedidos.

Nada disso é novo para a loja: são regras que você já testou separadamente. O novo é que hoje elas chegam juntas, e que
você tem um dia.

Com um dia não dá para testar tudo. A ISTQB chama de **testes baseados em risco** decidir o que testar, em que ordem e
com quanto esforço de acordo com o risco de cada coisa; o risco se estima com o impacto e a probabilidade. Para cada
critério, pergunte-se duas coisas: quanto estrago faz se falhar (impacto)? E quão provável é que falhe
(probabilidade)? E uma terceira, que é regra deste curso: com que ferramenta eu o vejo com menos esforço?

| CA | Se falhar… | Impacto | Probabilidade | Ordem | Ferramenta | Por que essa |
|---|---|---|---|---|---|---|
| CA-2 pagar pela página | Ela acha que pagou e o pedido dela nunca foi pago | Alto | Alta: é a novidade da história | 1.º | **Navegador** (lição 11) | Só se vê pela página |
| CA-1 frete | A cliente paga $99.00 que não devia | Alto | Alta: cupom e frete juntos, na borda | 2.º | **Cenários** (lições 02 e 03) | É uma regra com bordas: $999.00 exatos, com e sem cupom |
| CA-4 só eu | Outra cliente vê o pedido da Marta | Alto | Média: já existia | 3.º | **Coleção** (lição 08) | É uma permissão: testa-se com duas sessões contra a API |
| CA-3 cancelar | Reembolsa-se algo que já saiu do armazém | Alto | Média: já existia | 4.º | **Cenários** (lição 04) | É um caminho de estados |

Esta é a avaliação deste exercício, não uma regra: outra equipe, com outros dados, pode ordená-los de outro jeito. Aqui
os quatro fazem muito estrago, então a probabilidade desempata: o que a história muda é o mais provável de quebrar. Os
passos 2 a 4 vão por ferramenta para você não pular de arquivo em arquivo; se um dia não desse, CA-2 e CA-1 seriam os
primeiros.

Repare na coluna «Ferramenta». **O navegador aparece uma só vez**, para a única coisa que não se pode ver de outra forma.
É a regra da lição 11, e coincide com o que propõe Ham Vocke em «The Practical Test Pyramid»: muitos testes pequenos e
rápidos, e pouquíssimos de ponta a ponta. Como primeiro cálculo, o blog de testes do Google sugere 70% de testes
unitários, 20% de integração e 10% de ponta a ponta; é uma sugestão dessa equipe, não uma proporção obrigatória.

---

## Passo 2 · Os cenários

Em `~/practica`, crie o arquivo:

```bash
nano lunes.feature
```

Escreva os cenários de CA-1 e CA-3. Use só frases do catálogo, as mesmas das lições 02 a 04. Estes são os que foram
medidos; os seus podem ser outros, desde que cubram as bordas:

```gherkin
# language: pt
Funcionalidade: Comprar com cupom e cancelar a tempo

  Regra: O frete é grátis a partir de $999.00, medido depois do cupom

    Cenário: Sem cupom, exatamente $999.00 · não paga frete
      Dado que Marta não tem nenhum cupom aplicado
      E ela tem no carrinho produtos no valor de $999.00
      Quando ela vai pagar
      Então o frete que a loja mostra a ela é de $0.00

    Cenário: Com cupom, $1,110.00 fica exatamente em $999.00 · não paga frete
      Dado que o cupom BIENVENIDA10 está vigente
      E que Marta nunca usou o cupom BIENVENIDA10
      E ela tem no carrinho produtos no valor de $1,110.00
      Quando ela aplica o cupom BIENVENIDA10
      Então a loja mostra a ela um desconto de $111.00
      E o frete que a loja mostra a ela é de $0.00

  Regra: Cancela-se enquanto o pedido não sair do armazém

    Cenário: No armazém · ainda dá para cancelar
      Dado que Marta tem um pedido no armazém
      Quando ela cancela o pedido
      Então o pedido fica cancelado
      E devolvem $432.00 ao cartão dela

    Cenário: Enviado · não dá mais para cancelar
      Dado que Marta tem um pedido enviado
      Quando ela cancela o pedido
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado
      E o pedido continua enviado
```

**Preveja antes de seguir:** por que o segundo cenário usa $1,110.00 e não $999.00?

O behave lê cenários escritos em linguagem natural, que alguém que não programa consegue ler, e os roda contra a loja.
Até agora, seus cenários eram rodados pelo `verifica`. Hoje você mesmo os roda, porque no modo segunda-feira você vai
precisar vê-los vermelhos com seus próprios olhos. O behave procura as frases em uma pasta `steps`; crie uma com uma só
linha, que traz o catálogo de frases da loja:

```bash
mkdir -p steps
echo "from pasos_tienda import *" > steps/tienda.py
```

O `>` cria o arquivo e, se ele já existia, o substitui. Se você repetir a lição e já tiver `steps/tienda.py`, pule essa
linha.

E rode-os:

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

No final, no resumo, têm que aparecer estas linhas:

```text
2 rules passed, 0 failed, 0 skipped
4 scenarios passed, 0 failed, 0 skipped
18 steps passed, 0 failed, 0 skipped
```

O resumo sai em inglês mesmo que sua loja esteja em outro idioma: quem o imprime é o behave, não a loja.

Se alguma frase sair como `undefined`, ela não está no catálogo: copie-a exatamente das lições 02 a 04.

---

## Passo 3 · A coleção

Você já tem as requisições: a coleção da lição 07 testa o frete de três camisetas, e a da 08 testa que outra cliente não
veja o pedido da Marta. Para segunda-feira, junte-as em uma só coleção:

```bash
jq -s '{info: {name: "lunes", schema: .[0].info.schema}, item: (.[0].item + .[1].item)}' \
  tienda.postman_collection.json permisos.postman_collection.json > lunes.postman_collection.json
```

Este comando é uma receita para juntar as duas coleções: não é o que esta lição ensina, então cole-o do jeito que está.
O que cada peça faz, caso você queira saber:

| Peça | O que faz |
|---|---|
| `jq -s` | Lê os dois arquivos e os coloca numa lista: `.[0]` é o da 07 e `.[1]` o da 08 |
| `info: {…}` | Dá nome à coleção nova e copia o formato da 07 |
| `item: (.[0].item + .[1].item)` | Coloca as requisições da 07 e, atrás, as da 08 |
| `> lunes.postman_collection.json` | Salva o resultado em `lunes.postman_collection.json`; os dois originais não são tocados. Se esse arquivo já existia, ele o substitui |

O newman é o programa que roda coleções do Postman pelo terminal. Confira que as doze requisições ficaram e rode-a com
o ambiente da lição 08:

```bash
jq '.item | length' lunes.postman_collection.json
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

O primeiro comando diz `12`: as três da lição 07 e as nove da 08. No resumo do newman, as duas linhas que importam:

```text
│                requests │              12 │               0 │
│              assertions │              19 │               0 │
```

Doze requisições, dezenove verificações, zero falhas.

---

## Passo 4 · O teste de navegador

Para CA-2 você já tem o teste: seu `compra.py` da lição 11 entra como Marta, compra uma camiseta pela página e confere
em «Meus pedidos» que ela ficou paga. É o que pede a documentação do Playwright: que o teste confira que a página
funciona para quem a usa, não como ela é feita por dentro. Copie-o com o nome de segunda-feira:

```bash
cp -n compra.py lunes.py
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

O `-n` diz ao `cp` que não substitua `lunes.py` se ele já existir: se você repetir a lição, não perde a sua versão.

Termina em `código de salida: 0`.

**Você já tem as três peças em verde com a loja limpa.** Na lição 13 você aprendeu que isso ainda não diz se elas servem.
Para saber, é preciso a segunda-feira.

---

## Passo 5 · A segunda-feira

Ligue o modo segunda-feira:

```bash
tienda lunes
```

A loja responde:

```text
🌙 Modo segunda-feira ligado: a loja tem erros escondidos. Ela não diz quais; encontre-os com seus testes.
   Enquanto durar, «tienda error» não muda nada. Quando terminar: tienda lunes fin
```

Se você tentar descobrir, a loja não conta:

```bash
tienda error estado
```

```text
🌙 Modo segunda-feira: há erros escondidos e a loja não diz quais. Encerre com: tienda lunes fin
```

Ela não diz quais nem quantos. E, como avisou ao ligar, enquanto durar a segunda-feira «tienda error» não muda nada:
você não pode desligar um erro para ver se era aquele.

Agora rode suas três peças, uma por uma, com `tienda reiniciar` antes de cada uma. Reiniciar não desliga a
segunda-feira, e a loja lembra você disso toda vez:

```text
✅ a loja voltou ao estado de recém-aberta
🌙 O modo segunda-feira continua ligado: reiniciar não o desliga. Encerre com: tienda lunes fin
```

```bash
tienda reiniciar
behave --no-capture --format plain lunes.feature
```

Com os erros da história ligados, os cenários dizem isto (as linhas que importam):

```text
      Então o frete que a loja mostra a ela é de $0.00 ... failed in 0.000s
ASSERT FAILED: a loja mostrou um frete de $99.00, não de $0.00
      E o frete que a loja mostra a ela é de $0.00 ... failed in 0.000s
ASSERT FAILED: a loja mostrou um frete de $99.00, não de $0.00
      Então a loja diz a ela que o pedido já saiu do armazém; não pode mais ser cancelado ... failed in 0.000s
ASSERT FAILED: a loja disse «(nada: aceitou)», não «o pedido já saiu do armazém; não pode mais ser cancelado»
1 scenario passed, 3 failed, 0 skipped
```

```bash
tienda reiniciar
newman run lunes.postman_collection.json -e local.postman_environment.json
```

No final, a tabela de falhas do newman:

```text
 1.  AssertionError  frete grátis
 2.  AssertionError  pedido alheio: código 404
 3.  AssertionError  sem produtos
```

```bash
tienda reiniciar
python3 lunes.py
echo "código de salida: $?"
```

Termina em `código de salida: 1`, e antes do código vêm as linhas do Playwright que você já conhece da lição 11:

```text
  - waiting for locator("#lista-pedidos .pedido .estado").first
    13 × locator resolved to <span class="estado" data-estado="creado">criado</span>
       - unexpected value "creado"
```

O número de tentativas (`13 ×`) pode sair diferente para você: depende de quão rápido é o seu computador.

**Agora interprete os vermelhos:** você não precisa saber qual interruptor foi ligado;
identifique a regra quebrada e o critério afetado:

| Vermelho | Que regra se quebrou | Critério |
|---|---|---|
| Frete de $99.00 em $999.00, sem cupom e com cupom | O frete grátis não começa em $999.00 exatos | CA-1 |
| O cancelamento de um pedido enviado foi aceito | Cancela-se algo que já saiu do armazém | CA-3 |
| A outra cliente recebeu 200 e os produtos | Uma cliente vê o pedido de outra | CA-4 |
| O pedido pago pela página fica em «criado» | Pagar pela página não paga | CA-2 |

Quatro achados, um por critério. Repare em duas coisas:

1. **Cada ferramenta viu algo diferente.** O navegador só viu CA-2; a coleção viu CA-1 e CA-4; os cenários viram CA-1 e
   CA-3. Nenhuma peça sozinha teria encontrado os quatro.
2. **CA-1 foi visto por duas peças.** Isso não é desperdício: é a mesma regra vista por dois lados, e se um dia você
   mudar um dos dois testes, o outro continua cuidando de você.

**A história sai na quarta?** Não. Com quatro critérios quebrados, sua resposta é «não sai», com os quatro achados como
evidência.

---

## Passo 6 · O relatório

Reporte **um** dos quatro, com o formato da lição 12. Escolha o que você consegue reproduzir com menos passos. O do
frete se reproduz com dois comandos: crie `~/practica/reporte.md` com estas seções.

```markdown
# O frete é cobrado em um carrinho de exatamente $999.00

**Severidade:** alta — cobra a mais da cliente.
**Prioridade:** média — no que foi medido, só acontece com um carrinho de exatamente $999.00; proponho o trabalho planejado.

## Passos
```

e dentro de «Passos», o bloco que se cola:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Depois, «Resultado esperado», «Resultado obtido» e «Evidência», como na lição 12. Severidade alta porque cobra a mais;
prioridade média porque, no que você mediu, só acontece com um carrinho de exatamente $999.00 (a mesma resposta do
exercício 1 da lição 12). As saídas medidas:

| Loja | O que imprime |
|---|---|
| Limpa | `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}` |
| Na segunda-feira | `{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}` |

Duas regras da lição 12 que hoje pesam mais:

- **O relatório não nomeia o erro nem o liga.** Não escreva `tienda lunes` nem `tienda error` nos passos: quem vai
  consertar não conhece os interruptores do curso. Também não escreva «E1»: você não sabe que número é; você sabe que
  regra se quebrou.
- **Fatos à parte das suspeitas.** O que você viu é «$99.00 em $999.00». Que «a comparação usa maior que em vez de
  maior ou igual» é uma suspeita: se você a colocar, marque-a como tal.

Quando terminar, feche a segunda-feira:

```bash
tienda lunes fin
```

```text
✅ Modo segunda-feira encerrado: os 4 erros que ele tinha foram desligados. Os demais ficaram como estavam antes da segunda-feira.
```

Até aqui você não sabia quantos eram. Agora sabe, e pode comparar: a sua suíte viu quatro vermelhos diferentes?

**O que a sua suíte de segunda-feira não cobre.** A loja tem oito erros e a sua suíte vê quatro. Os outros quatro
precisam de condições que você hoje não criou: dois pagamentos ao mesmo tempo (lição 09), um gateway que demora (lições
08 e 10) ou um relógio fora de hora (lição 09). É a ideia da lição 13 aplicada a um dia real: um verde diz que o que
você testou funciona, não que a loja funciona. Dizer o que você **não** testou faz parte do relatório de um dia de QA.

---

## Passo 7 · Onde você fica diante do exame ISTQB

Um exame de entrada conhecido em QA é o **ISTQB Certified Tester Foundation Level (CTFL)**, versão 4.0; a página oficial
oferece o programa 4.0.1. Este curso **situa você em relação a** esse programa: mostra que partes você já tocou e
quais ficam de fora. Assim eles se cruzam, capítulo por capítulo:

| Capítulo do programa CTFL | O que você tocou neste curso | O que falta para você |
|---|---|---|
| 1 · Fundamentos de teste | De uma falha se busca o seu defeito; testar tudo não é possível (00); um verde não prova que não há erros (13) | Os sete princípios completos, como o programa os enuncia; atividades, produtos de teste (*testware*) e papéis; habilidades e boas práticas de quem testa |
| 2 · Testes ao longo do ciclo de vida de desenvolvimento de software | Testes de API e de navegador (07, 11); testes que se repetem depois de uma mudança (07, 13) | Níveis de teste (unidade, integração, sistema, aceitação) e tipos de teste, com nome; testes de manutenção |
| 3 · Testes estáticos | — | Revisões e inspeções de documentos e de código, sem rodar nada |
| 4 · Análise e modelagem de testes | Cenários a partir de uma história (01), partições e bordas (02), tabelas de decisão (03), transição de estados (04), combinações (05) | Técnicas de caixa branca; técnicas baseadas na experiência, como o teste exploratório; abordagens baseadas na colaboração |
| 5 · Gerenciamento das atividades de teste | Testes baseados em risco (14); relatório de defeitos (12) | Planejamento dos testes; monitoramento, controle e encerramento; gerenciamento de configuração; o ciclo completo de gerenciamento de defeitos |
| 6 · Ferramentas de teste | behave, newman e Playwright (02, 07, 11); testes escritos por uma IA (13) | Benefícios e riscos de automatizar, como o programa os apresenta |

Os capítulos e suas seções saem da página oficial da ISTQB, aberta em 22 e 25/11/2026. A tabela é um guia para você se
situar, não o programa completo: para o exame, quem manda é o programa. O capítulo em que mais falta para você é o 3: os
testes estáticos se fazem **sem** rodar nada, e este curso não os ensinou como técnica. O mais perto que você chegou foi
na lição 13, quando leu um teste contra a regra dele antes de rodá-lo.

---

## Como se confere

Antes de rodar o `verifica`, confira:

- [ ] Com a loja limpa, as três peças saem verdes: os cenários sem frases `undefined`, a coleção sem falhas e `lunes.py`
      terminando em 0.
- [ ] `lunes.py` e a coleção não trazem escritos à mão o endereço da loja, nem a Marta, nem o Luis, nem as senhas
      deles (procure-os com
      `grep -n -i -e localhost -e marta -e luis -e practica lunes.py lunes.postman_collection.json`; não pode imprimir
      nada).
- [ ] Na segunda-feira, cada critério da história tem pelo menos uma peça vermelha, e você anotou junto a cada critério
      o nome do teste vermelho que o viu.
- [ ] No relatório, «Resultado esperado» nomeia a regra («a partir de $999.00») e $0.00; «Resultado obtido» nomeia
      $99.00 e $1,098.00; «Evidência» copia uma saída com esses valores.
- [ ] `reporte.md` tem as seções da lição 12 e um único bloco `bash` em «Passos», sem `tienda error`, `tienda lunes` nem
      `/control/`.
- [ ] Os passos do relatório, colados numa loja limpa, imprimem algo diferente do que na segunda-feira.
- [ ] Você fechou a segunda-feira com `tienda lunes fin`.

Duas caixas desta lista não são conferidas pelo `verifica`: a de anotar qual teste vermelho viu cada critério e a do que
você escreveu em «Resultado esperado», «Resultado obtido» e «Evidência». Acontece como na lição 12: o `verifica`
confere o que os seus passos fazem com a loja, não o que você escreveu. **Essas duas quem confere é você.** Um relatório
com os passos certos e essas seções vazias sai verde e não serve para ninguém.

Depois, no terminal da loja:

```bash
verifica 14
```

**O que o `verifica 14` faz:** ele não usa o modo segunda-feira. Liga **cada** erro da história separadamente e, com
cada um, exige que pelo menos uma das suas três peças saia vermelha. Depois roda os passos do seu relatório limpos e com
cada erro, e exige que com pelo menos um a saída mude.

O `verifica` também não diz quais são os erros: ele os conta como «erro 1 de 4», «erro 2 de 4», e assim por diante.

Com tudo no lugar, o `verifica 14` fica assim:

```text
Verificando a lição 14…

✅ Seu arquivo lunes.feature está em ~/practica
✅ Seu arquivo lunes.postman_collection.json está em ~/practica
✅ Seu arquivo local.postman_environment.json está em ~/practica
✅ Seu arquivo lunes.py está em ~/practica
✅ Seu arquivo reporte.md está em ~/practica
✅ Seu local.postman_environment.json traz base, cliente, contrasena, otra_cliente e otra_contrasena, como o da lição 08
✅ Seu lunes.py e sua coleção não trazem escritos à mão o endereço da loja, nem Marta, nem Luis, nem as senhas deles
✅ O seu reporte.md tem as quatro seções: Passos, Resultado esperado, Resultado obtido e Evidência
✅ A seção «Passos» tem um único bloco de comandos bash
✅ Os seus passos não ligam erros nem mexem no controle da loja
✅ Cada passo de lunes.feature é uma frase do catálogo da loja
✅ Com a loja limpa, seus cenários saem em verde (4)
✅ Com a loja limpa, sua lunes.postman_collection.json sai verde
✅ Com a loja limpa, seu lunes.py termina em 0
✅ Com o erro 1 de 4 da segunda-feira ligado sozinho, seu lunes.feature sai vermelho
✅ Com o erro 2 de 4 da segunda-feira ligado sozinho, seu lunes.feature sai vermelho
✅ Com o erro 3 de 4 da segunda-feira ligado sozinho, seu lunes.postman_collection.json sai vermelho
✅ Com o erro 4 de 4 da segunda-feira ligado sozinho, seu lunes.py sai vermelho
✅ Com a loja limpa, os passos do seu relatório imprimem a mesma coisa nas duas vezes
✅ Na segunda-feira, os passos do seu relatório imprimem outra coisa que com a loja limpa: reproduzem um erro da história

🎉 Lição completa!
```

Se você rodar com a loja limpa, ao terminar ele deixa os oito erros desligados, como os encontrou.

---

## Seus exercícios

1. **Uma peça a menos.** Rode a segunda-feira de novo, mas sem `lunes.py`. Que critério fica sem nenhum vermelho? O que
   você diria ao produto sobre esse critério, se o navegador não existisse?
2. **Outro relatório.** Reporte o achado de CA-4 (a outra cliente vê o pedido da Marta) em
   `~/practica/reporte-ajeno.md`. Use duas sessões nos passos, como na coleção da lição 08. Teste-o limpo e na
   segunda-feira antes de dá-lo por bom.
3. **No papel, sem a loja.** Uma história nova: «Como cliente, quero que meu carrinho seja guardado se eu fechar a
   página». Escreva os critérios de aceitação dela e, para cada um, que ferramenta do curso você usaria e por quê, com
   uma tabela como a do passo 1. Resolva sem IA para praticar seu critério.

---

## Para fechar

Você começou o curso com uma história e uma pergunta: que cenários encontram erros? Hoje você recebeu uma história nova,
decidiu o que testar primeiro, escreveu três tipos de teste, encontrou quatro erros que ninguém contou para você e
reportou um para que o consertem. Isso é um dia de QA.

**Revisão:**

1. Por que o navegador aparece uma só vez na tabela do passo 1?
2. Duas peças viram CA-1. É desperdício? Por quê?
3. O que falta ao seu relatório se você disser «E1» em vez da regra que se quebrou?
4. Nomeie uma condição que a sua suíte de segunda-feira não criou, e um erro que por isso ela não podia ver.
5. Que capítulo do programa CTFL este curso não tocou, e por quê?

---

## Compare as respostas

**A previsão do passo 2.** Com o cupom de 10%, $1,110.00 fica em $999.00 exatos depois do desconto: $1,110.00 menos
$111.00. É a borda de CA-1 medida **depois** do cupom. Com $999.00 antes do cupom, a cliente paga $899.10 e aí sim paga
frete: esse é outro cenário, o da coluna 8a da lição 03.

**Exercício 1.** CA-2 fica sem nenhum vermelho: só o navegador o via. Sem navegador, você diria ao produto que CA-2 não
está testado: na medição, a coleção e os cenários continuaram verdes com este erro, e a página é o que ninguém
conferiu. Dizê-lo faz parte do relatório.

**Exercício 2.** Os passos precisam de dois `TOKEN`: o da Marta cria o pedido e o do Luis o consulta. Limpa, a consulta
do Luis dá 404; na segunda-feira, 200 com os produtos da Marta.

**Exercício 3.** Não há uma única resposta. Uma boa tabela tem um critério por linha, impacto e probabilidade com seu
porquê, uma ferramenta por critério, e critérios que podem ser observados. Um exemplo de duas linhas: «ao fechar a
página e voltar a abri-la, o carrinho conserva produto e quantidade» vai para o **navegador**, porque fechar e reabrir a
página faz parte do percurso; «o carrinho guardado é só de quem o montou» vai para a **coleção**, porque é uma
permissão que se testa com duas sessões. Se o navegador aparecer em mais de uma linha, confira se alguma pode ser vista
pela API.

**Revisão.**

1. Porque só CA-2 se vê unicamente pela página. Os testes de navegador demoram mais (umas 1,3 vezes a coleção na lição
   11) e podem sair vermelhos sem que a loja tenha erro (o exercício 3 da lição 11); guardam-se para o que não se vê de
   outra forma.
2. Não. É a mesma regra vista por dois testes diferentes: se um muda ou quebra, o outro continua cuidando da regra.
3. Quem vai consertar não sabe o que é «E1». O relatório diz que regra se quebrou e como vê-la, não o interruptor do
   curso.
4. Por exemplo, dois pagamentos ao mesmo tempo: sem eles, o cupom que se usa duas vezes (lição 09) não aparece.
5. O 3, testes estáticos: tudo no curso foi testado rodando a loja, e os testes estáticos revisam documentos e código sem
   rodá-los.

---

## Fontes da lição

Consultadas em 22 de novembro de 2026.

1. ISTQB, «Certified Tester Foundation Level (CTFL) v4.0» (capítulos e seções do programa; programa vigente v4.0.1).
   https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
2. ISTQB Glossary, *risk-based testing*, *exploratory testing* e *test basis*. https://glossary.istqb.org/
3. Ham Vocke, «The Practical Test Pyramid», em martinfowler.com.
   https://martinfowler.com/articles/practical-test-pyramid.html
4. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog.
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
5. Playwright, «Best Practices». https://playwright.dev/docs/best-practices
6. behave, «Behavior Driven Development». https://behave.readthedocs.io/en/stable/philosophy/
7. Postman, «Run collections using Newman». https://learning.postman.com/docs/collections/using-newman-cli/command-line-integration-with-newman/
8. Mozilla, «Bug Writing Guidelines». https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
