# Lição 07 — Testes de API que rodam sozinhos

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Coleção:** um arquivo que guarda as suas requisições à API, em ordem, cada uma com os seus testes.
- **Teste (em uma coleção):** uma linha que confere uma parte da resposta e diz «passa» ou «não passa».
- **newman:** o programa que lê a sua coleção, manda as requisições dela à loja e te diz quais testes passaram.
- **Ambiente:** um arquivo à parte com os dados que mudam de uma máquina para outra: o endereço da loja, a cliente
  e a senha dela.

**O que fica com você:** uma coleção que testa uma compra da loja com um único comando, que sai verde quando a
loja está certa e vermelha quando ela tem o erro do frete, e que roda igual com outra cliente sem ser tocada.

**Ideia nova desta lição (a única):** um teste guardado, que se repete com um comando, volta a rodar toda vez sem
depender de que alguém se lembre dele.

**Em que ordem vai:** você guarda a sua primeira requisição com um teste e a roda (passo 1), pede que ela confira as
três partes da resposta (passo 2), ensina-a a fazer login e a lembrar o token (passo 3), faz com que ela pegue o erro
do frete (passo 4) e tira os dados da coleção para um ambiente, para rodá-la com outra cliente (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e o erro da loja são reais.*

Na terça, depois da reclamação do frete, o QA fez as coisas direito: mandou a requisição do carrinho com `curl`, leu
o código, os cabeçalhos e o corpo, e encontrou os $99.00 (pesos mexicanos). A equipe corrigiu na quarta. O QA repetiu a
requisição, leu o corpo e viu $0.00.

Três semanas depois alguém muda o cálculo dos descontos. Ninguém mexe no frete, ou pelo menos é o que acham. Ninguém
repete a requisição da terça, porque ela estava em um terminal que já foi fechado e na memória de uma pessoa que
naquele dia estava ocupada com outra coisa.

A cliente volta a escrever.

O que o QA fez na terça foi um **teste manual**, e bem feito. O limite dele é que não ficou guardado: para repeti-lo,
alguém tinha de se lembrar dele e montá-lo de novo. Um **teste automatizado** é esse mesmo teste guardado em um
arquivo, que qualquer pessoa roda de novo com um comando, quando quiser, e que diz sozinho se continua certo. Esta
lição transforma as suas requisições da lição 06 em testes automatizados.

---

## Antes de começar

**Você precisa da loja no ar.** Como na lição 00: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra janela,
o terminal da loja. Tudo se faz **lá dentro**, no terminal da loja, que já te deixa na sua pasta `~/practica`. O que
você guardar ali continua ali mesmo que você desligue a loja.

**Você não instala nada.** O newman já vem na loja. Confira:

```bash
newman --version
```

Ele tem de te responder `6.2.3`.

**Para escrever os arquivos** você usa o `nano`, o editor que também vem na loja: `nano nome-do-arquivo` o abre (ou o
cria), você escreve ou cola, salva com `Ctrl+O` e Enter, e sai com `Ctrl+X`.

**Faça o passo 3 sem IA.** O que você treina ali é prever o código do login, com o porquê dele, antes de rodá-lo:
é isso que depois te deixa saber o que cada teste tem de conferir e por quê.

**O que você já sabe e vai usar:** da lição 06, as três partes de uma resposta, o 201 do login, o token e o carrinho
de $999.00 com E1; da 00, `./practicar` no seu computador; da 06, `tienda reiniciar` para começar limpo e
`tienda error E1 on|off` para ligar e desligar o E1 pelo terminal da loja.

**Comece limpo antes de cada rodada.** A coleção supõe uma loja recém-aberta: se o seu carrinho traz produtos de antes,
os valores não batem. Antes de cada `newman run`, rode:

```bash
tienda reiniciar
```

Você não precisa fazer login à mão: a partir do passo 3, a coleção o faz sozinha.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · A sua primeira requisição guardada

Na lição 06 você pediu a camiseta azul com `curl -i` e leu a resposta. Agora você vai guardar essa mesma requisição
em um arquivo, com um teste que confere o código por você.

Uma coleção é um arquivo de texto em um formato chamado **JSON**: chaves `{ }`, nomes entre aspas e valores. O newman
entende o formato das coleções do Postman, uma ferramenta muito usada para testar APIs. Você não precisa decorá-lo:
vai copiar o esqueleto e mudar só o que está dentro.

Crie o arquivo:

```bash
nano tienda.postman_collection.json
```

E escreva isto:

```json
{
 "info": {
  "name": "Loja",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "A camiseta azul existe",
   "request": {
    "method": "GET",
    "url": "http://localhost:8080/api/productos/playera-azul"
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));"
      ]
     }
    }
   ]
  }
 ]
}
```

Leia de cima para baixo:

| Parte | O que diz |
|---|---|
| `info` | O nome da coleção e o formato. Nesta lição, o `schema` se copia tal qual |
| `item` | A lista de requisições, na ordem em que vão ser mandadas. Hoje tem uma |
| `request` | A requisição: o método e o endereço. É o mesmo que você dizia ao `curl` |
| `event` → `test` | O que roda **depois** que a resposta chega: os seus testes |
| `pm.test('código 200', …)` | Um teste. Entre aspas, o nome dele; depois da seta, o que ele confere |

A linha do teste se lê assim: «um teste que se chama *código 200* e que espera que a resposta tenha o código 200».
`pm` é a caixa de ferramentas que o newman empresta aos seus testes; `pm.response` é a resposta que chegou.

Salve, saia e rode:

```bash
newman run tienda.postman_collection.json
```

Você vai ver algo assim (os seus tamanhos e tempos mudam; o resto tem de coincidir):

```text
newman

Loja

→ A camiseta azul existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 264B, 12ms]
  ✓  código 200
```

E embaixo, uma tabela com o resumo. A linha que importa é `assertions`, as conferências: `1` executada e `0` com
falha.

Esse visto `✓` é o que você vai procurar daqui em diante. O que na lição 06 você lia, agora o newman confere.

> **Se o newman reclamar de uma vírgula ou de uma chave:** o JSON é estrito. Cada `{` fecha com o seu `}`, cada `[`
> com o seu `]`, e entre dois elementos de uma lista vai uma vírgula, mas **depois do último não**. Quase todos os
> erros do primeiro dia são uma vírgula a mais ou a menos. Antes de rodar, confira com o `jq`, que também vem na
> loja:
>
> ```bash
> jq empty tienda.postman_collection.json
> ```
>
> Se ele não imprimir nada, o JSON está bem escrito. Se algo falhar, ele te diz a linha e a coluna onde se perdeu.

---

## Passo 2 · Que ela confira as três partes

Um teste que só olha o código tem o mesmo problema do QA da segunda-feira da lição 06: um 200 diz que a loja
respondeu, não que respondeu certo. Acrescente mais dois testes à mesma requisição, um para o corpo e um para um
cabeçalho.

Abra o arquivo de novo e deixe a lista `exec` assim:

```json
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.test('chama-se Camiseta azul', () => pm.expect(pm.response.json().nombre).to.eql('Camiseta azul'));",
       "pm.test('responde em JSON', () => pm.expect(pm.response.headers.get('content-type')).to.include('application/json'));"
      ]
```

Cada teste é uma linha entre aspas, separada da seguinte por uma vírgula. Os dois novos:

| Teste | Que parte confere | Como se lê |
|---|---|---|
| `chama-se Camiseta azul` | O **corpo** | Lê o corpo como JSON, pega o `nombre` dele e espera que seja igual a `'Camiseta azul'` |
| `responde em JSON` | Um **cabeçalho** | Pega o cabeçalho `content-type` e espera que ele **inclua** `application/json` |

`pm.expect(algo).to.eql(outra coisa)` é a forma geral: «espero que *algo* seja igual a *outra coisa*». Com ela você
confere qualquer dado do corpo.

Rode de novo:

```bash
newman run tienda.postman_collection.json
```

```text
→ A camiseta azul existe
  GET http://localhost:8080/api/productos/playera-azul [200 OK, 264B, 12ms]
  ✓  código 200
  ✓  chama-se Camiseta azul
  ✓  responde em JSON
```

Três vistos, um para cada parte da resposta: código, corpo e cabeçalho.

---

## Passo 3 · Fazer login e lembrar o token

Para encher um carrinho você precisa fazer login, como na lição 06. Ali você copiava o token à mão e o guardava em
`TOKEN`. Em uma coleção, a requisição do login o guarda sozinha para as que vêm depois.

**Antes de escrevê-la, preveja** (sem IA, sem voltar à lição 06): com que código a loja responde quando você faz
login direito? Escreva em um papel.

Agora acrescente uma segunda requisição à lista `item`. Procure a chave `}` que fecha a primeira requisição (é a que
está logo antes do `]` do final), escreva uma **vírgula** depois dela e cole isto:

```json
  {
   "name": "Faça login",
   "request": {
    "method": "POST",
    "url": "http://localhost:8080/api/sesiones",
    "header": [
     {"key": "Content-Type", "value": "application/json"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cliente\":\"Marta\",\"contrasena\":\"marta-practica\"}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.collectionVariables.set('token', pm.response.json().token);"
      ]
     }
    }
   ]
  }
```

O que há de novo:

- **`header`** é o que com o `curl` você escrevia com `-H`, e **`body`** o que você escrevia com `-d`. As aspas de
  dentro levam uma barra invertida (`\"`) porque o corpo vai dentro de outro texto entre aspas.
- **`pm.collectionVariables.set('token', …)`** guarda o token da resposta em uma variável da coleção chamada `token`.
  Qualquer requisição que venha depois pode usá-lo escrevendo `{{token}}`.

O teste diz 200 de propósito, para comparar uma previsão com a evidência. Antes de rodar, confira o seu papel.
`tienda reiniciar` e rode:

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Faça login
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 4ms]
  1. código 200
