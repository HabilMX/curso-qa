# Lição 09 — Ao mesmo tempo e fora de hora

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

**Antes de ler, três palavras.** Uma linha cada uma; as demais chegam no passo em que são usadas.

- **Em paralelo:** duas requisições que saem juntas, sem que uma espere a outra terminar.
- **Condição de corrida:** um erro que só aparece quando duas coisas acontecem quase ao mesmo tempo e uma se mete no meio
  da outra.
- **Fuso horário:** a diferença entre a hora de um lugar e a hora UTC, a hora de referência do mundo. A loja de prática
  escreve a sua no fim de cada hora: `-06:00`, seis horas atrás do UTC.

**O que fica com você:** um script de terminal que paga dois pedidos ao mesmo tempo e uma coleção que confere a data de um
pedido contra a hora da loja. Os dois saem verdes quando a loja está certa e vermelhos quando o cupom é usado duas vezes
ou quando o pedido fica com o dia, o mês ou o ano errado.

**Ideia nova desta lição (a única):** o que uma pessoa faz de um em um, o sistema recebe em paralelo e a qualquer hora.

**Em que ordem vai:** você paga dois pedidos com o mesmo cupom, um depois do outro (passo 1) e ao mesmo tempo (passo 2);
repete o script para ver que o resultado não muda (passo 3); mexe no relógio da loja (passo 4) e testa a data de um
pedido ao meio-dia e fora de hora (passo 5).

---

## A cena

*Cenário inventado; as respostas, os testes e os erros da loja são reais.*

No dia 1º de janeiro de manhã, a equipe da loja examina duas coisas estranhas.

A primeira: uma cliente usou o cupom BIENVENIDA10 em **dois** pedidos. O cupom é de uso único, e o teste da equipe
confirmava isso: pagava um pedido com o cupom, depois o outro, e o segundo saía recusado. A cliente não fez nada de
estranho. Estava com a loja aberta no celular e no computador, e apertou «Pagar» nos dois quase ao mesmo tempo.

A segunda: o relatório de vendas de dezembro não fecha. Os pedidos da noite do dia 31, das seis da tarde em diante,
aparecem como vendas de **janeiro do ano seguinte**.

Os testes da equipe estavam verdes. Todos rodavam uma requisição de cada vez, e todos rodavam ao meio-dia.

---

## Antes de começar

**Você precisa da loja no ar.** Como nas lições 07 e 08: `TIENDA_IDIOMA=pt ./practicar` no seu computador e, em outra
janela, o terminal da loja. Tudo se faz **lá dentro**, na sua pasta `~/practica`.

> **Esta lição usa a loja da lição 09.** Ela traz o erro E2 «cupom duas vezes» e o erro E6 «data em UTC». Se
> `tienda error E6 on` te disser que esse erro não existe, atualize a sua loja antes de seguir: com uma versão anterior,
> as suas saídas não vão coincidir.

**O que você já sabe e vai usar:** da lição 06, `curl` com `-X`, `-H` e `-d`, e o token em uma variável; da 07,
`newman run`, `jq empty` e o ambiente `local`; da 08, `pm.collectionVariables` e comparar um valor contra outro da
própria loja; da 01, a regra R4: o cupom vence em 31 de dezembro às 23:59, horário da Cidade do México.

**Faça o passo 1 sem IA.** O que você treina ali é prever o que acontece com um erro que você ainda não vê.

**Comece limpo antes de cada rodada:**

```bash
tienda reiniciar
```

```text
✅ a loja voltou ao estado de recém-aberta
```

O `tienda reiniciar` também devolve o relógio da loja à hora real. Se no passo 4 ou 5 você quiser outra hora, coloque-a
**depois** de reiniciar.

**Quanto tempo:** cerca de 60 minutos (estimativa; vamos ajustá-la com a primeira turma de alunos).

---

## Passo 1 · Dois pedidos com o mesmo cupom, um depois do outro

