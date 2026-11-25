# Lição 06 — Testar uma API à mão

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **API:** a porta pela qual um programa pede coisas à loja, sem tela no meio. A página que você usou
  nas lições anteriores também passa por ali.
- **Requisição:** o que você manda: o que quer fazer, para qual rota e, às vezes, alguns dados.
- **Resposta:** o que a loja responde. Traz três partes: código, cabeçalhos e corpo.
- **Código:** um número de três dígitos no início da resposta que diz como foi a sua requisição: 200, 404, 422…

**O que fica com você:** você fala com a API da loja usando `curl`, lê as três partes de cada resposta e prevê o
código de uma requisição inválida antes de mandá-la.

**Ideia nova desta lição (a única):** uma API responde com um código, um corpo e cabeçalhos, e os três se
conferem.

**Em que ordem vai:** você faz a sua primeira chamada e separa as três partes dela (passo 1), aprende a ler o código
(passo 2), faz uma compra completa pela API (passo 3), descobre por que o código sozinho não basta (passo 4), confere
os cabeçalhos (passo 5) e prevê cinco erros antes de provocá-los (passo 6).

---

## A cena

*Cenário inventado; os códigos, as mensagens e o erro da loja são reais.*

Segunda-feira, 10:00. Chega o aviso: «O frete grátis com cupom já foi corrigido, você testa?». O QA abre o terminal,
manda a requisição que aplica o cupom a um carrinho de $1,110.00 (pesos mexicanos) e vê na primeira linha:

```text
HTTP/1.1 200 OK
```

«Duzentos. Funciona.» Marca como testado e segue com o resto.

Na terça, a mesma cliente da lição 05 volta a escrever: cobraram de novo $99.00 de frete.

O QA volta ao seu terminal. A resposta de segunda continua lá, completa. Embaixo do 200, no corpo, dizia
`"envio":{"texto":"$99.00"…}`. Ele nunca leu.

O 200 só dizia que a loja **entendeu e respondeu**. Não dizia que respondeu **certo**. Esta lição é para ler a
resposta inteira, não só a primeira linha.

---

## Antes de começar

**Você precisa da loja no ar.** Como na lição 00: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra janela, o
terminal da loja. Todos os comandos desta lição se digitam **lá dentro**, no terminal da loja.

**Faça o passo 6 sem IA.** O que se avalia é se **você** prevê o código antes de ver a resposta. Uma IA pode te dizer
o código de cada requisição, mas o que se treina aqui é o reflexo de esperar algo antes de rodar.

**O que você já sabe e vai usar:** da lição 00, `curl http://localhost:8080/api/salud` e o painel de rede do
navegador, onde você viu o código de cada requisição; da 03, o cupom BIENVENIDA10 e o mínimo dele de $500.00; da
04, que um pedido pago não pode mais ser pago; da 05, a cliente do carrinho de $1,110.00.

**Comece limpo quando a lição disser.** A loja guarda o que você fez nas lições anteriores: os seus pedidos, o seu
carrinho e as suas sessões. Os valores desta lição supõem uma loja recém-aberta, então quando um passo disser
«comece limpo», faça duas coisas no terminal da loja:

1. Rode `tienda reiniciar`. É o mesmo que `./practicar reiniciar` da lição 00, mas por dentro. Apaga
   pedidos, carrinhos e **sessões**; os erros ligados ficam como estavam.
2. Entre de novo com o comando «Apresente-se» do passo 3 e guarde o token **novo** em `TOKEN`. O de antes
   não serve mais: com ele, a loja te responde 401.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · A sua primeira chamada, em três partes

Na lição 00 você perguntou à loja se ela estava no ar. Agora peça um produto, e acrescente `-i`:

```bash
curl -i http://localhost:8080/api/productos/playera-azul
```

`-i` pede ao `curl` que te mostre também os **cabeçalhos** da resposta, não só o corpo. Você verá algo assim
(tirei a data e o nome do servidor, que mudam):

```text
HTTP/1.1 200 OK
content-length: 116
content-type: application/json
content-language: pt

{"id":"playera-azul","nombre":"Camiseta azul","precio":{"texto":"$333.00","centavos":33300},"categoria":"Camisetas"}
```

Nas respostas da API que você vai ver nesta lição, as três partes chegam nesta ordem:

| Parte | Onde está | O que te diz aqui |
|---|---|---|
| **Código** | A primeira linha, depois de `HTTP/1.1` | `200 OK`: deu certo |
| **Cabeçalhos** | As linhas `nome: valor`, até a linha vazia | Que o corpo vem em JSON e em português |
| **Corpo** | Tudo o que vem depois da linha vazia | A camiseta: o nome, o preço e a categoria dela |

A linha vazia é a fronteira: em cima, dados **sobre** a resposta; embaixo, a resposta em si.

**Agora você:** peça um produto que não existe, `/api/productos/no-existe`, com `-i`. Antes de rodar, **preveja**
o código e o corpo. Depois compare com o que você vê:

```text
HTTP/1.1 404 Not Found
content-type: application/json
content-language: pt

{"mensaje":"esse produto não existe"}
```

(A partir daqui não copio mais `content-length`: muda a cada corpo e não te diz nada novo.)

---

## Passo 2 · Como se lê um código

O código tem três dígitos, e **o primeiro já te diz quase tudo**. A norma do HTTP (RFC 9110) os agrupa assim:

| Começa com | Quer dizer | Na loja |
|---|---|---|
| **2** | Deu certo | 200, 201 |
| **4** | O problema está na **sua requisição** | 400, 401, 404, 409, 422 |
| **5** | O problema está **no servidor** | 504, que você verá na lição 08 |

Antes de ler a mensagem, o primeiro dígito já te diz de que lado procurar. Um 4 diz «revise o que você mandou»; um 5
diz «a loja falhou».

Estes são os códigos que você vai ver na loja, com o que a norma diz de cada um e um exemplo medido:

| Código | O que a norma diz | Quando a loja o dá |
|---|---|---|
| **200 OK** | Deu certo | Você pede um produto que existe |
| **201 Created** | Deu certo e algo novo foi **criado** | Você faz login ou cria um pedido |
| **400 Bad Request** | A requisição está malformada | Você manda um JSON quebrado, como `{"cantidad:2` |
| **401 Unauthorized** | Falta uma credencial válida | Você pede os seus pedidos sem ter feito login |
| **404 Not Found** | Não encontrou o que você pediu, ou não quer te dizer se existe | Um produto ou um pedido que não existe |
| **409 Conflict** | Choca com o estado atual do que você pediu | Você paga um pedido que já está pago |
| **422 Unprocessable Content** | Entendeu a requisição, mas não pode fazer o que ela pede | Você pede 0 peças ou aplica o cupom a um carrinho pequeno |

Repare na diferença entre **400** e **422**, porque é a que mais se confunde. Nesta loja:

- **400:** a loja **não conseguiu ler** a sua requisição. `{"cantidad:2` não é JSON: falta uma aspa.
- **422:** a loja **leu**, e o que você pede não se pode fazer. `{"cantidad":0}` é um JSON perfeito, mas ninguém
  compra zero peças.

A norma reserva o 422 para isso, uma requisição bem escrita que não se pode cumprir. O 400 é mais amplo: cobre
qualquer requisição que o servidor veja como malfeita, e o JSON quebrado é só um exemplo.

---

## Passo 3 · Uma compra completa pela API

Na página, comprar são alguns cliques. Pela API são quatro requisições, e cada uma ensina algo do `curl`.

**Comece limpo:** rode `tienda reiniciar`. A primeira requisição abaixo é justamente o login.

**1. Apresente-se.** Para quase tudo é preciso fazer login:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Três coisas novas. As linhas que terminam em `\` são um mesmo comando partido para ler melhor:

| Opção | O que faz |
|---|---|
| `-X POST` | Diz **o que** você quer fazer: o método. Sem `-X`, o `curl` usa `GET`, que só pede. Aqui o `POST` abre uma sessão; em outras rotas cria um pedido, aplica um cupom ou paga |
| `-H '…'` | Acrescenta um **cabeçalho** à sua requisição. Este avisa à loja que o que você manda é JSON |
| `-d '…'` | Os **dados** que você manda: o corpo da sua requisição |

A loja responde:

```text
HTTP/1.1 201 Created
content-type: application/json
content-language: pt

