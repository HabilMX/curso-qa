# Lição 08 — Permissões e novas tentativas

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Pedido alheio:** um pedido que outra pessoa fez. Você não deveria conseguir vê-lo, mesmo que saiba o número dele.
- **Nova tentativa:** mandar de novo uma requisição porque a primeira não teve uma resposta clara.
- **Chave de idempotência:** um texto único que você manda com a cobrança, no cabeçalho `Idempotency-Key`, para que a
  loja saiba que uma nova tentativa é **a mesma** cobrança e não uma nova.

**O que fica com você:** uma segunda coleção que testa um pedido de três formas que a lição 07 não tocava: sem login,
com outra cliente e com uma cobrança que se repete. Ela sai verde quando a loja está certa, vermelha quando deixa ver um
pedido alheio e vermelha quando cobra duas vezes.

**Ideia nova desta lição (a única):** cada teste importante se repete com outra pessoa, e cada requisição que muda algo
se repete duas vezes.

**Em que ordem vai:** você monta a coleção com um pedido de verdade (passo 1), pede esse pedido sem login (passo 2) e com
outra cliente (passo 3), cobra e repete a cobrança com a mesma chave (passo 4), e repete tudo com o gateway lento, que é
quando a cobrança dupla aparece (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são reais.*

Numa sexta à noite, duas mensagens chegam ao suporte com dez minutos de diferença.

A primeira é da Marta. Ela pagou o pedido, a página ficou pensando, apareceu um aviso de «não sabemos se o valor foi
cobrado» e ela pagou de novo. No banco dela há **duas** cobranças de $432.00 (pesos mexicanos). O pedido, na loja,
continua sem pagar.

A segunda é do Luis, e é pior. Ele abriu o pedido dele, viu que o endereço terminava em `/api/pedidos/12`, trocou o 12
por um 11 por curiosidade e a loja mostrou o pedido de outra pessoa, com os produtos e o total.

Os testes da equipe estavam verdes. Testavam a compra completa, com uma cliente, uma vez. Nenhum perguntou o que acontece
se **outra** pessoa pedir o mesmo pedido, nem o que acontece se a cobrança **se repetir**. As duas coisas que as pessoas
de fato fazem.

---

## Antes de começar

**Você precisa da loja no ar.** Como na lição 07: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra janela, o
terminal da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`, onde você já tem os ambientes da lição 07.

**O que você já sabe e vai usar:** da lição 07, a coleção, `pm.test`, `pm.collectionVariables.set`, os ambientes `local` e
`luis`, `newman run` e `jq empty`; da 06, o 401 sem token e o cabeçalho `www-authenticate: Bearer`; da 04, que repetir um
pagamento com a mesma chave não é um pagamento novo; da 00, que a página manda a chave de idempotência quando você paga.

**Faça o passo 3 sem IA.** O que você treina ali é prever qual código a loja deve responder quando outra cliente pede o
seu pedido, com o porquê dele, antes de rodá-lo.

**Comece limpo antes de cada rodada,** como na 07:

```bash
tienda reiniciar
```

> **Esta lição usa a loja da lição 08.** Ela traz o erro E5, o cartão cortado (`•••• 4242`) e um `tienda reiniciar` que
> descarta as cobranças que o gateway tinha a caminho. Se `tienda error E5 on` te disser que esse erro não existe,
> atualize a sua loja antes de seguir: com uma versão anterior, as suas saídas não vão coincidir.

Atenção a um detalhe: o `tienda reiniciar` também devolve o gateway de pagamento ao normal. Se no passo 5 você quiser o
gateway lento, coloque-o **depois** de reiniciar.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Uma coleção nova, com um pedido de verdade

Para testar quem pode ver um pedido, primeiro você precisa de um pedido. Esta coleção o faz sozinha: a cliente faz login,
põe uma camiseta no carrinho e faz o pedido dela. Dessa resposta ela guarda duas coisas para depois: o **número do
pedido** e uma **chave de idempotência** nova.

**Primeiro, a outra cliente nos seus ambientes.** Para testar «com outra cliente» sem escrever o nome dela na coleção,
cada ambiente diz quem é a outra. Abra o seu:

```bash
nano local.postman_environment.json
```

e deixe-o assim (as três primeiras chaves são as da lição 07; as duas últimas são novas):

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"},
  {"key": "otra_cliente", "value": "Luis"},
  {"key": "otra_contrasena", "value": "luis-practica"}
 ]
}
```

E o do Luis, ao contrário: para ele, a outra é a Marta.

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"},
  {"key": "otra_cliente", "value": "Marta"},
  {"key": "otra_contrasena", "value": "marta-practica"}
 ]
}
```

**Agora a coleção.** É um arquivo novo; a da lição 07 não é tocada:

```bash
nano permisos.postman_collection.json
```

```json
{
 "info": {
  "name": "Permissões",
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
  }
 ]
}
```

Tudo isto você já conhece da lição 07, menos as últimas linhas:

| Linha | O que faz |
|---|---|
| `pm.collectionVariables.set('pedido', …id)` | Guarda o número do pedido que acabou de criar, para pedi-lo depois como `{{pedido}}` |
| `pm.variables.replaceIn('{{$guid}}')` | `{{$guid}}` é uma variável que o Postman inventa a cada rodada: um texto único, como `611c2e81-2ccb-42d8-9ddc-2d0bfa65c1b4`. O `replaceIn` o converte em texto |
| `pm.collectionVariables.set('llave', …)` | Guarda esse texto como a chave de idempotência **desta** cobrança, para usá-la duas vezes no passo 4 |

Por que a chave não se escreve à mão, como `compra-1`? Porque cada cobrança precisa da sua. Se você a escrevesse fixa, na
segunda vez que rodasse a coleção a loja veria uma chave já usada em outro pedido (você testa isso no exercício 3).

Confira que o JSON está bem escrito e rode-a:

```bash
jq empty permisos.postman_collection.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ A cliente faz login
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 14ms]
  ✓  código 201

