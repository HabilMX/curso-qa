# Lição 12 — Reportar para que consertem

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Relatório de defeito:** o texto que você entrega a quem vai consertar um erro. Nas equipes, dizem *bug report* ou
  *issue*.
- **Severidade:** quanto dano o erro causa.
- **Prioridade:** com que urgência ele precisa ser consertado.

**O que fica com você:** um arquivo, `reporte.md`, com o erro da lição 04 escrito de modo que qualquer pessoa o
reproduza colando seus passos no terminal dela. Você também aprende a dar a ele severidade e prioridade, e a registrá-lo
numa matriz de testes e num relatório de QA com o formato que usamos na Hábil.

**Ideia nova de QA desta lição:** um erro que outra pessoa não consegue reproduzir quase nunca é consertado. Encontrá-lo
era metade do trabalho; a outra metade é que alguém mais o veja como você. A severidade, a prioridade e o formato da
casa são o que acompanha essa ideia quando o relatório entra numa equipe; você os vê nos passos 4 e 5.

**Em que ordem vai:** você vê o que faltava a um relatório que não serviu (passo 1); escreve os passos como comandos
(passo 2); confere que funcionam na loja de outra pessoa (passo 3); dá a ele severidade e prioridade (passo 4); e o
registra no formato da casa (passo 5).

---

## A cena

*Cenário inventado; as respostas e os erros da loja são reais.*

Lembra da Sofía, da lição 04? Ela recebeu a camiseta dela, apertou «Cancelar» e a loja devolveu o dinheiro. Desta vez
alguém do QA viu primeiro e escreveu este relatório:

> **Dá para cancelar pedidos que não deveriam ser cancelados!!! URGENTE**
>
> Cancelei um pedido e a loja deixou eu cancelar. Isso está errado. Acho que é por causa da mudança da semana passada.

O programador leu, entrou na loja dele, fez um pedido, pagou e cancelou. A loja cancelou e reembolsou. Ele respondeu
«funciona como deve: um pedido pago pode ser cancelado» e fechou o relatório.

Os dois tinham razão com o que sabiam. O relatório não dizia **em que estado** estava o pedido, nem **o que** deveria
ter acontecido, nem trazia **nada** que o provasse. E a frase sobre «a mudança da semana passada» era uma suspeita, não
um fato; o programador perdeu um tempo verificando.

---

## Antes de começar