{"token":"OsnWdHMafjKUECEhtSIUQ-vU32wnHNDM","cliente":"Marta"}
```

**201**, não 200: algo foi criado, a sua sessão. O `token` é o seu passe; o seu será diferente. Guarde-o em uma
variável para não copiá-lo toda vez (cole o seu entre as aspas):

```bash
TOKEN='cole-aqui-seu-token'
```

**2. Adicione duas camisetas ao carrinho.** O token viaja no cabeçalho `Authorization`:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":2}'
```

`PUT` deixa algo como você diz: «no meu carrinho eu quero 2 desta camiseta». As aspas aqui são duplas, para que o
terminal ponha o seu token no lugar de `$TOKEN`.

**3. Transforme o carrinho em um pedido:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos \
  -H "Authorization: Bearer $TOKEN"
```

De novo **201**. No corpo procure `"id"`: é o número do seu pedido, com `"estado":"criado"` e um total de
$765.00: duas camisetas de $333.00 mais $99.00 de frete. Se você começou limpo, é o 1. Guarde-o, como o token
(ponha o seu):

```bash
PEDIDO='1'
```

**4. Pague-o:**

```bash
curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/pago \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tarjeta":"4242 4242 4242 4242"}'
```

**200**, com `"mensaje":"pagamento aprovado"` e o pedido em `"estado":"pago"`.

Você acabou de fazer pela API o que na lição 00 fez com cliques. Assim é que se testam as regras sem depender
da tela.

---

## Passo 4 · Por que o código sozinho não basta

Volte à cena. Agora você vai ver com os seus olhos o que o QA não leu.

**Comece limpo** (`tienda reiniciar` e um token novo da Marta em `TOKEN`). Depois monte um carrinho de $1,110.00
com 10 bonés de $111.00:

```bash
curl -i -X PUT http://localhost:8080/api/carrito/productos/gorra \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"cantidad":10}'
```

E aplique o cupom:

```bash
curl -i -X POST http://localhost:8080/api/carrito/cupon \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"codigo":"BIENVENIDA10"}'
```

Antes de olhar, **preveja**: o código e o que o frete deve dizer.

Com a loja limpa, estas são as partes do corpo que importam:

```text
HTTP/1.1 200 OK
…
"subtotal":{"texto":"$1,110.00"…},"descuento":{"texto":"$111.00"…},"envio":{"texto":"$0.00"…},"total":{"texto":"$999.00"…}
```

Agora ligue o erro E1, o da lição 05 (o quadro abaixo diz como), **comece limpo** de novo e repita
as duas requisições. A resposta
muda assim:

```text
HTTP/1.1 200 OK
…
"envio":{"texto":"$99.00"…},"total":{"texto":"$1,098.00"…}
```

**O mesmo 200.** O código não mudou, e o cliente pagaria $99.00 a mais. Por isso os três se conferem: o código diz
se a loja entendeu; o corpo diz **o que** ela respondeu. Neste caso, o 200 não revela o erro: o corpo sim. Em outros,
uma regra quebrada muda o código, o corpo ou os dois.

> **Como se liga o E1.** No terminal da loja: `tienda error E1 on`; para desligá-lo, `tienda error E1 off`.
> Do seu computador é o mesmo com `./practicar error E1 on` e `off`, como na lição 00. Ao terminar este
> passo, desligue-o.

---

## Passo 5 · Os cabeçalhos também dizem coisas

Os cabeçalhos são a parte que menos se olha, e às vezes é justamente a que falha. Dois que todas as respostas
da API trazem nesta lição:

| Cabeçalho | O que diz | Por que você o confere |
|---|---|---|
| `content-type: application/json` | Em que formato vem o corpo | Se um dia chegar outra coisa, quem ler a resposta como JSON vai quebrar |
| `content-language: pt` | Em que idioma vem o corpo | A loja fala cinco idiomas; ela tem de dizer em qual te respondeu |

E um que **você** manda para pedir outro idioma, `Accept-Language`:

```bash
curl -i http://localhost:8080/api/pedidos -H 'Accept-Language: es'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer
content-type: application/json
content-language: es

