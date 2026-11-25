# Lição 13 — Seu teste serve?

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Semear um erro:** colocá-lo de propósito para ver se os seus testes o percebem. Na loja, você faz isso com
  `tienda error EX on`.
- **Sobreviver:** um erro sobrevive quando você o semeia e todos os seus testes continuam verdes.
- **Abençoar um erro:** um teste o abençoa quando fica verde **porque** espera o resultado errado.

**O que fica com você:** uma tabela que diz quais erros da loja os seus testes enxergam e quais não, e um script de
testes herdados em que você encontrou e corrigiu o teste que estava protegendo um erro.

**Ideia nova de QA desta lição (a única):** um teste só serve se ficar vermelho quando o erro está lá. Enquanto você
não o vir vermelho, um teste ainda não lhe deu evidência de que detecta esse erro.

**Em que ordem vai:** você vê por que um verde não basta (passo 1); semeia os oito erros nas suas coleções (passo 2);
entende por que quase todos sobrevivem (passo 3); encontra o teste que abençoa um erro (passo 4); e aplica a mesma
regra a testes escritos por uma IA (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são reais.*

Uma equipe herda a loja de outra. Junto com o código chega um script com cinco testes do carrinho, e os cinco ficam
verdes. «Pelo menos o carrinho está testado», diz alguém, e ninguém volta a abri-lo.

Três meses depois, uma cliente reclama: montou um carrinho de exatamente $999.00 e cobraram $99.00 de frete. É o erro
da lição 02. Quando a equipe o corrige, o script de testes fica **vermelho**. Um dos cinco testes esperava os
$99.00. Estava verde fazia três meses porque o erro estava lá.

---

## Antes de começar

**Você precisa da loja de pé.** Como nas lições 06 a 12: `./practicar` no seu computador e, em outra janela, o
terminal da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`.

> **Esta lição usa a loja da lição 11**, com os oito erros, de E1 a E8. Se `tienda error estado` mostrar menos,
> atualize a sua loja antes de seguir.

**Você precisa das suas coleções** da lição 07 (`tienda.postman_collection.json`) e da 08
(`permisos.postman_collection.json`), com o seu ambiente `local.postman_environment.json` **como você o deixou na
lição 08**, com `otra_cliente` e `otra_contrasena`. Se você mudou algo nelas depois, deixe-as como estavam quando
passaram no `verifica`.

**O que você já sabe e vai usar:** da lição 02, a regra do frete grátis a partir de $999.00; da 03, que com cupom o
frete grátis se mede **depois** do desconto; da 07, `newman run`; da 09, o código de saída (0 é verde), `$(…)` e as
funções do bash; da 11, as variáveis do ambiente com `export`; e das lições 04, 08, 09, 10 e 11, qual erro cada uma
encontrou.

**Resolva o exercício 2 sem IA.** Assim você pratica revisar o esperado com o seu próprio critério, que é justamente o
que esse exercício treina.

**Comece limpo:**

```bash
tienda reiniciar
tienda error estado
```

Os oito erros têm que dizer «desligado».

---

## Passo 1 · Um verde que nunca foi vermelho

Quando um teste fica verde, há duas explicações possíveis: a loja funciona, ou o teste não está olhando para o que
você pensa. De fora, elas se veem iguais. A única forma de distingui-las é **colocar o erro de propósito** e ver se o
teste fica vermelho.

As equipes que fazem isso a sério usam ferramentas que semeiam erros pequenos no código, um por um, e rodam os testes
a cada vez. Chama-se **teste de mutação**. A documentação do PIT, uma dessas ferramentas, explica em duas linhas: se os
seus testes falham, a mutação foi morta; se passam, a mutação sobreviveu. A porcentagem de mutações que os seus testes
matam é um sinal útil de quão bem eles detectam falhas. O Google a avaliou dentro da sua revisão de código, com mais
de 24.000 programadores.

Na loja você não precisa de ferramenta: os oito erros já estão semeados e você os liga com um comando. É a mesma ideia,
à mão.

**Cuidado com um número que se confunde com este: a cobertura**, a porcentagem do código que os seus testes tocam.
Martin Fowler adverte que um número alto de cobertura é fácil demais de alcançar com testes de baixa qualidade. Tocar
o código não é revisá-lo: um teste pode passar pelo cálculo do frete e nunca comparar o resultado com nada.

---

## Passo 2 · Semeie os oito erros

Você vai ligar cada erro, sozinho, rodar as suas duas coleções e anotar se ficaram vermelhas. Oito erros vezes duas
coleções são dezesseis rodadas; um laço as faz por você.

**Primeiro, sem nenhum erro.** Um vermelho no laço só significa algo se a coleção sai verde com a loja limpa. Se uma
coleção falha por outro motivo (um arquivo que não está lá, um ambiente sem `otra_cliente`, a loja desligada), no laço
ela sairia vermelha com todos os erros e pareceria pegar todos.

```bash
tienda reiniciar
newman run tienda.postman_collection.json -e local.postman_environment.json
tienda reiniciar
newman run permisos.postman_collection.json -e local.postman_environment.json
```

As duas têm que terminar sem nenhuma verificação falhada. Se alguma falhar, conserte-a antes de seguir: o laço esconde
a saída do newman e aí você já não veria por quê.

Agora escreva isto num arquivo, `~/practica/siembra.sh`:

```bash
for e in E1 E2 E3 E4 E5 E6 E7 E8; do
  tienda error $e on > /dev/null
  tienda reiniciar > /dev/null
  newman run tienda.postman_collection.json -e local.postman_environment.json > /dev/null && L07=verde || L07=vermelha
  tienda reiniciar > /dev/null
  newman run permisos.postman_collection.json -e local.postman_environment.json > /dev/null && L08=verde || L08=vermelha
  echo "$e  07: $L07  08: $L08"
  tienda error $e off > /dev/null
done
```

O novo está numa única linha: `&& L07=verde || L07=vermelha`. Depois de `&&` vai o que se faz **se o comando de antes
terminou em 0**, e depois de `||`, o que se faz **se não**. É o código de saída da lição 09, usado para decidir.
(Como `L07=verde` nunca falha, `L07=vermelha` só é executado quando o newman falhou.) O resto você já
conhece: `> /dev/null` joga fora a saída para que você veja só o resumo, e cada volta liga o erro, reinicia, roda e desliga.

Se você interromper o laço no meio (com Ctrl+C), um erro pode ficar ligado: rode `tienda error estado` e desligue o
que disser «ligado».

**Preveja antes de rodar:** com quais dos oito erros você acha que cada coleção fica vermelha? Escreva.

```bash
bash siembra.sh
```

```text
E1  07: vermelha  08: verde
E2  07: verde  08: verde
E3  07: verde  08: verde
E4  07: verde  08: verde
E5  07: verde  08: vermelha
E6  07: verde  08: verde
E7  07: verde  08: verde
E8  07: verde  08: verde
```

Foi assim que saiu com as coleções de exemplo do curso, em uns oito segundos. Se as suas coleções não forem iguais às
de exemplo, a sua tabela pode sair diferente: o que conta é a **sua**.

Passe o seu resultado a um arquivo, `~/practica/siembra.md`, com esta forma:

```markdown
| Erro | Alguma ficou vermelha? | Qual |
|---|---|---|
| E1 | sim | 07 |
| E2 | não | |
| E3 | não | |
| E4 | não | |
| E5 | sim | 08 |
| E6 | não | |
| E7 | não | |
| E8 | não | |
```

Dois erros eliminados, seis sobreviventes. E as duas coleções saem verdes com a loja limpa, então até hoje você as via
igualmente boas.

Ao terminar, confira que tudo ficou desligado:

```bash
tienda error estado
```

---

## Passo 3 · Por que sobrevivem

Seis erros sobrevivem, e não porque as suas coleções estejam mal feitas. Cada erro vive num lugar da loja, e um teste
só o elimina se **passa por esse lugar, com a condição que o desperta**.

| Erro | O que faz | O que é preciso para vê-lo | Onde você o viu |
|---|---|---|---|
| E2 | Cupom duas vezes | Dois pedidos da mesma cliente com o cupom, pagos **ao mesmo tempo** | Lição 09, `al-mismo-tiempo.sh` |
| E3 | Cancela o que foi entregue | Um pedido que **avança** até enviado ou entregue | Lições 04 e 12 |
| E4 | Cobra em dobro ao tentar de novo | Um gateway **lento** e uma nova tentativa com a mesma chave | Lição 08 |
| E6 | Data em UTC | O relógio da loja **fora de hora**, como a noite de 31 de dezembro | Lição 09, `tienda reloj` |
| E7 | A cobrança tardia não é conciliada | Um gateway que **demora** 7 segundos | Lição 10 |
| E8 | A página não deixa pagar | Pagar **pela página**, com o botão | Lição 11, `compra.py` |

No laço, as suas coleções da 07 e da 08 rodam com o gateway aprovando na hora, o relógio na hora real, um pagamento de
cada vez, sem avançar pedidos e sem abrir a página. Nenhuma dessas condições desperta estes seis.

Repare no E4: na lição 08 a sua coleção de permissões **o** pegou, mas com o gateway demorando 7 segundos. É a mesma
coleção; o que mudou foi a condição. Por isso uma tabela de semeadura vale para as condições com que você rodou, não
para a coleção em abstrato.

Isto muda como você lê um «tudo verde». **Um verde diz que o que você testou funciona, não que a loja funciona.** Para
saber o que você não está vendo, você semeia e olha o que sobrevive. Cada sobrevivente é uma pergunta: esse erro me
importa? Se sim, você precisa do teste que o desperte.

---

## Passo 4 · O teste que abençoa

Agora o caso da cena. Copie estes testes herdados em `~/practica/heredadas.sh`:

```bash
# Testes herdados do carrinho. Cada um imprime ✅ ou ❌; se algum falhar, o script termina em 1.
BASE=${TIENDA_URL:-http://localhost:8080}
FALLAS=0
revisa() {  # revisa "nome" "esperado" "obtido"
  if [ "$2" = "$3" ]; then echo "✅ $1"; else echo "❌ $1: esperava $2, veio $3"; FALLAS=1; fi
}
TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)
carrito() {  # carrito <quantidade de camisetas azuis>
  curl -s -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d "{\"cantidad\":$1}"
}
revisa "uma camiseta: subtotal" '$333.00' "$(carrito 1 | jq -r .subtotal.texto)"
revisa "uma camiseta: paga frete" '$99.00' "$(carrito 1 | jq -r .envio.texto)"
revisa "três camisetas: subtotal" '$999.00' "$(carrito 3 | jq -r .subtotal.texto)"
revisa "três camisetas: frete" '$99.00' "$(carrito 3 | jq -r .envio.texto)"
revisa "duas camisetas: paga frete" '$99.00' "$(carrito 2 | jq -r .envio.texto)"
exit $FALLAS
```

Como se lê:

| Parte | O que faz |
|---|---|
| `BASE=${TIENDA_URL:-http://localhost:8080}` | O endereço da loja: o de `TIENDA_URL` se você o tiver definido (lição 11), e se não, `http://localhost:8080` |
| `FALLAS=0` | Começa sem falhas; cada teste vermelho a põe em 1 |
| `revisa() { … }` | Uma função, como as da lição 09. Compara o esperado com o obtido e imprime ✅ ou ❌ |
| `carrito() { … }` | Outra função: deixa no carrinho N camisetas azuis e devolve o carrinho |
| `$1`, `$2`, `$3` | O que você passa à função, em ordem. Em `revisa`, o nome, o esperado e o obtido |
| As cinco linhas `revisa …` | Os cinco testes |
| `exit $FALLAS` | Termina em 0 se todos passaram e em 1 se algum falhou |

O script lê a cliente e a senha dela do ambiente, como o seu `compra.py` da lição 11:

```bash
export CLIENTE=Marta
export CONTRASENA=marta-practica
```

**Primeiro, como estava a loja que a equipe herdou:** com o E1 ligado.

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ uma camiseta: subtotal
✅ uma camiseta: paga frete
✅ três camisetas: subtotal
✅ três camisetas: frete
✅ duas camisetas: paga frete
0
```

Cinco verdes. Assim se via durante três meses.

**Qual abençoa o erro?** Há duas formas de encontrá-lo, e convém usar as duas.

**A primeira é ler cada esperado contra a regra.** O valor esperado de um teste não sai do que a loja responde: sai da
regra. O glossário do ISTQB diz assim: o resultado esperado é o comportamento que se prevê **a partir da base do
teste**, isto é, da história, da regra ou do requisito. Pegue cada linha e pergunte a ela pela regra da lição 02,
«frete grátis a partir de $999.00»:

| # | Teste | Esperado | O que a regra diz? |
|---|---|---|---|
| 1 | uma camiseta: subtotal | $333.00 | O preço da camiseta: $333.00 ✔ |
| 2 | uma camiseta: paga frete | $99.00 | $333.00 é menos que $999.00: paga $99.00 ✔ |
| 3 | três camisetas: subtotal | $999.00 | 3 × $333.00 ✔ |
| 4 | três camisetas: frete | $99.00 | $999.00 é «a partir de $999.00»: frete **grátis**. A regra diz $0.00 ✘ |
| 5 | duas camisetas: paga frete | $99.00 | $666.00 é menos que $999.00: paga $99.00 ✔ |

**A segunda é tirar o erro e ver o que fica vermelho.** Numa equipe, isso é rodar os testes contra a versão corrigida.
Aqui é desligar o E1:

```bash
tienda reiniciar
tienda error E1 off
bash heredadas.sh; echo $?
```

```text
✅ uma camiseta: subtotal
✅ uma camiseta: paga frete
✅ três camisetas: subtotal
❌ três camisetas: frete: esperava $99.00, veio $0.00
✅ duas camisetas: paga frete
1
```

As duas formas apontam para o **4**. O esperado dele não sai da regra: tudo indica que foi tirado do que a loja
respondia, que com o E1 dava $99.00. Assim, o teste virou o guarda-costas do erro: com o erro, verde; no dia em que
alguém o corrige, vermelho, e a primeira coisa que pensa quem o vê é que a correção quebrou algo.

**Corrija-o.** Em `heredadas.sh`, troque o esperado do teste 4 de `'$99.00'` para `'$0.00'`. Agora ele deve fazer o
contrário de antes:

```bash
tienda reiniciar
bash heredadas.sh; echo $?
```

```text
✅ uma camiseta: subtotal
✅ uma camiseta: paga frete
✅ três camisetas: subtotal
✅ três camisetas: frete
✅ duas camisetas: paga frete
0
```

```bash
tienda reiniciar
tienda error E1 on
bash heredadas.sh; echo $?
```

```text
✅ uma camiseta: subtotal
✅ uma camiseta: paga frete
✅ três camisetas: subtotal
❌ três camisetas: frete: esperava $0.00, veio $99.00
✅ duas camisetas: paga frete
1
```

Verde sem o erro, vermelho com ele. **Agora sim você o viu vermelho pela razão certa**, e é isso que o faz servir.
Desligue o E1:

```bash
tienda error E1 off
```

---

## Passo 5 · Testes escritos por uma IA

Hoje é comum pedir a uma IA que escreva testes. Ela escreve muitos, rápido, e costumam sair verdes. Esse último ponto é
justamente o que precisa ser revisado.

A Meta publicou como funciona a sua ferramenta para gerar testes com IA. Quando um
teste gerado falha, a ferramenta não consegue saber se encontrou um erro ou se só traz uma comparação incorreta, e
eles dizem que o mais provável é a segunda hipótese. Por isso, no fluxo automático dela, **descarta todo teste que não
passa na primeira rodada**. Para eles faz sentido: a ferramenta deles acrescenta testes aos que já existem, e não
consegue saber sozinha qual esperado é o correto.

Pense no que isso significa numa loja que tem um erro: um teste que passa de primeira descreve o que a loja **faz**,
não o que ela **deve** fazer. Se a loja faz algo errado, esse teste o abençoa, igual ao teste 4. A OWASP, na
lista de riscos das aplicações com IA, diz sem rodeios: o que um modelo gera, uma pessoa revisa.

A regra é a mesma de qualquer teste, venha de quem vier:

1. **De onde saiu o esperado?** Da regra ou da história, não do que a loja responde hoje.
2. **Você o viu vermelho?** Semeie o erro que ele deveria pegar e confira que fica vermelho.
3. **Contra o quê ele compara?** Um teste que compara a loja consigo mesma (pede duas vezes o mesmo dado e compara as
   duas respostas) não confere regra nenhuma: continua verde com qualquer erro. Fowler cita como o caso mais absurdo
   os testes que não verificam nada; este se parece muito com eles.

---

## Como se confere

**O seu trabalho** é conferido pelo `verifica 13`. Em `~/practica` ele precisa de três arquivos:

- `siembra.md`, a sua tabela do passo 2;
- `bendice.txt`, com **só o número** do teste que abençoava o erro;
- `heredadas.sh`, com esse teste corrigido.

No terminal da loja, escreva:

```bash
verifica 13
```

O `verifica`:

1. roda as suas coleções da 07 e da 08, com o seu ambiente, com cada erro ligado sozinho, e compara o que aconteceu com
   o seu `siembra.md`, linha por linha (aceita «sim», «nao» e «não», com maiúsculas ou sem elas);
2. nessa mesma rodada, no mínimo a sua coleção da 07 tem que sair vermelha com o E1 e a da 08 com o E5, como nas
   respectivas lições. Se pegarem mais erros, melhor;
3. confere que `bendice.txt` diga o número certo;
4. roda o seu `heredadas.sh` com a loja limpa: tem que terminar em 0, com **cinco** ✅, e o quarto teste tem que
   esperar `$0.00`;
5. roda com o E1 ligado: **não** pode terminar em 0.

O ponto 2 existe por causa do exercício 3: se você deixar a sua coleção com o esperado trocado, a tabela sairia
honesta, mas a sua coleção já não pegaria o E1. O ponto 4 pede cinco ✅ para que o teste seja corrigido, não apagado:
sem o teste 4, o script sai verde com o E1 e o ponto 5 o rejeita. Ele passa ao script o endereço, a cliente e a senha
pelo ambiente. Liga e desliga os erros sozinho e reinicia a loja, então **apaga os seus pedidos, o seu carrinho e a
sua sessão**.

Com tudo no lugar, o `verifica 13` fica assim:

```text
Verificando a lição 13…

✅ Seu arquivo tienda.postman_collection.json está em ~/practica
✅ Seu arquivo permisos.postman_collection.json está em ~/practica
✅ Seu arquivo local.postman_environment.json está em ~/practica
✅ Seu arquivo siembra.md está em ~/practica
✅ Seu arquivo bendice.txt está em ~/practica
✅ Seu arquivo heredadas.sh está em ~/practica
✅ Seu local.postman_environment.json traz base, cliente, contrasena, otra_cliente e otra_contrasena, como você deixou na lição 08
✅ Seu siembra.md tem as oito linhas, de E1 a E8, com «sim» ou «não»
✅ Seu bendice.txt diz 4: o teste que abençoava o erro
✅ O quarto teste do seu heredadas.sh espera $0.00, o que a regra diz
✅ Com a loja limpa, sua coleção da 07 sai em verde (3)
✅ Com a loja limpa, sua coleção da 08 sai em verde (12)
✅ Seu siembra.md coincide com o que aconteceu, linha por linha
✅ Sua coleção da 07 fica vermelha com E1 e a da 08 com E5, como nas lições delas
✅ Com a loja limpa, seu heredadas.sh termina em 0 com cinco ✅
✅ Com E1 ligado, seu heredadas.sh não termina em 0: agora pega o erro

🎉 Lição completa!
```

Na medição levou uns 22 segundos. Ao terminar, deixa os erros como estavam antes de você rodá-lo e a loja
reiniciada: Marta sem pedidos, com o carrinho em $0.00 e sem sessão aberta.

**Antes de dar a lição por terminada, revise:**

- [ ] Antes do laço, as suas duas coleções saíram verdes com a loja limpa.
- [ ] `siembra.md` tem oito linhas, E1 a E8, com «sim» ou «não».
- [ ] Cada «sim» diz qual coleção ficou vermelha.
- [ ] Antes de rodar o laço você escreveu a sua previsão, e a comparou.
- [ ] Para cada sobrevivente você sabe que condição falta às suas coleções (passo 3).
- [ ] `bendice.txt` traz só um número.
- [ ] Em `heredadas.sh`, o teste que você corrigiu continua lá, com o esperado tirado da regra.
- [ ] Você viu `heredadas.sh` verde com a loja limpa e vermelho com o E1.
- [ ] Você deixou todos os erros desligados (`tienda error estado`).

---

## Seus exercícios

1. **Desperte um sobrevivente.** Escolha o E3. Com os seus passos da lição 12 (`pasos.sh`), ligue o E3, rode-os e veja
   se ficam «vermelhos»: que linha lhe diz que o erro está lá? Desligue o E3. Por que os seus passos o veem e a sua
   coleção da 07 não?
2. **Testes escritos por uma IA** (sem IA). Uma IA escreveu estes seis testes para o carrinho, com a mesma função
   `revisa` do passo 4. Todos, menos um, saem verdes na loja que ela tinha naquele momento. Para cada um decida se é
   **bom**, se **abençoa um erro**, se **não confere regra nenhuma** ou se **está errado**, e escreva por quê em uma
   linha. Use a regra do frete (lição 02) e a do cupom com frete (lição 03).

   | # | Teste |
   |---|---|
   | 1 | `revisa "uma camiseta: total" '$432.00' "$(carrito 1 \| jq -r .total.texto)"` |
   | 2 | `revisa "três camisetas: total" '$1,098.00' "$(carrito 3 \| jq -r .total.texto)"` |
   | 3 | `revisa "três camisetas com cupom: frete" '$99.00' "…"` (três camisetas e o cupom BIENVENIDA10) |
   | 4 | `revisa "três camisetas: frete" "$(carrito 3 \| jq -r .envio.texto)" "$(carrito 3 \| jq -r .envio.texto)"` |
   | 5 | `revisa "uma camiseta com cupom: desconto" '$0.00' "…"` (uma camiseta, tente o cupom BIENVENIDA10 e depois leia o carrinho) |
   | 6 | `revisa "duas camisetas: frete" '$0.00' "$(carrito 2 \| jq -r .envio.texto)"` |

3. **A sua coleção o pega?** Abra a sua coleção da lição 07 e procure o teste que ficou vermelho com o E1. Troque o
   esperado dele para que diga o que a loja responde **com** o E1. Preveja: o que sai agora em `siembra.sh`? Rode-o e
   depois devolva o teste como estava.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. O que quer dizer que um erro «sobrevive»? (passo 1)
2. A sua coleção da lição 07 está verde com o E3 ligado. Isso quer dizer que o E3 não faz mal? (passo 3)
3. Quais são as duas formas de encontrar o teste que abençoa um erro? (passo 4)
4. De onde sai o valor esperado de um teste? (passo 4)
5. Uma IA lhe entrega vinte testes, todos verdes de primeira. O que você faz antes de aceitá-los? (passo 5)

---

## Para fechar

Até a lição 12 você escreveu testes para encontrar erros. Esta lição pôs os seus testes à prova.

O que fica com você daqui:

- **Um teste serve se ficar vermelho quando o erro está lá.** Enquanto você não o vir vermelho, ele ainda não lhe deu
  evidência de que o detecta.
- **Semear lhe diz o que você não vê.** Com a loja, você faz isso com um comando; as equipes grandes fazem com
  ferramentas de teste de mutação. O resultado é o mesmo: uma lista de sobreviventes.
- **Um erro sobrevive quando os seus testes não passam pelo lugar dele com a condição que o desperta.** Não é que o
  teste esteja ruim: é que ele olha outra coisa.
- **O esperado sai da regra, não do que a loja responde hoje.** Um teste que copia a resposta do sistema abençoa
  qualquer erro que o sistema já tenha.
- **A regra vale igual para testes escritos por uma IA**: de onde saiu o esperado, se você o viu vermelho e se ele
  pode ficar vermelho.

Na lição 14 você junta tudo o que aprendeu numa história nova, com os erros semeados da loja.

---

## Compare as respostas

**Passo 2, a previsão.** A coleção da 07 fica vermelha só com o E1, porque confere o frete de um carrinho de $999.00.
A da 08, só com o E5, porque confere que o Luis não veja o pedido da Marta. O E8 também não as deixa vermelhas:
nenhuma das duas abre a página. Se você previu mais vermelhos, não se preocupe: é o que quase todo mundo espera de um
«tudo verde». O passo 3 explica por que não.

**Exercício 1.** Com o E3, o cancelamento dos seus passos responde `cancelar: HTTP 200` e o pedido fica cancelado com
reembolso; sem o E3, 409. Os seus passos o veem porque levam o pedido até entregue e depois cancelam: passam pelo lugar
do erro com a condição que o desperta. A sua coleção da 07 nunca avança um pedido nem cancela.

**Exercício 2.**

| # | O que é? | Por quê |
|---|---|---|
| 1 | Bom | $333.00 + $99.00 de frete = $432.00, e é isso que a regra diz |
| 2 | Abençoa um erro | Três camisetas são $999.00: frete grátis, total $999.00. $1,098.00 só sai com o E1. A IA copiou o que a loja respondia |
| 3 | Bom | Com cupom, o frete se mede depois do desconto: $999.00 − $99.90 = $899.10, menos que $999.00, então paga $99.00 (lição 03) |
| 4 | Não confere regra nenhuma | Compara a resposta da loja com a mesma resposta. Sai verde com qualquer erro |
| 5 | Bom | O cupom é para compras a partir de $500.00. Com $333.00 a loja o rejeita (422, «o cupom é para compras de $500.00 ou mais») e o carrinho fica com desconto de $0.00. Atenção: a resposta do 422 não traz `descuento`; por isso o teste lê o carrinho depois |
| 6 | Está errado | Duas camisetas são $666.00: paga $99.00. Este é o que saía vermelho, com a loja sã |

O 3 e o 6 são os difíceis. O 3 parece abençoar algo porque espera frete com $999.00, mas a regra do cupom lhe dá
razão. O 6 é vermelho e não há erro nenhum: segundo a Meta, quando um teste gerado falha, o mais provável é uma
verificação errada. Por isso não se descarta sem olhar: lê-se contra a regra e depois se decide.

**Exercício 3.** Com o E1, a coleção da 07 sai **verde**: agora ela abençoa o E1. E com a loja limpa sai vermelha. Em
`siembra.sh`, a linha do E1 passa a «07: verde». Você trocou um número e o teste deixou de servir: é assim tão fácil
escrever um teste que abençoa.

**Revisão.**

1. Que você o semeia e todos os seus testes continuam verdes: nenhum o percebe.
2. Não. Quer dizer que a sua coleção não passa por ali: nunca avança um pedido nem o cancela. O E3 devolve o dinheiro
   de pedidos entregues.
3. Ler cada esperado contra a regra, e tirar o erro (ou rodar a versão corrigida) para ver qual fica vermelho.
4. Da regra, da história ou do requisito. O que o sistema responde hoje é justamente o que você está conferindo: não
   pode ser também o esperado.
5. Revisar de onde saiu cada esperado, semear os erros que eles deveriam pegar para vê-los vermelhos, e descartar os
   que não podem ficar vermelhos.

---

## Fontes da lição

1. PIT, «What is mutation testing?» (consultado em 22 de novembro de 2026). «If your tests fail then the mutation is
   killed, if your tests pass then the mutation lived.»; «The quality of your tests can be gauged from the percentage
   of mutations killed.» https://pitest.org/
2. Stryker Mutator, «Introduction» (consultado em 22 de novembro de 2026). «Bugs, or mutants, are automatically
   inserted into your production code. Your tests are run for each mutant.»; «If your tests passed, the mutant
   survived.» https://stryker-mutator.io/docs/
3. Goran Petrović, Marko Ivanković, Gordon Fraser e René Just, «Practical Mutation Testing at Scale» (arXiv, 2021;
   consultado em 22 de novembro de 2026). «Mutation analysis assesses a test suite's adequacy by measuring its
   ability to detect small artificial faults, systematically seeded into the tested program.»; «Evaluation in a
   code-review-based setting with more than 24,000 developers on more than 1,000 projects…»
   https://arxiv.org/abs/2102.11378
4. Martin Fowler, «TestCoverage» (consultado em 22 de novembro de 2026). «The trouble is that high coverage numbers
   are too easy to reach with low quality testing.»; «At the most absurd level you have AssertionFreeTesting.»
   https://martinfowler.com/bliki/TestCoverage.html
5. ISTQB, «Glossary»: *expected result* e *test oracle* (consultado em 22 de novembro de 2026). «The observable
   predicted behavior of a test item under specified conditions based on its test basis.»; «A source to determine an
   expected result.» https://glossary.istqb.org/en_US/term/expected-result
6. Nadia Alshahwan e outros, «Automated Unit Test Improvement using Large Language Models at Meta» (arXiv, 2024;
   consultado em 22 de novembro de 2026). «Any test that does not pass may reveal a fault. However, it is more likely
   that the test simply contains an incorrect assertion.»; «Therefore, […] discards any test case that does
   not pass on first execution.» https://arxiv.org/abs/2402.09171
7. OWASP Gen AI Security Project, «LLM09:2025 Misinformation» (consultado em 25 de novembro de 2026).
   «Implement human oversight and fact-checking processes, especially for critical or sensitive information.»; «if
   trusted without verification, leads to security risks.»
   https://genai.owasp.org/llmrisk/llm092025-misinformation/
8. GNU Bash Reference Manual, «Lists of Commands» (consultado em 22 de novembro de 2026). «command2 is executed if,
   and only if, command1 returns an exit status of zero (success).»; «command2 is executed if, and only if, command1
   returns a non-zero exit status.» https://www.gnu.org/software/bash/manual/html_node/Lists.html