BIENVENIDA10 é de uso único por cliente. A loja não o confere só ao aplicá-lo ao carrinho: confere de novo ao **pagar**,
porque uma cliente pode ter o cupom em dois pedidos que ainda não pagou.

Você vai escrever um script: um arquivo com comandos de terminal que rodam em ordem, como se você os digitasse um por um.
Assim dá para repeti-lo com um só comando.

```bash
nano al-mismo-tiempo.sh
```

```bash
#!/bin/bash
# Dois pedidos com o mesmo cupom, pagos ao mesmo tempo. Termina em 0 se o cupom foi usado uma vez e em 1 se foi usado duas.
BASE=http://localhost:8080
CLIENTE=Marta
CONTRASENA=marta-practica

TOKEN=$(curl -s -X POST $BASE/api/sesiones -H 'Content-Type: application/json' \
  -d "{\"cliente\":\"$CLIENTE\",\"contrasena\":\"$CONTRASENA\"}" | jq -r .token)

pedido_con_cupon() {
  curl -s -o /dev/null -X PUT $BASE/api/carrito/productos/playera-azul -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"cantidad":2}'
  curl -s -o /dev/null -X POST $BASE/api/carrito/cupon -H "Authorization: Bearer $TOKEN" \
    -H 'Content-Type: application/json' -d '{"codigo":"BIENVENIDA10"}'
  curl -s -X POST $BASE/api/pedidos -H "Authorization: Bearer $TOKEN" | jq -r 'select(.cupon == "BIENVENIDA10") | .id'
}

pagar() {
  curl -s -o /dev/null -w "pagamento do pedido $1: %{http_code}\n" -X POST $BASE/api/pedidos/$1/pago \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: al-mismo-tiempo-$1-$$" -d '{"tarjeta":"4242 4242 4242 4242"}'
}

UNO=$(pedido_con_cupon)
DOS=$(pedido_con_cupon)
if [ -z "$UNO" ] || [ -z "$DOS" ]; then
  echo "Não consegui fazer os dois pedidos com o cupom. Rode tienda reiniciar e tente de novo."
  exit 2
fi

pagar $UNO
pagar $DOS

PAGADOS=0
for P in $UNO $DOS; do
  ESTADO=$(curl -s $BASE/api/pedidos/$P -H "Authorization: Bearer $TOKEN" | jq -r .estado)
  echo "pedido $P: $ESTADO"
  if [ "$ESTADO" = "pagado" ]; then PAGADOS=$((PAGADOS + 1)); fi
done

if [ $PAGADOS -eq 2 ]; then
  echo "VERMELHO: o cupom foi usado duas vezes"
  exit 1
fi
if [ $PAGADOS -ne 1 ]; then
  echo "Não consegui conferir: nenhum pedido ficou pago. A loja está no ar?"
  exit 2
fi
echo "VERDE: o cupom foi usado uma só vez"
```

Parece longo, mas são as mesmas requisições da lição 06, com três coisas novas:

| Parte | O que faz |
|---|---|
| `TOKEN=$(curl … \| jq -r .token)` | Faz login e guarda o token, sem que você o copie à mão. `jq -r .token` tira o campo `token` da resposta |
| `pedido_con_cupon() { … }` e `pagar() { … }` | São **funções**: um grupo de comandos com nome. `pedido_con_cupon` põe duas camisetas no carrinho, aplica o cupom, faz o pedido e escreve o número dele só se o pedido de fato leva o cupom. `pagar 1` paga o pedido 1 e escreve o código que a loja respondeu |
| `exit 0`, `exit 1`, `exit 2` | O **código de saída** do script, como o do newman na lição 07: 0 se o cupom foi usado uma vez, 1 se foi usado duas, e 2 se não deu para conferir (não fez os pedidos, ou nenhum ficou pago). Assim um problema de conexão nunca sai como verde. No final não precisa de `exit 0`: um script que chega ao fim sem erro termina em 0 |