→ Uma camiseta no carrinho
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 547B, 3ms]
  ✓  código 200

→ Ela faz o pedido
  POST http://localhost:8080/api/pedidos [201 Created, 681B, 3ms]
  ✓  código 201
```

Três de três. Os tamanhos e os tempos das saídas desta lição são os da medição; os seus podem mudar. Os códigos, os
vistos e os vermelhos, não.

---

## Passo 2 · Sem login

A primeira pergunta de permissões é a mais simples: alguém que **não fez login** pode ver o pedido?

Acrescente uma quarta requisição, como na lição 07: uma vírgula depois da `}` que fecha «Ela faz o pedido», e isto:

> **Como colar em `item`.** Cada requisição nova vai **antes do `]` que fecha `item`**. Ponha uma vírgula depois da `}` da
> última requisição que você já tinha. Se colar duas ou três de uma vez, também vai uma vírgula entre cada uma delas,
> mas **não** depois da última. Ao terminar, o arquivo fecha com `]` e `}`, e o `jq empty` não imprime nada.

```json
  {
   "name": "Sem login não se vê",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('sem login: código 401', () => pm.response.to.have.status(401));",
    "pm.test('pede token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
   ]}}]
  }
```

Ela não leva cabeçalho `Authorization`: esse é o ponto. Os dois testes você já escreveu no exercício 1 da lição 07, para
a lista de pedidos; aqui eles vão sobre **um** pedido, o que a coleção acabou de criar.

`jq empty`, `tienda reiniciar` e rode. As três primeiras continuam iguais, e a nova:

```text
→ Sem login não se vê
  GET http://localhost:8080/api/pedidos/1 [401 Unauthorized, 217B, 2ms]
  ✓  sem login: código 401
  ✓  pede token
