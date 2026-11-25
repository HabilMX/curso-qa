# Lição 00 — Sua loja de prática

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, quatro palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **API:** a porta pela qual um programa pede coisas a outro. A página da loja não guarda os produtos,
  o carrinho nem os pedidos: ela os pede à API da loja.
- **Requisição e resposta:** cada vez que a página precisa de algo, manda uma **requisição** à API («me dê o
  carrinho») e a API devolve uma **resposta** («aqui está: uma camiseta, $333.00 (pesos mexicanos)»).
- **Código de status:** o número de três dígitos que acompanha cada resposta e diz como foi a requisição. 200
  é «deu certo»; 401, «não sei quem você é».
- **Falha:** o que se vê dar errado: uma cobrança em dobro, um pedido que não chega. O **defeito** é a causa, e pode
  estar no código, em uma regra mal escrita, em um dado ou na configuração. Como QA, você parte da falha e
  procura a causa.

**O que fica com você:** a sua loja de prática funcionando no seu computador; você sabe conferir que a API e a página
respondem; percorre uma compra completa à mão anotando que tela vê e que requisição a página manda em cada
passo; e consegue explicar o que custa a uma loja que falhe a cobrança, o estoque ou a entrega.

**Ideia nova desta lição (a única que se avalia):** antes de testar, conhece-se o sistema: o que ele faz, quem o
usa e o que acontece se falhar. Assim você sabe onde olhar primeiro.

**Em que ordem vai:** você sobe a loja (passo 1), confere que a API e a página respondem (passo 2), faz uma
compra olhando o que acontece por baixo (passo 3), deixa o `verifica` conferir (passo 4) e pensa no que custaria
se algo disso falhasse (passo 5).

**Quanto tempo:** uns 60 minutos, mais o que a imagem demorar na primeira vez (estimativa; vamos ajustá-la com a primeira
turma de alunos).

---

## A cena

*Cenário inventado; as telas e respostas da loja que aparecem na lição são reais.*

Segunda-feira, 9:05. Andrea começa hoje como QA em uma loja de roupas online. Dão a ela um notebook, um acesso e uma frase:
«na sexta saiu uma versão nova; confira se está tudo bem».

Ela abre a página. Vê camisetas, um carrinho e um botão que diz «Pagar». Clica em coisas. Tudo parece funcionar.

Às 11:40 chega um e-mail do atendimento ao cliente. Uma cliente pagou uma única vez e no extrato dela aparecem
**duas cobranças**. Às 12:10, outro. Às 12:30, a chefe de Andrea pergunta o que ela testou.

Andrea testou o que se via. Mas a cobrança em dobro não se vê na tela: acontece **por baixo**, na conversa entre
a página e a API, quando o pagamento demora e a página o pede de novo. Para encontrá-la, primeiro era preciso saber
que essa conversa existe, o que elas dizem uma à outra, e por que uma cobrança em dobro custa mais que um botão desalinhado.

Esta lição te dá isso em uma loja feita para errar: a sua, de prática. Ela traz erros plantados de
propósito, e um deles se parece muito com o da segunda-feira de Andrea. Hoje você ainda não o procura: hoje você conhece a loja.

---

## Antes de começar

**O que você precisa:**

| | O quê | Notas |
|---|---|---|
| Curso anterior | «O terminal do zero», lições 00 a 02, ou saber se mover no terminal sem ajuda | Ali você instalou o Docker e aprendeu a entrar e sair de um terminal de prática |
| Docker | Instalado e respondendo | Se você não o tem, abaixo diz como |
| Navegador | Chrome ou Firefox, no seu computador | Para ver a página e o que ela manda por baixo |
| Disco | Uns 1.3 GB para a imagem | Traz a loja e tudo o que você vai usar no curso para testá-la |
| Rede | Para baixar a imagem base e as ferramentas na primeira vez | Depois, a loja roda sem internet |

**Onde foi testado, e onde falta:**