```

Onde ia um visto há um número: o teste falhou. Lá embaixo, o newman explica a falha 1:

```text
 1.  AssertionError  código 200
                     expected response to have status code 200 but got 201
```

«Esperava 200 e chegou 201.» Se no seu papel você escreveu 201, acertou: fazer login **cria** uma sessão, e a norma do
HTTP diz que 201 é «deu certo e algo novo foi criado» (lição 06, passo 3). Se você escreveu 200, agora sabe por que se
prevê antes: sem o seu papel, este vermelho teria sido lido como «a loja está errada», e a que estava errada era o
teste.

Corrija o teste para 201:

```json
       "pm.test('código 201', () => pm.response.to.have.status(201));",
```

Rode de novo depois de `tienda reiniciar`. Agora sai `✓  código 201`.

> **Um vermelho nem sempre é um erro da loja.** Antes de reportá-lo, pergunte-se quem tem razão: a loja ou o seu
> teste. É para isso que serve ter previsto com um porquê, e não só com um número.

---

## Passo 4 · Que ela pegue o erro do frete

Agora, a requisição que importa: três camisetas de $333.00, um carrinho de $999.00, que pela regra tem frete grátis.
Acrescente uma terceira requisição igual à segunda: uma vírgula depois da `}` que fecha o login, e isto:

```json
  {
   "name": "Carrinho de $999.00",
   "request": {
    "method": "PUT",
    "url": "http://localhost:8080/api/carrito/productos/playera-azul",
    "header": [
     {"key": "Content-Type", "value": "application/json"},
     {"key": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": {
     "mode": "raw",
     "raw": "{\"cantidad\":3}"
    }
   },
   "event": [
    {
     "listen": "test",
     "script": {
      "exec": [
       "pm.test('código 200', () => pm.response.to.have.status(200));",
       "pm.test('subtotal $999.00', () => pm.expect(pm.response.json().subtotal.texto).to.eql('$999.00'));",
       "pm.test('frete grátis', () => pm.expect(pm.response.json().envio.texto).to.eql('$0.00'));"
      ]
     }
    }
   ]
  }
```

`Bearer {{token}}` é o token que a requisição anterior guardou. Por isso **a ordem da lista importa**: se esta
requisição fosse a primeira, ainda não haveria token e a loja responderia 401.

Por que conferir o subtotal e o frete separadamente? Porque, se algo sair vermelho, você quer saber **o quê**. Se você
conferisse só o total, um vermelho não te diria se falhou o preço, a quantidade ou o frete.

**Com E1 desligado:**

```bash
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Carrinho de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 543B, 2ms]
  ✓  código 200
  ✓  subtotal $999.00
  ✓  frete grátis