```

---

## Passo 3 · Com outra cliente

Agora a pergunta da cena: o Luis tem login, sabe o número do pedido da Marta e o pede. O que a loja deve responder?

**Antes de escrever o teste, preveja no papel:** o código, e um porquê de uma linha. Não continue lendo até tê-lo.

Você tem três candidatos razoáveis, e os três fazem sentido:

| Código | O que a loja estaria dizendo |
|---|---|
| 401 | «Não sei quem você é» |
| 403 | «Sei quem você é e não deixo» |
| 404 | «Esse pedido não existe» |

401 não é: o Luis fez login, a loja sabe quem ele é. Entre 403 e 404, esta loja escolheu **404**, e tem uma regra escrita
para isso: um pedido alheio **não existe** para quem não o fez. O motivo é que um 403 já diz ao Luis algo que ele não
deveria saber: que o pedido 11 existe. Com 404, a resposta não o confirma; é o que a lição 06 chamava de «não quer te
dizer se existe». Outras APIs escolhem 403, e também está certo: o indispensável é que o Luis não veja nem toque o
pedido. Se você previu 403 com esse porquê, o seu raciocínio era bom; a diferença é uma decisão da loja, e o teste confere
**o que a loja decidiu**.

Acrescente mais duas requisições, com uma vírgula entre as duas. A primeira faz login com a outra cliente e guarda o
token **dela** à parte; a segunda pede o pedido com esse token:

```json
  {
   "name": "A outra cliente faz login",
   "request": {
    "method": "POST",
    "url": "{{base}}/api/sesiones",
    "header": [{"key": "Content-Type", "value": "application/json"}],
    "body": {"mode": "raw", "raw": "{\"cliente\":\"{{otra_cliente}}\",\"contrasena\":\"{{otra_contrasena}}\"}"}
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 201', () => pm.response.to.have.status(201));",
    "pm.collectionVariables.set('token_otra', pm.response.json().token);"
   ]}}]
  },
  {
   "name": "A outra cliente não o vê",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token_otra}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('pedido alheio: código 404', () => pm.response.to.have.status(404));",
    "pm.test('sem produtos', () => pm.expect(pm.response.json()).to.not.have.property('productos'));"
   ]}}]
  }
```

| Teste | Por que está |
|---|---|
| `pedido alheio: código 404` | A regra da loja |
| `sem produtos` | Para o caso de um dia a loja responder outro código **e mesmo assim** mandar o pedido. O que importa é que o Luis não veja os produtos da Marta, não só o número da resposta |

Rode de novo. As duas novas:

```text
→ A outra cliente faz login
  POST http://localhost:8080/api/sesiones [201 Created, 213B, 2ms]
  ✓  código 201

→ A outra cliente não o vê
  GET http://localhost:8080/api/pedidos/1 [404 Not Found, 191B, 2ms]
  ✓  pedido alheio: código 404
  ✓  sem produtos
```

**Agora ligue o erro da cena.** O E5 faz a loja mostrar o pedido a qualquer um que tenha login:

```bash
tienda error E5 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ A outra cliente não o vê
  GET http://localhost:8080/api/pedidos/1 [200 OK, 676B, 2ms]
  1. pedido alheio: código 404
  2. sem produtos
```

E embaixo:

```text
 1.  AssertionError  pedido alheio: código 404
                     expected response to have status code 404 but got 200
 2.  AssertionError  sem produtos
                     expected { id: 1, estado: 'creado', …(11) } to not have property 'productos'
