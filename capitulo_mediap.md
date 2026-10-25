# Capítulo: construindo o MediaP, um reprodutor de mídia no terminal

## Objetivos de aprendizagem

Ao final deste capítulo, você deverá conseguir:

- separar modelo de dados, estruturas, regras do player e interface de terminal;
- implementar e percorrer uma lista duplamente encadeada com nós sentinela;
- manter um cursor que avança e retrocede em tempo constante;
- escolher `deque` para filas FIFO e `PriorityQueue` para ordenação por prioridade;
- serializar estado de objetos em JSON e restaurá-lo sem deixar o programa parcialmente alterado;
- interpretar testes como exemplos executáveis de contratos e casos de borda;
- avaliar as complexidades de tempo das operações mais importantes.

Este é um capítulo original baseado no projeto MediaP. O foco é ensinar as decisões que aparecem no código deste repositório, não reproduzir a redação ou a estrutura de qualquer livro.

## 1. O problema antes do código

O MediaP é um player simulado. Ele não decodifica áudio: recebe comandos no terminal, escolhe faixas e informa o que estaria tocando. A biblioteca inicial vem de `library.json`; playlists, fila Up Next, histórico e reprodução são manipulados em memória; `save` e `load` persistem o estado em JSON.

Uma faixa contém ID, título, artista, duração em segundos, avaliação e data de adição. Uma playlist é uma sequência editável, com um cursor indicando sua faixa atual. A fila Up Next guarda faixas que serão executadas antes da próxima faixa natural da playlist. O histórico guarda as últimas 30 execuções.

O problema é didaticamente interessante porque uma única aplicação usa quatro estruturas com responsabilidades distintas:

| Necessidade | Estrutura escolhida | Motivo |
| --- | --- | --- |
| Playlist com cursor | Lista duplamente encadeada própria | Avançar e retroceder a partir de um nó conhecido é O(1). |
| Próximas faixas prioritárias | `collections.deque` | Inserção no fim e retirada do início expressam uma fila FIFO. |
| Execuções recentes | `deque(maxlen=30)` | Limita o histórico e descarta automaticamente as entradas mais antigas. |
| Smart shuffle | `queue.PriorityQueue` | Retira primeiro a faixa com menor chave calculada. |

A escolha da estrutura não é decoração. Ela define quais operações ficam simples e qual custo precisamos aceitar. O cursor da playlist, por exemplo, fica rápido porque guarda uma referência a um nó, e não porque a lista inteira é reorganizada a cada avanço.

## 2. Como executar e explorar o projeto

O pacote é executado a partir do diretório pai:

```bash
cd /workspaces
python -m mediap
```

A biblioteca está em `mediap/library.json`. Caminhos relativos passados a `library load`, `save` e `load` são resolvidos a partir da pasta do pacote. O arquivo de estado salvo inclui a biblioteca, portanto também contém o contexto necessário para resolver IDs do histórico, da playlist e da fila.

Para executar os testes:

```bash
cd /workspaces
python -m unittest mediap.test_media_player
```

O código usa apenas a biblioteca padrão. Anotações como `list[int]` e `dict[str, Any]` pressupõem Python 3.9 ou mais recente.

### Mapa de módulos

```text
models.py                 Track e conversão para/de dicionários
    |
doubly_linked_list.py     Nós, sentinelas, encadeamento e iteração
    |
playlist.py               Cursor, navegação, remoção e exceções
    |
player.py                 Biblioteca, filas, reprodução, shuffle e estado
    |
cli.py                    Leitura de comandos e mensagens ao usuário
```

`test_media_player.py` exercita as estruturas e também percorre uma sessão da CLI com entrada simulada. `README.md` documenta execução e comandos.

## 3. Primeiro objeto: a faixa

`Track`, em `models.py`, é o modelo dos dados. Ele mantém os atributos conhecidos pelo restante do projeto e valida valores quando são atribuídos. Por exemplo, o rating precisa estar entre 1 e 5, enquanto ID e duração não podem ser negativos.