```

Na tabela do resumo, `assertions`: 7 executadas, 0 com falha.

**Agora ligue o E1** (no seu computador, `./practicar error E1 on`; ou lá dentro, `tienda error E1 on`) e rode igual:

```bash
tienda error E1 on
tienda reiniciar
newman run tienda.postman_collection.json
```

```text
→ Carrinho de $999.00
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 550B, 2ms]
  ✓  código 200
  ✓  subtotal $999.00
  1. frete grátis
```

E embaixo:

```text
 1.  AssertionError  frete grátis
                     expected '$99.00' to deeply equal '$0.00'
```

É a mesma borda de $999.00 da cena da lição 06: lá você chegava com o cupom; aqui, com três camisetas. O código
continua sendo 200 e o subtotal está certo. A única coisa que mudou é o frete, e a sua coleção o apontou sem que
ninguém lesse o corpo.

**O sim ou não, para uma máquina.** Logo depois de rodar o newman, escreva:

```bash
echo $?
```

`$?` é o **código de saída** do último programa: um número que todo programa deixa ao terminar. Nas rodadas desta
lição, o newman terminou em **0** quando todos os testes passaram e em **1** quando algum falhou. Com E1 ligado ele te
responde `1`; desligue-o, comece limpo, rode de novo e ele te responde `0`.

Esse número é o que deixa **outro programa** ler o resultado sem que ninguém olhe a tela. Um servidor que roda os
testes toda vez que alguém muda o código (na indústria se chama **integração contínua**) pode rodar a sua coleção e
olhar esse número. O que ele faz com um 1 cada equipe decide: marcar a mudança como falha, avisar ou impedir que ela
seja integrada. Em qualquer caso, ninguém precisa se lembrar da requisição da terça.

Antes de seguir, desligue o E1:

```bash
tienda error E1 off
```

---

## Passo 5 · Tirar os dados para um ambiente

A sua coleção funciona, mas tem escritas à mão três coisas que não são do teste e sim **da sua máquina**: o endereço
`http://localhost:8080`, a cliente `Marta` e a senha dela. Se alguém a rodar contra a loja de um colega, com outro
endereço ou com outra cliente, tem de editá-la, e um teste que precisa ser editado para rodar já não roda sozinho.

