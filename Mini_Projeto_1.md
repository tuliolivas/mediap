# Mini Projeto 1 — Sequenciador e Reprodutor de Mídia

## Objetivo

Neste mini projeto, você irá construir, em Python, um sequenciador e reprodutor de mídia que opera exclusivamente pela linha de comando (terminal).

O programa carrega uma biblioteca de faixas a partir de um arquivo, monta playlists, simula a reprodução (sem áudio real) e gerencia uma fila de reprodução imediata, um histórico de execução e um modo de embaralhamento inteligente.

O foco do projeto está no uso adequado de quatro estruturas lineares distintas, cada uma cumprindo um papel funcional específico.

## 1. Dados para o player

A biblioteca é o conjunto de todas as faixas conhecidas pelo programa. Cada faixa (`track`) é descrita pelos seguintes atributos:

| Atributo | Tipo / descrição |
| --- | --- |
| `id` | Identificador inteiro único |
| `título` | String |
| `artista` | String |
| `duração` | Duração em segundos (`int`) |
| `rating` | Avaliação inteira de 1 a 5 estrelas |
| `data_adicao` | Data em que a faixa foi cadastrada (`datetime`) |

As músicas devem ser carregadas a partir de um arquivo JSON armazenado em `library`. Um exemplo mínimo com 30 faixas acompanha a entrega para facilitar os testes.

## 2. Comandos do terminal

A interação com o player acontece exclusivamente pela linha de comando. O programa deve executar um laço que lê uma linha por vez, interpreta o comando e o executa.

Em caso de erro de sintaxe ou de comando desconhecido, exiba uma mensagem de erro clara e retorne ao prompt. O prompt sugerido é `mediap>`.

| Comando | Comportamento |
| --- | --- |
| `library load <arquivo>` | Carrega a biblioteca a partir de um arquivo JSON |
| `library list <rating\|title\|artist\|etc>` | Lista as faixas, ordenando pelo critério informado (padrão: `id`) |
| `playlist new <nome>` | Cria uma playlist vazia e a torna a playlist atual |
| `playlist add <track_id>` | Adiciona a faixa ao final da playlist atual |
| `playlist remove <pos>` | Remove a faixa que está na posição `pos` |
| `playlist show` | Exibe a playlist com o cursor marcado por `>` |
| `play` | Inicia ou retoma a reprodução a partir do cursor |
| `next` | Avança; a fila Up Next tem precedência sobre a próxima faixa da playlist |
| `prev` | Retrocede o cursor da playlist |
| `enqueue <track_id>` | Acrescenta a faixa à fila Up Next |
| `queue show` | Exibe o conteúdo da fila Up Next na ordem em que será tocado |
| `history` | Exibe o histórico, do mais recente ao mais antigo |
| `smart-shuffle <n>` | Gera uma nova playlist com `n` faixas usando uma fila com prioridade |
| `save <arquivo>` | Serializa o estado completo (playlist, fila Up Next, histórico e cursor) em JSON |
| `load <arquivo>` | Restaura o estado a partir de um arquivo JSON |
| `help` | Exibe os comandos disponíveis |
| `quit` | Encerra o programa |

## 3. Funcionalidades e estruturas de dados auxiliares

A solução deve usar obrigatoriamente as quatro estruturas de dados indicadas a seguir.

### 3.1. Playlist — lista duplamente encadeada

A playlist deve ser representada por uma lista duplamente encadeada construída por você. É permitido basear-se na classe `DoublyLinkedList`.

> **Restrição:** não use o tipo `list` do Python para representar a playlist.

A solução deve indicar qual música está tocando no momento (implementar um cursor) e oferecer operações para avançar (`next`) e retroceder (`prev`) na playlist. Ambas devem ter complexidade temporal **O(1)**.

A playlist não é circular. Se o programa estiver executando o primeiro item e o usuário pedir para ir ao item anterior (`prev`), indique um erro e continue tocando a primeira música. O mesmo deve acontecer se o usuário solicitar a próxima música (`next`) estando no último item da playlist.

Implemente as seguintes operações:

| Operação | Comportamento |
| --- | --- |
| `add(track)` | Anexa uma nova faixa ao final da playlist |
| `remove_at(pos)` | Remove a faixa que está na posição `pos` |
| `current()` | Retorna a faixa da playlist que está em execução |
| `play_next()` | Começa a executar a próxima faixa da lista |
| `play_prev()` | Começa a executar a faixa anterior |
| `reset_cursor()` | Reinicializa o cursor, posicionando-o na primeira faixa |
| `__len__` | Retorna o tamanho da playlist |
| `__iter__` | Implementa um iterador para a playlist |

O cursor representa a faixa que está em execução no momento.

### 3.2. Fila Up Next — músicas com precedência

A fila Up Next guarda uma sequência de faixas que devem ser tocadas antes da próxima faixa natural da playlist.

Implemente essa funcionalidade com uma fila baseada em `collections.deque`, restringindo as operações para respeitar o comportamento de uma fila.

Quando o usuário executar o comando `next`:

1. Se a fila Up Next não estiver vazia, toque a faixa do início da fila e remova-a. Essa faixa não deve ser adicionada à playlist.
2. Caso contrário, avance o cursor da playlist e toque a próxima faixa.

Em resumo, os itens da fila Up Next têm precedência sobre os itens da playlist e são descartados após a execução.