{"mensaje":"inicia sesión primero"}
```

Confira as três partes juntas: **401** porque você não mandou o seu token; o corpo em espanhol, e `content-language: es`, que
o confirma. E um cabeçalho novo, `www-authenticate: Bearer`: a norma do HTTP pede que todo 401 diga **como** a pessoa
se apresenta. Aqui diz «com um token Bearer», justo o que você fez no passo 3. Se o corpo viesse em espanhol e o cabeçalho dissesse `pt`, seria um erro mesmo que o código estivesse
certo.

**Agora você:** repita a requisição com `-H 'Accept-Language: en'` e confira que o corpo e o cabeçalho coincidem.

---

## Passo 6 · Preveja antes de rodar

Esta é a habilidade da lição: **saber que código você espera antes de ver a resposta.** Se você não o esperava, não
sabe se o que vê está certo.

**Prepare a loja:** comece limpo e repita as quatro requisições da compra do passo 3. Ficam um pedido
pago em `$PEDIDO` e um carrinho vazio.

Copie esta folha. Para cada requisição, escreva **antes de rodá-la** o código que você espera e por quê. Depois rode e
anote o que saiu: o código, o que o corpo diz e um cabeçalho que você tenha conferido.

| # | A requisição | Sua previsão | Por quê | Código e corpo que saíram | Um cabeçalho que conferi |
|---|---|---|---|---|---|
| 1 | Os seus pedidos, **sem** o cabeçalho `Authorization` | | | | |
| 2 | O produto `/api/productos/zapatos` | | | | |
| 3 | Adicionar camisetas com `-d '{"cantidad":0}'` | | | | |
| 4 | Adicionar camisetas com `-d '{"cantidad":2'` (falta a chave do final) | | | | |
| 5 | Pagar **de novo** o pedido que você pagou | | | | |

Para as requisições 3 e 4 use o comando do passo 3, número 2, e mude só o que vai em `-d`. Para a 5, repita o
número 4 do jeito que está.

Quando terminar, compare com as respostas no final. Para cada erro de previsão, escreva uma linha: o que você achava e
o que a resposta te ensinou. Essas linhas valem mais que os acertos.

---

## Como se confere

**A sua folha de previsões** (passo 6) se confere com «Compare as respostas»: o código, e que o seu «por quê» nomeie
a causa certa.

**A sua prática com `curl`** é revisada pelo `verifica 06`. Rode-o **logo ao terminar o passo 6**, antes de
reiniciar a loja de novo:

```bash
verifica 06
```

Ele confere três coisas na loja: que a Marta tem um pedido pago pela API, que você provocou os cinco erros da folha e
que o E1 ficou desligado. Não importa a ordem nem quantas vezes você tentou. A loja lembra das suas requisições desde
o último reinício: `tienda reiniciar` apaga esse registro e, se você reiniciou, repita a compra e os cinco erros (é
rápido). De cada requisição ela guarda só quem fez, para qual rota, que código respondeu e a que horas; nunca o que
você mandou, nem a sua senha, nem o seu token.

Com a sua prática feita, a saída fica assim:

```text
Verificando a lição 06…

✅ A loja registrou as suas requisições desde o último reinício
✅ Marta tem um pedido pago, e você fez o pagamento pela API
✅ Você provocou o 401: pediu GET /api/pedidos sem sessão
✅ Você provocou o 404: pediu /api/productos/zapatos
✅ Você provocou o 422: colocou quantidade 0 no carrinho
✅ Você provocou o 400: mandou um JSON quebrado para o carrinho
✅ Você provocou o 409: tentou pagar de novo um pedido já pago
✅ O erro E1 ficou desligado

