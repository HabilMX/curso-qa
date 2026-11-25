# Lição 10 — Quando o outro sistema falha

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Dependência:** outro sistema de que o seu sistema precisa para terminar o seu trabalho. A loja não cobra sozinha:
  ela pede a cobrança ao **gateway de pagamento**, que vive em outro lugar.
- **Tempo de espera:** quanto um sistema aguenta esperar que outro lhe responda antes de desistir. A loja de prática
  espera **5 segundos** pelo gateway.
- **Conciliar:** comparar o que diz o pedido com o que aconteceu com o dinheiro, e corrigir a diferença.

**O que fica com você:** uma coleção que paga um pedido e depois confere que **o estado e o dinheiro batem**. Ela sai
verde com o gateway aprovando, recusando, sem responder ou demorando, e vermelha quando uma cobrança chega tarde e
ninguém a concilia.

**Ideia nova desta lição (a única):** uma dependência lenta é mais perigosa do que uma que caiu.

**Em que ordem vai:** você monta uma coleção que paga (passo 1); confere como ficou o pedido quando o gateway diz que
não (passo 2) e quando ele não responde (passo 3); faz o gateway demorar e espera o tempo que ele leva (passo 4); e
encontra o pedido pela metade (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são de verdade.*

Numa sexta-feira à noite, o gateway de pagamento passa por um mau momento: umas vezes responde em um segundo e outras
leva sete.

Na segunda-feira, a Marta escreve brava. Na sexta quis comprar uma camiseta, a página lhe disse «não sabemos se o valor
foi cobrado», e ela deixou assim. Na segunda viu no banco uma cobrança de $432.00. Na loja, o pedido dela continua
«creado»: ninguém o embalou, porque para a loja ele nunca foi pago.

Os testes da equipe estavam verdes. Eles testavam o gateway aprovando e o gateway recusando, e nos dois o pedido ficava
certo. Nunca o testaram **lento**.

---

## Antes de começar

**Você precisa da loja no ar.** Como nas lições 07 a 09: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra
janela, o terminal da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`.

> **Esta lição usa a loja da lição 10.** Ela traz o erro E7. Se `tienda error E7 on` te disser que esse erro não existe,
> atualize a sua loja antes de seguir: com uma versão anterior, as suas saídas não vão coincidir.

**O que você já sabe e vai usar:** da lição 07, `newman run`, `jq empty` e o ambiente `local` (com `base`, `cliente` e
`contrasena`); da 08, a chave de idempotência, o 504 e `tienda pasarela`; da 09, conferir **o efeito** e não só o
código.

**Faça o passo 3 sem IA.** O que você treina ali é prever o que acontece com um pedido quando o outro sistema não
responde.

**Comece limpo antes de cada rodada, e nesta ordem:**

```bash
tienda reiniciar
tienda pasarela aprueba
```

```text
✅ a loja voltou ao estado de recém-aberta
💳 O gateway aprova
```

O `tienda reiniciar` devolve o gateway ao modo «aprova». Por isso o modo do gateway se coloca sempre **depois** de
reiniciar; ao contrário, o reinício o apaga e a rodada sai com o gateway aprovando sem que você perceba.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Uma coleção que paga

O gateway de prática tem quatro modos, e a loja tem um comando para cada um:

| Comando | O que o gateway faz |
|---|---|
| `tienda pasarela aprueba` | Cobra e responde na hora |
| `tienda pasarela rechaza` | Responde na hora que não cobrou |
| `tienda pasarela no-contesta` | Não responde durante todo o tempo da prática, e não cobra |
| `tienda pasarela tarda 7` | Cobra, mas responde aos 7 segundos |

Para testar os quatro você precisa de uma coleção que pague. É um arquivo novo; as das lições 07 a 09 não são tocadas:

```bash
nano pasarela.postman_collection.json
```

```json
{
 "info": {
  "name": "Gateway",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "A cliente faz login",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "Uma camiseta no carrinho",
   "request": {
    "method": "PUT",
    "url": "{{base}}/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"cantidad\":1}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Ela faz o pedido",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('pedido', pm.response.json().id);",
    "pm.collectionVariables.set('llave', pm.variables.replaceIn('{{$guid}}'));"
   ]}}]
  },
  {
   "name": "Ela paga",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/pedidos/{{pedido}}/pago",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"},
     {"key": "Idempotency-Key", "value": "{{llave}}"}
    ],
    "body": {"mode": "raw", "raw": "{\"tarjeta\":\"4242 4242 4242 4242\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('aprovado, recusado ou sem resposta', () => pm.expect(pm.response.code).to.be.oneOf([200, 402, 504]));"
   ]}}]
  }
 ]
}
```

As três primeiras requisições são as da lição 08: a cliente faz login, põe uma camiseta no carrinho e faz o pedido, e
ficam guardados o número do pedido e uma chave de idempotência nova. A novidade está em «Ela paga»: ela aceita **três**
respostas, porque as três são honestas.

| Código | O que quer dizer aqui |
|---|---|
| 200 | O gateway cobrou |
| 402 | O gateway disse que não: não cobrou |
| 504 | O gateway não respondeu em 5 segundos: **a loja não sabe** se cobrou |

O 402 não tem um significado fixo em HTTP: a norma o deixa «reservado para uso futuro». Algumas APIs de pagamento o usam
para erros da cobrança, e **esta loja** o usa quando o gateway diz que não.

Confira que o JSON está bem escrito e rode-a:

```bash
jq empty pasarela.postman_collection.json
tienda reiniciar
tienda pasarela aprueba
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ A cliente faz login
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 16ms]
  ✓  código 201

