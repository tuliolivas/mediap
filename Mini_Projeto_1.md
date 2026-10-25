No presente Mini Projeto, seu objetivo será o de construir, em Python, um sequenciador/reprodutor de mídia, que opera exclusivamente por meio da linha de comando (Terminal).
O programa carrega uma biblioteca de faixas a partir de um arquivo, monta playlists, simula a reprodução (sem áudio real, é claro!) e gerencia uma fila de reprodução imediata, um histórico de execução e um modo de embaralhamento “inteligente”.
O foco do projeto está no uso adequado de quatro estruturas lineares distintas, cada uma cumprindo um papel funcional específico.
1 Dados para o Player
A biblioteca é o conjunto de todas as faixas conhecidas pelo programa.
Cada faixa (track) é descrita pelos atributos:
• id: identificador inteiro único;
• título (string);
• artista (string);
• duração em segundos (int);
• rating: avaliação inteira de 1 a 5 estrelas;
• data_adicao: data em que a faixa foi cadastrada (datetime).
Os dados (músicas) devem ser carregados a partir de um arquivo json (armazenado em library).
Um exemplo mínimo (com 30 faixas) acompanha a entrega para facilitar testes.
2 Comandos do terminal
Como dito, a interação com o Player se dá exclusivamente via linha de comando.
Ela acontece em um laço que lê uma linha por vez, faz o parse do comando e executa.
Em caso de erro de sintaxe ou comando desconhecido, você deve exibir uma mensagem de erro clara e voltar ao prompt.
O prompt sugerido é mediap>.
A seguir, segue a lista de comandos que a sua solução deve conseguir executar:
• library load <arquivo> — carrega a biblioteca a partir de CSV ou JSON;
• library list [--by rating|title|artist] — lista as faixas, ordenando pelo critério informado (default: id);
• playlist new <nome> — cria uma nova playlist vazia e a torna a “atual”;
• playlist add <track_id> — adiciona a faixa ao final da playlist atual;
• playlist remove <pos> — remove a faixa na posição pos;
• playlist show — imprime a playlist com cursor marcado por “>” (ou seja, indica a música em execução ou que será executada);
• play — inicia/retoma a reprodução a partir do cursor;
• next — avança (a fila Up Next tem precedência sobre a próxima faixa da playlist);
• prev — retrocede o cursor da playlist;
• enqueue <track_id> — acrescenta a faixa à fila Up Next;
• queue show — imprime o conteúdo da fila Up Next na ordem em que será tocada;
• history — imprime o histórico, do mais recente ao mais antigo;
• smart-shuffle <n> — gera nova playlist de n faixas usando a fila com prioridade;
• save <arquivo> — serializa o estado completo (playlist, fila up next, histórico, cursor) em JSON;
• load <arquivo> — restaura o estado a partir de JSON;
• help — imprime os comandos disponíveis;
• quit — encerra o programa.
3 Funcionalidades e Estruturas de Dados Auxiliares
Nesta Seção, descrevo as funcionalidades e estruturas de dados auxiliares para a implementação de cada uma delas.
Sua solução deve usar, obrigatoriamente, as quatro estruturas de dados indicadas a seguir.
3.1 Playlist — Lista Duplamente Encadeada
A playlist é representada por uma lista duplamente encadeada construída por você (você pode se basear na classe DoublyLinkedList).
Não é permitdo usar o tipo list do Python para representar a playlist.
Sua solução deve indicar qual a música que está “tocando” no momento (ou seja, deve implementar uma espécie de cursor), bem como implementar as operações de avanço (next - tocar o próximo item da playlist) e retrocesso (prev - tocar o item anterior da playlist).
Ambas devem ter complexidade temporal O(1).
A playlist não é circular, ou seja, se o programa estiver executando o primeiro item da lista e o usuário pedir para ir ao item anterior (comando prev), o programa indica um erro e continua tocando a primeira música.
O mesmo deve acontecer caso o usuário solicite a execução da próxima música (comando next) estando o tocador executando a última música da playlist.
Abaixo, segue a descrição das funcionalidades:
• add(track): anexa uma nova faixa ao final da playlist;
• remove_at(pos): remove a faixa que se encontra na posição pos da lista;
• current(): retorna a faixa da playlist que se encontra em execução;
• play_next(): começa a executar a próxima música da lista;
• play_prev(): começa a executar a música anterior da lista;
• reset_cursor(): reinicializa o cursor da playlist, posicionando-o na primeira música (o cursor representa a música que está em execução no momento);
• __len__: método especial que retorna o tamanho da playlist; e
• __iter__: método especial que implementa um iterador para a playlist.
3.2 Fila Up Next — Músicas com Precedência
A fila Up Next guarda uma sequência de faixas que devem ser tocadas antes da próxima faixa “natural” da playlist.
Para implementar esta funcionalidade você deve utilizar uma fila, por meio da classe collections.deque, restringindo suas operações para respeitar o funcionamento de uma fila.
A presente funcionalidade possui a seguinte regra de funcionamento: quando o usuário executa o comando next, se a fila Up Next não estiver vazia, o programa toca a faixa do início da fila Up Next, remove-a da fila e não a adiciona na playlist.
Caso contrário, avança o cursor da playlist e toca a música seguinte na lista.
Em suma: itens da fila Up Next têm precedência sobre os itens da playlist, sendo descartados após a execução.
3.3 Histórico — Deque com tamanho máximo
Toda faixa efetivamente executada (via play, next ou prev) é registrada em um histórico, que é um deque com tamanho máximo (maxlen=30).
Quando se atinge a capacidade máxima, a faixa mais antiga é descartada automaticamente (descarte FIFO pelo lado oposto da inserção).
Cada item do histórico deve incluir, no mínimo, o id da faixa e o timestamp de reprodução (momento início da execução).
3.4 Smart Shuffle — Fila com Prioridade
O comando smart-shuffle <n> gera uma nova playlist com n faixas selecionadas da biblioteca, ordenadas por uma fila com prioridade, que deve ser implementada por meio da classe queue.PriorityQueue.
A chave que indica a prioridade do item na fila deve combinar os seguintes valores:
• Rating (peso maior): faixas com rating mais alto têm maior prioridade (saem antes da fila);
• Quão recente é a música no histórico (peso menor): faixas tocadas há pouco tempo têm menor prioridade (saem depois da fila).
Em suma, esta funcionalidade prioriza as músicas que têm maior rating.
A seguir, apresento uma sugestão de fórmula para a definição da prioridade do item.
Ela não é obrigatória, mas se você optar por outra fórmula, você deve documentá-la adequadamente.
Para uma faixa f, a chave de prioridade é:
chave(f) = -10 · rating(f) + penalty_rec(f), (1)
onde penalty_rec(f) é a penalidade relativa ao fato do item ter sido tocado mais recentemente.
Este valor é calculado a partir da posição pos_hist(f) da faixa no histórico (com pos_hist(f) = 0
para a última faixa tocada):
penalty_rec(f) = pos_hist(f), se pos_hist(f) < 5 (entre as 5 últimas tocadas), 0, caso contrário. (2)
O sinal negativo no rating compensa o fato de PriorityQueue retornar o menor valor primeiro.
4 Reprodução simulada
Neste trabalho você não deve se preocupar com a reprodução do áudio.
Desta forma, faremos uma reprodução simulada.
Quando uma faixa for tocada (via play, next ou prev), o programa imprime uma linha no formato:
>>> Tocando: "<título>" — <artista> (mm:ss)
e registra a faixa no histórico.
A formatação mm:ss da duração deve ser implementada explicitamente (use uma biblioteca como datetime para ajudar na tarefa).
5 Persistência
Os comandos save e load devem manter o estado completo entre execuções: ordem das faixas na playlist, posição do cursor, conteúdo da fila Up Next e do histórico.
O formato JSON é obrigatório.
Após save e load, os comandos playlist show, queue show e history devem produzir saída idêntica.
6 Testes automatizados
Você deve entregar a solução com testes automatizados, perfazendo uma cobertura mínima de 70%.
As bibliotecas pytest ou unittest podem ser utilizadas opara realizar a testagem.
Em particular, as seguintes operações e funcionalidades devem estar completamente testadas:
1. a estrutura da lista duplamente encadeada com sequência de inserções, remoções e movimentação
do cursor;
2. a precedência da fila Up Next sobre a playlist no comando next;
3. o limite de itens do histórico, com o descarte do item mais antigo (princípio FIFO) ao exceder o tamanho máximo estabelecido;
4. a ordenação produzida pela PriorityQueue do smart-shuffle;
5. os comandos de salvamento e carga de dados da solução (comandos save / load devem apresentar estado idêntico, antes e depois).
7 Entrega
O arquivo README.md é obrigatório e deve conter as seguintes informações: como executar sua solução, exemplo de sessão e descrição da fórmula adotada para o smart-shuffle, caso ela seja diferente da que aqui foi proposta.
8 Restrições
• Não é permitido usar list do Python para representar a playlist. A playlist deve ser uma
lista duplamente encadeada implementada com base na implementação de lista duplamente encadeada fornecida.
• Não é permitido substituir a PriorityQueue por sorted() ou list.sort() para gerar a playlist do smart-shuffle. A inserção e a retirada devem passar efetivamente pela fila com prioridade.
• Não é permitido utilizar bibliotecas externas, apenas bibliotecas padrão do Python.
9 Exemplo de sessão
Como referência informal de comportamento esperado, apresento um exemplo de sessão utilizando a solução:
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
