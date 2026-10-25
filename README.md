# MediaP

Reprodutor de mídia simulado, controlado pelo terminal e implementado apenas com a biblioteca padrão do Python.

## Visão geral

O projeto gerencia uma biblioteca JSON, playlists com cursor, uma fila Up Next, histórico de reprodução, smart shuffle e persistência completa do estado.

## Como executar

Execute o programa somente a partir da pasta pai do pacote. Neste Codespace:

```bash
cd /workspaces
python -m mediap
```

Arquivos de biblioteca e de estado (incluindo o histórico) ficam na pasta `mediap`. Caminhos relativos informados aos comandos são resolvidos a partir dela; caminhos absolutos também são aceitos.

## Comandos

```text
library load <arquivo>
library list [id|title|artist|duration|rating|data_adicao]
playlist new <nome>
playlist add <id> [id ...]
playlist remove <posição>
playlist show
playlist reset
play
next
prev
current
enqueue <id> [id ...]
queue show
history
smart-shuffle <n>
save <arquivo>
load <arquivo>
help
quit
```

As posições de remoção começam em 1. `current` mostra a faixa no cursor da playlist. `next` consome a primeira faixa da fila Up Next sem alterar o cursor da playlist; `prev` sempre navega a playlist, então usa a posição preservada mesmo depois de tocar uma faixa da Up Next.

## Exemplo de sessão

```text
mediap> library load library.json
Biblioteca carregada: 30 faixas.
mediap> playlist new Favoritas
Playlist 'Favoritas' criada e definida como ativa.
mediap> playlist add 3 4
mediap> playlist show
> 1. "Ghost of Perdition" — Opeth (10:29)
  2. "The Drapery Falls" — Opeth (10:54)
mediap> play
>>> Tocando: "Ghost of Perdition" — Opeth (10:29)
mediap> enqueue 8
mediap> next
>>> Tocando: "Homage for Satan" — Deicide (3:59)
mediap> history
1. "Homage for Satan" — Deicide (3:59) [12:00:01]
2. "Ghost of Perdition" — Opeth (10:29) [12:00:00]
mediap> save estado.json
Estado salvo em 'estado.json'.
```

## Smart Shuffle

O comando cria uma playlist sem repetições. `n` deve ser positivo e não pode exceder o número de faixas da biblioteca. As faixas são inseridas e retiradas por `queue.PriorityQueue`; o menor score sai primeiro:

```text
score = -10 * rating + penalty_rec
```

Para uma faixa entre as cinco execuções mais recentes, `penalty_rec = 5 - posição`, considerando posição 0 a mais recente; para as demais, a penalidade é 0. Assim, ratings maiores têm prioridade, enquanto faixas tocadas recentemente descem na fila. IDs menores desempatarão scores iguais.

## Persistência

`save` grava em JSON a biblioteca, playlist, cursor, fila Up Next e histórico. Um nome relativo, como `estado.json`, grava o arquivo dentro de `mediap`; como a biblioteca também é incluída, `load estado.json` funciona em uma nova execução sem carregar a biblioteca separadamente.

## Testes

Na pasta que contém `mediap`, execute:

```bash
python -m unittest mediap.test_media_player
```

Os testes cobrem a lista duplamente encadeada e o cursor, precedência da Up Next, limite FIFO do histórico, prioridade do shuffle e restauração do estado.

## Estrutura do projeto

- `models.py`: representação das faixas
- `doubly_linked_list.py`: lista duplamente encadeada genérica
- `playlist.py`: playlist e cursor
- `player.py`: biblioteca, reprodução, histórico, shuffle e persistência
- `cli.py`: comandos do terminal e apresentação das faixas
- `library.json`: biblioteca de exemplo