→ Uma camiseta no carrinho
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 547B, 3ms]
  ✓  código 200

→ Ela faz o pedido
  POST http://localhost:8080/api/pedidos [201 Created, 681B, 2ms]
  ✓  código 201

→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 970B, 3ms]
  ✓  aprovado, recusado ou sem resposta
```

Quatro de quatro. Os tamanhos e os tempos das saídas desta lição são os da medição; os seus podem mudar. Os códigos, os
vistos e os vermelhos, não.

Ela já confere que o pagamento recebeu uma das três respostas previstas. Como «Ela paga» sai verde com qualquer um dos
quatro modos, o que falta é conferir o que de fato importa: **como o pedido terminou**.

---

## Passo 2 · Quando o gateway diz que não

Acrescente uma quinta requisição no final, depois de «Ela paga» (com uma vírgula entre as duas):

```json
  {
   "name": "Como ficou o pedido",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "const pedido = pm.response.json();",
    "pm.test('não cobrado a mais', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
    "pm.test('pago se e somente se cobrado', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
   ]}}]
  }
```

São dois testes, e eles não conferem um caso: conferem uma **regra que vale nos quatro modos do gateway**, logo depois de
tentar pagar. (Mais adiante, quando o pedido é enviado ou cancelado, o estado dele já não é «pagado» nem «creado», e a
regra seria outra.)

| Teste | O que compara |
|---|---|
| `não cobrado a mais` | O que foi cobrado (`cobrado`) não passa do total do pedido |
| `pago se e somente se cobrado` | Duas perguntas de sim ou não: «o pedido diz pago?» e «o total foi cobrado?». As duas respostas têm de ser **iguais**: sim e sim, ou não e não |

O `cobrado` você conhece da lição 08: é o que o gateway de fato cobrou do cartão, já descontados os reembolsos.
Comparamos os **centavos**, que são números, e não o texto `$432.00`, porque «no máximo» só se pode perguntar de um
número.

Rode-a com o gateway aprovando e depois recusando:

```bash
tienda reiniciar
tienda pasarela rechaza
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [402 Payment Required, 251B, 3ms]
  ✓  aprovado, recusado ou sem resposta

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 676B, 2ms]
  ✓  não cobrado a mais
  ✓  pago se e somente se cobrado
```

Seis de seis com o gateway aprovando, e seis de seis recusando. Com o gateway aprovando, o pedido fica **pago e
cobrado**: sim e sim. Recusando, fica **criado e sem cobrança**: não e não. As duas respostas são diferentes e as duas
estão certas, e um único teste aceita as duas.

---

## Passo 3 · Quando o gateway não responde

**Faça este passo sem IA.** Antes de rodar, preveja: com o gateway sem responder, que código recebe «Ela paga», e como
fica o pedido? Escreva.

```bash
tienda reiniciar
tienda pasarela no-contesta
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado, recusado ou sem resposta

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 676B, 2ms]
  ✓  não cobrado a mais
  ✓  pago se e somente se cobrado