```

Esse é o pedido da Marta nas mãos do Luis, e a sua coleção o pegou. Repare numa coisa: **todos os outros testes
continuaram verdes.** Só com a Marta, a loja com E5 parece perfeita. O erro só aparece quando outra pessoa pergunta.

Desligue-o antes de seguir:

```bash
tienda error E5 off
```

---

## Passo 4 · Cobrar, e repetir a cobrança com a mesma chave

Cobrar é uma requisição que **muda algo**: move dinheiro. Essas requisições têm uma pergunta extra: o que acontece se
chegarem duas vezes?

Podem chegar duas vezes: a página fica pensando e a pessoa aperta «Pagar» de novo, ou a rede cai e o programa tenta de
novo sozinho. Por isso a loja aceita o cabeçalho `Idempotency-Key`: se duas cobranças chegam com a **mesma** chave, uma
**depois** da outra, ela cobra uma só vez. Se a primeira já teve resposta, à segunda ela responde o mesmo; se a primeira
ficou sem resposta (um 504, no passo 5), a segunda espera que essa mesma cobrança termine. Se duas chegassem exatamente
ao mesmo tempo, esta loja responde 409 à segunda enquanto a primeira ainda está em andamento; esse é tema da lição 09.

Acrescente as três últimas requisições, com uma vírgula entre cada uma. As duas primeiras são **a mesma cobrança**, com a
mesma chave; a terceira confere
como o pedido ficou:

```json
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
    "pm.test('aprovado ou sem resposta', () => pm.expect(pm.response.code).to.be.oneOf([200, 504]));"
   ]}}]
  },
  {
   "name": "Tenta de novo com a mesma chave",
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
    "pm.test('nova tentativa: código 200', () => pm.response.to.have.status(200));"
   ]}}]
  },
  {
   "name": "Como ficou o pedido",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/pedidos/{{pedido}}",
    "header": [{"key": "Authorization", "value": "Bearer {{token}}"}]
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('pedido pago', () => pm.expect(pm.response.json().estado).to.eql('pagado'));",
    "pm.test('cobrado igual ao total', () => pm.expect(pm.response.json().cobrado.texto).to.eql(pm.response.json().total.texto));"
   ]}}]
  }
```

Três coisas novas:

- **`to.be.oneOf([200, 504])`:** a primeira cobrança aceita duas respostas. 200 é «aprovado»; 504 é «o gateway não
  respondeu a tempo e não sei se o valor foi cobrado». As duas são honestas, e o que importa vem depois. Por que o 504 é
  necessário você vê no passo 5.
- **`cobrado` e `total`:** o pedido traz os dois. `total` é o que a cliente deve; `cobrado` é o que o gateway de fato
  lançou no cartão dela. Se forem diferentes, alguém cobrou a mais ou a menos. O teste compara um com o outro, então não
  depende do valor: serve igual para um pedido de $432.00 e para um de $999.00.
- **O cartão** `4242 4242 4242 4242` é o de prática da lição 00, que não é de ninguém. Nas respostas da loja ele sai
  cortado, `•••• 4242`: em uma resposta não se mostra o número completo de um cartão.

Rode:

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 970B, 3ms]
  ✓  aprovado ou sem resposta

→ Tenta de novo com a mesma chave
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 970B, 2ms]
  ✓  nova tentativa: código 200

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 881B, 2ms]
  ✓  pedido pago
  ✓  cobrado igual ao total
```

Doze de doze. A segunda cobrança respondeu o mesmo que a primeira e não cobrou de novo.

**Agora ligue o E4**, o erro da cobrança dupla, e rode igual:

```bash
tienda error E4 on
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

Doze de doze **outra vez**. O E4 não faz nada? Faz, mas só quando a primeira cobrança fica sem resposta. Com o gateway
respondendo rápido, a loja guardou a resposta da primeira cobrança e à nova tentativa devolveu essa mesma, sem chegar à
parte que o E4 quebra. Para ver o erro você tem de provocar o que aconteceu com a Marta: que o gateway demore.

---

## Passo 5 · Quando o gateway demora

A loja espera o gateway por **5 segundos**. Se nesse tempo ele não responde, a loja diz à cliente **504**: «o gateway não
respondeu a tempo; não sabemos se o valor foi cobrado. Tente de novo com a mesma chave de idempotência». Mas o gateway
continua trabalhando, e a cobrança pode terminar depois.

Esse é o momento perigoso: a cliente não sabe se foi cobrada e paga de novo. Com a mesma chave, a loja reconhece que é a
mesma cobrança: espera a primeira terminar e responde 200, sem cobrar outra vez. Com uma chave diferente, ou com uma loja
que não respeita a chave, são duas cobranças.

Faça o gateway demorar 7 segundos (depois de reiniciar, porque reiniciar o devolve ao normal), com o E4 ainda ligado:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

A rodada demora uns dez segundos. As três últimas requisições:

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado ou sem resposta

→ Tenta de novo com a mesma chave
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  1. nova tentativa: código 200

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 817B, 5ms]
  2. pedido pago
  ✓  cobrado igual ao total
```