```python
class Track:
    def __init__(self, track_id, title, artist, duration, rating, data_adicao):
        self.id = track_id
        self.title = title
        self.artist = artist
        self.duration = duration
        self.rating = rating
        self.data_adicao = data_adicao
```

Os atributos públicos são propriedades. O construtor usa `self.id = track_id` em vez de escrever diretamente em `self.__id`; assim, a mesma validação também vale durante a construção. Se outro trecho posteriormente executar `track.rating = 8`, o setter rejeita o valor.

`from_dict` e `to_dict` formam a fronteira entre os objetos Python e o formato JSON:

```python
track = Track.from_dict({
    "id": 3,
    "title": "Ghost of Perdition",
    "artist": "Opeth",
    "duration": 629,
    "rating": 5,
    "data_adicao": "2026-09-17",
})

record = track.to_dict()
```

O nome do parâmetro Python é `track_id`, mas a chave do arquivo continua sendo `id`. Essa separação evita usar `id`, nome de uma função embutida do Python, como nome de parâmetro, sem alterar o formato da biblioteca.

A data de adição é mantida como `str`. O setter verifica que o valor é texto, mas não valida se ele corresponde a uma data real. Isso é uma decisão do código atual; validar o calendário exigiria converter o texto com `datetime` e definir claramente o formato aceito.

A apresentação de uma faixa pertence à CLI, em `format_track`, e não ao modelo. Isso permite que o modelo continue útil para serialização e lógica sem impor um formato de terminal. A apresentação comum usa título, artista e duração `mm:ss`; a listagem da biblioteca acrescenta ID e rating porque esses campos são úteis para escolher uma faixa.

## 4. Construindo a lista duplamente encadeada

Uma lista duplamente encadeada é formada por nós. Cada nó conhece o elemento, seu predecessor e seu sucessor. Se os nós forem `A`, `B` e `C`, os vínculos são:

```text
A <-> B <-> C
```

Em `doubly_linked_list.py`, a lista ainda mantém dois nós sentinela: `_header` antes do primeiro elemento e `_trailer` depois do último. Eles não representam faixas. As sentinelas deixam a lista vazia neste formato:

```text
_header <-> _trailer
```

Com elementos:

```text
_header <-> A <-> B <-> _trailer
```

### 4.1 O nó e a lista

A classe `_Node` é interna: clientes da lista trabalham com elementos, não constroem nós manualmente. `is_valid()` considera um nó ligado quando suas duas referências de vizinhança não são `None`. Ao remover um nó, `invalidate()` limpa esses vínculos. Isso é importante porque a playlist pode guardar uma referência direta ao nó atual.

A lista guarda `_length` em vez de contá-la percorrendo os nós toda vez. Assim, `len(playlist)` é O(1). O preço dessa conveniência é que toda inserção e remoção precisa atualizar `_length` corretamente.

### 4.2 Inserção no fim

`_insert_last` insere antes da sentinela final. Primeiro encontra o último nó real através de `_trailer.n_prev`; depois cria o novo nó e atualiza os dois vínculos vizinhos:

```python
previous = self._require_node(self._trailer.n_prev)
new_node = self._Node(elem, previous, self._trailer)
previous.n_next = new_node
self._trailer.n_prev = new_node
self._length += 1
```

O `_require_node` transforma uma referência opcional em uma referência que o restante da operação pode usar. Se o ponteiro estiver quebrado, gera um erro interno em vez de continuar silenciosamente com `None`.

A inserção é O(1): não depende do número de elementos. A lista rejeita `None` como elemento para distinguir claramente um nó real das sentinelas, cujo `n_elem` é `None`.

### 4.3 Localização por posição

`_find_node_by_index` usa posições começando em 1, porque é assim que o comando `playlist remove <pos>` é apresentado. Primeiro rejeita posições menores que 1 ou maiores que o tamanho. Depois escolhe a ponta mais próxima: começa no início para a metade inicial e no final para a metade final.