A solução é separar: **a coleção diz o que se testa; o ambiente diz onde e com quem.**

**1. Crie o ambiente** `local.postman_environment.json`:

```bash
nano local.postman_environment.json
```

```json
{
 "name": "local",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Marta"},
  {"key": "contrasena", "value": "marta-practica"}
 ]
}
```

Três variáveis: `base` (o endereço da loja), `cliente` e `contrasena`.

**2. Mude a coleção para que ela as use.** Nas três requisições, troque `http://localhost:8080` por `{{base}}`. No
corpo do login, troque `Marta` por `{{cliente}}` e `marta-practica` por `{{contrasena}}`:

```json
    "url": "{{base}}/api/productos/playera-azul"
```

```json
    "url": "{{base}}/api/sesiones",
```

```json
     "raw": "{\"cliente\":\"{{cliente}}\",\"contrasena\":\"{{contrasena}}\"}"
```

```json
    "url": "{{base}}/api/carrito/productos/playera-azul",
```

As chaves duplas `{{ }}` dizem ao newman: «aqui vai o valor desta variável». Quando você rodar, ele o pega do
ambiente.

**3. Rode-a com o ambiente**, com `-e`:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Os mesmos sete vistos do passo 4. Não mudou nada do que se testa; mudou de onde saem os dados.