E embaixo:

```text
 1.  AssertionError  nova tentativa: código 200
                     expected response to have status code 200 but got 504
 2.  AssertionError  pedido pago
                     expected 'creado' to deeply equal 'pagado'
```

Dois vermelhos: a nova tentativa também ficou sem resposta e o pedido continua «creado». E «cobrado igual ao total» em
verde? Naquele instante, sim: uma cobrança de $432.00 já tinha entrado. A segunda cobrança, a que o E4 lançou com outra
chave escondido, ainda estava a caminho. A sua coleção o pegou pelos outros dois testes, mas essa segunda cobrança
ninguém ainda viu.

**Veja você mesmo.** Sem reiniciar, espere alguns segundos e peça o pedido à mão, como na lição 06. Faça login como a
Marta:

```bash
curl -i -X POST http://localhost:8080/api/sesiones \
  -H 'Content-Type: application/json' \
  -d '{"cliente":"Marta","contrasena":"marta-practica"}'
```

Guarde o token que ele respondeu e peça o pedido 1:

```bash
TOKEN='pega-aquí-tu-token'
curl -i http://localhost:8080/api/pedidos/1 -H "Authorization: Bearer $TOKEN"
```

No corpo, procure `"estado"` e `"cobrado"`: o pedido continua em `"creado"`, e o cobrado já diz `"$864.00"`, o dobro do
total. Essa é a cena da Marta: duas cobranças e o pedido sem pagar.

O valor de `estado` é um código e fica em espanhol (`creado`, `pagado`); a página o mostra no seu idioma
(criado, pago).

**Agora desligue o E4 e rode igual, com o gateway lento:**

```bash
tienda error E4 off
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela paga
  POST http://localhost:8080/api/pedidos/1/pago [504 Gateway Timeout, 341B, 5s]
  ✓  aprovado ou sem resposta

→ Tenta de novo com a mesma chave
  POST http://localhost:8080/api/pedidos/1/pago [200 OK, 970B, 1989ms]
  ✓  nova tentativa: código 200

→ Como ficou o pedido
  GET http://localhost:8080/api/pedidos/1 [200 OK, 881B, 5ms]
  ✓  pedido pago
  ✓  cobrado igual ao total
```

Doze de doze. A primeira cobrança disse 504; a nova tentativa, com a mesma chave, esperou o gateway terminar (por isso
demorou uns dois segundos) e respondeu 200. Uma só cobrança. Agora você vê por que a primeira cobrança aceita 200 **ou**
504: a mesma coleção tem de sair verde com o gateway rápido e com o lento, porque o erro só se vê com o lento.

**E com a outra pessoa.** A ideia desta lição vale também ao contrário: rode a coleção como o Luis, com o gateway lento:

```bash
tienda reiniciar
tienda pasarela tarda 7
newman run permisos.postman_collection.json -e luis.postman_environment.json
```

Doze de doze. Agora o pedido é do Luis, e quem tenta vê-lo é a Marta. Você não tocou a coleção: só o ambiente.

Deixe o gateway normal ao terminar:

```bash
tienda pasarela aprueba
```

---

## Como se confere

**A sua coleção e os seus ambientes** são revisados pelo `verifica 08`. Salve-os em `~/practica` como
`permisos.postman_collection.json`, `local.postman_environment.json` e `luis.postman_environment.json` e, no terminal
da loja, escreva:

```bash
verifica 08
```

O `verifica`:

1. roda a sua coleção com a loja limpa três vezes: com o seu ambiente `local`, com `local` e o gateway demorando 7
   segundos, e com o seu ambiente `luis`: as três vezes tem de sair **verde**;
2. roda-a com E5 ligado: **pelo menos um teste tem de sair vermelho**; se sair verde, a sua coleção não perguntou a
   outra cliente;
3. roda-a com E4 ligado e o gateway demorando 7 segundos: **pelo menos um teste tem de sair vermelho**; se sair verde,
   a sua coleção não conferiu a nova tentativa;
4. confere que nenhuma requisição tenha escritos à mão o endereço, `Marta`, `Luis` ou as senhas deles.

Se faltar algo, ele diz o que arrumar. Com o gateway lento, leva uns dois minutos. Antes de rodá-lo, a lista abaixo diz
se a forma está certa.

**Antes de dar a lição por terminada, confira:**

- [ ] Os seus dois ambientes têm `otra_cliente` e `otra_contrasena`, e em cada um a outra é a outra pessoa.
- [ ] A sua coleção tem nove requisições, na ordem dos passos 1 a 4.
- [ ] Com a loja limpa sai 12 de 12, com o gateway normal e com `tienda pasarela tarda 7`.
- [ ] Com E5 ligado falham «pedido alheio: código 404» e «sem produtos».
- [ ] Com E4 ligado e o gateway lento falham «nova tentativa: código 200» e «pedido pago».
- [ ] Com `-e luis.postman_environment.json` sai verde sem tocar a coleção.
- [ ] Na sua coleção não aparecem `localhost`, `Marta`, `Luis` nem as senhas (procure-os com
      `grep -n -e localhost -e Marta -e Luis -e practica permisos.postman_collection.json`; não pode imprimir nada).
- [ ] Você deixou E4 e E5 desligados e o gateway normal (`tienda error estado` e `tienda pasarela aprueba`).

---

## Seus exercícios

1. **Cancelar o que é alheio.** Acrescente uma requisição, depois de «A outra cliente não o vê», na qual a outra cliente
   tente **cancelar** o pedido: `POST {{base}}/api/pedidos/{{pedido}}/cancelacion`, com o token dela. Antes de rodá-la,
   preveja o código e escreva dois testes: um para o código e outro que confira, na requisição «Como ficou o pedido», que
   o pedido **continua** em «pagado». Por que o segundo teste é necessário, se o primeiro já confere o código?
2. **A chave nova a cada tentativa.** Faça uma cópia da sua coleção (`cp permisos.postman_collection.json copia.json`).
   Na cópia, em «Tenta de novo com a mesma chave», troque `{{llave}}` por `{{$guid}}`: assim cada tentativa leva uma
   chave diferente. Rode-a com E4 **desligado** e o gateway lento. Preveja primeiro: verde ou vermelha, e por quê? Depois,
   três segundos depois de terminar, peça o pedido à mão com `curl` e leia `cobrado` e `movimientos`. Ao terminar, `rm copia.json`.
3. **A mesma chave em outro pedido.** Com `curl`, como na lição 06, e com a loja recém-reiniciada: (1) faça login como a
   Marta e guarde o token em `TOKEN`; (2) ponha uma camiseta no carrinho e faça o pedido 1; (3) pague-o com a chave
   `prueba-1`; (4) ponha outra camiseta, faça o pedido 2 e, **antes de rodar o último comando**, preveja o código dele e
   por que a loja não pode simplesmente aprová-lo:

   ```bash
   curl -i -X POST http://localhost:8080/api/pedidos/2/pago \
     -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' \
     -H 'Idempotency-Key: prueba-1' \
     -d '{"tarjeta":"4242 4242 4242 4242"}'
   ```

   Para o passo 3, use o mesmo comando com `pedidos/1`. Os demais são os da lição 06.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. Na cena, o que tinham em comum os dois erros que os testes da equipe não viram? (cena)