O pior caso continua O(n), mas o número de passos é aproximadamente metade do comprimento. Uma lista ligada não oferece acesso aleatório; ter `pos` não significa que seja possível saltar diretamente para essa posição.

### 4.4 Desvincular um nó

Depois que um nó foi localizado, `_remove_node` faz trabalho constante: conecta o predecessor diretamente ao sucessor, diminui o tamanho, guarda o elemento e invalida o nó removido. A operação pública `remove_at` custa O(n) por causa da busca; o trecho de religação custa O(1).

Separar “achar” de “desligar” é útil: o método de baixo nível só precisa saber remover um nó conhecido, enquanto a playlist decide como ajustar seu cursor antes da remoção.

### 4.5 Iteração

`_nodes()` percorre os nós reais, começando depois de `_header` e parando antes de `_trailer`. `__iter__()` transforma esse percurso em uma sequência de elementos, permitindo:

```python
for track in playlist:
    print(track.title)
```

A iteração custa O(n). `__len__()` retorna o contador armazenado em O(1). O usuário do objeto consegue usar os protocolos comuns do Python sem acessar os ponteiros internos.

## 5. Playlist: um cursor que guarda um nó

`Playlist` herda o encadeamento e adiciona nome e cursor. O cursor guarda o nó atual, não um número de posição. Isso importa porque cada nó já aponta para o próximo e para o anterior.

### 5.1 Invariantes

Uma invariante é uma regra que deve permanecer verdadeira depois de cada operação. Para esta playlist, as principais são:

1. Se estiver vazia, `_cursor` é `None`.
2. Se tiver elementos, `_cursor` aponta para um nó real ligado à lista.
3. A playlist não é circular: nenhuma navegação atravessa uma sentinela.
4. Inserir uma faixa em uma playlist vazia torna essa faixa atual; inserir outras não move o cursor.

Essas regras explicam boa parte dos métodos. `_validate_cursor()` verifica os casos vazios ou inválidos antes de uma operação dependente do cursor.

### 5.2 Avançar e retroceder

`play_next()` valida o cursor, lê seu sucessor e compara esse nó com `_trailer`. Se for a sentinela, a playlist já está no fim e a operação gera `PlaylistLimitError`; caso contrário, o cursor passa para o sucessor. `play_prev()` faz o mesmo com o predecessor e `_header`.

Ambos são O(1), porque não percorrem a lista. Ao atingir um limite, lançam exceção antes de mover o cursor. Portanto, uma tentativa inválida não altera a posição atual.

### 5.3 Remover sem deixar o cursor pendurado

`remove_at(pos)` primeiro encontra o nó pela posição. Se esse nó não é o cursor, remove-o e mantém o cursor. Se ele é o cursor, escolhe o próximo nó; se não existe próximo elemento, usa o anterior; se não há nenhum dos dois, a playlist ficará vazia e o cursor vira `None`.

A ordem é deliberada: o cursor precisa deixar de apontar para o nó antes de `_remove_node()` invalidá-lo. Caso contrário, a próxima chamada a `current()` encontraria uma referência removida.

### 5.4 Persistência do cursor

JSON guarda dados, não referências de memória a nós. `get_cursor_index()` converte a referência do cursor em uma posição 1-based. `set_cursor_by_index()` faz a conversão inversa após recriar os nós. Obter ou restaurar a posição é O(n), o que é adequado: isso ocorre ao salvar ou carregar, não em cada `next` ou `prev`.

## 6. Player: coordenar sem misturar responsabilidades

`Player`, em `player.py`, conecta as estruturas. Ele não implementa uma segunda lista: possui uma `Playlist[Track]`, uma `deque` para Up Next e uma `deque(maxlen=30)` para histórico.

`_track_by_id()` procura pelo ID real. Não usa `track_id - 1` como posição, porque IDs únicos não precisam ser consecutivos nem começar em 1. Em bibliotecas pequenas, uma busca linear é simples. Se a biblioteca crescer muito, um dicionário `{id: track}` poderia reduzir a consulta média para O(1), ao custo de manter mais estado sincronizado.