🎉 Lição completa!
```

**Antes de dar a lição por terminada, confira:**

- [ ] Você fez as quatro requisições da compra e o seu pedido ficou em `"estado":"pago"`.
- [ ] Você viu o mesmo 200 com E1 desligado e ligado, e em cada caso apontou no corpo o frete.
- [ ] Você pediu um idioma com `Accept-Language` e o corpo coincidiu com `content-language`.
- [ ] Você preencheu a coluna «Sua previsão» das cinco requisições **antes** de rodá-las.
- [ ] Você deixou o E1 desligado (`./practicar error estado` confirma).
- [ ] Você rodou o `verifica 06` antes de reiniciar e saiu 🎉.

---

## Seus exercícios

1. **Mais cinco previsões** (sem IA). Continue com a loja do jeito que o passo 6 a deixou e rode-as **nesta ordem**,
   porque cada uma depende de como a anterior ficou. Antes de rodar cada uma, escreva o código que você espera e por
   quê: (a) fazer login como Luis com a senha `incorrecta`; (b) criar um pedido com o carrinho vazio;
   (c) pôr **uma** camiseta azul no carrinho (`{"cantidad":1}`, não precisa prever) e aplicar a ela o BIENVENIDA10;
   (d) pedir `/api/pedidos/uno`; (e) cancelar o pedido que você pagou. Use 25 minutos como limite. Os comandos, já
   montados:

   ```bash
   curl -i -X POST http://localhost:8080/api/sesiones -H 'Content-Type: application/json' -d '{"cliente":"Luis","contrasena":"incorrecta"}'
   curl -i -X POST http://localhost:8080/api/pedidos -H "Authorization: Bearer $TOKEN"
   curl -i -X PUT http://localhost:8080/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"cantidad":1}'
   curl -i -X POST http://localhost:8080/api/carrito/cupon -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
   curl -i http://localhost:8080/api/pedidos/uno -H "Authorization: Bearer $TOKEN"
   curl -i -X POST http://localhost:8080/api/pedidos/$PEDIDO/cancelacion -H "Authorization: Bearer $TOKEN"
   ```

2. **O pedido de outra pessoa.** Faça login como Luis (`luis-practica`), guarde o token dele em `TOKEN_LUIS` e peça
   o pedido da Marta, o que você tem em `$PEDIDO`, com o token do Luis:
   `curl -i http://localhost:8080/api/pedidos/$PEDIDO -H "Authorization: Bearer $TOKEN_LUIS"`. Preveja primeiro. A loja responde **404**, não «proibido». Por que você acha
   que uma loja prefere dizer «não existe» em vez de «existe, mas não é seu»? Responda em três linhas.
3. **Confira os três.** Com E1 ligado, escreva para a requisição do cupom do passo 4 o que você conferiria em cada parte:
   uma linha para o código, uma para um cabeçalho e uma para o corpo. Qual das três pega o erro?

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo 2):

1. Quais são as três partes de uma resposta, e o que as separa?
2. Uma resposta começa com 4. De que lado você procura o problema?
3. Que diferença há entre um 400 e um 422?
4. Por que fazer login responde 201 e não 200?
5. Uma resposta diz 200 OK. Já dá para dizer que a regra funciona? Por quê?

---

## Para fechar

O teste de segunda ficou pela metade: o 200 estava certo, e o corpo já mostrava o frete errado, completo, embaixo
da linha que sim foi lida. Ler as três partes é o que completa o teste.

O que você leva daqui:

- Toda resposta tem **três partes**: código, cabeçalhos e corpo, com uma linha vazia antes do corpo.
- O **primeiro dígito** do código te diz de que lado procurar: 2 deu certo, 4 é a sua requisição, 5 é o servidor.
- **400** é «não te entendi»; **422** é «te entendi, e não se pode».
- Com `curl`: `-i` para ver os cabeçalhos, `-X` para dizer o que você faz, `-H` para os seus cabeçalhos e `-d` para os seus
  dados.
- **Um 200 não prova a regra.** Diz que a loja entendeu; se a regra se cumpriu, dizem o corpo e, às vezes,
  o código.
- Antes de rodar, **preveja**: sem uma resposta esperada, você não sabe se a que chegou está certa.

Na lição 07 estas mesmas requisições deixam de ser escritas à mão: você as guarda em uma coleção que roda sozinha e
confere as três partes por você.

---

## Compare as respostas

**Passo 1, o produto que não existe.** `404 Not Found` e `{"mensaje":"esse produto não existe"}`. O 4 já te dizia
que o problema estava na sua requisição: você pediu algo que a loja não tem.

**Passo 4, a previsão.** `200 OK` e frete $0.00: o que se paga pela mercadoria depois do cupom fica em $999.00
exatos, e a partir daí o frete é grátis (lição 02). Com E1 ligado o código é o mesmo e o frete sai em $99.00.

**Passo 6, a folha.**