A chave de idempotência leva `$$`, o número do processo que roda o script: muda a cada rodada, então cada pagamento tem a
sua própria chave, como pede a lição 08.

Salve e confira que o bash consegue lê-lo:

```bash
bash -n al-mismo-tiempo.sh
```

Se não imprimir nada, o arquivo está bem escrito. Se imprimir uma linha, ela diz o número da linha com o problema: abra-o
no nano e revise-a; quase sempre é uma aspa ou uma chave que falta.

Dê a ele permissão para rodar (uma só vez) e rode-o:

```bash
chmod +x al-mismo-tiempo.sh
tienda reiniciar
./al-mismo-tiempo.sh
echo "saída: $?"
```

```text
pagamento do pedido 1: 200
pagamento do pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: o cupom foi usado uma só vez
saída: 0
```

O primeiro pagamento entra com o cupom; o segundo recebe 422, «já usou este cupom», e esse pedido continua sem pagar. A
loja está certa.

**Agora preveja, no papel:** você vai ligar o E2, o erro «cupom duas vezes», e rodar o mesmo script. Verde ou vermelho?
Escreva a sua previsão antes de seguir.

```bash
tienda error E2 on
tienda reiniciar
./al-mismo-tiempo.sh
echo "saída: $?"
```

```text
pagamento do pedido 1: 200
pagamento do pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: o cupom foi usado uma só vez
saída: 0
```

Verde, com o erro ligado. Se você previu vermelho, o seu raciocínio fazia sentido: o erro se chama «cupom duas vezes» e o
script usa o cupom duas vezes. Mas os dois pagamentos vão **um depois do outro**: quando chega o segundo, o primeiro já
anotou que o cupom foi usado, e a loja o recusa. É assim que uma pessoa testa, e é assim que testava a equipe da cena. O
erro está ali e este teste não o vê.

---

## Passo 2 · Os dois pagamentos ao mesmo tempo

A cliente da cena não pagou um depois do outro: apertou «Pagar» em duas telas quase ao mesmo tempo. Para a loja, são duas
requisições **em paralelo**.

No terminal, `&` no fim de um comando o manda **para o fundo**: o terminal não espera ele terminar e passa em seguida ao
próximo. `wait` espera terminarem todos os que você mandou para o fundo. Abra o script:

```bash
nano al-mismo-tiempo.sh
```

e troque estas duas linhas:

```bash
pagar $UNO
pagar $DOS
```

por estas três:

```bash
pagar $UNO &
pagar $DOS &
wait
```

Nada mais. Com o E2 ainda ligado:

```bash
tienda reiniciar
./al-mismo-tiempo.sh
echo "saída: $?"
```

```text
pagamento do pedido 1: 200
pagamento do pedido 2: 200
pedido 1: pagado
pedido 2: pagado
VERMELHO: o cupom foi usado duas vezes
saída: 1
```

Essa é a cena: dois pedidos pagos com o mesmo cupom de uso único.

**O que aconteceu lá dentro?** Com o E2, a loja **confere** se o cupom já foi usado e, um momento depois, **anota** que foi
usado, sem conferir de novo. Entre conferir e anotar há uma **janela**. Se o segundo pagamento confere dentro dessa
janela, o primeiro ainda não anotou nada: os dois veem o cupom livre e os dois seguem para a cobrança. Um depois do outro,
o segundo sempre chega quando a janela já fechou; ao mesmo tempo, cai dentro.

Desligue o E2 e rode igual, com os pagamentos em paralelo:

```bash
tienda error E2 off
tienda reiniciar
./al-mismo-tiempo.sh
echo "saída: $?"
```

```text
pagamento do pedido 1: 200
pagamento do pedido 2: 422
pedido 1: pagado
pedido 2: creado
VERDE: o cupom foi usado uma só vez
saída: 0
```

Com a loja certa, mesmo ao mesmo tempo, só um pagamento leva o cupom. Às vezes o 200 fica com o pedido 2 e o 422 com o 1, e
as duas linhas de «pagamento do pedido» saem em outra ordem: os dois pagamentos rodam ao mesmo tempo e qualquer um pode
terminar primeiro. O resultado é o mesmo.

