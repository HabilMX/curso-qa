# QA do zero: cenários que encontram erros

**Por Dorian Chávez, fundador da Hábil e arquiteto de integração.**

Um curso aberto e gratuito para aprender a testar software **encontrando erros de verdade**. Você pratica em uma loja
online inventada que traz oito erros plantados de propósito, e o seu trabalho é escrever os testes que os encontram:
cenários, testes de API que rodam sozinhos, um teste de navegador e relatórios que outra pessoa consegue reproduzir.

> O curso está em cinco idiomas: espanhol (a fonte), inglês, francês, português do Brasil e búlgaro.

## Para quem é

Para quem está começando em QA, ou para quem programa e quer testar melhor: estagiários, estudantes e pessoas de
desenvolvimento. Você não precisa de experiência prévia em testes; precisa, sim, se virar no terminal. Se você nunca o
usou, comece pelo curso «O terminal do zero».

## O que você precisa

- Um computador com **Docker**. A loja e tudo o que você usa para testá-la (behave, curl, newman e um navegador sem
  janela) já vêm dentro: você não instala mais nada.
- **Git**, para baixar este repositório.
- Um terminal. Cada lição diz o que digitar.

Medido em Linux x86_64 com Docker 29: a imagem pesa uns 1.3 GB, leva uns 2 minutos para construir na primeira vez, a
loja sobe em 2 segundos e, em repouso, usa uns 56 MB de memória. No macOS e no Windows com WSL2 ainda não foi medido.

## Como subir a loja

```bash
git clone <dirección de este repositorio>
cd <carpeta del repositorio>
./practicar
```

Na primeira vez, o comando constrói a imagem e depois deixa você no terminal da loja. A página fica em
**http://localhost:8080**. A partir daí você segue a lição 00, que ensina a conferir que tudo funciona e a usar
`verifica 00`, o comando que confere o seu trabalho no fim de cada lição.

## As lições

| # | Lição | O que fica com você |
|---|---|---|
| 00 | [Sua loja de prática](00-tu-tienda-de-practica.md) | A loja funcionando no seu computador, e o jeito de conferir que a API e a página respondem |
| 01 | [Da história ao cenário](01-de-la-historia-al-escenario.md) | Separar uma história de usuário em regras, exemplos e cenários antes de mexer no sistema |
| 02 | [Grupos e bordas](02-grupos-y-orillas.md) | Dividir os dados de uma regra em grupos e testar bem nas bordas, onde os erros se escondem |
| 03 | [Tabelas de decisão](03-tablas-de-decision.md) | Uma tabela que mostra todas as combinações quando várias regras decidem juntas |
| 04 | [Estados e ordem](04-estados-y-orden.md) | Os estados de um pedido, a sua tabela, e as células vazias em que ninguém pensou |
| 05 | [Combinar sem testar tudo](05-combinar-sin-probar-todo.md) | Uma tabela de combinações que cobre cada par de valores com poucos testes |
| 06 | [Testar uma API à mão](06-probar-una-api-a-mano.md) | Falar com a API com `curl`, ler cada resposta e prever o que ela vai responder |
| 07 | [Testes de API que rodam sozinhos](07-pruebas-de-api-que-corren-solas.md) | Uma coleção que testa uma compra com um único comando e fica vermelha quando há um erro |
| 08 | [Permissões e novas tentativas](08-permisos-y-reintentos.md) | Testar sem sessão, com outra cliente, e tentar de novo uma cobrança com a mesma chave sem cobrar duas vezes |
| 09 | [Ao mesmo tempo e fora de hora](09-al-mismo-tiempo-y-a-deshoras.md) | Pagamentos que chegam ao mesmo tempo e datas que mudam de dia conforme a hora |
| 10 | [Quando o outro sistema falha](10-cuando-el-otro-sistema-falla.md) | Conferir que o estado de um pedido e o dinheiro batem quando o gateway de pagamento demora |
| 11 | [O navegador, só para o crítico](11-el-navegador-solo-para-lo-critico.md) | Um teste de navegador para o que só se vê na página, e por que ele é pouco usado |
| 12 | [Reportar para que consertem](12-reportar-para-que-lo-arreglen.md) | Um relatório com passos que qualquer pessoa pode colar e reproduzir, com severidade e prioridade |
| 13 | [Seu teste serve?](13-tu-prueba-sirve.md) | Plantar erros para saber quais os seus testes enxergam, e achar o teste que protege um erro |
| 14 | [Junte tudo: a história de segunda-feira](14-junta-todo-la-historia-del-lunes.md) | Uma história completa, testada por risco com tudo o que veio antes, e onde você fica em relação ao exame ISTQB CTFL |

Cada lição termina com o seu `verifica`, que roda o seu trabalho contra a loja limpa e contra a loja com o erro da
lição ligado, e diz o que falta.

## Até onde vai

A lição 14 situa você em relação ao programa ISTQB CTFL: o que você tocou e o que fica de fora. O curso não é uma prova
nem dá certificado. Testes de carga, de acessibilidade e de segurança a fundo ficam de fora de propósito: cada um merece
o seu próprio curso.

## Quem faz este curso

A Hábil constrói e testa sistemas que não podem falhar: backend, integrações, web e apps. Se a sua equipe quiser ajuda
com os testes, a primeira conversa é sem custo: [habil.mx](https://www.habil.mx).

---

Mantém o curso ou a loja? Os comandos do `./practicar` e como rodar os testes estão em [MANTENIMIENTO.md](../MANTENIMIENTO.md) (em espanhol).