| Sistema | Estado | O que foi rodado |
|---|---|---|
| Linux x86_64, Docker 29 | Testado em 21/11/2026 por quem construiu a loja | Construir a imagem, subir a loja, `verifica 00` em vermelho sem compra e em verde com uma compra paga |
| Mac (Apple silicon ou Intel) | Ainda não testado | O script `practicar` distingue o Mac ao explicar erros do Docker |
| Windows com WSL 2 | Ainda não testado | Tudo se roda no terminal do Linux do WSL, não no PowerShell |

Se você testar em um dos que faltam, conte-nos como foi.

**As cifras desta lição, e como foram medidas:**

| Cifra | Como foi medida |
|---|---|
| Imagem: uns 1.3 GB | Linux x86_64, 21/11/2026, uma execução, por quem construiu a loja (consta no README do curso) |
| Construir a imagem na primeira vez: uns 2 minutos | A mesma execução; depende da sua rede e do seu computador |
| Subir a loja já construída: uns 2 segundos | A mesma execução |
| Carrinho de uma camiseta azul: $333.00 + $99.00 de frete = $432.00 | Rodando a loja do curso em 21/11/2026 |

**Se você não tem o Docker.** Se você fez «O terminal do zero», já o tem: vá para o passo 1. Se não, a
[lição 00](https://www.habil.mx/pt/cursos/terminal/00-tu-terminal-de-practica/) dele explica como instalá-lo em Linux,
Mac e Windows, e a [lição 1 do curso de Docker](https://www.habil.mx/pt/cursos/docker/01-instalacion/) faz isso
passo a passo no Linux. Para saber se ele responde, rode no terminal do seu computador:

```bash
docker version
```

Está tudo certo se você vir dois blocos, `Client` e `Server`, cada um com a sua versão.

---

## Passo 1 · Suba a loja e entre

**Preveja primeiro.** Escreva em um papel: quando você rodar o comando, onde a loja vai ficar? Em uma janela
nova? Na internet? Em outro lugar?

No terminal do seu computador, entre na pasta do curso (a que você baixou do repositório dele; com `ls` você deve
ver o arquivo `practicar`) e rode:

```bash
TIENDA_IDIOMA=pt ./practicar
```

Essa variável, `TIENDA_IDIOMA=pt`, coloca a loja no seu idioma (a página também tem um seletor de idioma no alto, à direita). `practicar` é um script do curso, como o do terminal. Na primeira vez ele constrói a imagem: baixa o Python e
coloca a loja nele, junto com as ferramentas que você usará mais adiante (behave, curl, newman e um navegador sem
janela). Ele avisa antes de começar:

```text
Construindo a imagem «curso-qa-tienda». Na primeira vez baixa Python, Node e um navegador sem janela:
pode levar vários minutos. O que já estava construído é reaproveitado.
```

Você verá passar muito texto e, no final, isto:

```text
✅ Imagem pronta.
✅ A loja está no ar: http://localhost:8080
Entrando no terminal da loja. Para sair, digite  exit  (ou Ctrl+D).
🛒 Tienda de práctica: http://localhost:8080  ·  ayuda: tienda --help  ·  tu avance: verifica NN
```

Esse último letreiro sai em espanhol seja qual for o idioma que você escolheu: a imagem o imprime assim para todos.

Leia as linhas em ordem. A segunda é a que importa hoje: **a loja está no ar**, em um endereço do seu próprio
computador. `localhost` quer dizer «este mesmo computador», e `8080` é a **porta**, o número da porta
por onde se entra na loja. Compare com o que você previu: ela não ficou na internet. O script a publica só para o seu
computador; a documentação do Docker explica assim: se ao publicar uma porta se inclui o endereço
`127.0.0.1`, só o seu próprio computador consegue entrar nela.

A última linha já é de **dentro**: você está no terminal da loja, um contêiner com tudo do curso. Ali
você trabalha como `alumno`, na sua pasta `~/practica`, que fica guardada mesmo que você saia.

Rode o seu primeiro comando lá dentro:

```bash
verifica 00
```

Deve sair assim:

```text
Verificando a lição 00…

✅ A API da loja responde em /api/salud
✅ A página da loja carrega
❌ Marta tem um pedido pago
   → Entre na página como Marta (senha: marta-practica), adicione algo ao carrinho e pague.

Ainda falta algo: corrija e rode de novo  verifica 00
```

Dois verdes e um vermelho. O vermelho é normal: é a compra que você faz no passo 3. Repare em algo que você vai ver em todo
o curso: o `verifica` **pergunta à loja**. Para saber se você comprou, ele confere se o pedido existe e está pago.
Assim você e o curso olham a mesma evidência.

**Isto demonstra** (objetivo 0.1, primeira metade): as duas marcas verdes.

---

## Passo 2 · Confira que a API e a página respondem

O `verifica` já disse que sim. Agora confira você mesmo, porque em QA você vai fazer isso centenas de vezes: antes de procurar um
erro, você se assegura de que o sistema está no ar. Se não estiver, qualquer teste falha, e não pelo erro que
você procurava.

**A API, por dentro.** No terminal da loja:

```bash
curl http://localhost:8080/api/salud
```

O `curl` é um programa que manda uma requisição e te mostra a resposta tal qual. Você vai vê-lo de perto na lição 06;
hoje basta lê-la:

```json
{"estado":"arriba","hora_de_la_tienda":"2026-11-21T20:27:25-06:00"}
```

Dois dados: a loja diz que está **no ar** (`arriba`) e que horas são para ela. A sua será a do seu momento. Essa hora você pode
mudar mais adiante para testar coisas como um cupom que vence à meia-noite, e por isso a loja a informa.

**A página, a partir do seu computador.** Abra o navegador em <http://localhost:8080>. Você deve ver no alto «Loja de
prática», uma linha que diz que a loja é inventada e tem erros de propósito, um seletor de idioma à
direita e, no meio, um quadro «Entre na loja» com dois campos: **Cliente** (já diz Marta) e **Senha**. Se
no alto à direita você já vir o carrinho e «Meus pedidos», comece mesmo assim pelo quadro: esses botões só funcionam
depois que você entra.

**O mapa da API.** Abra também <http://localhost:8080/docs>. É a documentação da API, que a loja monta
sozinha a partir do seu código: cada rota, o que ela recebe e o que devolve. A loja é feita com FastAPI, uma
ferramenta para construir APIs que monta essa página em `/docs` se não lhe disserem outra coisa. Você não precisa lê-la
inteira: olhe os títulos dos grupos (sessão, catálogo, carrinho, pedidos) e volte aqui. É um mapa que você vai
consultar sempre.

> **Se você usa outra porta.** Se ao subir a loja você usou `TIENDA_IDIOMA=pt TIENDA_PUERTO=8081 ./practicar` (abaixo, em «Não está rodando?»,
> diz quando), no seu navegador troque `8080` por `8081`. Dentro do terminal da loja o endereço
> continua sendo `http://localhost:8080`: a porta que muda é a do seu computador, não a de dentro.

**Isto demonstra** (objetivo 0.1, segunda metade): a resposta de `/api/salud` e a página aberta no seu navegador.

---

## Passo 3 · Faça uma compra olhando o que acontece por baixo

Aqui está o coração da lição. Você vai comprar como Marta, a cliente de teste, e em cada tela vai anotar
**o que viu** e **que requisição a página mandou**. É o que faltou a Andrea.

### Abra a janela que mostra a conversa

Os navegadores trazem ferramentas para desenvolvedores, e uma delas registra cada requisição que a página manda.

- **Chrome:** pressione Ctrl+Shift+J (no Mac, Command+Option+J). O console se abre; clique na aba
  **Network** (Rede).
- **Firefox:** pressione Ctrl+Shift+E (no Mac, Cmd+Opt+E). Abre-se o **Monitor de rede**.

Essa janela só anota o que acontece **enquanto está aberta**, então abra-a e depois **recarregue a página**. Na
caixa de filtro escreva `/api/`: assim você vê só as requisições à API e não as do estilo ou dos desenhos da página.

Cada linha dessa janela é uma requisição, e **um único clique pode produzir várias**. Na sua folha, anote todas
na mesma linha, separadas por ponto e vírgula. Repare em três colunas: a **rota** (o nome), o **método** e
o **código de status** (no Chrome, *Status*). O método diz que tipo de coisa a página pede:

| Método | O que pede | Exemplo na loja |
|---|---|---|
| GET | Que lhe **deem** algo, sem mudar nada | O carrinho, os produtos |
| POST | **Criar** algo ou fazer algo acontecer | Uma sessão, um pedido, um pagamento |
| PUT | **Substituir** algo pelo que ele manda | As peças de um produto no carrinho |
| DELETE | **Remover** algo | Um produto do carrinho |

### A folha de registro

Copie esta tabela no seu caderno ou em um arquivo. Você vai preenchê-la enquanto compra; a de baixo, em «Compare suas
respostas», é para depois, não antes.

| # | O que você faz | O que você vê na tela | Requisições (método e rota, todas) | Códigos | O que mudou na loja |
|---|---|---|---|---|---|
| 1 | Recarrega a página | | | | |
| 2 | Entra como Marta com uma senha **errada** | | | | |
| 3 | Entra como Marta com `marta-practica` | | | | |
| 4 | Adiciona uma Camiseta azul ao carrinho | | | | |
| 5 | Paga | | | | |
| 6 | Abre «Meus pedidos» | | | | |

**Preveja antes de cada linha.** Antes de clicar, escreva o que você acha que vai acontecer. Por exemplo, na 2:
que código você acha que a API devolve quando a senha está errada? Depois compare.

### Faça a compra

1. **Recarregue a página** com a janela de rede aberta. Anote que requisição aparece.
2. **Entre com uma senha errada.** Escreva `incorrecta` em *Senha* e pressione *Entrar*. A página
   diz que algo deu errado. Que código veio da API? Esta linha você faz de propósito: um QA olha também o
   que acontece quando as coisas dão errado, e aqui é inofensivo.
3. **Entre direito:** senha `marta-practica`. A página muda: aparece «Olá, Marta», o catálogo e o seu carrinho.
   Veja quantas requisições saíram de **um único** clique. Não é uma só.
4. **Adicione uma Camiseta azul.** Procure a camiseta no catálogo e pressione *Adicionar ao carrinho*. Olhe o carrinho:
   subtotal, desconto, frete e total. Escreva os quatro números.
5. **Pague.** O cartão de teste já vem preenchido (`4242 4242 4242 4242`) e a forma de pagamento é «Pagamento à vista». Pressione *Pagar*. Abra a linha da requisição de pagamento e procure entre os cabeçalhos (*Headers*) um
   chamado `Idempotency-Key`. Por ora apenas localize-o e anote que está lá; no passo 5 você vê para que serve, e
   na lição 08 você o testa.
6. **Abra «Meus pedidos»** (botão do alto). Ali está o seu pedido, com o número, o estado e o total.

> **Apenas dados de teste.** O cartão `4242 4242 4242 4242` não é de ninguém, e o gateway de pagamento desta loja
> é simulado: não fala com nenhum banco e não cobra nada de verdade. Em uma loja de prática nunca escreva um
> cartão real, uma senha que você use em outro lugar nem dados pessoais.

**Para olhar com calma:** no passo 3 você viu que a página pede o carrinho **antes** de adicionar a camiseta e o
pede de novo **depois**. Por que você acha que ela faz isso? Não há uma única resposta certa; a que o código
da loja dá está em «Compare suas respostas».

**Isto demonstra** (objetivo 0.2): a sua folha de registro, comparada com a de «Compare suas respostas». O `verifica`
só consegue confirmar a parte que deixa marca na loja, que o seu pedido existe e está pago; a folha você confere
com esta lista:

- [ ] As seis linhas têm o que você viu na tela.
- [ ] Cada linha tem **todas** as suas requisições a `/api/`, com método, rota e código.
- [ ] Na linha 5 você anotou o cabeçalho `Idempotency-Key`.
- [ ] Cada linha diz o que mudou na loja, ou «nada».

---

## Passo 4 · Deixe o `verifica` conferir

Volte ao terminal da loja e rode de novo:

```bash
verifica 00
```

Agora deve sair algo assim. O seu número de pedido pode não ser 1 (se você já tinha comprado, ou se é a sua segunda vez);
com uma camiseta azul, o total é $432.00:

```text
Verificando a lição 00…

✅ A API da loja responde em /api/salud
✅ A página da loja carrega
✅ Marta tem um pedido pago (o 1, de $432.00)

🎉 Lição completa!
```

Três verdes. O `verifica` encontrou o seu pedido perguntando à loja, igual a você o viu em «Meus pedidos». Se
Marta tem vários pedidos pagos, ele cita o primeiro que encontra. Essa é a regra que o curso vai usar
sempre: **a evidência é o que a loja fez**, e pode ser repetida.

Se sair vermelho com «Marta tem N pedido(s), mas nenhum está pago», o pedido foi criado mas o pagamento não passou. A
mesma linha te diz o que fazer: conclua a compra com *Pagar* e, se o gateway recusou o pagamento, rode
`tienda pasarela aprueba` dentro do terminal e pague de novo.

---

## Passo 5 · O que custaria se isto falhasse?

Você já percorreu a compra. Agora a olha como o negócio a olha: nem todas as falhas custam o mesmo. Um texto
desalinhado incomoda; uma cobrança em dobro custa à loja um reembolso, uma ligação da cliente e, talvez, a
cliente. Escolher o que testar primeiro começa aqui. O programa da ISTQB, o exame de testes com o qual o
curso te deixa situado, diz assim: testar tudo não é possível, e o esforço se concentra, entre outras coisas, conforme
o risco.

**Uma palavra nova: caminho crítico.** É o caminho que, se quebra, custa dinheiro ou clientes ao negócio. O
que você fez no passo 3 (entrar, montar o carrinho, pagar, ver o pedido) é o caminho crítico desta loja.

Três partes desse caminho em que uma falha custa caro. Os dados vêm de fontes que medem coisas diferentes desta
loja: servem para raciocinar sobre o risco, não são uma medição dela.

**A cobrança.** É onde se juntam o dinheiro do cliente e a sua confiança. O Baymard Institute, que estuda como as
pessoas compram online, perguntou a compradores dos Estados Unidos por que abandonaram um carrinho sem comprar (deixando de fora
quem só estava olhando). Entre as razões que deram: **19%** não confiaram o cartão ao site, **17%**
disseram que o site teve erros ou caiu, e **10%**, que o cartão foi recusado. É uma pesquisa em outro país,
não uma contagem de vendas perdidas; mesmo assim, diz onde dói para o comprador. E a cobrança tem uma falha que dói
mais que não cobrar: **cobrar duas vezes**. Para isso existe a **chave de idempotência**, o cabeçalho que você localizou no
passo 3. A Stripe, um gateway de pagamento muito usado, explica assim: se a conexão cai, a página pode repetir
a requisição com a mesma chave sem o risco de fazer a mesma operação duas vezes.

**O estoque.** Se a loja vende algo que não tem, cobrou por uma promessa que não pode cumprir. No México, a
Ley Federal de Protección al Consumidor (a lei mexicana de proteção ao consumidor) obriga a loja a respeitar o que ofereceu e combinou com o cliente, entre
outras coisas quantidades, prazos e datas, para a entrega. O que segue já é raciocínio do curso, não texto da
lei: vender o que não há quase sempre obriga a cancelar, devolver o dinheiro e dar explicações ao cliente. Esta loja de
prática não tem estoque, mas tem o caminho do pedido depois do pagamento (no armazém, enviado, entregue),
e esse você percorre na lição 04.

**A entrega.** O cliente já pagou; agora espera. Na mesma pesquisa da Baymard, **20%** disseram que abandonaram um
carrinho porque a entrega era muito lenta: o prazo pesa na decisão desde antes de pagar. E a mesma lei exige
que o valor total a pagar seja informado de forma notória e visível: um frete que aparece de surpresa no final não é
só uma má experiência. Por isso a sua folha de registro anotou o frete ($99.00) junto ao total.

**O que isto diz a um QA:** se um dia você só tiver tempo para um teste, ele vai no caminho crítico. O curso
usa isso na lição 11, em que um teste de navegador percorre justamente esse caminho.

**Isto demonstra** (objetivo 0.3): a revisão de «Para fechar», 4 de 5.

---

## Três notas sobre a sua loja de prática

1. **Os erros estão lá, mas desligados.** A loja traz quatro erros plantados que se ligam um por lição.
   Hoje estão todos desligados, e você pode conferir pelo terminal do seu computador com
   `./practicar error estado`. Não os ligue ainda: cada lição diz qual e quando. Se algum ficar
   ligado, o `./practicar` avisa quando você entra.
2. **O seu trabalho fica guardado.** `./practicar apagar` desliga a loja; os seus pedidos e a sua pasta `~/practica` continuam lá
   na próxima vez. `./practicar reiniciar` deixa a loja como recém-aberta, sem pedidos. `./practicar desde-cero`
   apaga também a sua pasta, e por isso pede confirmação.
3. **A loja é publicada só para o seu computador.** O script abre a porta dela em `127.0.0.1`, de modo que outras
   pessoas não conseguem abrir a sua loja por essa porta, e o gateway de pagamento é simulado. Ela é para você errar sem
   consequências: entre com senhas erradas, mude quantidades estranhas, abra e feche. Use sempre os dados de
   teste da lição.

---

## Os seus exercícios

1. **Compre como Luis.** Saia da loja (botão *Sair*), entre como Luis (`luis-practica`) e faça outra compra com
   um produto diferente. Preencha uma folha de registro nova. As requisições foram as mesmas? O que mudou?
   Depois rode `verifica 00`: mudou algo no que ele diz? Por quê?
2. **Peça à API sem se identificar.** No terminal da loja, preveja o que ela responde e depois rode:
   ```bash
   curl http://localhost:8080/api/pedidos
   ```
   Compare a resposta com a linha 2 da sua folha. O que elas têm em comum?
3. **Três falhas, três custos.** Sem olhar o passo 5, escreva uma falha possível na cobrança, uma no estoque e
   uma na entrega desta loja, e para cada uma: quem a nota primeiro (o cliente, a loja, o banco) e o que
   ela custa à loja. Depois compare com o passo 5.

---

## Não está rodando?

| O que você vê | O que acontece | O que fazer |
|---|---|---|
| `no such file or directory: ./practicar` (ou `No such file or directory`) | Você não está na pasta do curso | Entre na pasta onde você baixou o curso, rode `ls` e confira que aparece `practicar` |
| `❌ Não encontro o comando «docker» neste computador.` | O Docker não está instalado | «Se você não tem o Docker», em «Antes de começar» |
| `❌ O Docker está instalado, mas não consegui falar com ele.` | No Mac, o programa do Docker está fechado. No Linux, o serviço está desligado ou o seu usuário não está no grupo `docker` | A mesma mensagem diz o que conferir no seu sistema. Se não for isso, rode `docker info` e siga o erro exato |
| `❌ Não consegui subir a loja.` com `port is already allocated` | Outro programa usa a porta 8080 | Feche-o, ou suba a loja em outra porta: `TIENDA_IDIOMA=pt TIENDA_PUERTO=8081 ./practicar` |
| `❌ ./practicar abre um terminal interativo…` | Você o rodou com um pipe (`|`) ou um redirecionamento | Rode-o direto no seu terminal |
| A página não carrega no navegador | A loja está desligada, ou você usa outra porta | Rode `./practicar` de novo; se você usou `TIENDA_PUERTO`, troque o número no endereço |
| `verifica 00`: «nenhum está pago» | O gateway recusou o pagamento ou você não terminou a compra | Dentro: `tienda pasarela aprueba`, e pague de novo |

---

## Para fechar

Andrea conferiu o que se via. Você já sabe que por baixo de cada clique há uma conversa (requisição, resposta e código
de status), que você pode olhá-la, e que nem todas as falhas custam o mesmo. Isso é conhecer o sistema antes de
testá-lo.

Na lição 01 você deixa de olhar a loja como compradora e começa a lê-la como QA: recebe uma história de
usuário, a separa em regras e escreve os seus primeiros cenários no papel e em um arquivo. Rodá-los contra esta
mesma loja chega quando existir o seu `verifica 01`; enquanto isso, a lição te dá uma lista para conferir a forma deles.

**Revisão (4 de 5).** Para cada caso escreva três coisas: (1) que parte do caminho crítico ele toca (cobrança, estoque
ou entrega), (2) quem o nota primeiro e (3) a cadeia completa: **falha → o que acontece com o cliente ou com a operação →
quanto custa à loja**. Nomear só a parte não conta como resposta.

1. Lucía vê $333.00 em cada tela do caminho; já com os seus dados preenchidos, o último passo diz $432.00.
2. A internet de Pedro cai justo quando ele pressiona *Pagar*; a página tenta de novo sozinha, e no extrato dele
   aparecem dois lançamentos de $432.00.
3. A loja confirma dez pedidos da caneca no mesmo dia; na sexta alguém descobre que só havia seis.
4. Uma cliente pagou na segunda; na sexta o pedido dela diz o mesmo que na terça e ninguém lhe escreveu.
5. Durante uma hora, todas as compras terminam com «o gateway recusou o pagamento», embora as pessoas usem cartões que
   funcionam em outras lojas.

---

## Compare as respostas

**A sua folha de registro.** Assim ficou ao fazer a compra contra a loja do curso. As suas horas e o seu número de pedido
podem ser outros (aqui é o 1); as rotas, os métodos e os códigos têm de ser os mesmos.

| # | O que você faz | O que você vê | Requisições a `/api/` | Códigos | O que mudou |
|---|---|---|---|---|---|
| 1 | Recarrega | «Entre na loja» | `GET /api/textos` | 200 | Nada: a página pediu os seus textos no seu idioma |
| 2 | Senha errada | «cliente ou senha incorretos» | `POST /api/sesiones` | 401 | Nada |
| 3 | Entra como Marta | «Olá, Marta», catálogo e carrinho vazio | `POST /api/sesiones`, `GET /api/productos`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Abriu-se uma sessão de Marta |
| 4 | Adiciona uma Camiseta azul | «Adicionado ao carrinho»; subtotal $333.00, desconto $0.00, frete $99.00, total $432.00 | `GET /api/carrito`, `PUT /api/carrito/productos/playera-azul`, `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 200, 200, 200, 200 | O carrinho de Marta tem 1 peça |
| 5 | Paga | «Pedido 1 pago. Obrigado pela sua compra!» e o carrinho vazio | `POST /api/pedidos`, `POST /api/pedidos/1/pago` (com `Idempotency-Key`), `GET /api/carrito`, `GET /api/carrito/formas-de-pago` | 201, 200, 200, 200 | Existe o pedido 1, pago, com uma cobrança de $432.00 |
| 6 | «Meus pedidos» | «Pedido 1 · pago · $432.00» | `GET /api/pedidos` | 200 | Nada |

Três coisas que vale a pena notar:

- **A linha 3:** um clique, quatro requisições. A tela te mostra uma coisa; a API recebe várias. Muitos erros
  vivem entre uma e outra.
- **A linha 5:** pagar são **duas** requisições, uma que cria o pedido e outra que o cobra. Entre as duas, o
  pedido existe sem estar pago. Por isso o `verifica` distingue «você tem pedido» de «você tem pedido pago».
- **O GET antes de adicionar (pergunta do passo 3):** a página pergunta quantas peças desse produto você já tem, soma
  uma e manda o total com `PUT`, porque o `PUT` substitui a quantidade, não a soma. Depois pede de novo o
  carrinho para pintar os números que a loja calculou, não os que a página calculou.

**Exercício 1:** as requisições são as mesmas; mudam a rota do produto no `PUT` e os valores. O `verifica 00`
não muda o que diz, porque confere os pedidos de **Marta**, não os de Luis: mede o que a lição pediu.

**Exercício 2:** a API responde `{"mensaje":"faça login primeiro"}` com código 401, o mesmo código da linha 2.
Nos dois casos a API não sabe quem você é. Em uma requisição sem se identificar, você nem sequer tentou.

**Exercício 3:** qualquer falha bem pensada vale. O que importa é que você tenha escrito quem a nota primeiro e quanto
custa. Exemplos: cobrança → o banco recusa cartões bons, o cliente nota, custa a venda; estoque → se
vende o que não há, o armazém nota, custa um cancelamento e um reembolso; entrega → o pedido fica
parado sem aviso, o cliente nota, custa a confiança dele e uma reclamação.

**Revisão.** Conta como correta a resposta que traz as três partes; as cadeias abaixo são exemplos, e a
sua pode ser outra se se sustentar:

1. **Cobrança ou entrega, as duas valem.** Lucía nota no último passo. Toca a cobrança porque muda o que ela paga, e a
   entrega porque a diferença é o frete ($99.00), que o passo 5 trata ali. O total não foi informado de forma
   visível desde antes → Lucía se sente surpreendida e abandona ou paga irritada → a loja perde a venda ou ganha uma
   reclamação, e a lei pede que se mostre o total.
2. **Cobrança.** Nota Pedro, ou o banco dele. O pagamento se repetiu sem uma chave que o identificasse como a mesma tentativa
   → duas cobranças por uma compra → reembolso, ligação ao atendimento ao cliente e um cliente que desconfia.
3. **Estoque.** Nota quem separa os pedidos. Cobrou-se o que não havia → quatro clientes sem a sua caneca →
   quatro cancelamentos com reembolso e quatro explicações.
4. **Entrega.** Nota a cliente. O pedido não avança e ninguém avisa → ela não sabe se o dinheiro dela está seguro → reclamação, e
   provavelmente não volta a comprar.
5. **Cobrança.** Notam os clientes. O gateway recusa pagamentos bons → eles não conseguem comprar → cada compra daquela hora
   se perde ou vai para outra loja (é a razão que deu os 10% da pesquisa da Baymard).

**Se você não acertou 4,** volte ao passo 5: cada caso sai de uma das suas três partes.

---

## Fontes da lição

Todas foram abertas em 21/11/2026 e conferidas frase por frase. O detalhe, com a frase de cada uma, está no
research da lição.

1. Docker, «Port publishing and mapping». Uma porta publicada com `127.0.0.1` só é alcançada pelo próprio
   computador. https://docs.docker.com/engine/network/port-publishing/
2. MDN (Mozilla), «HTTP request methods». O que fazem GET, POST, PUT e DELETE.
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
3. MDN (Mozilla), «HTTP response status codes». 200 (a requisição deu certo) e 201 (algo novo foi criado).
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
4. Chrome for Developers, «Inspect network activity». Como se abre o painel Network, que só anota enquanto está
   aberto, e a caixa de filtro. https://developer.chrome.com/docs/devtools/network
5. Firefox Source Docs (Mozilla), «Network Monitor». O que mostra e o seu atalho de teclado.
   https://firefox-source-docs.mozilla.org/devtools-user/network_monitor/
6. FastAPI, «First Steps». A documentação interativa da API em `/docs`.
   https://fastapi.tiangolo.com/tutorial/first-steps/
7. Stripe, «Idempotent requests». A chave de idempotência para repetir uma requisição sem fazer a operação duas
   vezes. https://docs.stripe.com/api/idempotent_requests
8. Baymard Institute, «Cart Abandonment Rate: 50 Statistics & Why People Abandon (2026)», 28/10/2026. Razões
   para abandonar um carrinho: 19% não confiaram o cartão, 17% erros do site, 10% cartão recusado, 20% entrega
   lenta. https://baymard.com/lists/cart-abandonment-rate
9. Ley Federal de Protección al Consumidor, Cámara de Diputados, última reforma DOF 12/12/2025, artigos 7 e 7 BIS.
   Respeitar o que foi oferecido e combinado para a entrega, e mostrar de forma notória o valor total.
   https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf
10. ISTQB, Certified Tester Foundation Level Syllabus v4.0.1, 15/09/2024, §1.2 e §1.3. De erros saem defeitos, e
    de defeitos, falhas; testar tudo não é possível e o esforço se concentra conforme o risco (princípio 2).
    https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/

Do curso e da Hábil: a loja de prática, o seu `practicar` e o seu `verifica` são do curso, no repositório dele. É
**regra do curso**, sem fonte externa: «se você só tiver tempo para um teste, ele vai no caminho crítico»; existe
para que o primeiro teste que você escrever proteja o que mais custa.