```

**504 aos 5 segundos.** É o tempo de espera da loja: ela aguentou 5 segundos e desistiu. Um 504 quer dizer justamente
isso: o servidor, que estava de intermediário, não recebeu a tempo a resposta do outro sistema de que precisava. No
corpo, a loja diz com as palavras dela: «o gateway não respondeu a tempo; não sabemos se o valor foi cobrado. Tente de
novo com a mesma chave de idempotência».

E o pedido ficou **criado e sem cobrança**: não e não, verde. Neste **modo de prática** o gateway que não responde também
não cobra, então o pedido não mente. Mas a Marta ainda não tem como saber: ela só vê um 504 que diz «não sabemos se o
valor foi cobrado». Por isso a loja pede que ela tente de novo **com a mesma chave**, e não com uma nova.

Repare no «não sabemos». A loja não consegue distinguir, no segundo 5, entre um gateway que nunca vai responder e um que
vai responder no segundo 7. Por isso diz «não sabemos» e não «não foi cobrado». Um tempo de espera esgotado não te diz
que nada aconteceu.

> Se você tentar de novo com a mesma chave enquanto o gateway continua sem responder, recebe 504 de novo aos 5 segundos:
> a loja continua esperando a **mesma** cobrança, como na lição 08. Para seguir com a lição, `tienda reiniciar`.

---

## Passo 4 · Quando o gateway demora

Agora o gateway **cobra** de verdade, mas leva 7 segundos para responder. A loja só o espera 5.

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado, recusado ou sem resposta

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 676B, 2ms]
  ✓  não cobrado a mais
  ✓  pago se e somente se cobrado
```

Verde, e com o **mesmo** tamanho de resposta de quando o gateway não respondia: o pedido estava criado e sem cobrança.
Mas desta vez o gateway ia cobrar. Quando?

Faça a conta com a linha do tempo desta rodada:

| Segundo | O que acontece |
|---|---|
| 0 | «Ela paga» sai para a loja, e a loja pede a cobrança ao gateway |
| 5 | A loja se cansa de esperar e responde 504. O newman passa de imediato a «Como ficou o pedido» |
| 5 | O pedido ainda está criado e sem cobrança: o teste sai verde |
| 7 | O gateway termina: **cobra** $432.00 |

O seu teste conferiu o pedido **dois segundos antes** de a cobrança chegar. Conferiu a tempo para a loja, mas não para o
gateway.

Para ver o que acontece no segundo 7, o teste tem de **esperar o tempo que o gateway leva**. O gateway leva 7 segundos e
a loja já esperou 5: faltam 2. Esperamos 5: os 2 que faltam e 3 de margem.

Em «Como ficou o pedido», **substitua por inteiro** o `"event": [ … ]` que você colou no passo 2 por este bloco. Ele traz
os mesmos testes, e antes deles um evento novo que roda **antes** de mandar a requisição (`prerequest`). Não deixe dois
`"event"` na mesma requisição. As vírgulas não mudam: há uma entre «Ela paga» e «Como ficou o pedido», e nenhuma depois
de «Como ficou o pedido», porque é a última:

```json
   "event": [
    {"listen": "prerequest", "script": {"exec": [
     "setTimeout(() => {}, 5000);"
    ]}},
    {"listen": "test", "script": {"exec": [
     "const pedido = pm.response.json();",
     "pm.test('não cobrado a mais', () => pm.expect(pedido.cobrado.centavos).to.be.at.most(pedido.total.centavos));",
     "pm.test('pago se e somente se cobrado', () => pm.expect(pedido.estado === 'pagado').to.eql(pedido.cobrado.centavos === pedido.total.centavos));"
    ]}}
   ]
```

