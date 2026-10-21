"""
Módulo: playlist.py
Implementa uma Playlist especializada para gerenciar a execução musical.
Também define exceções de domínio para manipulação de playlists.
"""


from __future__ import annotations
from typing import Optional, TypeVar

from.doubly_linked_list import DoublyLinkedList


T = TypeVar("T")

# Classe Principal: Playlist

class Playlist(DoublyLinkedList[T]):
    """
    Gerenciador de execução musical baseado em lista duplamente encadeada.
    """

    def __init__(self, name: str = "Minha Playlist") -> None:
        super().__init__()
        self.name = name
        self._cursor: Optional[DoublyLinkedList._Node] = None

    def _validate_cursor(self) -> DoublyLinkedList._Node:
        """
        Valida o cursor atual, garantindo que ele aponte para um nó válido.
        """
        if self._cursor is None:
            raise PlaylistEmptyError("A playlist está vazia. Nenhuma música ativa.")
        if not self._cursor.is_valid():
            raise InvalidCursorError("O cursor aponta para um nó inválido/removido.")
        return self._cursor

    def add(self, track: T) -> None:
        """
        1. add(track): anexa uma nova faixa ao final da playlist.
        """
        node = self._insert_last(track)
        if self._cursor is None:
            self._cursor = node

    def remove_at(self, pos: int) -> T:
        """
        2. remove_at(pos): remove a faixa na posição `pos` (1-based) da playlist.
        """
        node_to_remove = self._find_node_by_index(pos)
        if self._length == 1:
            self._cursor = None
        else:
            if self._cursor is node_to_remove:      # a faixa em execução for removida
                next_node = self._require_node(node_to_remove.n_next)
                prev_node = self._require_node(node_to_remove.n_prev)
                if next_node is not self._trailer:
                    self._cursor = next_node
                elif prev_node is not self._header:
                    self._cursor = prev_node
        return self._remove_node(node_to_remove)

    def current(self) -> T:
        """
        3. current(): retorna a faixa atual em execução.
        """
        cursor = self._validate_cursor()
        return self._extract_element(cursor)

    def play_next(self) -> T:
        """
        4. play_next(): avança o cursor em O(1) e retorna a faixa."""
        cursor = self._validate_cursor()
        proximo = self._require_node(cursor.n_next)
        if proximo is self._trailer:
            raise PlaylistLimitError("Limite atingido: Já está na última música.")
        self._cursor = proximo
        return self._extract_element(self._cursor)

    def play_prev(self) -> T:
        """
        5. play_prev(): retrocede o cursor em O(1) e retorna a faixa.
        """
        cursor = self._validate_cursor()
        anterior = self._require_node(cursor.n_prev)
        if anterior is self._header:
            raise PlaylistLimitError("Limite atingido: Já está na primeira música.")
        self._cursor = anterior
        return self._extract_element(self._cursor)

    def reset_cursor(self) -> None:
        """
        6. reset_cursor(): reseta o cursor para a primeira faixa.
        """
        primeiro = self._require_node(self._header.n_next)
        if primeiro is self._trailer:
            self._cursor = None
        else:
            self._cursor = primeiro

    # 7. __len__: herdado da DoublyLinkedList
    # 8. __iter__: herdado da DoublyLinkedList

    # Suporte à Persistência JSON (Exigência do Save/Load)
    def get_cursor_index(self) -> Optional[int]:
        """
        Devolve o índice (1-based) do cursor para persistência em JSON.
        """
        if self._cursor is None:
            return None
        if not self._cursor.is_valid():
            raise InvalidCursorError("Impossível ler índice de um cursor inválido.")
        for i, node in enumerate(self._nodes(), start=1):
            if node is self._cursor:
                return i
        raise InvalidCursorError("Cursor válido não encontrado na estrutura.")

    def set_cursor_by_index(self, index: Optional[int]) -> None:
        """
        Restaura o cursor via índice numérico vindo do JSON.
        """
        if index is None:
            if len(self) > 0:
                raise InvalidCursorError("Cursor não pode ser None em playlist povoada.")
            self._cursor = None
            return
        if len(self) == 0:
            raise InvalidCursorError("Impossível atribuir índice a uma playlist vazia.")
        try:
            self._cursor = self._find_node_by_index(index)
        except IndexError as err:
            raise InvalidCursorError(f"Índice {index} do JSON fora dos limites.") from err


# Exceções de Domínio

class PlaylistError(Exception):
    """Exceção base para falhas de domínio e estrutura da playlist."""


class PlaylistEmptyError(PlaylistError):
    """Lançada ao tentar acessar ou manipular o cursor em uma playlist vazia."""


class PlaylistLimitError(PlaylistError):
    """Lançada ao tentar avançar além da última faixa ou retroceder além da primeira."""


class InvalidCursorError(PlaylistError):
    """Lançada quando a restauração ou validação de cursor falha/está corrompida."""