**Você precisa da loja de pé.** Como nas lições 06 a 11: `./practicar` no seu computador e, em outra janela, o terminal
da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`.

**O erro desta lição é o E3**, o da lição 04: um pedido que já saiu do armazém pode ser cancelado e é reembolsado. Você
vai ligá-lo para vê-lo, e vai reportá-lo **sem nomeá-lo**: quem conserta a loja não sabe que existe um interruptor
chamado E3. Só vê o que a loja faz.

**O que você já sabe e vai usar:** da lição 04, os estados do pedido e a regra «pode-se cancelar enquanto o pedido não
tiver saído do armazém»; da 06, `curl` e os códigos de resposta; da 09, guardar um valor com `$(…)` e `jq -r`; da 10, o
filtro do `jq` que resume um pedido em uma linha.

**Faça o passo 4 e a revisão sem IA.** O que você treina ali é decidir quanto dano um erro causa e quão urgente ele é, e
isso é critério seu.

**Comece limpo:**

```bash
tienda reiniciar
```

---

## Passo 1 · O que faltava ao relatório

Os grandes projetos de software já escreveram o que precisam de um relatório. A Mozilla, a equipe do Firefox, diz isso
em uma linha: passos precisos para reproduzir, o resultado esperado e o resultado obtido. O Chromium, o projeto por trás
do Chrome, pede o mesmo e acrescenta capturas de tela quando ajudarem. Simon Tatham, no guia «How to Report Bugs
Effectively», resume para que tudo isso serve: para que o programador consiga reproduzir o problema sem você na frente
dele.

Neste curso, um relatório tem estas partes:

| Parte | O que leva | O que faltava ao da cena |
|---|---|---|
| **Título** | O que falha, em uma linha. A Mozilla pede menos de 60 caracteres que digam o problema, não a sua solução | «Dá para cancelar pedidos que não deveriam ser cancelados» não diz quais |
| **Severidade e prioridade** | As duas, separadas (passo 4) | Só dizia «URGENTE» |
| **Passos** | O que você fez, em ordem, de modo que outra pessoa repita igual | Não havia passos |
| **Resultado esperado** | O que deveria ter acontecido, e por quê: a regra que diz isso | Não dizia que o pedido já estava entregue nem que regra ele quebrava |
| **Resultado obtido** | O que aconteceu de verdade | «Deixou eu cancelar», sem o estado nem o dinheiro |
| **Evidência** | A saída que o prova, copiada tal qual | Nada |

**Fatos separados de suspeitas.** Tatham pede para deixar bem claro o que é um fato («eu estava no computador e isto
aconteceu») e o que é uma especulação («acho que o problema pode ser isto»). «Acho que é por causa da mudança da semana
passada» pode ir num relatório, mas marcado como suspeita e no final, nunca misturado com o que você viu.

---

## Passo 2 · Os passos, como comandos que se colam

Uns passos em prosa («entre como a Marta, compre, avance o pedido, cancele») deixam coisas sem dizer: qual produto?
com qual cartão? até qual estado? Nesta loja você pode fazer melhor: escrever os passos **como os comandos que você
rodou**, para que a outra pessoa os cole no terminal dela e veja o mesmo.

Escreva isto num arquivo, `~/practica/pasos.sh`:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":1}' > /dev/null
PEDIDO=$(curl -s -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r .id)
curl -s -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: reporte-$PEDIDO" -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}' > /dev/null
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
tienda pedido $PEDIDO avanzar
curl -s -o /dev/null -w 'cancelar: HTTP %{http_code}\n' -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion \
  -H "Authorization: Bearer $TOKEN"
curl -s http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

Linha por linha:

| Linha | O que faz |
|---|---|
| `TOKEN=$(…)` | Entra como a Marta e guarda o token dela, como na lição 09 |
| `curl … -X PUT …/carrito/…` | Coloca uma camiseta azul no carrinho. `> /dev/null` joga fora a resposta: ela não faz parte da evidência |
| `PEDIDO=$(… \| jq -r .id)` | Cria o pedido e **guarda o número dele**. O passo 3 explica por que você não escreve o número à mão |
| `curl … /pago …` | Paga com o cartão de teste; a chave leva o número do pedido para não se repetir |
| `tienda pedido $PEDIDO avanzar` ×3 | Faz o que o armazém faria: no armazém, enviado, entregue |
| `curl -s -o /dev/null -w '…'` | Tenta cancelar. `-o /dev/null` joga fora o corpo e `-w` imprime só o código de resposta |
| `curl … \| jq -c '{…}'` | Mostra o pedido em uma linha: estado, quanto ficou cobrado e as movimentações |

`-w` é novo: diz ao `curl` para imprimir algo depois de terminar, e `%{http_code}` é o código da resposta.

**Rode com a loja limpa.** Preveja primeiro: que código dá o cancelamento?

```bash
tienda reiniciar
bash pasos.sh
```

```text
📦 O pedido 1 ficou «no armazém»
📦 O pedido 1 ficou «enviado»
📦 O pedido 1 ficou «entregue»
cancelar: HTTP 409
{"estado":"entregado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

Está certo: o pedido já saiu do armazém, a loja responde **409** e a cobrança fica. Se em vez de `-o
/dev/null` você deixar o `curl` imprimir o corpo, a loja explica: «o pedido já saiu do armazém; não pode mais ser cancelado».

**Agora com o E3.**

```bash
tienda reiniciar
tienda error E3 on
bash pasos.sh
```

```text
📦 O pedido 1 ficou «no armazém»
📦 O pedido 1 ficou «enviado»
📦 O pedido 1 ficou «entregue»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

A mesma sequência, outro final: **200**, o pedido entregue fica cancelado e os $432.00 voltam. Essa diferença, copiada
tal qual, é a sua evidência.

Repare no que **não** está no `pasos.sh`: `tienda error E3 on`. Essa linha você usa para ver o erro na sua prática, mas
numa equipe de verdade o erro já está na loja; ninguém o liga. Se os seus passos o ligam, eles só testam o interruptor
de prática; não mostram como a loja falha sozinha.

---

## Passo 3 · Passos que funcionam na loja de outra pessoa

A sua loja acabou de reiniciar, e por isso o seu pedido é o 1. A do programador não: tem os pedidos dos próprios testes
dele. O que acontece se os seus passos disserem `pedido 1` em vez de `$PEDIDO`?

Faça uma cópia com o número escrito à mão. `sed` é uma ferramenta que muda texto dentro de um arquivo; você não precisa
entender esta linha, copie-a tal qual. Ela troca `$PEDIDO` por `1` em todo o arquivo, mantém a criação do pedido mas
sem guardar o número dele, e escreve o resultado em `pasos-1.sh`:

```bash
sed -e 's/\$PEDIDO/1/g' -e 's/^PEDIDO=\$(\(.*\) | jq -r .id)$/\1 > \/dev\/null/' pasos.sh > pasos-1.sh
```

Agora rode as duas versões **uma segunda vez, sem reiniciar**, com o E3 ainda ligado. Assim está a loja de quem já fez
testes antes de você. Preveja primeiro.

```bash
bash pasos.sh
```

```text
📦 O pedido 2 ficou «no armazém»
📦 O pedido 2 ficou «enviado»
📦 O pedido 2 ficou «entregue»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

```bash
bash pasos-1.sh
```

```text
❌ um pedido «cancelado» não avança mais
❌ um pedido «cancelado» não avança mais
❌ um pedido «cancelado» não avança mais
cancelar: HTTP 409
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Com `$PEDIDO`, o erro aparece de novo, agora no pedido 2. Com o 1 escrito à mão, os passos mexem num pedido velho que já
estava cancelado, o cancelamento dá **409**, e quem o receber conclui que a loja está certa. É o mesmo erro da cena,
agora com comandos: um relatório que **só** se reproduz na sua loja.

**Regra deste curso: antes de mandar um relatório, rode-o duas vezes sem reiniciar.** Se a segunda não mostrar o erro,
os seus passos dependem de algo que só a sua loja tem. Por isso o `verifica 12` deixa um pedido prévio antes de rodar
os seus passos.

Ao terminar, desligue o E3 e apague a cópia:

```bash
tienda error E3 off
rm pasos-1.sh
```

---

## Passo 4 · Severidade e prioridade

O relatório da cena dizia «URGENTE». Urgente porque causa muito dano, ou porque precisa ser consertado hoje? Não é a
mesma coisa, e numa equipe quem decide cada uma é gente diferente.

- **Severidade** é o dano. O glossário do ISTQB (International Software Testing Qualifications Board) a define como o
  grau de impacto que um defeito tem no desenvolvimento, nos testes ou na operação do sistema. O Bugzilla, a
  ferramenta de relatórios da Mozilla, a explica igual: quão grave é o problema, desde «a aplicação não pode ser
  usada» até «um detalhe cosmético».
- **Prioridade** é a ordem em que se conserta. O Bugzilla diz que ela é usada por quem tem autoridade para dirigir o
  tempo da equipe, como quem conduz o projeto. O WebKit, o motor do Safari, diz a quem reporta que normalmente ela é
  definida por alguém de QA ou de desenvolvimento.

Normalmente a severidade muda menos que a prioridade: o erro causa o mesmo dano hoje e daqui a um mês, a menos que você
descubra um efeito novo; então ela é revista. A prioridade sim muda com o calendário, com quem sofre o erro e com o que
vai ser publicado. Por isso as duas são anotadas separadamente:

| | **Prioridade alta** | **Prioridade baixa** |
|---|---|---|
| **Severidade alta** | A loja reembolsa pedidos já entregues, toda vez que alguém cancela tarde | Um relatório que se usa uma vez por ano soma errado, e o próximo uso é daqui a 11 meses |
| **Severidade baixa** | Um erro de ortografia no botão «Pagar», um dia antes de uma campanha | O logo aparece cortado num telefone que quase ninguém usa |

**A escala deste curso** usa três níveis para cada uma. É uma regra do curso, adaptada da tabela de severidade que
usamos na Hábil:

| Nível | Severidade (o dano) | Prioridade (quando se conserta) |
|---|---|---|
| **alta** | Cobra errado, perde dinheiro, impede comprar, expõe dados de alguém ou dá um número errado sem avisar | Antes da próxima coisa que for publicada |
| **média** | Algo falha, mas há outra forma de fazer, ou acontece com pouquíssima gente | No trabalho que já está planejado |
| **baixa** | Cosmético: não muda o que se cobra, o que se entrega nem o que se guarda | Quando houver espaço |

Você, como QA, **propõe** as duas e escreve por quê em uma linha. A severidade quem sustenta é você, porque você viu o
dano. A prioridade pode ser mudada por quem dirige o trabalho, porque essa pessoa sabe coisas que você não sabe: o que
é publicado amanhã ou que cliente está esperando.

> **Na Hábil há um caso em que a prioridade não se escolhe.** Nas nossas auditorias, cada incidência leva uma tarefa
> no quadro, e a prioridade dela sai direto da severidade: alta vai como urgente, média como alta e baixa como normal.
> É uma regra da casa para as auditorias, em que o prazo para corrigir depende do dano. A diferença que você aprendeu
> aqui é a da indústria, e é a que você vai usar num relatório de produto.

**Para o E3:** severidade **alta**, porque a loja perde o dinheiro de algo que já entregou. Prioridade **alta**: em
todas as suas rodadas, cada cancelamento de um pedido entregue foi reembolsado, e isso pode acontecer com qualquer
cliente que cancele depois de receber.

---

## Passo 5 · O formato da casa: matriz e relatório de QA

Numa equipe, o seu relatório não vive sozinho. Na Hábil, cada história leva uma **matriz de testes**, que diz o que foi
testado para cada critério, e um **relatório de QA**, que conta cada rodada de revisão. O seu achado aparece nos dois.

O que vem a seguir é uma **versão de prática**: traz as partes que um QA preenche na primeira rodada, com a história de
cancelar da lição 01. No fim do passo está o que falta a ela para ser o formato completo.

**A matriz de testes.** Sua tabela principal põe cada critério de aceitação (CA) junto do seu cenário. A coluna **Tipo**
diz o que se revisa: `Funcional` é o caminho do negócio (cancelar, reembolsar) e `Segurança` é um controle, como quem
pode fazer o quê.

| CA | Cenário | Tipo | Evidência esperada | Resultado |
|---|---|---|---|---|
| CA-1 Pode-se cancelar enquanto o pedido não tiver saído do armazém | QA-001 Cancelar um pedido pago | Funcional | `cancelación` 200, estado cancelado, reembolso | Aprovado |
| CA-1 | QA-002 Cancelar um pedido entregue | Funcional | `cancelación` 409, estado entregue, sem reembolso | Reprovado |
| CA-2 Se já foi cobrado, o reembolso vai para o mesmo cartão | QA-003 Reembolso de um pedido pago | Funcional | Movimentação de reembolso em `•••• 4242` | Aprovado |
| CA-3 Só quem fez o pedido pode cancelá-lo | QA-004 Luis cancela um pedido da Marta | Segurança | 404 «esse pedido não existe» | Aprovado |

Debaixo da tabela, cada cenário tem o seu detalhe: o que se valida, como, e uma última linha com o resultado final. O
de QA-002 fica assim:

```markdown
### QA-002 — Cancelar um pedido entregue

A Marta paga um pedido, o armazém o leva a entregue e a Marta o cancela. Valida-se que a loja responda 409 e que o
pedido continue entregue e cobrado. Passos e evidência em reporte.md.

Resultado final: reprovado; registrado como OBS-001
```

O modelo da casa diz «Resultado final: aprovado» ou «reprovado com INC-001». Como nesta prática não há INC (abaixo você
vê por quê), a última linha nomeia a observação.

Três regras da casa que aparecem aqui:

- um CA pode ter **mais de um cenário**: o CA-1 tem dois, um de cada lado da regra;
- a coluna **Resultado** se preenche **depois** de testar, nunca antes;
- o detalhe **liga** ao relatório; não copia os passos.

**Por que OBS e não INC?** Na Hábil, uma incidência (`INC-001`) só existe se tiver a sua tarefa no quadro da equipe, com
o seu número. Sem tarefa, o defeito se anota como **observação** (`OBS-001`) na tabela de observações da matriz. Nesta
prática não há quadro, então o seu achado é uma observação:

| OBS | Tema | Estado | Justificativa |
|---|---|---|---|
| OBS-001 | Um pedido entregue pode ser cancelado, e é reembolsado (reporte.md) | Aberto | Sem tarefa no quadro; numa equipe cria-se a tarefa e passa a ser INC-001 |

**O relatório de QA** cresce com uma seção por rodada de revisão. A sua é a primeira:

```markdown
## Ciclo 1 — Revisão QA 1

| Campo | Valor |
|---|---|
| Data | 2026-11-22 10:00 CDMX |
| Revisor | (seu nome) |
| Resultado | Não aprovado |

### Achados deste ciclo

| Achado | Descrição | INC | Estado |
|---|---|---|---|
| H-001 | Um pedido entregue pode ser cancelado, e é reembolsado | — (OBS-001) | Aberto |
```

O relatório de QA **não copia** o seu relatório: ele o liga. O detalhe vive em um só lugar.

**O que falta à versão de prática para ser o formato completo da casa:** no ciclo, o campo da etiqueta da revisão e o
link para o documento dessa revisão; na matriz, o cabeçalho de dados, o objetivo e a tabela de incidências, que tem seis
colunas e se preenche quando a tarefa existe. Você os verá quando trabalhar num expediente real.

---

## Como se confere

**O seu relatório** quem revisa é o `verifica 12`. Guarde-o em `~/practica` como `reporte.md`, com esta forma:

````markdown
# Um pedido entregue pode ser cancelado, e é reembolsado

**Severidade:** alta
**Prioridade:** alta

## Passos

```bash
(aqui vão os seus passos: o conteúdo de pasos.sh)
```

## Resultado esperado

(o que deveria ter acontecido e que regra diz isso)

## Resultado obtido

(o que aconteceu)

## Evidência

(a saída que o prova, copiada tal qual)
````

No terminal da loja, escreva:

```bash
verifica 12
```

O `verifica`:

1. confere que as quatro seções estejam lá (maiúsculas e espaços a mais não importam) e que «Passos» traga **um**
   bloco de comandos `bash`;
2. rejeita os passos que ligam um erro (`tienda error`) ou mexem no controle da loja;
3. com a loja limpa, deixa um pedido prévio da Marta e roda os seus passos: algum pedido tem que chegar a enviado ou
   entregue e **não** ficar cancelado;
4. com o E3 ligado, deixa de novo um pedido prévio e roda os seus passos **duas vezes seguidas, sem reiniciar**: nas
   duas, algum pedido tem que ficar cancelado **depois** de ter saído do armazém. É a regra do passo 3: um relatório que
   só funciona da primeira vez não serve.

Ele não lê o que você escreveu em «Resultado esperado», «Resultado obtido» nem «Evidência»: confere o que os seus passos
fazem com a loja. **Essas três seções você mesmo revisa** com a lista abaixo; um relatório com os passos bons e essas
seções vazias sai verde no `verifica` e não serve a ninguém. Ele liga e desliga o E3 sozinho e reinicia a loja, então
**apaga os seus pedidos, o seu carrinho e a sua sessão**.

Com um bom relatório, a saída fica assim:

```text
Verificando a lição 12…

✅ Seu arquivo reporte.md está em ~/practica
✅ O seu reporte.md tem as quatro seções: Passos, Resultado esperado, Resultado obtido e Evidência
✅ A seção «Passos» tem um único bloco de comandos bash
✅ Os seus passos não ligam erros nem mexem no controle da loja
✅ Com a loja limpa, os seus passos levam um pedido até enviado ou entregue e a loja não deixa cancelá-lo
✅ Com o erro E3 ligado, os seus passos cancelam um pedido que já tinha saído do armazém: o relatório reproduz o erro
✅ Rodados de novo sem reiniciar, os seus passos reproduzem o erro num pedido novo

🎉 Lição completa!
```

Na medição, levou uns 4 segundos. Ao terminar, os erros ficam como estavam antes de você rodá-lo: ele não liga nem
desliga nenhum por você. Se os seus passos não terminarem em 60 segundos, ele os interrompe e diz:

```text
❌ Com a loja limpa, os seus passos levam um pedido até enviado ou entregue e a loja não deixa cancelá-lo
   → Os seus passos não terminaram em 60 segundos. Confira se nenhum comando fica esperando você digitar algo.
```

**Antes de dar a lição por terminada, revise:**

- [ ] `reporte.md` está em `~/practica`.
- [ ] O título diz o que falha em uma linha, sem «urgente» nem sinais a mais.
- [ ] Traz severidade e prioridade, cada uma com o seu nível.
- [ ] Os passos usam `$PEDIDO`, não um número escrito à mão.
- [ ] Os passos não trazem `tienda error`.
- [ ] Você rodou os seus passos duas vezes sem reiniciar, com o E3 ligado, e as duas vezes viu o cancelamento com 200.
- [ ] As quatro seções têm texto seu: nenhuma está vazia nem com o texto de exemplo entre parênteses.
- [ ] «Resultado esperado» diz o 409 e cita a regra («pode-se cancelar enquanto o pedido não tiver saído do armazém»).
- [ ] «Resultado obtido» diz o 200, que o pedido entregue ficou cancelado e que foram reembolsados $432.00.
- [ ] A evidência é a saída de uma rodada com o E3, copiada tal qual, e diz o mesmo que «Resultado obtido».
- [ ] Se você escreveu uma suspeita, ela está marcada como suspeita e no final.
- [ ] Você deixou o E3 desligado (`tienda error estado`).

---

## Seus exercícios

1. **Outro relatório.** Ligue o E1 (`tienda error E1 on`) e escreva em `~/practica/reporte-envio.md` o relatório do frete
   que se cobra num carrinho de exatamente $999.00, com as mesmas partes. Para os passos, comece com o `TOKEN=$(…)` do
   `pasos.sh` e acrescente um carrinho de **três** camisetas azuis que imprima subtotal, frete e total com `jq`. Que
   regra da lição 02 ele quebra? Este relatório não é revisado pelo `verifica`: compare-o com o de baixo. Ao terminar,
   desligue o E1.
2. **Reproduz na loja de outra pessoa?** Com o E3 ligado, rode os seus passos três vezes seguidas sem reiniciar. Anote o
   número do pedido e o código do cancelamento de cada rodada. As três dão 200?
3. **Sua matriz e seu ciclo.** Com a loja limpa e depois com o E3, rode à mão os quatro cenários da matriz do passo 5
   (QA-003 sai do mesmo cancelamento de QA-001; QA-004 precisa do token do Luis, como na lição 06). Em
   `~/practica/matriz.md`, preencha você mesmo a coluna Resultado com o que viu **com o E3 ligado**, escreva o detalhe
   de cada cenário com o seu «Resultado final», a tabela de observações e a seção «Ciclo 1» do seu relatório de QA.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo 4). Para cada caso, proponha
severidade e prioridade, cada uma com uma linha dizendo por quê:

1. A loja reembolsa os pedidos já entregues quando alguém os cancela (E3).
2. Na página em búlgaro, o botão «Pagar» tem um erro de ortografia, e amanhã começa uma campanha na Bulgária.
3. O relatório anual de vendas por categoria soma errado se um produto não tiver categoria. Hoje todos têm, e o
   relatório é tirado de novo daqui a 11 meses.
4. No catálogo, o filtro «Acessórios» não mostra a caneca; ela aparece se você a procurar pelo nome.
5. Num telefone que representa menos de 1 em cada 100 visitas, o logo aparece cortado.

---

## Para fechar

Até a lição 11 você aprendeu a encontrar erros. Esta lição ensinou você a entregá-los, porque um erro que não se
entende não se conserta.

O que fica com você daqui:

- **Um relatório serve se outra pessoa reproduz o erro sem você.** Por isso ele leva passos, resultado esperado,
  resultado obtido e evidência.
- **Nesta loja, passos que se colam poupam dúvidas a quem conserta**, e não devem depender da sua loja: guarde o número
  do pedido, não o escreva à mão, e rode-os duas vezes antes de mandá-los.
- **Descreva o que o sistema faz**, não como você o fez falhar, e separe o que viu do que suspeita.
- **Severidade é o dano; prioridade é quando se conserta.** Você propõe as duas; a prioridade pode ser movida por quem
  dirige o trabalho.
- **Numa equipe, o seu achado vive em três lugares**: o relatório com o detalhe, a matriz com o cenário reprovado e o
  relatório de QA com a rodada em que apareceu. Os três se ligam; nenhum copia o outro.

Na lição 13 você vira a pergunta do avesso: os seus testes encontram erros, mas como você sabe que encontrariam um que
você ainda não conhece?

---

## Compare as respostas

**Passo 2, a previsão.** Com a loja limpa, **409**: o pedido já saiu do armazém. Com o E3, **200**.

**Passo 3, a previsão.** O `pasos.sh` mostra o erro de novo no pedido 2. O `pasos-1.sh` não: mexe no pedido 1, que já
estava cancelado, e o cancelamento dá 409.

**O seu relatório**, um que cumpre:

````markdown
# Um pedido entregue pode ser cancelado, e é reembolsado

**Severidade:** alta — a loja devolve o dinheiro de algo que já entregou.
**Prioridade:** alta — em cada rodada, o pedido entregue foi cancelado e reembolsado.

## Passos

```bash
(o conteúdo de pasos.sh do passo 2)
```

## Resultado esperado

O cancelamento responde 409, «o pedido já saiu do armazém; não pode mais ser cancelado». O pedido continua entregue e
cobrado: «pode-se cancelar enquanto o pedido não tiver saído do armazém» (história de cancelar um pedido).

## Resultado obtido

O cancelamento responde 200. O pedido entregue fica cancelado e são reembolsados os $432.00.

## Evidência

```text
📦 O pedido 1 ficou «no armazém»
📦 O pedido 1 ficou «enviado»
📦 O pedido 1 ficou «entregue»
cancelar: HTTP 200
{"estado":"cancelado","cobrado":"$0.00","movimientos":["cargo $432.00","reembolso $432.00"]}
```

Reproduz-se também num pedido enviado, antes de ser entregue.
````

A última linha é um fato que você pode comprovar: avance o pedido duas vezes em vez de três e cancele. Se você não
comprovou, não a escreva.

**Exercício 1.** Os passos, depois do `TOKEN=$(…)`:

```bash
curl -s -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cantidad":3}' \
  | jq -c '{subtotal: .subtotal.texto, envio: .envio.texto, total: .total.texto}'
```

Com a loja limpa sai `{"subtotal":"$999.00","envio":"$0.00","total":"$999.00"}`; com o E1,
`{"subtotal":"$999.00","envio":"$99.00","total":"$1,098.00"}`. Quebra a regra de frete grátis **a partir de** $999.00:
na borda, o frete deve ser $0.00. Severidade **alta** (cobra a mais) e prioridade **média**: no que você mediu, só
acontece com um carrinho de exatamente $999.00, e se conserta no trabalho planejado. Se você propôs prioridade alta
porque cobrar a mais é delicado, também vale: escreva essa razão.

**Exercício 2.** Três vezes 200. Se você vem direto do passo 3 sem reiniciar, são os pedidos 4, 5 e 6 (o `pasos-1.sh`
também criou um, o 3). O número muda; o erro, não.

**Exercício 3.** Com o E3 ligado, QA-001, QA-003 e QA-004 saem como diz a matriz: Aprovado. QA-002 sai Reprovado.
Revise a sua `matriz.md` com esta lista:

- [ ] Cada CA tem pelo menos um cenário, e cada cenário tem o seu código QA-00N.
- [ ] Cada linha tem um Tipo (`Funcional` ou `Segurança`) e uma evidência esperada que se pode ver: um código, um
      estado ou uma movimentação.
- [ ] A coluna Resultado diz Aprovado, Reprovado, Aprovado, Aprovado.
- [ ] Cada cenário tem o seu detalhe debaixo da tabela. QA-002 termina com «Resultado final: reprovado; registrado como
      OBS-001»; os outros, com «Resultado final: aprovado».
- [ ] A tabela de observações tem uma linha, OBS-001, que nomeia o seu `reporte.md` e diz por que não é INC.
- [ ] Você não escreveu nenhum INC: não há tarefa num quadro.
- [ ] A seção «Ciclo 1» traz data, revisor e resultado «Não aprovado», e a tabela de achados liga H-001 com OBS-001.
- [ ] Nem a matriz nem o ciclo copiam os passos: ligam ao `reporte.md`.

**Revisão.** Estas são as respostas-guia; conte quantas coincidem com as suas nas duas colunas. Há uma única exceção: no
4, a **prioridade** pode ser baixa ou alta se a sua razão trouxer um dado do negócio que mude a urgência (por exemplo,
que nessa semana as canecas estão em promoção).

1. Severidade **alta** (perde dinheiro); prioridade **alta** (acontece agora, a cada cancelamento tardio).
2. Severidade **baixa** (não muda o que se cobra); prioridade **alta** (a campanha é amanhã).
3. Severidade **alta** (dá um número errado sem avisar); prioridade **baixa** (hoje não acontece e o relatório é usado
   daqui a 11 meses).
4. Severidade **média** (falha, mas há outra forma de encontrar a caneca); prioridade **média** (vai no trabalho
   planejado).
5. Severidade **baixa** (cosmético); prioridade **baixa** (quase ninguém vê).

Se no 2 ou no 3 você colocou a mesma severidade que prioridade, volte à tabela do passo 4: são os dois casos em que as
duas se separam.

---

## Fontes da lição

1. Simon Tatham, «How to Report Bugs Effectively» (consultado em 22 de novembro de 2026). «If you have to report a
   bug to a programmer who can't be present in person, the aim of the exercise is to enable them to reproduce the
   problem.»; «In bug reports, try to make very clear what are actual facts ("I was at the computer and this
   happened") and what are speculations ("I think the problem might be this").»
   https://www.chiark.greenend.org.uk/~sgtatham/bugs.html
2. Mozilla, «Bug Writing Guidelines» (consultado em 22 de novembro de 2026). «Provide precise steps to reproduce,
   expected results and actual results»; «How would you describe the bug in less than 60 characters? It should
   quickly and uniquely identify a bug report as well as explain the problem, not your suggested solution.»
   https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html
3. The Chromium Projects, «Bug Life Cycle and Reporting Guidelines» (consultado em 22 de novembro de 2026).
   «Mention detailed steps to replicate the issue. Include the expected behavior.»; «Include screenshots, if they
   might help.» https://www.chromium.org/for-testers/bug-reporting-guidelines/
4. ISTQB, «Glossary»: *severity*, *priority* e *defect report* (consultado em 22 de novembro de 2026). «The degree
   of impact that a defect has on the development, testing or operation of a component or system.»
   https://glossary.istqb.org/en_US/term/severity
5. Bugzilla, «Understanding a Bug» (consultado em 22 de novembro de 2026). «The Priority field is used to prioritize
   bugs, either by the assignee, or someone else with authority to direct their time such as a project manager.»;
   «The Severity field indicates how severe the problem is—from blocker (“application unusable”) to trivial (“minor
   cosmetic issue”).» https://bugzilla.readthedocs.io/en/latest/using/understanding.html
6. WebKit, «Bug Report Guidelines» (consultado em 22 de novembro de 2026). «Good bug reports help developers and
   quality assurance (QA) people decide an appropriate priority and severity for a bug»; «Normally a QA person or
   developer will set this». https://webkit.org/bug-report-guidelines/
7. GitHub Docs, «Syntax for issue forms» (consultado em 22 de novembro de 2026). O formulário de exemplo para reportar
   um erro pergunta «What happened?» e «Also tell us, what did you expect to happen?», e pede para colar
   «any relevant log output».
   https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms
8. curl, «curl.1 the man page» (consultado em 22 de novembro de 2026). «-w, --write-out <format> Make curl display
   information on stdout after a completed transfer.»; «http_code The numerical response code that was found in the
   last retrieved HTTP(S) or FTP(s) transfer.» https://curl.se/docs/manpage.html

**Formato da casa** (passo 5 e a regra de auditorias do passo 4): padrões internos da Hábil de matriz de testes,
relatório de QA e documentação de incidências. Não são públicos; a lição mostra só as partes que usa.