**4. A prova de que você separou direito.** Faça um segundo ambiente com a outra cliente de prática, o Luis:

```bash
nano luis.postman_environment.json
```

```json
{
 "name": "luis",
 "values": [
  {"key": "base", "value": "http://localhost:8080"},
  {"key": "cliente", "value": "Luis"},
  {"key": "contrasena", "value": "luis-practica"}
 ]
}
```

E rode **a mesma coleção, sem tocá-la**:

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e luis.postman_environment.json
```

Sete vistos de novo, agora como o Luis. Esse é o sinal de que a sua coleção ficou bem separada: para trocar de cliente
você só trocou o arquivo de ambiente. Os dois ambientes apontam para a mesma loja; para rodar a coleção contra a loja
de outra máquina, você faria um ambiente com a **dela** `base`, e a coleção também não seria tocada.

> **O ambiente separa os dados; não os protege.** A senha vai no ambiente porque muda de uma pessoa para outra, não
> porque ali ela fique a salvo: o ambiente também é um arquivo de texto que pode ser compartilhado. Aqui as senhas
> são de prática. Em um trabalho real, uma senha não se escreve nem na coleção nem em um ambiente compartilhado: ela
> se guarda no cofre de segredos que a sua equipe usar.

---

## Como se confere

**A sua coleção e o seu ambiente** são revisados pelo `verifica 07`. Salve-os em `~/practica` como
`tienda.postman_collection.json` e `local.postman_environment.json` e, no terminal da loja, escreva:

```bash
verifica 07
```

O `verifica`:

1. roda a sua coleção com o seu ambiente e a loja limpa: tem de sair **verde**;
2. roda-a com E1 ligado: **pelo menos um teste tem de sair vermelho**; se sair verde, a sua coleção não estava olhando
   o frete;
3. roda-a com um ambiente que ele mesmo monta, com o Luis, e confere que a sua coleção fez login **como o Luis**;
4. confere que nenhuma requisição tenha escritos à mão o endereço, `Marta` ou a senha dela.

Se faltar algo, ele diz qual requisição e o que arrumar. Antes de rodá-lo, a lista abaixo diz se a forma está certa.

**Antes de dar a lição por terminada, confira:**

- [ ] A sua coleção tem três requisições nesta ordem: o produto, o login e o carrinho.
- [ ] Com E1 desligado, `newman run … -e local.postman_environment.json` termina com 0 falhas e `echo $?` dá `0`.
- [ ] Com E1 ligado, falha «frete grátis» e `echo $?` dá `1`.
- [ ] Com `-e luis.postman_environment.json` sai verde sem ter tocado a coleção.
- [ ] Na sua coleção não aparecem `localhost`, `Marta` nem `marta-practica` (procure-os com
      `grep -n -e localhost -e Marta -e marta-practica tienda.postman_collection.json`; não pode imprimir nada.
      Se não imprimir nada, ele encontrou o esperado: aqui o `echo $?` dele dá 1, que no `grep` quer dizer «sem
      coincidências»).
- [ ] Você deixou o E1 desligado (`./practicar error estado` confirma).

---

## Seus exercícios

1. **Uma requisição que deve falhar.** Acrescente ao final da coleção, como no passo 3 (uma vírgula depois da `}` da
   última requisição), uma quarta requisição que peça os seus pedidos **sem**
   token: `GET {{base}}/api/pedidos`, sem cabeçalho `Authorization`. Antes de rodá-la, preveja o código e escreva
   dois testes: um para o código e um para o cabeçalho que, segundo a lição 06, tem de acompanhá-lo. Uma requisição
   que espera um erro também é um teste: se algum dia a loja deixar ver os pedidos sem login, este teste fica
   vermelho.
2. **O cupom sobre o carrinho de $999.00.** Acrescente, da mesma forma, uma quinta requisição que aplique o
   BIENVENIDA10 ao carrinho do passo 4 (`POST {{base}}/api/carrito/cupon`, com o token e o corpo
   `{"codigo":"BIENVENIDA10"}`). Antes de escrever os testes, preveja com E1 **desligado**: quanto de desconto?,
   quanto de frete?, por quê? Escreva um teste para o desconto e outro para o frete, e rode. Se a sua previsão do
   frete não coincidir com o que chega, volte à regra do frete da lição 02 e decida quem tem razão antes de corrigir
   qualquer coisa.
3. **A armadilha da cliente escrita à mão.** Faça uma cópia da sua coleção (`cp tienda.postman_collection.json
   copia.json`) e, na cópia, volte a escrever `Marta` e `marta-practica` no corpo do login. Rode-a com o ambiente do
   Luis. Preveja primeiro: verde ou vermelha? Depois responda em três linhas: de quem é o carrinho que se encheu?,
   por que o resultado do newman não te disse?, e o que um teste teria de conferir para perceber? Ao terminar,
   apague a cópia com `rm copia.json`.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. O que faltava ao teste manual da terça para se repetir sem depender de ninguém? (cena)
2. Em `pm.test('frete grátis', …)`, o que é `'frete grátis'` e para que serve ele ter um bom nome? (passo 1)
3. Por que a requisição do carrinho tem de vir depois do login? (passo 4)
4. Que código de saída o newman deixa quando um teste falha, e quem o usa? (passo 4)
5. O que vai na coleção e o que vai no ambiente? (passo 5)

---

## Para fechar

O que o QA fez na terça continua sendo necessário: alguém tem de ler a resposta completa na primeira vez, entender a
regra e decidir o que conferir. O que muda com uma coleção é que essa leitura se guarda. A pessoa seguinte, ou o
servidor de integração, a repete sem reconstruí-la de memória.

O que você leva daqui:

- Uma **coleção** guarda requisições em ordem, cada uma com os seus **testes**; `newman run` a roda.
- Cada teste confere **uma** coisa e tem um nome que diz qual. Confira as três partes: código, corpo e
  cabeçalhos.
- `pm.collectionVariables.set` guarda um dado de uma resposta, como o token, para as requisições seguintes; por isso
  a ordem importa.
- Nesta lição, o newman terminou em **0** se tudo passou e em **1** se algo falhou; esse número é o que a integração
  contínua pode ler.
- **A coleção diz o que se testa; o ambiente diz onde e com quem.** Se a sua coleção roda com outro ambiente sem ser
  tocada, está bem separada.
- Um vermelho pode ser da loja ou do seu teste: preveja com um porquê para saber qual.

Na lição 08 você monta uma segunda coleção com os mesmos ambientes: testes com outra cliente, sem login e com uma
cobrança que se repete, para ver o que acontece quando alguém faz o que não deve ou faz duas vezes.

---

## Compare as respostas

**Passo 3, a previsão.** 201. Fazer login cria uma sessão nova, e 201 é «deu certo e algo foi criado». Se você
escreveu 200 com o porquê «deu certo», o porquê não estava errado, mas faltava distinguir entre «deu certo» e «deu
certo e algo foi criado».

**Exercício 1.** **401**, e o cabeçalho `www-authenticate: Bearer`. Medido:

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer

{"mensaje":"faça login primeiro"}
```