`playlist_add_track()` resolve os IDs antes de inserir as faixas. Se um ID não existir, a operação falha antes de acrescentar qualquer elemento, evitando uma playlist parcialmente alterada. `up_next_enqueue()` usa a mesma estratégia.

Os métodos de fronteira também verificam se há playlist ativa antes de delegar a operação. A CLI recebe exceções de domínio, como `PlaylistError`, em vez de precisar conhecer nós, sentinelas ou detalhes de `Playlist`.

## 7. Fila Up Next e histórico

### 7.1 Up Next é FIFO

O termo “prioridade” aqui significa precedência em relação à playlist natural; dentro da fila, a ordem é FIFO. `up_next_enqueue()` acrescenta no final com `extend`, e `play_next()` retira do início com `popleft()`.

Quando há uma faixa na fila, `play_next()` toca e descarta essa faixa sem mover o cursor da playlist. Quando a fila está vazia, delega o avanço à playlist. A fila afeta `next`, não `play`: `play` inicia ou retoma a faixa do cursor.

### 7.2 Histórico limitado

`history` é `deque(maxlen=30)`. Cada execução registrada contém ID e timestamp ISO com fuso horário. `_record_playback()` centraliza essa regra; `play`, `next` e `prev` chamam o método depois de escolher uma faixa.

Quando o deque já contém 30 entradas, adicionar outra remove automaticamente a mais antiga. Não é necessário escrever um `if` manual de descarte. `history_list()` apresenta as entradas do mais recente para o mais antigo e associa cada ID ao objeto `Track` correspondente.

## 8. Smart shuffle com fila de prioridade

A especificação pede que ratings maiores tenham prioridade e que faixas tocadas recentemente sejam penalizadas. O projeto usa a fórmula:

```text
score = -10 * rating + penalty_rec
```

Como `PriorityQueue` devolve o menor item primeiro, o sinal negativo faz rating alto produzir score baixo. Para as cinco posições mais recentes do histórico, começando em zero para a mais recente, a penalidade atual é `5 - posição`; fora dessas posições, é zero. Assim, uma faixa tocada há pouco recebe score maior e tende a descer na fila.

Exemplo simplificado:

| Faixa | Rating | Posição recente | Penalidade | Score |
| --- | ---: | ---: | ---: | ---: |
| A | 5 | não recente | 0 | -50 |
| B | 5 | 0 | 5 | -45 |
| C | 4 | não recente | 0 | -40 |

A ordem é A, B, C, pois scores menores saem primeiro. A diferença de 10 entre ratings garante que uma faixa de rating 5 ainda precede uma de rating 4, mesmo com penalidade recente máxima de 5.

A fila recebe tuplas `(score, id, track)`. O ID desempata scores iguais de forma previsível; sem ele, `PriorityQueue` poderia tentar comparar objetos `Track`, que não definem ordem. As faixas são realmente inseridas e retiradas pela fila, e não apenas ordenadas com `sorted`.

`smart_shuffle(count)` rejeita zero, negativos e quantidades maiores que a biblioteca. Cada faixa entra uma vez, então não há repetição. O custo dominante é inserir e retirar até N itens da fila: O(N log N). Construir a penalidade recente custa O(H), em que H é o histórico, limitado a 30.

## 9. JSON e restauração do estado

`save()` cria um dicionário com:

```text
library       dados completos das faixas
playlist      nome, IDs ordenados e posição do cursor
up_next       IDs na ordem FIFO
history       IDs e timestamps das execuções
```

O formato armazena IDs para evitar duplicar os mesmos objetos em todos os lugares. A biblioteca inteira também é incluída para que o estado seja autossuficiente: é possível restaurar sem executar `library load` antes.

