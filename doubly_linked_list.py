"""
Módulo: doubly_linked_list.py
Implementa uma lista duplamente encadeada genérica com nós sentinela, incluindo
uma classe Playlist especializada para gerenciar a execução musical.
Também define exceções de domínio para manipulação de playlists.
"""


from __future__ import annotations
from typing import Any, Generic, Iterator, Optional, TypeVar, cast


T = TypeVar("T")

# Estrutura Base: Lista Duplamente Encadeada

class DoublyLinkedList(Generic[T]):
    """
    Lista duplamente encadeada genérica com nós sentinela.
    """

    class _Node:
        """
        Nó interno da lista duplamente encadeada,
        contendo referências para o elemento, o nó anterior e o próximo nó.
        """
        def __init__(
            self,
            elem: Any,
            prev: Optional[DoublyLinkedList._Node],
            next_node: Optional[DoublyLinkedList._Node],
        ) -> None:
            self.n_elem = elem
            self.n_prev = prev
            self.n_next = next_node

        def invalidate(self) -> None:
            """
            Invalida, por segurança, a referências de um nó removido.
            """
            self.n_prev, self.n_next = None, None

        def is_valid(self) -> bool:
            """
            True: nó está vinculado à lista.
            False: nó foi removido ou é sentinela.
            """
            return self.n_prev is not None and self.n_next is not None

    def __init__(self) -> None:
        '''
        Inicializa a lista com nós sentinela e tamanho zero (_header <-- --> _trailer).
        '''
        self._header = self._Node(None, None, None)
        self._trailer = self._Node(None, None, None)
        self._header.n_next = self._trailer
        self._trailer.n_prev = self._header
        self._length = 0

    def _require_node(self, node: Optional[DoublyLinkedList._Node]) -> DoublyLinkedList._Node:
        """
        Garante que o nó não seja None, caso contrário, lança RuntimeError.
        """
        if node is None:
            raise RuntimeError("Erro interno: Ponteiro nulo encontrado na lista.")
        return node

    def _extract_element(self, node: DoublyLinkedList._Node) -> T:
        """
        Extrai o elemento de um nó, garantindo que não seja None.
        """
        if not node.is_valid():
            raise RuntimeError("Erro interno: Tentativa de leitura em nó inválido ou removido.")
        if node.n_elem is None:
            raise RuntimeError("Erro interno: Nó válido mas elemento é None.")
        return cast(T, node.n_elem)

    def _nodes(self) -> Iterator[DoublyLinkedList._Node]:
        """
        Iterador interno sobre os nós da lista, ignorando sentinelas.
        """
        current = self._require_node(self._header.n_next)
        while current is not self._trailer:
            yield current
            current = self._require_node(current.n_next)

    def __iter__(self) -> Iterator[T]:
        """
        Método especial: implementa um iterador para a lista.
        """
        for node in self._nodes():
            yield self._extract_element(node)

    def __len__(self) -> int:
        """
        Método especial: retorna o tamanho atual da lista.
        """
        return self._length

    def _insert_last(self, elem: T) -> DoublyLinkedList._Node:
        """Anexa um elemento no fim da lista e devolve seu nó."""
        if elem is None:
            raise ValueError("Erro interno: Elementos nulos (None) não são permitidos.")
        previous = self._require_node(self._trailer.n_prev)
        new_node = self._Node(elem, previous, self._trailer)
        previous.n_next = new_node
        self._trailer.n_prev = new_node
        self._length += 1
        return new_node

    def _find_node_by_index(self, pos: int) -> DoublyLinkedList._Node:
        """
        Retorna o nó na posição `pos` (1-based) da lista.
        """
        if pos <= 0 or pos > self._length:
            raise IndexError(f"Erro interno: Posição {pos} fora dos limites da lista.")
        if pos <= self._length // 2:
            current = self._require_node(self._header.n_next)
            for _ in range(pos - 1):
                current = self._require_node(current.n_next)
        else:
            current = self._require_node(self._trailer.n_prev)
            for _ in range(self._length - pos):
                current = self._require_node(current.n_prev)
        return current

    def _remove_node(self, node: DoublyLinkedList._Node) -> T:
        """ Remove o nó `node` da lista e retorna seu elemento. """
        if not node.is_valid():
            raise ValueError("Erro interno: Tentativa de remover nó desvinculado ou inválido.")
        prev_node = self._require_node(node.n_prev)
        next_node = self._require_node(node.n_next)
        prev_node.n_next = next_node
        next_node.n_prev = prev_node
        self._length -= 1
        elem = self._extract_element(node)
        node.invalidate()
        return elem