---

## Passo 3 · O mesmo resultado toda vez

Um teste de algo que acontece «ao mesmo tempo» tem um risco: às vezes pegar o erro e às vezes não, conforme quem chegue
primeiro. Com um teste assim, um verde isolado ainda não basta para confiar. Antes de confiar no seu script, rode-o várias
vezes seguidas.

Com o E2 ligado, cinco vezes:

```bash
tienda error E2 on
for i in 1 2 3 4 5; do tienda reiniciar > /dev/null; ./al-mismo-tiempo.sh > /dev/null; echo "saída: $?"; done
```

```text
saída: 1
saída: 1
saída: 1
saída: 1
saída: 1
```

| Parte | O que faz |
|---|---|
| `for i in 1 2 3 4 5; do …; done` | Repete o que está no meio cinco vezes |
| `> /dev/null` | Joga fora a saída normal desse comando, para que você veja só o que importa |

Cinco de cinco em vermelho. Agora com o E2 desligado: têm de sair cinco `saída: 0`. Esta loja é feita para que a corrida
seja repetível: os dois pagamentos saem juntos e sempre caem na janela. Em uma loja de verdade, a janela pode ser de
milésimos de segundo, e aí você pode precisar de muitas mais tentativas; a ideia é a mesma.

Desligue o E2:

```bash
tienda error E2 off
```

---

## Passo 4 · A hora da loja

O outro erro da cena não depende de **como** as requisições chegam, e sim de **quando**. Para testar a noite do dia 31 de
dezembro você não precisa esperar o dia 31 de dezembro: a loja tem o seu próprio relógio e você o mexe.

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
```

```text
🕒 Hora da loja: 2026-12-31T23:30:00-06:00
```

A partir daí o relógio continua correndo, como um de verdade: um minuto depois vai dizer 23:31.

A hora se escreve como nas respostas da loja: ano-mês-dia, um `T` e a hora. O `-06:00` do final é o **fuso**: a loja está
seis horas atrás do UTC. A loja também te diz isso em `GET /api/salud`:

```bash
curl -s http://localhost:8080/api/salud
```

```json
{"estado":"arriba","hora_de_la_tienda":"2026-12-31T23:30:00-06:00"}
```

E a anota em cada pedido, no campo `creado`. Essa é a data que a sua coleção vai conferir.

Para voltar à hora real:

```bash
tienda reloj real
```

(O `tienda reiniciar` também a devolve.)

---

## Passo 5 · A data do pedido, ao meio-dia e fora de hora

O teste de que você precisa é simples de dizer: **o pedido tem de ficar com a data da loja**. Sem escrever nenhuma data à
mão: a coleção pergunta a hora à loja e compara.

É uma coleção nova, com o seu ambiente `local` da lição 07:

```bash
nano deshoras.postman_collection.json
```

```json
{
 "info": {
  "name": "Fora de hora",
  "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
 },
 "item": [
  {
   "name": "A hora da loja",
   "request": {
    "method": "GET",
    "url": "{{base}}/api/salud"
   },
   "event": [{"listen": "test", "script": {"exec": [
    "pm.test('código 200', () => pm.response.to.have.status(200));",
    "pm.collectionVariables.set('hoy', pm.response.json().hora_de_la_tienda.slice(0, 10));"
   ]}}]
  },
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
    "pm.test('mesmo ano da loja', () => pm.expect(pm.response.json().creado.slice(0, 4)).to.eql(pm.collectionVariables.get('hoy').slice(0, 4)));",
    "pm.test('mesmo dia da loja', () => pm.expect(pm.response.json().creado.slice(0, 10)).to.eql(pm.collectionVariables.get('hoy')));"
   ]}}]
  }
 ]
}
```

As três últimas requisições você já conhece da lição 08. O que é novo:

| Linha | O que faz |
|---|---|
| `hora_de_la_tienda.slice(0, 10)` | `slice(0, 10)` pega os dez primeiros caracteres de um texto. De `2026-12-31T23:30:00-06:00` deixa `2026-12-31`: a data, sem a hora |
| `pm.collectionVariables.set('hoy', …)` | Guarda essa data como `hoy`, para compará-la depois |
| `creado.slice(0, 4)` contra `hoy.slice(0, 4)` | Compara só o ano: `2026` contra `2026` |
| `creado.slice(0, 10)` contra `hoy` | Compara a data completa: ano, mês e dia |

Por que dois testes, se o do dia já inclui o ano? Porque, quando falha, o nome do teste vermelho te diz quão grave é: um
pedido no dia errado, ou no **ano** errado, que é o que quebra o relatório anual.

Confira o JSON e rode-a na hora real:

```bash
jq empty deshoras.postman_collection.json
tienda reiniciar
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ A hora da loja
  GET http://localhost:8080/api/salud [200 OK, 214B, 11ms]
  ✓  código 200