`load()` lê e valida o JSON, cria uma biblioteca local e um mapa de IDs, reconstrói playlist/fila/histórico em variáveis locais e somente então substitui os atributos do player. Essa ordem evita deixar metade do player restaurado se uma referência estiver inválida. JSON malformado e estado inconsistente viram erros claros.

`_data_path()` resolve nomes relativos dentro da pasta `mediap`; um caminho absoluto continua sendo absoluto. Isso faz com que `python -m mediap`, executado da pasta pai, encontre os dados sem depender do diretório corrente do processo.

## 10. A CLI como camada de entrada e saída

`run_cli()` lê uma linha por vez, remove espaços externos e separa tokens com `split()`. O primeiro token escolhe o comando; os demais são argumentos. Nomes de playlist são recompostos com `" ".join(parts[2:])` para permitir espaços.

A CLI converte argumentos numéricos com `int()`, chama `Player` e apresenta o resultado. Ela não manipula ponteiros ou deques diretamente. Erros esperados são capturados no laço para que o usuário veja a mensagem e possa continuar usando o prompt.

`format_duration()` usa `divmod(seconds, 60)` para separar minutos e segundos; `format_track()` aplica esse formato aos objetos `Track`. Por exemplo, 212 segundos viram `3:32`. Separar a função de apresentação evita replicar contas e formato em biblioteca, playlist, fila, reprodução e histórico.

Uma sessão ilustrativa:

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

Os horários são ilustrativos. O programa gera o horário real no momento da execução.

## 11. Complexidade das operações

Considere N o tamanho da playlist/biblioteca e H o tamanho do histórico, com H ≤ 30.

| Operação | Custo esperado/garantido | Razão |
| --- | --- | --- |
| `len(lista)` | O(1) | Usa `_length`. |
| Iterar a lista | O(N) | Visita cada nó uma vez. |
| Anexar faixa | O(1) | Insere antes da sentinela final. |
| Encontrar posição | O(min(pos, N - pos)) passos; O(N) pior caso | Parte da ponta mais próxima. |
| `remove_at(pos)` | O(N) | Busca linear e depois religa em O(1). |
| `play_next` / `play_prev` da playlist | O(1) | Segue uma referência de nó. |
| Enfileirar/retirar Up Next | O(1) | `deque.append` e `deque.popleft`. |
| Adicionar histórico | O(1) | `deque(maxlen=30)` descarta automaticamente. |
| Smart shuffle | O(N log N) | Insere e retira itens da fila de prioridade. |
| Salvar/carregar estado | O(N) | Serializa/reconstrói as faixas e referências. |

O percurso bidirecional melhora o número de passos médios de busca, mas não muda a classe assintótica: encontrar um nó arbitrário ainda é O(N) no pior caso. Por isso o cursor é valioso para `next`/`prev`, mas não substitui busca por posição.

## 12. Testes como especificação executável

`test_media_player.py` usa `unittest`. Cada teste prepara um cenário pequeno e verifica um contrato observável:

- navegar A → B → C e voltar;
- falhar nos limites sem mover o cursor;
- remover faixa atual, última faixa ou a única faixa;
- garantir precedência da Up Next e que ela não altera a playlist;
- garantir que o histórico conserva as últimas 30 entradas;
- verificar prioridade por rating e penalidade por recência;
- salvar e restaurar biblioteca, playlist, cursor, fila e histórico;
- simular comandos com `unittest.mock.patch` e capturar a saída com `StringIO`.

O teste da CLI não precisa de uma pessoa digitando. `patch("builtins.input", side_effect=commands)` entrega uma sequência fixa; `patch("sys.stdout", new_callable=StringIO)` captura as mensagens. Isso transforma uma sessão interativa em um teste repetível.

Uma boa estratégia ao mudar uma regra é atualizar primeiro a expectativa correspondente e executar apenas o teste relacionado. Depois de validar o caso local, rode a suíte inteira:

```bash
cd /workspaces
python -m unittest mediap.test_media_player
```

## 13. Decisões, alternativas e limites