| # | Código | Por quê | Corpo | Um cabeçalho |
|---|---|---|---|---|
| 1 | **401** | Sem token, a loja não sabe quem você é | `{"mensaje":"faça login primeiro"}` | `www-authenticate: Bearer` |
| 2 | **404** | Esse produto não existe | `{"mensaje":"esse produto não existe"}` | `content-language: pt` |
| 3 | **422** | O JSON está certo; zero peças não se pode | `{"mensaje":"o mínimo é 1 peça"}` | `content-type: application/json` |
| 4 | **400** | Não é JSON: a loja não conseguiu lê-lo | `{"mensaje":"a requisição não traz o que esta rota espera",…}` | `content-language: pt` |
| 5 | **409** | O pedido já está pago: choca com o estado dele | `{"mensaje":"este pedido não pode mais ser pago: está «pago»"}` | `content-type: application/json` |

Na coluna do cabeçalho vale qualquer um que você tenha conferido; o importante é que você o tenha lido. Na 1, o
que diz algo novo é `www-authenticate`.

Na 4, o corpo traz além disso um `"detalle"` com o que falhou; não precisa lê-lo inteiro.

**Exercício 1.** (a) **401**, «cliente ou senha incorretos», com `www-authenticate: Bearer`. (b) **422**, «o
carrinho está vazio»: criar o pedido do passo 6 o esvaziou. (c) **422**, «o cupom é para compras de $500.00 ou mais»:
uma camiseta de $333.00 não chega ao mínimo. (d) **400**: `uno` não é um número, e a rota espera um. (e) **200**: um
pedido pago ainda pode ser cancelado (lição 04), e o corpo traz o reembolso de $765.00.

**Exercício 2.** **404**, «esse pedido não existe», igual a se você pedisse um que não existe, como o 999. Uma resposta defensável: se a loja
respondesse «existe, mas não é seu», qualquer pessoa poderia ir testando números e descobrir quantos pedidos há e quais
existem. A norma do HTTP permite justamente isto: um 404 pode querer dizer que o servidor não quer revelar se algo
existe.

**Exercício 3.** Código: 200, o esperado, então não pega nada. Cabeçalho: `content-type: application/json`, o
esperado. Corpo: `"envio"` em $99.00 quando devia ser $0.00. **Só o corpo pega o erro.**

**Revisão.** 1, código, cabeçalhos e corpo; a linha vazia separa os cabeçalhos do corpo. 2, da sua requisição.
3, o 400 é uma requisição que a loja não conseguiu ler; o 422, uma que ela leu e que pede algo que não se pode fazer.
4, porque algo novo foi criado: a sua sessão. 5, não: o código diz que a loja entendeu e respondeu; se a regra se
cumpriu, diz o corpo.

---

## Fontes da lição

1. IETF, *RFC 9110: HTTP Semantics*, junho de 2022, §15 «Status Codes» e §8.5 «Content-Language».
   «The first digit of the status code defines the class of response»; «4xx (Client Error): The request contains bad
   syntax or cannot be fulfilled»; «The 201 (Created) status code indicates that the request has been fulfilled and
   has resulted in one or more new resources being created»; «The 404 (Not Found) status code indicates that the
   origin server did not find a current representation for the target resource or is not willing to disclose that
   one exists»; «The server generating a 401 response MUST send a WWW-Authenticate header field»; «The 409 (Conflict) status code indicates that the request could not be completed due to a conflict
   with the current state of the target resource»; «the syntax of the request content is correct, but it was unable
   to process the contained instructions» (422); «The "Content-Language" header field describes the natural
   language(s) of the intended audience for the representation». https://www.rfc-editor.org/rfc/rfc9110
2. curl, *curl.1 the man page* (curl.se/docs/manpage.html, consultado em 21 de novembro de 2026). `-i`: «Show
   response headers in the output»; `-X`: «Change the method to use when starting the transfer»; `-H`: «Extra header
   to include in information sent»; `-d`: «Send the specified data to a server».
   https://curl.se/docs/manpage.html

Medição própria: cada código, corpo e cabeçalho desta lição foi medido com `curl -i` contra a loja do curso
(HabilMX/curso-qa) em 21 de novembro de 2026, com a API dela no ar sem Docker, incluídas as cinco
requisições da folha, as cinco do exercício 1 e o pedido da Marta visto pelo Luis. A requisição do cupom do passo 4
foi rodada com E1 desligado e ligado: 200 nas duas vezes, com frete $0.00 e $99.00.

Regras do curso, sem fonte externa:

- «Preveja antes de rodar»: é a forma como este curso treina o oráculo, a resposta esperada que o ISTQB pede
  para cada caso de teste; sem ela, uma resposta não pode ser julgada.