→ A cliente faz login
  POST http://localhost:8080/api/sesiones [201 Created, 214B, 5ms]
  ✓  código 201

→ Uma camiseta no carrinho
  PUT http://localhost:8080/api/carrito/productos/playera-azul [200 OK, 547B, 3ms]
  ✓  código 200

→ Ela faz o pedido
  POST http://localhost:8080/api/pedidos [201 Created, 681B, 3ms]
  ✓  código 201
  ✓  mesmo ano da loja
  ✓  mesmo dia da loja
```

Seis de seis. Os tamanhos e os tempos das saídas desta lição são os da medição; os seus podem mudar. Os códigos, os
vistos e os vermelhos, não.

**Agora ligue o E6, o erro «data em UTC», e rode-a ao meio-dia:**

```bash
tienda error E6 on
tienda reiniciar
tienda reloj 2026-11-21T12:00:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

Seis de seis **de novo**. Com o E6, a loja passa a hora para UTC, seis horas à frente, e a anota em `creado` sem fuso,
então já ninguém consegue saber de que fuso era. Ao meio-dia isso dá 18:00 do mesmo dia: a data não muda e o seu teste não
tem nada a ver com isso.

**Agora, fora de hora.** A noite do dia 31 de dezembro, depois de reiniciar:

```bash
tienda reiniciar
tienda reloj 2026-12-31T23:30:00
newman run deshoras.postman_collection.json -e local.postman_environment.json
```

```text
→ Ela faz o pedido
  POST http://localhost:8080/api/pedidos [201 Created, 675B, 3ms]
  ✓  código 201
  1. mesmo ano da loja
  2. mesmo dia da loja
```

E embaixo:

```text
 1.  AssertionError  mesmo ano da loja
                     expected '2027' to deeply equal '2026'
 2.  AssertionError  mesmo dia da loja
                     expected '2027-01-01' to deeply equal '2026-12-31'
```

Um pedido de 31 de dezembro às 23:30 ficou com data de 1º de janeiro de 2027. Essa é a segunda metade da cena. E não é
preciso o fim de ano: o último dia de um mês, à noite, também falha. Com a loja às 19:00 de 30 de novembro:

```text
 1.  AssertionError  mesmo dia da loja
                     expected '2026-12-01' to deeply equal '2026-11-30'
```

Um vermelho: o ano está certo, mas o pedido foi para dezembro.

Desligue o E6 ao terminar:

```bash
tienda error E6 off
tienda reiniciar
```

---

## Como se confere

**O seu script e a sua coleção** são revisados pelo `verifica 09`. Salve-os em `~/practica` como `al-mismo-tiempo.sh`
e `deshoras.postman_collection.json`, junto com o seu ambiente `local.postman_environment.json`, e no terminal da loja
escreva:

```bash
verifica 09
```

O `verifica`:

1. roda o seu script com a loja limpa: tem de terminar em **0**;
2. roda-o com E2 ligado: tem de terminar em **1**; se terminar em 0, os seus pagamentos não saíram ao mesmo tempo;
3. roda a sua coleção com a loja limpa, com o relógio em uma hora normal, em 30 de novembro às 23:30 e em 31 de
   dezembro às 23:30: as três vezes tem de sair **verde**;
4. roda-a com E6 ligado nessas mesmas horas: **pelo menos um teste tem de sair vermelho**;
5. confere que a sua coleção não tenha nenhuma data escrita à mão.

Se faltar algo, ele diz o que arrumar. Ele mexe no relógio e liga e desliga os erros sozinho. No fim, deixa ligados os
erros que você tinha ligado e o relógio na hora real, mas reinicia a loja: apaga os seus pedidos, o seu carrinho e a
sua sessão. Antes de rodá-lo, a lista abaixo diz se a forma está certa.

**Antes de dar a lição por terminada, confira:**

- [ ] O seu script paga os dois pedidos com `&` e `wait`, não um depois do outro.
- [ ] Com a loja limpa termina em 0; com E2 ligado, em 1, cinco de cinco vezes.
- [ ] A sua coleção tem quatro requisições e sai 6 de 6 com a loja limpa, na hora real e com
      `tienda reloj 2026-12-31T23:30:00`.
- [ ] Com E6 ligado, ao meio-dia sai verde e em 31 de dezembro às 23:30 falham «mesmo ano da loja» e
      «mesmo dia da loja».
- [ ] Na sua coleção não aparece nenhuma data (procure-as com `grep -nE '20[0-9]{2}-[0-9]{2}' deshoras.postman_collection.json`; não
      pode imprimir nada).
- [ ] Você deixou E2 e E6 desligados e o relógio na hora real (`tienda error estado` e `tienda reloj real`).

---

## Seus exercícios

1. **A hora exata.** Com E6 ligado, a partir de que hora de 30 de novembro a sua coleção começa a falhar? Preveja a hora
   com o fuso da loja, e depois confira com duas rodadas: um minuto antes e justo nessa hora. O relógio da loja continua
   correndo a partir da hora que você coloca, então escreva os três comandos em uma só linha, para que não passem
   segundos de um a outro:

   ```bash
   tienda reiniciar && tienda reloj 2026-11-30T17:59:00 && newman run deshoras.postman_collection.json -e local.postman_environment.json
   ```

   (e outra igual com a hora que você previu).
2. **O cupom à meia-noite.** A regra R4 da lição 01 diz que o cupom vence em 31 de dezembro às 23:59. Com `curl`, como na
   lição 06, e com a loja recém-reiniciada: faça login e ponha duas camisetas no carrinho. Já com tudo pronto, coloque o
   relógio em `2026-12-31T23:59:00` e aplique o cupom; depois coloque-o em `2027-01-01T00:00:00` e aplique-o outra vez.
   Preveja os dois códigos. Usamos um minuto antes, não um segundo, porque o relógio continua correndo enquanto você
   digita o `curl`. (Se você já está em 2027 ou depois, use o 31 de dezembro do seu ano corrente: o cupom vence em 31 de
   dezembro do ano em que a loja é aberta.)
3. **O mesmo pagamento ao mesmo tempo.** Copie o seu script (`cp al-mismo-tiempo.sh misma-llave.sh`) e, na cópia, faça
   duas mudanças: troque `pagar $DOS &` por `pagar $UNO &`, assim os dois pagamentos vão para o mesmo pedido e levam a
   mesma chave (o número do pedido e `$$` são iguais dentro de uma rodada); e na linha de `ESTADO=` troque
   `jq -r .estado` por
   `jq -r '.estado + " " + .cobrado.texto + " de " + .total.texto'`, para ver quanto se cobrou. Antes de rodá-lo, preveja
   **quantas cobranças** haverá no pedido 1. Rode-o cinco vezes, com `tienda reiniciar` antes de cada uma, e compare os
   códigos das cinco rodadas. A última linha, «VERDE…», aqui não significa nada: o pedido 2 nunca é pago. Ao terminar,
   `rm misma-llave.sh`.