### Por que não usar `list` para a playlist?

Uma lista Python teria acesso por índice O(1), mas inserir/remover no meio desloca elementos e `next`/`prev` não exercitariam uma lista duplamente encadeada com cursor, exigida pelo projeto. Para outra aplicação, a lista nativa pode ser a melhor escolha; aqui a estrutura própria é requisito de aprendizagem.

### Por que sentinelas?

Sem sentinelas, inserir/remover o primeiro ou último elemento exige ramos especiais para atualizar `head` e `tail`. Com `_header` e `_trailer`, todo nó real sempre tem vizinhos. A pequena complexidade adicional de dois nós simplifica os casos de borda.

### Por que manter o cursor como nó?

Um índice teria de ser atualizado quando a lista mudasse e avançar exigiria buscar de novo. O nó já tem `n_next` e `n_prev`; isso dá O(1) para navegação.

### Por que não usar `sorted` no shuffle?

A exigência didática pede `PriorityQueue`. Em um produto sem essa restrição, `sorted` poderia ser uma alternativa simples para produzir toda a ordenação de uma vez. Aqui, usar a fila mostra inserção/remoção por prioridade e evita comparar `Track` diretamente.

### O que o player não faz?

Não reproduz áudio real, não implementa playlists múltiplas persistentes independentes, não usa banco de dados e não trata concorrência. Essas decisões mantêm o projeto concentrado em estruturas lineares, regras de estado e CLI.

## 14. Erros comuns e como diagnosticá-los

1. **Usar o ID como índice:** IDs podem não ser consecutivos. Sempre procure pelo valor de `track.id`.
2. **Mover o cursor ao tocar Up Next:** a faixa de fila é temporária e não pertence à playlist; o cursor permanece no mesmo nó.
3. **Atualizar apenas um lado do vínculo:** ao remover um nó, atualize tanto `prev.n_next` quanto `next.n_prev`.
4. **Esquecer `_length`:** uma lista pode iterar corretamente e ainda retornar `len()` errado.
5. **Comparar objetos na prioridade:** se a tupla não tiver desempate numérico, a fila pode tentar ordenar `Track`.
6. **Aplicar a penalidade ao contrário:** `PriorityQueue` retira o menor score; uma faixa recente precisa receber penalidade maior para perder prioridade.
7. **Restaurar o cursor antes de criar os nós:** cursor salvo é índice, e o nó só existe depois da reconstrução da playlist.
8. **Aplicar estado parcialmente:** construa e valide as novas estruturas antes de substituir os atributos atuais do player.
9. **Confiar no diretório corrente:** caminhos relativos são resolvidos pela pasta do pacote; use o nome do arquivo ou um caminho absoluto explícito.
10. **Confundir `current` com som:** o comando mostra a faixa no cursor da playlist. O programa simula execução e não produz áudio.

## 15. Questões e soluções comentadas

### 1. Por que a playlist não usa `deque`?

**Solução:** a playlist precisa de um cursor que navegue em ambas as direções em O(1), além de remoção por posição e nós próprios. `deque` é apropriado para as pontas de uma fila, mas não expõe os nós internos necessários ao cursor.

### 2. Por que `play_next()` é O(1), mas `remove_at(20)` pode ser O(N)?

**Solução:** `play_next()` já tem o nó atual e segue `n_next`. `remove_at(20)` recebe uma posição, não uma referência; primeiro precisa encontrar esse nó percorrendo a lista. A religação do nó encontrado é O(1), mas a busca domina o custo.

### 3. Por que começar a busca pela ponta mais próxima se o pior caso ainda é O(N)?

**Solução:** a notação assintótica descreve crescimento no pior caso, não o número exato de operações em toda entrada. Começar pela ponta mais próxima reduz o percurso sem mudar a classe de complexidade.

### 4. O que aconteceria se `remove_at()` invalidasse o nó antes de mover o cursor?