| Linha | O que faz |
|---|---|
| `"listen": "prerequest"` | Este script roda antes de mandar a requisição; o de `"test"` roda depois de receber a resposta |
| `setTimeout(() => {}, 5000)` | Programa «não fazer nada» para dali a 5000 milissegundos. O newman não manda a requisição até isso terminar, então espera 5 segundos |

Esses 5 segundos **não são um número mágico**, e não são os 7 do gateway: a espera começa quando a loja já esperou 5. Eles
cobrem os 2 segundos que faltam ao gateway, mais 3 de margem. Se o gateway demorasse 12, você refaria a conta a partir do
segundo 5. Uma espera sem porquê dá um teste lento que, além disso, você não sabe se é suficiente.

Rode-a outra vez, com o gateway demorando:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado, recusado ou sem resposta

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 881B, 5ms]
  ✓  não cobrado a mais
  ✓  pago se e somente se cobrado
```

Verde de novo, mas agora a resposta é maior: 881B. O pedido traz um movimento, a cobrança de $432.00, e diz **pagado**.
Quando a cobrança chegou no segundo 7, a loja a **conciliou**: viu que a cobrança era de um pedido criado e o passou a
pago. Sim e sim.

Muitos sistemas de verdade funcionam de modo parecido: o gateway avisa depois, quando a cobrança termina (por exemplo,
com um *webhook*, um aviso que o gateway manda para a loja), e a loja decide nesse momento o que fazer com o pedido. Em
produção, uma resposta que não chegou a tempo é tratada como incerta até ser conciliada, quer chegue tarde, quer não
responda.

Antes de seguir, confira que a espera não quebrou o que você já tinha: com `aprueba`, `rechaza` e `no-contesta`, a
coleção sai seis de seis as três vezes. Agora cada rodada leva uns 5 segundos a mais, e 10 com `no-contesta`.

---

## Passo 5 · O pedido pela metade

Ligue o E7 e rode com o gateway demorando:

```bash
tienda reiniciar
tienda error E7 on
tienda pasarela tarda 7
newman run pasarela.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado, recusado ou sem resposta

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 817B, 6ms]
  ✓  não cobrado a mais
  1. pago se e somente se cobrado
```

```text
  #  failure         detail

 1.  AssertionError  pago se e somente se cobrado
                     expected false to deeply equal true
```

Um vermelho. O `expected false to deeply equal true` lê-se ao contrário de como o teste está escrito: «o pedido diz
pago?» deu **não** (`false`), e «o total foi cobrado?» deu **sim** (`true`). Não batem.

Olhe o pedido com `curl`, como na lição 06 (com a loja ainda assim, sem reiniciar):

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}' | jq -r .token)
curl -s http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN" \
  | jq -c '{estado, cobrado: .cobrado.texto, movimientos: [.movimientos[] | .tipo + " " + .monto.texto]}'
```

```text
{"estado":"creado","cobrado":"$432.00","movimientos":["cargo $432.00"]}
```

Essa é a cena da Marta: **cobrado e criado**. A cobrança chegou no segundo 7 e a loja **a anotou** (está aí, em
`movimientos`), mas com o E7 ela não a concilia: deixa o pedido como estava, sem avisar ninguém. E assim fica. Ninguém
vai embalá-lo, porque para o armazém ele não foi pago.

Compare os três gateways que não responderam a tempo:

| Gateway | O que a cliente viu | O pedido |
|---|---|---|
| Não responde | 504, «não sabemos se o valor foi cobrado» | Criado e sem cobrança: não comprou, e não perdeu dinheiro |
| Demora 7, loja limpa | 504, «não sabemos se o valor foi cobrado» | Pago e cobrado: comprou |
| Demora 7, com E7 | 504, «não sabemos se o valor foi cobrado» | **Criado e cobrado**: pagou e não comprou |

A cliente viu **o mesmo** nos três. O que muda é o que aconteceu depois de a loja deixar de esperar. Nesta prática, o
gateway que caiu é o mais fácil: não cobra, e o pedido não mente. O lento cobra quando já ninguém o está esperando, e
alguém tem de se encarregar dessa cobrança.

Por isso uma dependência lenta é mais perigosa do que uma que caiu. E não só pelo dinheiro: quem fica esperando um
sistema que não responde também fica ocupado, e se são muitos esperando, o que cai é quem esperava.

