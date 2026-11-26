# Lição 11 — O navegador, só para o crítico

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Teste de navegador:** um programa que abre a página, escreve, clica e lê a tela, como faria a Marta.
- **Sem janela:** o navegador roda completo, mas não desenha nada na sua tela. Em inglês, dizem *headless*.
- **Seletor:** a forma de dizer ao teste em qual elemento da página agir, por exemplo «o botão Pagar».

**O que fica com você:** um script, `compra.py`, que entra como a Marta, compra uma camiseta e confere em «Meus pedidos»
que o pedido ficou pago. Ele sai verde com a loja limpa e vermelho com um erro que nenhuma das suas coleções vê.

**Ideia nova de QA desta lição (a única):** o teste de navegador é o mais caro: ele se reserva para o percurso que não
pode falhar. As ferramentas, sim, são novas (Python e Playwright), mas você não precisa aprendê-las por completo: copia
um script e o entende linha por linha.

**Em que ordem vai:** você compra à mão e encontra um erro que a API não vê (passo 1); escreve o teste (passo 2); roda
verde e vermelho (passo 3); vê as duas formas de ele te enganar (passo 4); e mede quanto custa (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são de verdade.*

Numa terça-feira de manhã, sai uma versão nova da página da loja. Antes de publicá-la, a equipe rodou todas as suas
coleções: a da lição 07, a de permissões, a do gateway. Tudo verde.

À tarde, o almoxarifado pergunta por que não há nada para embalar. Desde de manhã, a Marta e várias outras clientes
viram na página «Pedido 7 pago. Obrigado pela sua compra!». Nenhuma foi cobrada, e nenhum pedido passou a pago. A API
estava perfeita: ninguém pediu a ela que cobrasse.

---

## Antes de começar

**Você precisa da loja no ar.** Como nas lições 07 a 10: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra
janela, o terminal da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`. Desta vez você também vai usar o
navegador do seu computador, no endereço que o terminal mostra ao entrar (`http://localhost:8080`).

> **Esta lição usa a loja da lição 11.** Ela traz o erro E8. Se `tienda error E8 on` te disser que esse erro não existe,
> atualize a sua loja antes de seguir: com uma versão anterior, as suas saídas não vão coincidir.

**O que você já sabe e vai usar:** da lição 07, não escrever à mão o endereço nem a Marta nos seus testes; da 09, o
**código de saída** (0 é verde, qualquer outro número é vermelho) e conferir **o efeito**, não o que a resposta diz; da
10, conferir que o estado do pedido bate.

**O que é novo:** Python e Playwright, a ferramenta que dirige o navegador. Os dois já vêm na loja: você não instala
nada.

**Faça o exercício 2 sem IA.** O que você treina ali é decidir onde vai cada teste, e isso é critério seu.

**Comece limpo:**

```bash
tienda reiniciar
```

```text
✅ a loja voltou ao estado de recém-aberta
```

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Uma compra que a API não vê

Primeiro compre à mão, como a Marta. No navegador do seu computador, abra `http://localhost:8080`:

1. Escreva a senha da Marta (`marta-practica`; o nome já vem preenchido) e clique em **Entrar**.
2. Em «Camiseta azul», clique em **Adicionar ao carrinho**. O carrinho lá em cima muda para 1.
3. No carrinho, clique em **Pagar**. O cartão de teste já vem preenchido.
4. Embaixo aparece «Pedido 1 pago. Obrigado pela sua compra!». Clique em **Meus pedidos**: o pedido 1 diz **pago**.

O `tienda reiniciar` apaga as sessões. Se você reiniciar com a página aberta, a página leva você de volta à entrada com o
aviso «A sua sessão não existe mais (por exemplo, porque a loja foi reiniciada). Entre de novo.»: entre outra vez como a
Marta.

Agora ligue o erro desta lição, no terminal da loja:

```bash
tienda reiniciar
tienda error E8 on
```

```text
✅ a loja voltou ao estado de recém-aberta
  E1  ⚪ desligado
  E2  ⚪ desligado
  E3  ⚪ desligado
  E4  ⚪ desligado
  E5  ⚪ desligado
  E6  ⚪ desligado
  E7  ⚪ desligado
  E8  🔴 ligado

⚠️ erro E8 ligado
```

Recarregue a página, entre de novo como a Marta e repita a compra. A mensagem é a mesma: «Pedido 1 pago. Obrigado pela
sua compra!». Mas em **Meus pedidos**, o pedido 1 diz **criado**. A Marta acha que comprou, e a loja não cobrou dela.

**Preveja antes de rodar:** com E8 ligado, a sua coleção da lição 07 sai verde ou vermelha?

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
```

Sai **verde**: os mesmos sete vistos da lição 07. A coleção da lição 10, a do gateway, também: seis de seis (medido com
E8 ligado). Não é um descuido das suas coleções. O E8 só atinge **o pagamento que chega da página**: quando a
Marta clica em «Pagar», a loja responde que sim, a página escreve a mensagem de pago, e o pedido não é cobrado. Se o
pagamento chega direto pela API, como na sua coleção, ele é cobrado normalmente. Um teste que fala com a API, por
melhor que seja, não passa por esse botão e não consegue ver isso.

Para encontrar este erro é preciso fazer o que a Marta faz: abrir a página, clicar e olhar.

**Desligue o E8** antes de seguir:

```bash
tienda error E8 off
```

---

## Passo 2 · A compra, escrita como teste

Um teste de navegador faz o mesmo que você fez no passo 1, mas sozinho e sem janela. Em `~/practica`, crie o arquivo:

```bash
nano compra.py
```

e escreva isto. Você não precisa saber Python: copie o bloco completo, tal qual, e depois leia-o com a tabela abaixo.
Quatro coisas de Python que você vai ver: `import` traz uma ferramenta; `NOME = valor` guarda um dado com um nome;
`pagina.algo(…)` pede uma ação à página; e os quatro espaços no começo de uma linha a colocam dentro do bloco de cima.

```python
"""A compra crítica, no navegador: a cliente entra, compra uma camiseta e o pedido dela fica pago."""
import os

from playwright.sync_api import expect, sync_playwright

TIENDA_URL = os.environ["TIENDA_URL"]
CLIENTE = os.environ["CLIENTE"]
CONTRASENA = os.environ["CONTRASENA"]

with sync_playwright() as p:
    navegador = p.chromium.launch()
    pagina = navegador.new_page()
    pagina.goto(TIENDA_URL)

    pagina.fill("#cliente", CLIENTE)
    pagina.fill("#contrasena", CONTRASENA)
    pagina.click("#form-entrada button")

    pagina.get_by_test_id("agregar-playera-azul").click()
    expect(pagina.locator("#piezas")).to_have_text("1")

    pagina.click("#pagar")
    expect(pagina.locator("#piezas")).to_have_text("0")

    pagina.click("#ver-pedidos")
    estado = pagina.locator("#lista-pedidos .pedido .estado").first
    expect(estado).to_have_attribute("data-estado", "pagado")

    navegador.close()

print("✅ a cliente comprou e o pedido dela ficou pago")
```

| Parte | O que faz |
|---|---|
| `os.environ["TIENDA_URL"]` | Lê o endereço da loja **do ambiente**, como `{{base}}` na sua coleção da lição 07. O mesmo com `CLIENTE` e `CONTRASENA`. Assim o teste não traz nada escrito à mão e serve para outra loja ou outra cliente |
| `with sync_playwright() as p:` | Liga o Playwright. As linhas de baixo que começam com quatro espaços vão **dentro** deste bloco e podem usá-lo; ao terminar o bloco, o Playwright se desliga |
| `p.chromium.launch()` | Abre o Chromium, o navegador. O Playwright o abre **sem janela** se você não pedir outra coisa |
| `pagina.goto(TIENDA_URL)` | Abre a loja, como quando você digitou o endereço no seu navegador |
| `pagina.fill("#cliente", CLIENTE)` | Escreve no campo cujo `id` é `cliente`. O `#` quer dizer «o elemento com este id» |
| `pagina.click("#form-entrada button")` | Clica no botão do formulário de entrada: «Entrar» |
| `get_by_test_id("agregar-playera-azul")` | Procura o botão **Adicionar ao carrinho** da camiseta azul pelo seu **test id**, uma marca que a página coloca só para os testes |
| `expect(…).to_have_text("1")` | **Confere**: o contador do carrinho tem de dizer 1. Se ainda não diz, espera e olha de novo, por até 5 segundos |
| `expect(pagina.locator("#piezas")).to_have_text("0")` | Depois de pagar, espera o carrinho se redesenhar em 0. A página o redesenha **no final**, quando esta tentativa de pagamento já terminou; assim o teste não pede «Meus pedidos» antes da hora. Que o carrinho fique em 0 não diz que foi pago: isso quem confere é a verificação de baixo |
| `.first` e `to_have_attribute("data-estado", "pagado")` | Em «Meus pedidos», pega o pedido lá de cima (o mais novo) e confere que o estado dele seja `pagado` |
| `print(…)` | Só é impresso se todas as verificações passaram |

**Por que estes seletores e não o texto dos botões.** A documentação do Playwright recomenda procurar pelo que o usuário
vê, como o texto de um botão. Aqui isso não serve: a sua loja fala cinco idiomas, e «Adicionar ao carrinho» é «Add to
cart» em inglês e «Добави в количката» em búlgaro. O `id` e o test id não mudam com o idioma. Por isso o botão
**Adicionar ao carrinho** traz `data-testid="agregar-playera-azul"`: é uma marca que a página coloca para os testes, e o
Playwright a considera a forma mais resistente de encontrar um elemento.

**Por que o teste diz «a cliente» e não «Marta».** O `verifica` procura a Marta escrita à mão em tudo o que não for
comentário, e o texto entre `"""` do começo e o do `print` não são comentários: contam. Um comentário começa com `#`.

**Por que o estado e não a mensagem.** A mensagem da página é o que a página diz. O estado em «Meus pedidos» é o que a
loja guardou. No passo 1 você viu que, com E8, não são a mesma coisa.

**Se algo falhar, o Python termina com um número diferente de 0**, igual ao seu script da lição 09. Uma verificação
`expect` que não se cumpre em 5 segundos interrompe o script ali mesmo, e o `print` do final não é executado.

---

## Passo 3 · Verde, e depois vermelho

O teste lê o endereço, a cliente e a senha do ambiente. Coloque-os uma vez no terminal da loja:

```bash
export TIENDA_URL=http://localhost:8080
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

O `export` deixa a variável colocada enquanto aquela janela continuar aberta. Se você fechar o terminal, escreva as três
linhas de novo.

**Preveja:** com a loja limpa, quanto ele demora? Mais ou menos que a sua coleção da lição 07? Rode-o:

```bash
tienda reiniciar
python3 compra.py
echo "código de salida: $?"
```

```text
✅ a loja voltou ao estado de recém-aberta
✅ a cliente comprou e o pedido dela ficou pago
código de salida: 0
```

Demora cerca de um segundo e meio (medido: entre 1.4 e 1.5 segundos em cinco rodadas).

Você não viu nenhuma janela, mas um navegador completo abriu a loja, entrou, comprou e conferiu. Na página, no seu
computador, entre como a Marta e abra **Meus pedidos** (se a página levou você de volta à entrada, entre de novo):
ali está o pedido que o seu teste fez.

Agora com o erro:

```bash
tienda reiniciar
tienda error E8 on
python3 compra.py
echo "código de salida: $?"
```

```text
✅ a loja voltou ao estado de recém-aberta
  E1  ⚪ desligado
  E2  ⚪ desligado
  E3  ⚪ desligado
  E4  ⚪ desligado
  E5  ⚪ desligado
  E6  ⚪ desligado
  E7  ⚪ desligado
  E8  🔴 ligado

⚠️ erro E8 ligado
Traceback (most recent call last):
  File "/home/alumno/practica/compra.py", line 27, in <module>
    expect(estado).to_have_attribute("data-estado", "pagado")
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.15/site-packages/playwright/sync_api/_generated.py", line 15155, in to_have_attribute
    self._sync(
    ~~~~~~~~~~^
        self._impl_obj.to_have_attribute(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        )
        ^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_sync_base.py", line 124, in _sync
    return task.result()
           ~~~~~~~~~~~^^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 357, in to_have_attribute
    await self._expect_impl(
    ...<7 lines>...
    )
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/assertions.py", line 122, in _expect_impl
    _record_soft_or_raise(
    ~~~~~~~~~~~~~~~~~~~~~^
        AssertionError(
        ^^^^^^^^^^^^^^^
    ...<2 lines>...
        self._is_soft,
        ^^^^^^^^^^^^^^
    )
    ^
  File "/usr/local/lib/python3.15/site-packages/playwright/_impl/_assertions.py", line 50, in _record_soft_or_raise
    raise error
AssertionError: Locator expected to have attribute 'pagado'
Actual value: creado 
Call log:
  - Expect "to_have_attribute" locator("#lista-pedidos .pedido .estado").first with timeout 5000ms
  - waiting for locator("#lista-pedidos .pedido .estado").first
    14 × locator resolved to <span class="estado" data-estado="creado">criado</span>
       - unexpected value "creado"

Aria snapshot:
- text: criado
código de salida: 1
```

É longa, e quase tudo é o caminho por dentro do Playwright. O que importa está no final: `Locator expected to have
attribute 'pagado'`, `Actual value: creado` e `código de salida: 1`.

O teste sai **vermelho**. Ele chega a «Meus pedidos», espera 5 segundos que o pedido diga `pagado` e ele não diz: diz
`creado`. O Python imprime qual verificação falhou e termina com um código diferente de 0. É justamente o que a sua
coleção não viu no passo 1.

**Desligue o E8:**

```bash
tienda error E8 off
```

---

## Passo 4 · Dois verdes que não bastam

Um teste de navegador custa mais para escrever e para rodar do que um de API. Só vale a pena se vê o que a API não vê.
Há duas maneiras comuns de ele sair verde sem ter visto.

**Olhar a mensagem em vez do estado.** Se a última verificação fosse «a mensagem da página diz pago», com E8 o teste
sairia verde: a página escreve a mensagem mesmo sem ter pago. É o mesmo erro da lição 09: acreditar no que se diz em vez
de conferir o que aconteceu. Você vai comprovar isso no exercício 1.

**Falar com a API em vez de usar a página.** Um `compra.py` que, em vez de abrir o navegador, inicia a sessão, adiciona
a camiseta e paga com chamadas diretas à API, sai verde com E8: medido. Esse script compra mesmo, mas não passa pelo
botão «Pagar», que é justamente o que falha. Por isso o `verifica 11` roda o seu teste com E8 ligado e exige que ele
falhe: uma compra direta pela API continua verde com E8, e ali ele a rejeita. O `verifica` não lê como o seu teste está
escrito; confere o que ele faz.

---

## Passo 5 · O que custa

Rode a sua coleção da lição 07 e o seu `compra.py`, com a loja limpa, e meça o tempo de cada um com `time`:

```bash
tienda reiniciar
time newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
time python3 compra.py
```

O `time` imprime no final quanto o comando demorou; olhe a linha `real`.

Medido na imagem da loja, com a loja limpa:

| Teste | O que confere | Tempo (mediana de 5) |
|---|---|---|
| Coleção da lição 07 | 3 requisições à API, 7 verificações | 1.1 s |
| `compra.py` | 1 percurso no navegador | 1.5 s |

Numa loja tão pequena, o `compra.py` demora cerca de 1.3 vezes o que demora a sua coleção: pouco. Mas compare o
que cada um confere: a coleção faz sete verificações; o `compra.py`, um único percurso.

O tempo não é o único custo. Um teste de navegador:

- **é mais lento**: liga um navegador, carrega a página e espera que cada coisa apareça;
- **quebra mais fácil**: se alguém muda um `id`, um test id ou o caminho da compra, o teste falha ainda que a loja
  funcione bem;
- **diz menos quando falha**: «o pedido não ficou pago» pode ser a página, a API, o gateway ou o banco de dados, e é
  preciso procurar qual.

Por isso as equipes desenham os seus testes como uma **pirâmide**: embaixo, muitos testes pequenos e rápidos; no meio,
testes de API como as suas coleções; em cima, **poucos** de navegador. Mike Cohn, que a tornou conhecida num livro de
2009, põe os testes de interface lá no topo porque se quer ter o menos possível deles. Martin Fowler diz assim: os
testes que passam pela interface são frágeis, caros de escrever e demorados de rodar. E no Google, mesmo com muitos
testes dos outros tipos, recomendam ficar com um número **pequeno** de testes de ponta a ponta para conferir o sistema
completo.

**Regra prática deste curso** (não é uma lei: é como a aplicamos a esta loja): as regras que vivem na API se testam pela
API; no navegador vai o percurso que não pode falhar e o que só a página pode mostrar.

**O que vai em cima, então, nesta loja.** O percurso que não pode falhar, e o que só se vê na página. Comprar é as duas
coisas: se a Marta não consegue comprar, a loja não serve, e na cena as coleções estavam verdes. Que o cupom seja usado
uma única vez, que o Luis não veja os pedidos da Marta ou que uma cobrança tardia seja conciliada não precisa do
navegador: as suas coleções conferem isso mais rápido e, quando falham, te dizem onde.

---

## Como se confere

**O seu teste** é conferido pelo `verifica 11`. Guarde-o em `~/practica` como `compra.py` e, no terminal da loja,
escreva:

```bash
verifica 11
```

O `verifica`:

1. confere que o seu `compra.py` não tenha escritos à mão o endereço, `Marta` nem a senha dela (os comentários não
   contam);
2. o roda com a loja limpa: tem de **terminar em 0**, e a loja tem de ter um pedido **pago** da Marta;
3. o roda com E8 ligado: **não pode terminar em 0**. Se terminar em 0, o seu teste não está conferindo o que a loja
   guardou, ou não está usando a página.

Ele passa ao seu teste o endereço, a cliente e a senha pelo ambiente; você não precisa dos seus `export` para rodá-lo.
Liga e desliga o E8 sozinho. Reinicia a loja antes de cada rodada e no final, então **apaga os seus pedidos, o seu
carrinho e a sua sessão** (a página pede que você entre de novo); o que volta como estava é quais erros você tinha ligados. Dá
ao seu teste até 2 minutos por rodada.

```text
Verificando a lição 11…

✅ Seu arquivo compra.py está em ~/practica
✅ O compra.py não traz escritos à mão o endereço, Marta nem a senha dela: tudo sai do ambiente
✅ Com a loja limpa, o compra.py termina com 0 e a loja tem o pedido pago
✅ Com o erro E8 ligado, o compra.py termina com 1: o teste vê que o pedido não ficou pago

🎉 Lição completa!
```

Demora cerca de 9 segundos.

**Antes de dar a lição por terminada, confira:**

- [ ] `compra.py` está em `~/practica`.
- [ ] Lê `TIENDA_URL`, `CLIENTE` e `CONTRASENA` com `os.environ`.
- [ ] Procura o botão **Adicionar ao carrinho** com `get_by_test_id`.
- [ ] Depois de **Pagar**, espera o carrinho ficar em 0.
- [ ] A última verificação olha o **estado** em «Meus pedidos», não a mensagem.
- [ ] Com a loja limpa termina em 0; com E8, não.
- [ ] No seu teste não aparecem `localhost`, `Marta` nem a senha (procure-os com
      `grep -n -i -e localhost -e marta -e practica compra.py`; não deve imprimir nada).
- [ ] Você deixou o E8 desligado (`tienda error estado`).

---

## Seus exercícios

1. **O teste que acredita na mensagem.** Faça uma cópia (`cp compra.py mensaje.py`) e, na cópia, troque as três últimas
   verificações (a partir de `pagina.click("#ver-pedidos")`) por uma só:

   ```python
   expect(pagina.locator("#mensaje")).to_contain_text("pago")
   ```

   Preveja: com a loja limpa, verde ou vermelho? E com E8? Rode os dois. Ao terminar, desligue o E8 e
   `rm mensaje.py`.
2. **API ou navegador?** (sem IA). Para cada cenário, decida se você o testa com uma coleção de API ou com o navegador,
   e escreva por quê em uma linha.

   | Cenário | API ou navegador? | Por quê |
   |---|---|---|
   | O cupom BIENVENIDA10 só pode ser usado uma vez (lição 09) | | |
   | O Luis não consegue ver os pedidos da Marta (lição 08) | | |
   | O botão «Pagar» manda o pagamento (este passo 1) | | |
   | Uma cobrança que chega tarde deixa o pedido pago (lição 10) | | |
   | A Marta consegue entrar, comprar uma camiseta e vê-la paga | | |
   | O botão «Adicionar ao carrinho» de cada um dos produtos do catálogo funciona | | |

3. **Quanto esperar.** No seu `compra.py`, tire a linha que espera o carrinho ficar em 0 depois de pagar, e rode o teste
   dez vezes com a loja limpa:

   ```bash
   for i in 1 2 3 4 5 6 7 8 9 10; do tienda reiniciar > /dev/null; python3 compra.py > /dev/null; echo $?; done
   ```

   Saem os dez zeros? Preveja antes de rodar. Ao terminar, ponha a linha de volta.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. Na cena, por que as coleções da equipe saíram verdes? (passo 1)
2. Por que o botão «Adicionar ao carrinho» traz um test id e o teste não o procura pelo texto? (passo 2)
3. Por que o teste confere o estado em «Meus pedidos» e não a mensagem da página? (passos 2 e 4)
4. Por que um `compra.py` que paga pela API não te serve aqui, ainda que compre de verdade? (passo 4)
5. Se os testes de navegador encontram o que os de API não veem, por que não escrever todos assim? (passo 5)

---

## Para fechar

Até a lição 10 você testou a loja pela API, que é onde vive quase tudo: os preços, os cupons, as permissões, os
pagamentos. Esta lição testou a única coisa que a API não consegue ver: o que a página faz com ela.

O que você leva daqui:

- **Há erros que só se veem na página.** Com E8, a sua coleção paga sem problema e a Marta não consegue comprar
  pela página. Nenhuma coleção vê isso.
- **Um teste de navegador confere o que a loja guardou, não o que a página diz.** A mensagem de pago saía igual com E8;
  o estado do pedido, não.
- **Procure os elementos por algo que não mude:** numa página em cinco idiomas, o test id e não o texto.
- **O teste de navegador é o mais caro**: mais lento, mais frágil e mais difícil de ler quando falha. Ele se reserva
  para o percurso que não pode falhar, e todo o resto se testa mais embaixo.

Na lição 12 você leva o que encontrou a quem tem de consertar: um relatório que se entenda à primeira.

---

## Compare as respostas

**Passo 1, a previsão.** **Verde**, os sete vistos. A sua coleção paga pela API, e a API funciona. O E8 só atinge o
pagamento que chega do botão da página, e a sua coleção nunca passa por ele.

**Passo 3, a previsão.**

Demora um pouco mais que a sua coleção: na medição, 1.5 segundo contra 1.1 (mediana de cinco rodadas cada um). Se você
previsou muito mais, não é estranho: nesta loja pequena a diferença é pouca, e o passo 5 explica por que o tempo não
é o único custo.

**Exercício 1.** Com a loja limpa, **verde**. Com E8, também **verde**: a página escreve «Pedido 1 pago. Obrigado pela
sua compra!» ainda que não tenha mandado o pagamento, e o teste só olhava isso. Passou pela página, deu os mesmos
cliques que a Marta e mesmo assim não viu o erro, porque conferiu o que a página diz e não o que a loja guardou.

Medido: as duas rodadas imprimem «✅ a cliente comprou e o pedido dela ficou pago» e terminam em `0`.

**Exercício 2.**

| Cenário | API ou navegador? | Por quê |
|---|---|---|
| O cupom se usa uma única vez | API | A regra vive na API; o seu script da lição 09 a confere em segundos, também com dois pedidos ao mesmo tempo |
| O Luis não vê os pedidos da Marta | API | A permissão quem decide é a API; uma página que esconde um botão não protege nada se a API responde |
| O botão «Pagar» manda o pagamento | Navegador | Só se vê na página: com E8, o pagamento que o botão manda não é cobrado, e o da sua coleção é |
| A cobrança tardia deixa o pedido pago | API | Acontece entre a loja e o gateway, depois de a página já ter respondido |
| A Marta entra, compra e a vê paga | Navegador | É o percurso que não pode falhar; se falha, a loja não vende |
| O «Adicionar ao carrinho» de cada produto | Navegador, mas **um**, não todos | Cada produto usa o mesmo botão e a mesma chamada; testar um no navegador confere o botão, e os preços de todos se conferem mais rápido pela API |

A última linha não tem uma única resposta boa. Se você respondeu «API», está bem se a sua razão é que o carrinho se
confere pela API; se respondeu «navegador para todos», pergunte-se quanto demoraria e o que encontraria que um só
produto não encontre.

**Exercício 3.**

Quase sempre sim, e esse é o problema. Na medição rodamos o seu laço de dez rodadas duas vezes em cada um dos cinco
idiomas: cem rodadas. Noventa e nove saíram em `0`; **uma saiu em `1`**, com o pedido em `creado`. Sem a espera, o
teste clicou em «Meus pedidos» antes de o pagamento terminar, e o pedido nunca chegou a pago: esperou 5 segundos e
continuou em `creado`. A loja responde em milissegundos, então quase sempre o pagamento ganha; uma vez em cem, não.
Em outra medição, mais cem rodadas saíram todas em `0`: a falha é rara, e por isso é tão difícil de ver. Um teste assim fica vermelho de vez em quando sem que a loja tenha nenhum erro, e ninguém volta a acreditar nele. Por
isso se espera algo que muda **somente** quando a ação terminou, como o carrinho em 0.

**Revisão.**

1. Porque testavam a API, e a API estava bem. O erro estava na página: o botão «Pagar» não pedia à API que cobrasse.
2. Porque o texto muda com o idioma: «Adicionar ao carrinho», «Add to cart», «Добави в количката». O test id é o mesmo
   nos cinco, e o Playwright o considera a forma mais resistente de encontrar um elemento.
3. Porque a mensagem é o que a página diz, e o estado é o que a loja guardou. Com E8, a mensagem diz pago e o pedido
   continua criado.
4. Porque não passa pelo botão «Pagar», que é o que falha. Sai verde com E8, e o `verifica 11` o rejeita por isso.
5. Porque custam mais: demoram mais, quebram quando a página muda ainda que a loja funcione, e quando falham não te dizem
   onde está o problema. Ficam para o que não pode falhar e para o que só se vê na página.

---

## Fontes da lição

1. Martin Fowler, «TestPyramid» (consultado em 22 de novembro de 2026). «In short, tests that run end-to-end through
   the UI are: brittle, expensive to write, and time consuming to run.»; «Most people know about the the Test Pyramid
   due to Mike Cohn, when he described it in his 2009 book Succeeding with Agile.»
   https://martinfowler.com/bliki/TestPyramid.html
2. Mike Cohn, «The Forgotten Layer of the Test Automation Pyramid», Mountain Goat Software (consultado em 22 de
   novembro de 2026). «Automated user interface testing is placed at the top of the test automation pyramid because
   we want to do as little of it as possible.»
   https://www.mountaingoatsoftware.com/blog/the-forgotten-layer-of-the-test-automation-pyramid
3. Mike Wacker, «Just Say No to More End-to-End Tests», Google Testing Blog (2015; consultado em 22 de novembro de
   2026). «Even with both unit tests and integration tests, you probably still will want a small number of end-to-end
   tests to verify the system as a whole.»
   https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html
4. Playwright para Python, «Library» (consultado em 22 de novembro de 2026). «By default, Playwright runs the
   browsers in headless mode.»
   https://playwright.dev/python/docs/library
5. Playwright para Python, «Locators» (consultado em 22 de novembro de 2026). «Testing by test ids is the most
   resilient way of testing as even if your text or role of the attribute changes, the test will still pass.»
   https://playwright.dev/python/docs/locators
6. Playwright, «Best Practices» (consultado em 22 de novembro de 2026). «The end user will see or interact with what
   is rendered on the page, so your test should typically only see/interact with the same rendered output.»
   https://playwright.dev/docs/best-practices
7. Playwright para Python, «Assertions» (consultado em 22 de novembro de 2026). «By default, the timeout for
   assertions is 5 seconds.»
   https://playwright.dev/python/docs/test-assertions
8. Python, documentação de `os.environ` e de `sys.exit` (consultado em 22 de novembro de 2026). «A mapping object
   where keys and values are strings that represent the process environment.»; «zero is considered “successful
   termination” and any nonzero value is considered “abnormal termination” by shells and the like.»
   https://docs.python.org/3/library/os.html · https://docs.python.org/3/library/sys.html