### 3.3. Histórico — deque com tamanho máximo

Toda faixa efetivamente executada por meio de `play`, `next` ou `prev` deve ser registrada em um histórico, implementado como um deque com tamanho máximo (`maxlen=30`).

Ao atingir a capacidade máxima, a faixa mais antiga deve ser descartada automaticamente (descarte FIFO pelo lado oposto da inserção).

Cada item do histórico deve incluir, no mínimo:

- o ID da faixa;
- o timestamp de reprodução (momento de início da execução).

### 3.4. Smart Shuffle — fila com prioridade

O comando `smart-shuffle <n>` gera uma nova playlist com `n` faixas selecionadas da biblioteca. As faixas devem ser ordenadas por meio de uma fila com prioridade implementada com `queue.PriorityQueue`.

A chave de prioridade deve combinar os seguintes valores:

- **Rating (peso maior):** faixas com rating mais alto têm maior prioridade e saem primeiro da fila.
- **Recência no histórico (peso menor):** faixas tocadas há pouco tempo têm menor prioridade e saem depois da fila.

Em suma, essa funcionalidade prioriza as músicas com maior rating.

A fórmula a seguir é uma sugestão, mas não é obrigatória. Se optar por outra fórmula, documente-a adequadamente.

Para uma faixa `f`, a chave de prioridade é:

```text
chave(f) = -10 · rating(f) + penalty_rec(f)
```

`penalty_rec(f)` representa a penalidade por a faixa ter sido tocada recentemente. Ela é calculada a partir da posição `pos_hist(f)` da faixa no histórico, em que `pos_hist(f) = 0` corresponde à última faixa tocada:

```text
penalty_rec(f) = pos_hist(f), se pos_hist(f) < 5 (entre as 5 últimas tocadas)
penalty_rec(f) = 0, caso contrário
```

O sinal negativo aplicado ao rating compensa o fato de `PriorityQueue` retornar primeiro o menor valor.

## 4. Reprodução simulada

Não é necessário reproduzir áudio. A reprodução será simulada.

Quando uma faixa for tocada por meio de `play`, `next` ou `prev`, o programa deve:

1. Exibir uma linha no formato abaixo.
2. Registrar a faixa no histórico.

```text
>>> Tocando: "<título>" — <artista> (mm:ss)
```

A formatação da duração em `mm:ss` deve ser implementada explicitamente. Você pode usar uma biblioteca como `datetime` para auxiliar.

## 5. Persistência

Os comandos `save` e `load` devem manter o estado completo entre execuções. O formato JSON é obrigatório.

O estado deve incluir:

- a ordem das faixas na playlist;
- a posição do cursor;
- o conteúdo da fila Up Next;
- o histórico.

Após executar `save` e `load`, os comandos `playlist show`, `queue show` e `history` devem produzir saídas idênticas.

## 6. Testes automatizados

A solução deve incluir testes automatizados e alcançar cobertura mínima de **70%**. Você pode usar `pytest` ou `unittest`.

As seguintes operações e funcionalidades devem ser completamente testadas:

1. A lista duplamente encadeada, incluindo sequências de inserções, remoções e movimentação do cursor.
2. A precedência da fila Up Next sobre a playlist no comando `next`.
3. O limite de itens do histórico e o descarte do item mais antigo (princípio FIFO) ao exceder a capacidade máxima.
4. A ordenação produzida pela `PriorityQueue` do `smart-shuffle`.
5. Os comandos de salvamento e carregamento (`save` / `load`), verificando que o estado permaneça idêntico.

## 7. Entrega

O arquivo `README.md` é obrigatório e deve conter:

- instruções para executar a solução;
- um exemplo de sessão;
- a descrição da fórmula adotada para o `smart-shuffle`, caso seja diferente da fórmula sugerida neste documento.

## 8. Restrições

- Não use o tipo `list` do Python para representar a playlist. Ela deve ser uma lista duplamente encadeada implementada com base na implementação fornecida.
- Não substitua a `PriorityQueue` por `sorted()` ou `list.sort()` para gerar a playlist do `smart-shuffle`. A inserção e a retirada devem passar efetivamente pela fila com prioridade.
- Não utilize bibliotecas externas; use apenas as bibliotecas padrão do Python.

## 9. Exemplo de sessão

O exemplo a seguir é uma referência informal do comportamento esperado:

```text
mediap> library load library_exemplo.json
Biblioteca carregada: 10 faixas.

mediap> playlist new minha
Playlist "minha" criada.

mediap> playlist add 3
mediap> playlist add 7
mediap> playlist add 1

mediap> playlist show
> 1. Águas de Março — Elis Regina (3:32)
  2. Construção — Chico Buarque (6:21)
  3. Carinhoso — Pixinguinha (3:05)

mediap> play
>>> Tocando: "Águas de Março" — Elis Regina (3:32)

mediap> enqueue 5
mediap> next
>>> Tocando: "Asa Branca" — Luiz Gonzaga (2:45) # veio da Up Next

mediap> next
>>> Tocando: "Construção" — Chico Buarque (6:21) # voltou para a playlist

mediap> history
1. Construção — Chico Buarque [11:42:17]
2. Asa Branca — Luiz Gonzaga [11:42:08]
3. Águas de Março — Elis Regina [11:42:00]

mediap> quit
```