Desligue o E7 antes de seguir:

```bash
tienda error E7 off
tienda reiniciar
```

---

## Como se confere

**A sua coleção** é revisada pelo `verifica 10`. Salve-a em `~/practica` como `pasarela.postman_collection.json`, junto
com o seu ambiente `local.postman_environment.json`, e, no terminal da loja, escreva:

```bash
verifica 10
```

O `verifica`:

1. roda a sua coleção com a loja limpa quatro vezes: com o gateway aprovando, recusando, sem responder e demorando 7
   segundos: as quatro vezes tem de sair **verde**;
2. roda-a com E7 ligado e o gateway demorando 7 segundos: **pelo menos um teste tem de sair vermelho**; se sair verde, a
   sua coleção não compara o estado do pedido com o que foi cobrado depois de esperar o gateway;
3. confere que a sua coleção não tenha escritos à mão o endereço, `Marta` nem a senha dela.

Se faltar algo, ele diz o que arrumar. Ele muda o gateway e liga e desliga o E7 sozinho. No final, deixa ligados os
erros que você tinha ligado e o gateway aprovando, mas reinicia a loja: apaga os seus pedidos, o seu carrinho e a sua
sessão. Leva menos de um minuto. Antes de rodá-lo, a lista abaixo diz se a forma está certa.

**Antes de dar a lição por terminada, confira:**

- [ ] A sua coleção tem cinco requisições, na ordem dos passos 1 e 2.
- [ ] «Ela paga» aceita 200, 402 e 504.
- [ ] «Como ficou o pedido» espera 5 segundos antes de ser enviada e tem os dois testes do passo 2.
- [ ] Com a loja limpa sai 6 de 6 com `aprueba`, `rechaza`, `no-contesta` e `tarda 7`.
- [ ] Com E7 ligado e `tarda 7` falha «pago se e somente se cobrado».
- [ ] Na sua coleção não aparecem `localhost`, `Marta` nem a senha (procure-os com
      `grep -n -e localhost -e Marta -e practica pasarela.postman_collection.json`; não pode imprimir nada).
- [ ] Você deixou o E7 desligado e o gateway aprovando (`tienda error estado` e `tienda pasarela aprueba`).

---

## Seus exercícios

1. **Dois pagamentos, duas chaves.** Faça uma cópia da sua coleção
   (`cp pasarela.postman_collection.json dos-llaves.postman_collection.json`) e, na cópia, duplique a requisição «Ela
   paga» logo abaixo dela. À cópia dê o nome «Ela paga de novo, com outra chave» e, no cabeçalho `Idempotency-Key` dela,
   troque `{{llave}}` por `{{$guid}}`: assim cada tentativa leva uma chave nova, como o exercício 2 da lição 08. Rode-a
   com o gateway demorando 7 segundos, primeiro com a loja limpa e depois com E7. Preveja: verde ou vermelha em cada caso?
   E na loja limpa, quantos movimentos tem o pedido? Confira com o `curl` do passo 5. Ao terminar,
   `rm dos-llaves.postman_collection.json`.
2. **Lento, mas a tempo.** Com a loja limpa e `tienda pasarela tarda 3`, que código recebe «Ela paga», e com quantos
   segundos? Como fica o pedido? Preveja e rode.
3. **Quem fica sabendo** (sem IA). Para cada linha, escreva o que a Marta vê na página e quem fica sabendo que há um
   problema: a Marta, a loja ou ninguém.

   | Caso | O que a Marta vê | Quem fica sabendo |
   |---|---|---|
   | O gateway recusa | | |
   | O gateway não responde | | |
   | O gateway demora 7, loja limpa | | |
   | O gateway demora 7, com E7 | | |

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. Na cena, por que os testes da equipe não viram o problema da Marta? (cena)
2. Por que «Ela paga» aceita o 504 como resposta boa? (passos 1 e 3)
3. O que quer dizer que o pedido saia «não e não» no teste «pago se e somente se cobrado»? (passo 2)
4. Por que a coleção esperava 5 segundos e não 1, nem 30? (passo 4)
5. Por que um gateway lento é mais perigoso do que um que caiu? (passo 5)