2. Por que esta loja responde 404, e não 403, quando outra cliente pede o seu pedido? (passo 3)
3. O que compara o teste «cobrado igual ao total», e por que não se escreve com um valor fixo? (passo 4)
4. Com E4 ligado e o gateway normal, a coleção saiu verde. Por quê? (passo 4)
5. Por que a primeira cobrança aceita 200 ou 504, mas a nova tentativa só 200? (passo 5)

---

## Para fechar

Os testes da lição 07 respondiam «funciona?». Os desta lição respondem outra pergunta: «funciona **também** quando alguém
faz o que não deve, ou faz duas vezes?». Nem o pedido alheio nem a cobrança dupla aparecem com uma cliente que compra uma
vez e vai embora; os dois aparecem assim que chega uma segunda pessoa ou uma segunda tentativa.

O que você leva daqui:

- **Cada teste importante, de novo com outra pessoa.** Sem login tem de dizer 401; com outra cliente, o que a loja decidiu
  para o que é alheio (aqui, 404), e sem mostrar o dado.
- A outra pessoa sai do **ambiente**, igual à primeira: a coleção não leva nomes.
- **Cada requisição que muda algo, duas vezes.** Uma cobrança repetida com a mesma chave de idempotência cobra uma vez e
  responde o mesmo.
- Confira o **efeito**, não só o código: `cobrado` contra `total` diz quanto se cobrou de verdade.
- Alguns erros só aparecem quando algo falha primeiro. Para testar uma nova tentativa, faça a primeira tentativa ficar
  sem resposta.

Na lição 09 o problema já não é quem nem quantas vezes, e sim **quando**: duas requisições que chegam ao mesmo tempo, e a
loja a um segundo de o dia, o mês ou o ano mudar.

---

## Compare as respostas

**Passo 3, a previsão.** 404, porque nesta loja um pedido alheio não existe para quem não o fez, e assim o Luis não fica
sabendo que o pedido existe. 403 com o porquê «sei quem você é e não deixo» também é um raciocínio correto; o que não é
correto é 401, porque o Luis fez login.

**Exercício 1.** **404** «esse pedido não existe», o mesmo da consulta: para a outra cliente o pedido não existe, nem para
vê-lo nem para cancelá-lo. O segundo teste é necessário porque o código diz o que a loja **respondeu**, não o que ela
**fez**: uma loja poderia responder 404 e cancelar mesmo assim. É a regra da lição 04 com as células vazias: confira a
mensagem e que o pedido não se mexeu.

```json
    "pm.test('cancelar alheio: código 404', () => pm.response.to.have.status(404));"
```

e em «Como ficou o pedido» você já tem `pedido pago`, que ficaria vermelho se alguém o tivesse cancelado.

**Exercício 2.** **Vermelha**, mesmo com E4 desligado: falha «nova tentativa: código 200». «pedido pago» e «cobrado
igual ao total» saem verdes, e três segundos depois `cobrado` continua em **$432.00**. Mas o pedido já tem **três
movimentos**: duas cobranças e um reembolso. Medido:

```text
primeira cobrança: 504 · nova tentativa com outra chave: 504 · na hora: pagado, cobrado $432.00, 1 cobrança · 3 s depois: cobrado $432.00, movimentos: cargo, cargo, reembolso
```

Com outra chave, a loja não tem como saber que é a mesma cobrança: para ela são duas, e o gateway cobrou duas vezes. Esta
loja percebe depois, porque a segunda cobrança chega a um pedido já pago, e a devolve sozinha (você vai ver isso na
lição 10). Para o teste tudo bate; para a Marta, não: no extrato dela aparecem duas cobranças e um reembolso. Com o E4
ligado é pior: ninguém devolve a segunda cobrança. O erro pode estar na loja **ou** em quem a chama; por isso a chave
quem gera é o cliente, uma vez por cobrança, e a repete a cada tentativa.