Uns testes que servem:

```json
       "pm.test('código 401', () => pm.response.to.have.status(401));",
       "pm.test('pede token', () => pm.response.to.have.header('www-authenticate', 'Bearer'));"
```

Se você conferiu também a mensagem do corpo, melhor: é a terceira parte.

**Exercício 2.** Com E1 desligado: código 200, desconto **$99.90** (10 % de $999.00) e frete **$99.00**; total
$998.10. O frete **não** é grátis porque o frete grátis se calcula sobre o que sobra **depois** do desconto:
$999.00 − $99.90 = $899.10, menos que $999.00. É a mesma regra da lição 05, em que o carrinho de $1,110.00 com cupom
ficava em $999.00 certinhos e sim tinha frete grátis. Se você previu $0.00, a loja tinha razão e o seu teste não: é o
caso do passo 3 de novo.

```json
       "pm.test('desconto $99.90', () => pm.expect(pm.response.json().descuento.texto).to.eql('$99.90'));",
       "pm.test('frete $99.00', () => pm.expect(pm.response.json().envio.texto).to.eql('$99.00'));"
```

**Exercício 3.** **Verde**: os sete testes passam. O carrinho que se encheu é o da **Marta**; o do Luis ficou vazio.
O newman não disse porque nenhum teste conferia **de quem** era o carrinho: todos olhavam valores, e os valores são
iguais para qualquer cliente. Para perceber, um teste teria de conferir algo que dependa da cliente (por exemplo,
pedir o carrinho com a sessão do Luis e ver que ele tem as três camisetas), ou revisar a coleção e não encontrar ali
nenhum nome. O `verifica 07` faz as duas coisas.