**Solução:** se o nó removido fosse o atual, o cursor passaria a apontar para uma referência sem vizinhos. `_validate_cursor()` detectaria o cursor inválido depois, mas a playlist já teria perdido a posição corrente. Por isso a decisão do novo cursor ocorre antes da invalidação.

### 5. Se IDs forem 10, 30 e 90, como `playlist add 30` deve funcionar?

**Solução:** `_track_by_id(30)` percorre as faixas e compara o atributo `id`. Usar `library[29]` confundiria identificador com posição e falharia.

### 6. O que `deque(maxlen=30)` faz na 31ª execução?

**Solução:** acrescenta a nova entrada e remove automaticamente a mais antiga. A ordem interna continua da mais antiga à mais recente; `history_list()` inverte essa visão para exibir recentes primeiro.

### 7. A Up Next é uma fila de prioridade?

**Solução:** não dentro da própria fila. É FIFO: o primeiro enfileirado é o primeiro retirado. Ela tem precedência sobre a playlist natural no comando `next`, mas não tem ordenação por rating. Smart shuffle é que usa `PriorityQueue`.

### 8. Por que `play()` não consome a Up Next?

**Solução:** o contrato atribui precedência da fila a `next`. `play()` inicia/retoma o cursor da playlist. Consumir a fila também em `play()` criaria uma regra adicional e diferente.

### 9. Por que a prioridade começa com `-10 * rating`?

**Solução:** o menor valor sai primeiro. Multiplicar rating positivo por -10 transforma nota maior em valor menor; peso 10 também faz a diferença de uma estrela superar a penalidade máxima de recência, que é 5.

### 10. O que acontece se duas faixas tiverem o mesmo score?

**Solução:** a tupla usa `(score, id, track)`. A fila compara score primeiro e ID depois. Como IDs são únicos, não precisa comparar o objeto `Track`.

### 11. Por que `smart_shuffle` recusa `count > len(library)`?

**Solução:** o algoritmo não repete faixas. Não há como produzir mais itens distintos do que existem na biblioteca; gerar duplicatas mudaria essa regra.

### 12. Por que salvar IDs em vez de guardar objetos repetidos na playlist e na fila?

**Solução:** o arquivo inclui uma biblioteca canônica e as estruturas guardam referências por ID. Isso evita repetir todos os campos da faixa em cada lugar e facilita reconstruir os mesmos objetos compartilhados na memória.

### 13. Por que o JSON inclui a biblioteca inteira?

**Solução:** para que `load` funcione sozinho em uma nova execução. Se armazenasse apenas IDs, o usuário precisaria carregar a mesma biblioteca antes e o arquivo não seria autossuficiente.

### 14. Por que `load()` constrói variáveis locais antes de atualizar `self`?

**Solução:** se o JSON estiver inválido, o método falha sem substituir metade do estado atual. A atualização final só ocorre quando biblioteca, playlist, fila e histórico foram reconstruídos com sucesso.

### 15. Por que o timestamp é guardado como texto ISO?

**Solução:** JSON não possui tipo `datetime` nativo. O texto ISO é legível e pode ser interpretado novamente com `datetime.fromisoformat()`.

### 16. Por que a CLI captura erros em vez de encerrar ao primeiro ID inválido?

**Solução:** a CLI é um loop interativo. Mostrar uma mensagem e voltar ao prompt permite corrigir o comando sem reiniciar o programa.

### 17. Como testar a mensagem de `playlist remove` sem abrir um terminal interativo?

**Solução:** fornecer comandos pré-definidos com `patch("builtins.input", side_effect=commands)`, capturar `sys.stdout` em `StringIO` e verificar que o texto esperado está na saída.

### 18. Por que os setters validam os valores?

**Solução:** porque `Track` é mutável. Validar apenas no construtor não impediria uma atribuição inválida feita posteriormente. Os setters preservam o contrato em cada alteração.

### 19. Um ID negativo é proibido; zero também é?