---

## Para fechar

Na lição 08 você já usou o gateway lento, para que uma nova tentativa não cobrasse em dobro. Esta lição olha a outra
metade do problema: o que acontece com o pedido **depois** do 504, mesmo que ninguém tente de novo, quando a loja depende
de **outro sistema** e esse sistema diz que não, não responde ou responde tarde.

O que você leva daqui:

- **Um 504 não te diz o que aconteceu.** Diz que alguém deixou de esperar. O que importa é o que aconteceu depois.
- **Um teste confere que o estado e o dinheiro batem, não só o código.** Uma única regra, «pago se e somente se
  cobrado», vale com o gateway aprovando, recusando, sem responder ou demorando.
- **A espera de um teste tem um porquê:** o tempo que o outro sistema leva, mais margem. Uma espera menor deixa o erro
  passar: com E7, a sua coleção sem espera sai verde.
- **Uma dependência lenta é mais perigosa do que uma que caiu.** Nesta prática, a que caiu não cobra; a lenta cobra
  quando já ninguém a espera, e alguém tem de conciliar.

Na lição 11 você deixa o terminal e testa a página como a Marta a usa, em um navegador.

---

## Compare as respostas

**Passo 3, a previsão.** **504 aos 5 segundos**, e o pedido **criado e sem cobrança**: verde. Se você previu que a loja ia
esperar para sempre, é um bom raciocínio: esperaria, se não tivesse tempo de espera. Esse é o trabalho dela: desistir a
tempo e dizer «não sabemos».

**Exercício 1.** Com a loja limpa, **verde**. Os dois pagamentos recebem 504, e as duas cobranças chegam: o pedido tem
**três movimentos**, duas cobranças e um reembolso, e diz pago com $432.00. Medido:

```text
{"estado":"pagado","cobrado":"$432.00","movimientos":["cargo $432.00","cargo $432.00","reembolso $432.00"]}
```

A primeira cobrança pagou o pedido; a segunda chegou a um pedido já pago, e a loja a devolveu sozinha. Para o teste tudo
bate, porque o `cobrado` já desconta o reembolso. Para a Marta não: no banco ela vê duas cobranças e uma devolução. Por
isso a chave se repete a cada tentativa, como na lição 08: com a mesma chave há uma só cobrança.

Com E7, **vermelho**: falha «não cobrado a mais», `expected 86400 to be at most 43200`. O pedido fica criado com $864.00
e duas cobranças, e ninguém devolve nada. «Pago se e somente se cobrado» sai verde, porque não se cobrou **o total**:
cobrou-se o dobro. Por isso são dois testes e não um.

**Exercício 2.** **200 aos 3 segundos**, e o pedido pago com $432.00: seis de seis. O gateway levou menos do que o tempo
de espera da loja, então a loja recebeu a resposta. Lento não é o mesmo que fora do tempo: o problema começa quando o
gateway leva mais do que a loja espera.

**Exercício 3.**

| Caso | O que a Marta vê | Quem fica sabendo |
|---|---|---|
| O gateway recusa | 402, «o gateway recusou o pagamento» | A Marta, na hora: sabe que não pagou |
| O gateway não responde | 504, «não sabemos se o valor foi cobrado» | A Marta sabe que não tem confirmação. Neste modo de prática nenhuma cobrança chega, então não há nada a conciliar |
| O gateway demora 7, loja limpa | 504, «não sabemos se o valor foi cobrado» | A loja: concilia a cobrança quando chega, e o pedido segue o seu caminho |
| O gateway demora 7, com E7 | 504, «não sabemos se o valor foi cobrado» | **Ninguém, por si só.** A loja anotou a cobrança, mas não passou o pedido a pago nem avisou ninguém. A Marta vê dias depois no banco; a equipe o encontraria ao conciliar movimentos contra pedidos |

A última linha é a cena. O gateway terminou a cobrança e a loja a anotou, mas o erro deixou de relacioná-la com o estado
do pedido: o dado estava ali, e ninguém o olhou.

**Revisão.**