**Revisão** (tente resolver pelo menos 4 de 5; se alguma não sair, volte ao passo indicado):

1. Na cena, o que tinham em comum os dois erros que os testes da equipe não viram? (cena)
2. Por que o script um depois do outro saiu verde com E2 ligado? (passo 1)
3. O que fazem `&` e `wait`? (passo 2)
4. Por que rodar cinco vezes um teste de algo que acontece ao mesmo tempo? (passo 3)
5. Por que a sua coleção saiu verde ao meio-dia com E6 ligado? (passo 5)

---

## Para fechar

As lições 07 e 08 testavam uma pessoa, ou duas, fazendo coisas uma depois da outra e na hora em que você rodava o teste.
Esta lição tira as duas comodidades: as requisições chegam **juntas** e a **qualquer hora**.

O que você leva daqui:

- **O que uma pessoa faz de um em um, teste também ao mesmo tempo.** Uma regra que se cumpre em sequência pode quebrar em
  paralelo, na janela entre conferir e anotar.
- `&` manda um comando para o fundo e `wait` espera por todos: com isso você dispara em paralelo a partir do terminal.
- **Um teste de corrida se repete antes de confiar nele:** um verde isolado ainda não basta.
- **As datas se testam na borda, não ao meio-dia:** fim de dia, de mês e de ano, no fuso da loja.
- Compare contra a hora da própria loja, não contra uma data escrita à mão.

Na lição 10 o problema sai da loja: o gateway de pagamento, outro sistema, falha ou fica lento, e você vê por que uma
dependência lenta é mais perigosa que uma queda.

---

## Compare as respostas

**Passo 1, a previsão.** Verde. Em sequência, o segundo pagamento chega quando o primeiro já anotou o uso do cupom, e a
loja o recusa mesmo com o E2 ligado. Se você previu vermelho porque o script «usa o cupom duas vezes», é um bom
raciocínio: o que falta é pensar em **quando** chega cada pagamento.

**Exercício 1.** Às **18:00:00**. A loja está seis horas atrás do UTC: às 18:00 da Cidade do México já são 00:00 do dia
seguinte em UTC, e o E6 anota essa hora. Medido:

```text
2026-11-30T17:59:00 → 6 de 6 em verde
2026-11-30T18:00:00 → 1. mesmo dia da loja: expected '2026-12-01' to deeply equal '2026-11-30'
```

Por isso, na cena, os pedidos «das seis da tarde em diante» iam para o dia seguinte. As bordas de uma data não são só a
meia-noite do seu fuso: também a meia-noite do UTC.

**Exercício 2.** **200** às 23:59 e **422** «o cupom já venceu» às 00:00:00. É a análise de bordas da lição 02 aplicada ao
tempo: o último minuto válido e o primeiro instante que já não é. Medido: com o relógio em 23:59:00 e o `curl` 20
segundos depois, 200; com o relógio em 00:00:00, 422.

**Exercício 3.** **Uma só cobrança**, nas cinco rodadas: `pedido 1: pagado $698.40 de $698.40`. O que muda entre rodadas são
os códigos. Quase sempre saem **200 e 200**: o segundo pagamento chega quando o primeiro já terminou e recebe a resposta
guardada, como na lição 08. Às vezes saem **200 e 409** «esse pagamento continua em processamento; espere e tente de novo
com a mesma chave»: o segundo chegou enquanto o primeiro ainda estava em processo. Medido em 20 rodadas: 17 vezes 200 e
200, 3 vezes 200 e 409, e as 20 com uma só cobrança igual ao total.

```text
pagamento do pedido 1: 200
pagamento do pedido 1: 200
pedido 1: pagado $698.40 de $698.40
pedido 2: creado $0.00 de $698.40
```