**Revisão.**

1. Ficar guardado: um teste automatizado vive em um arquivo, se repete com um comando e diz sozinho se continua certo.
   O da terça dependia de que alguém se lembrasse dele e o montasse de novo.
2. É o nome do teste. Quando ele falha, é a primeira coisa que você lê («1. frete grátis»), então tem de te dizer
   que regra se quebrou sem abrir o arquivo.
3. Porque precisa do token, e o token quem guarda é a requisição do login. Se ela viesse antes, `{{token}}` estaria
   vazio e a loja responderia 401.
4. 1, nas rodadas desta lição. Qualquer programa que rode a sua coleção pode lê-lo, por exemplo o servidor de
   integração contínua; o que ele faz com isso cada equipe decide.
5. Na coleção, as requisições e o que cada teste espera; no ambiente, o endereço da loja, a cliente e a senha dela.

---

## Fontes da lição

1. Postman, *newman — the cli companion for postman*, README do repositório postmanlabs/newman (consultado em 21 de
   novembro de 2026). «Newman is a command-line collection runner for Postman. It allows you to effortlessly run and
   test a Postman collection directly from the command-line»; «-e <source>, --environment <source>: Specify an
   environment file path or URL. Environments provide a set of variables that one can use within collections».
   https://github.com/postmanlabs/newman
2. Postman, *Write post-response scripts to test API response data* (learning.postman.com, consultado em 21 de
   novembro de 2026). «Define tests using the pm.test function»; «Use Chai.js BDD syntax and pm.expect in your
   assertions to test the response detail»; «Post-response scripts can use dynamic variables, carry out test
   assertions on response data, and pass data between requests».
   https://learning.postman.com/docs/tests-and-scripts/write-scripts/test-scripts/
3. Postman, *Store and reuse values using variables* (learning.postman.com, consultado em 21 de novembro de 2026).
   «A variable is a symbolic representation of data that enables you to access a value without having to enter it
   manually wherever you need it»; «Environment variables enable you to scope your work to different environments,
   such as local development versus testing or production environments»; «Collection variables are available
   throughout the requests in a collection and are independent of environments».
   https://learning.postman.com/docs/sending-requests/variables/variables/

Medição própria: cada saída desta lição foi medida com o newman 6.2.2 contra a loja do curso (HabilMX/curso-qa) em 21 de novembro de 2026, com a API dela no ar sem Docker e depois de reiniciá-la a cada rodada: a
coleção completa com a Marta e com o Luis (7 de 7 testes verdes, código de saída 0), com E1 ligado (1 vermelho, «frete
grátis», código de saída 1), o teste do login escrito com 200, e os três exercícios. A imagem da loja traz newman
6.2.3.

Regras do curso, sem fonte externa:

- «Um teste, uma coisa»: cada `pm.test` confere um único dado, para que um vermelho diga o que se quebrou.
- «Comece limpo antes de cada rodada»: a coleção supõe uma loja recém-aberta; com dados de antes, os valores
  mudam e o vermelho não diz nada da regra.
