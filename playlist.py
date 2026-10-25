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
    Lista duplamente encadeada com cursor para a faixa atual.

    O cursor guarda o nó, não a posição, para avançar e retroceder em O(1).
    A playlist não é circular: tentar passar de uma ponta gera erro.
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
        """Anexa a faixa e torna-a atual apenas se a playlist estava vazia."""
        node = self._insert_last(track)
        if self._cursor is None:
            self._cursor = node

    def remove_at(self, pos: int) -> T:
        """
        Remove a posição 1-based. Se remover a faixa atual, o cursor vai para a
        próxima; se ela era a última, vai para a anterior; se era a única, zera.
        """
        node_to_remove = self._find_node_by_index(pos)
        if self._cursor is node_to_remove:
            next_node = self._require_node(node_to_remove.n_next)
            if next_node is not self._trailer:
                self._cursor = next_node
            else:
                previous_node = self._require_node(node_to_remove.n_prev)
                self._cursor = None if previous_node is self._header else previous_node
        return self._remove_node(node_to_remove)

    def current(self) -> T:
        """Retorna a faixa do cursor ou gera erro se a playlist estiver vazia."""
        cursor = self._validate_cursor()
        return self._extract_element(cursor)

    def play_next(self) -> T:
        """Avança uma posição em O(1); não retorna ao início ao chegar ao fim."""
        cursor = self._validate_cursor()
        proximo = self._require_node(cursor.n_next)
        if proximo is self._trailer:
            raise PlaylistLimitError("Limite atingido: Já está na última música.")
        self._cursor = proximo
        return self._extract_element(self._cursor)

    def play_prev(self) -> T:
        """Retrocede uma posição em O(1); não passa do início da playlist."""
        cursor = self._validate_cursor()
        anterior = self._require_node(cursor.n_prev)
        if anterior is self._header:
            raise PlaylistLimitError("Limite atingido: Já está na primeira música.")
        self._cursor = anterior
        return self._extract_element(self._cursor)

    def reset_cursor(self) -> None:
        """Aponta o cursor para a primeira faixa, ou deixa-o vazio se necessário."""
        primeiro = self._require_node(self._header.n_next)
        if primeiro is self._trailer:
            self._cursor = None
        else:
            self._cursor = primeiro

    # __len__ e __iter__ são herdados da lista duplamente encadeada.

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