Por isso um teste de algo que acontece ao mesmo tempo confere **o efeito**, não o código: o código depende de quem chegou
primeiro; que se cobrou uma só vez, não.

**Revisão.**

1. Os dois precisavam de algo que os testes nunca faziam: duas requisições **ao mesmo tempo**, ou um teste **fora de
   hora**. Todos rodavam uma requisição de cada vez, ao meio-dia.
2. Porque o segundo pagamento chegou quando o primeiro já tinha anotado o uso do cupom: a janela já estava fechada.
3. `&` manda o comando para o fundo e o terminal segue sem esperá-lo; `wait` espera terminarem todos os que estão no
   fundo.
4. Porque quem chega primeiro pode mudar de uma rodada para a outra. Se o teste às vezes pega e às vezes não, um verde não
   te diz nada.
5. Porque ao meio-dia, seis horas a mais dão 18:00 do mesmo dia: a data não muda, e o teste compara a data.

---

## Fontes da lição

1. PortSwigger, *Web Security Academy*, «Race conditions» (consultado em 21 de novembro de 2026). Inspira o exemplo desta
   lição: um código de desconto de uso único, com uma janela entre conferi-lo e anotá-lo.
   «consider an online store that lets you enter a promotional code during checkout to get a one-time discount on
   your order»; «This introduces a small race window during which you can repeatedly claim the discount».
   https://portswigger.net/web-security/race-conditions
2. MITRE, CWE-362, «Concurrent Execution using Shared Resource with Improper Synchronization ('Race Condition')»
   (consultado em 21 de novembro de 2026). «a timing window exists in which the shared resource can be modified by
   another code sequence operating concurrently».
   https://cwe.mitre.org/data/definitions/362.html
3. MITRE, CWE-367, «Time-of-check Time-of-use (TOCTOU) Race Condition» (consultado em 21 de novembro de 2026). «The
   product checks the state of a resource before using that resource, but the resource's state can change between
   the check and the use in a way that invalidates the results of the check.»
   https://cwe.mitre.org/data/definitions/367.html
4. IETF, RFC 3339, *Date and Time on the Internet: Timestamps* (2002), §2 e §4.4. «Z … denotes a UTC offset of
   00:00»; «Since interpretation of an unqualified local time zone will fail in approximately 23/24 of the globe, the
   interoperability problems of unqualified local time are deemed unacceptable for the Internet».
   https://www.rfc-editor.org/rfc/rfc3339
5. GNU, *Bash Reference Manual*, «Job Control Builtins» (consultado em 21 de novembro de 2026). «If no options or ids
   are supplied, wait waits for all running background jobs…».
   https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html
6. GNU, *Bash Reference Manual*, «Lists of Commands» (consultado em 22 de novembro de 2026). «If a command is
   terminated by the control operator ‘&’, the shell executes the command asynchronously in a subshell»; «The shell
   does not wait for the command to finish».
   https://www.gnu.org/software/bash/manual/html_node/Lists.html

Medição própria: cada saída desta lição foi medida com curl, bash e newman 6.2.2 em 21 e 22 de novembro de 2026, com a API
da loja no ar sem Docker e reiniciada antes de cada rodada: o cupom, o relógio e o 409 contra a loja do curso
(HabilMX/curso-qa); o E2 «cupom duas vezes» em paralelo (20 de 20 ligado, 0 de 20 desligado, 0 de 20 em
sequência) e o E6 «data em UTC» contra um protótipo em uma cópia da loja, enquanto se constroem os de verdade.

Regras do curso, sem fonte externa:

- «O que uma pessoa faz de um em um, teste também ao mesmo tempo»: o erro de corrida não aparece em sequência.
- «Um teste de corrida se repete antes de confiar nele»: se às vezes pega e às vezes não, um verde isolado não basta. Nesta
  loja a janela é grande de propósito, para que o resultado se repita igual.
- «As datas se testam na borda, não ao meio-dia»: ao meio-dia, o erro de fuso não muda a data.