**Exercício 3.** **422** «essa chave de idempotência já foi usada para outro pedido». A loja não pode aprová-lo porque a
chave diz «sou a cobrança do pedido 1», e chega com o pedido 2: ou é um erro do programa que a manda, ou alguém está
reusando uma chave velha. Esta loja responde 422 porque já associou essa chave a outro pedido. O rascunho da IETF sobre
esse cabeçalho, que ainda não é um padrão, propõe 422 quando uma chave é reusada com um corpo diferente; a loja aplica a
mesma ideia à sua maneira.

**Revisão.**

1. Os dois precisavam de uma segunda vez: uma segunda pessoa (o Luis pedindo um pedido alheio) ou uma segunda tentativa (a
   Marta pagando de novo). Os testes da equipe faziam tudo com uma cliente, uma vez.
2. Porque um 403 confirma a quem pergunta que o pedido existe, e o 404 não. É uma decisão desta loja (outras APIs
   escolhem 403), e o teste confere o que a loja decidiu.
3. Compara o que o gateway cobrou (`cobrado`) com o que a cliente deve (`total`). Com um valor fixo, o teste só serviria
   para um pedido de $432.00; assim serve para qualquer um.
4. Porque com o gateway rápido a primeira cobrança teve resposta, e a nova tentativa recebeu essa mesma resposta
   guardada. O E4 só quebra o caminho da nova tentativa depois de um 504.
5. A primeira pode ficar sem resposta sem que isso seja um erro: o gateway demora. A nova tentativa, com a mesma chave,
   tem de terminar em 200 quando o gateway já resolveu a cobrança, sem uma segunda cobrança.

---

## Fontes da lição

1. OWASP, *API Security Top 10 2023*, «API1:2023 Broken Object Level Authorization» (repositório OWASP/API-Security,
   consultado em 21 de novembro de 2026). É o primeiro risco da lista: pedir um objeto alheio trocando o número dele.
   «Every API endpoint that receives an ID of an object, and performs any action on the object, should implement
   object-level authorization checks»; «Write tests to evaluate the vulnerability of the authorization mechanism.
   Do not deploy changes that make the tests fail.»
   https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
2. IETF, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-09 (rascunho de 21 de
   novembro de 2026; ainda não é um padrão publicado). «Per [RFC9110], the methods OPTIONS, HEAD, GET, PUT and
   DELETE are idempotent while methods POST and PATCH are not»; «The client is left uncertain about the status of the
   resource»; «If there is an attempt to reuse an idempotency key with a different request payload, the resource
   SHOULD reply with an HTTP 422 status code».
   https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
3. Stripe, *Idempotent requests* (documentação da API deles, consultada em 21 de novembro de 2026). «if a connection
   error occurs, you can safely repeat the request without risk of creating a second object or performing the update
   twice»; «Retries with the same key return the saved response»; «we suggest using V4 UUIDs».
   https://docs.stripe.com/api/idempotent_requests
4. Postman, *Use dynamic variables to return randomly generated data* (learning.postman.com, consultado em 21 de
   novembro de 2026). «To use dynamic variables in pre-request or post-response scripts, use
   pm.variables.replaceIn()»; «$guid A uuid-v4 style guid».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/variables-list/

Medição própria: cada saída desta lição foi medida com curl e newman 6.2.2 contra a loja do curso (hb-curso-qa, develop
13cdb22) em 21 de novembro de 2026, com a API dela no ar sem Docker e reiniciada antes de cada rodada: a coleção completa
com a Marta e com o Luis, com o gateway normal e com o gateway demorando 7 segundos (12 de 12), com E4 e o gateway lento
(2 vermelhos), com E4 e o gateway normal (12 de 12), e os três exercícios. O E5 foi medido com um protótipo em uma cópia
da loja, enquanto se constrói o de verdade.

Regras do curso, sem fonte externa:

- «Cada teste importante, de novo com outra pessoa»: o erro de permissões não se vê com a dona do dado; só aparece quando
  pergunta outra pessoa.
- «Para testar uma nova tentativa, faça a primeira tentativa ficar sem resposta»: com o gateway rápido, a cobrança dupla
  não se vê.