**Solução:** no código atual, não. A validação rejeita apenas valores menores que zero. Isso é válido se a regra do domínio permitir ID zero; a biblioteca de exemplo começa em 1, mas exemplo não é necessariamente restrição.

### 20. O que mudaria para suportar playlists circulares?

**Solução:** em `play_next()`, ao encontrar `_trailer`, mover o cursor para `_header.n_next`; em `play_prev()`, ao encontrar `_header`, mover para `_trailer.n_prev`. Também seria necessário alterar as exceções de limite e os testes. Não é uma mudança apenas visual: modifica o contrato da navegação.

### 21. Como reduzir a busca linear de IDs se a biblioteca crescer muito?

**Solução:** manter `tracks_by_id = {track.id: track}` ao carregar a biblioteca. Isso dá consulta média O(1), mas o mapa precisa ser atualizado sempre que a biblioteca mudar e validado na restauração. Para 30 faixas, a busca linear é mais simples.

### 22. Como testar que `next` vindo da Up Next preserva o cursor?

**Solução:** criar uma playlist com pelo menos duas faixas, enfileirar outra, executar `play_next()` e verificar que o ID retornado é o da fila e que `playlist.current()` continua sendo a faixa anterior.

### 23. A lista duplamente encadeada pode aceitar `None`?

**Solução:** a implementação escolhe não aceitar. As sentinelas usam `None` como marca de ausência de elemento; proibir `None` impede confundir uma faixa inexistente com um elemento válido. Se `None` fosse domínio válido, seria necessário separar o marcador de sentinela do valor.

### 24. O comando `current` indica a faixa que veio da Up Next?

**Solução:** não. Ele mostra o cursor da playlist. Isso é intencional neste projeto: Up Next não altera o cursor. Para mostrar “última faixa realmente iniciada”, seria preciso manter um estado separado de reprodução atual e persistir esse campo.

### 25. Qual é a diferença entre erro de domínio e erro de implementação?

**Solução:** tentar avançar além do fim é erro de domínio e usa `PlaylistLimitError`. Encontrar um ponteiro interno `None` onde deveria existir um nó é erro da estrutura e usa `RuntimeError`. Separar os tipos ajuda a CLI a mostrar erros esperados sem esconder defeitos internos.

## 16. Exercícios de extensão

Tente cada exercício antes de consultar as soluções acima e escreva primeiro o comportamento esperado:

1. Adicione testes diretos para rejeitar rating 0 e 6 e para aceitar rating 1 e 5.
2. Faça a CLI rejeitar `playlist remove -1` com uma mensagem explícita. Considere o que `str.isdigit()` retorna para números negativos.
3. Acrescente um comando `queue clear` sem expor a deque diretamente à CLI.
4. Mude o tamanho do histórico para uma constante nomeada e explique onde ela deve ficar.
5. Escreva um teste que salva e restaura com playlist vazia, fila vazia e histórico vazio.
6. Implemente uma opção de shuffle que permita repetição e compare suas regras com o shuffle atual sem alterar silenciosamente o contrato existente.
7. Adicione um mapa de IDs e compare com busca linear usando uma biblioteca artificialmente grande. Não assuma que uma otimização pequena melhora o programa sem medir.
8. Desenhe a lista antes e depois da remoção do nó central. Mostre os quatro ponteiros alterados.

## 17. Encerramento

O MediaP conecta estruturas conhecidas a contratos concretos: a lista mantém links, a playlist mantém um cursor válido, as filas definem ordem de execução, o histórico mantém uma janela das execuções e o JSON preserva o estado entre processos. A CLI transforma texto em chamadas do domínio e apresenta resultados sem conhecer detalhes internos.

A lição mais importante não é decorar uma classe. É perguntar, para cada operação: que estado ela pode alterar, qual invariável precisa continuar verdadeira, qual é seu custo e como um teste demonstrará o comportamento esperado? Com essas perguntas, uma aplicação pequena deixa de ser um conjunto de comandos e passa a ser um sistema que pode ser explicado, testado e evoluído.