1. Porque testavam o gateway aprovando e recusando, que respondem na hora. Nunca o testaram **lento**, que é quando a
   cobrança chega depois de a loja deixar de esperar.
2. Porque um 504 é uma resposta honesta: a loja diz que não sabe. O teste de «Ela paga» não decide se o pagamento deu
   certo; isso quem decide é «Como ficou o pedido».
3. Que o pedido não diz pago **e** não foi cobrado: a cliente não comprou e não perdeu dinheiro. É o que acontece quando
   o gateway recusa ou não responde, e está certo.
4. Porque o gateway leva 7 segundos e a loja já esperou 5: faltam 2, e os outros 3 são margem. Com 1 o teste chegaria
   antes da cobrança; com 30 seria lento sem ganhar nada.
5. Porque, nesta prática, o que caiu não cobra: o pedido fica sem pagar e sem cobrança, e não mente. O lento cobra quando
   já ninguém o espera, e se ninguém concilia, o pedido fica cobrado e sem pagar.

---

## Fontes da lição

1. IETF, RFC 9110, *HTTP Semantics* (2022), §15.6.5 e §15.5.3 (consultado em 22 de novembro de 2026). «The 504
   (Gateway Timeout) status code indicates that the server, while acting as a gateway or proxy, did not receive a
   timely response from an upstream server it needed to access in order to complete the request.»; «The 402 (Payment
   Required) status code is reserved for future use.»
   https://www.rfc-editor.org/rfc/rfc9110
2. Amazon, *Builders' Library*, «Timeouts, retries, and backoff with jitter» (consultado em 22 de novembro de 2026).
   «A timeout or failure doesn't necessarily mean that side effects haven't happened.»; «In general, our view is that
   APIs with side effects aren't safe to retry unless they provide idempotency.»
   https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
3. Martin Fowler, «CircuitBreaker» (consultado em 22 de novembro de 2026). «remote calls can fail, or hang without a
   response until some timeout limit is reached»; «if you have many callers on a unresponsive supplier, then you can
   run out of critical resources leading to cascading failures across multiple systems».
   https://martinfowler.com/bliki/CircuitBreaker.html
4. Stripe, *API Reference*, «Idempotent requests» (consultada em 22 de novembro de 2026). «Retries with the same key
   return the saved response, including 500 errors.»
   https://docs.stripe.com/api/idempotent_requests
5. Stripe, «Verificar el estado de un PaymentIntent» (versão em espanhol da Stripe; consultado em 22 de novembro de
   2026). «Stripe puede enviar eventos de webhook a tu servidor a fin de notificarte cuando cambie el estado de un
   PaymentIntent, que puedes usar para, por ejemplo, determinar cuándo entregar bienes y servicios.»
   https://docs.stripe.com/payments/payment-intents/verifying-status
6. Stripe, «Errores» (consultado em 22 de novembro de 2026). «402 Error en la solicitud Los parámetros eran válidos,
   pero se produjo un error en la solicitud».
   https://docs.stripe.com/error-low-level
7. Postman, `postman-sandbox`, CHANGELOG (consultado em 22 de novembro de 2026). «GH-106 Support for timers inside
   sandbox (not in browser)».
   https://github.com/postmanlabs/postman-sandbox/blob/develop/CHANGELOG.yaml

Medição própria: cada saída desta lição foi medida com curl e newman 6.2.2 em 22 de novembro de 2026, com a API da loja
no ar sem Docker e reiniciada antes de cada rodada, contra a loja do curso (hb-curso-qa, f9247aa): os quatro modos do
gateway, o E7, a espera de 5 segundos (sem ela, a coleção sai verde com E7) e os três exercícios.

Regras do curso, sem fonte externa:

- «Um teste confere que o estado e o dinheiro batem, não só o código»: o 504 é igual com o gateway que caiu e com o
  lento; o que muda é o que acontece depois.
- «A espera de um teste tem um porquê»: espera-se o tempo que o outro sistema leva, com margem. Uma espera menor deixa o
  erro passar (medido).
- «Uma dependência lenta é mais perigosa do que uma que caiu»: a que caiu não cobra; a lenta cobra quando já ninguém a
  espera.
