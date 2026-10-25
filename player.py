"""
Módulo: player.py
Implementa a classe Player, que gerencia a reprodução musical, incluindo:
- Playlist principal (baseada em lista duplamente encadeada).
- Fila de prioridade "Up Next" (deque).
- Histórico de reprodução (deque com tamanho máximo).
Também fornece funcionalidades de Smart Shuffle, persistência em JSON e controle de reprodução.
"""

import json
from pathlib import Path
# import time
from collections import deque
# from dataclasses import dataclass, asdict
# from queue import PriorityQueue
from typing import List, Optional

from .playlist import Playlist, PlaylistError#, PlaylistEmptyError, InvalidCursorError
from .models import Track


class Player:
    """
    Gerenciador de reprodução musical, incluindo:
    - Biblioteca de faixas (lista de objetos Track).
    - Playlist principal (Playlist[Track]).
    - Fila de prioridade "Up Next" (deque[Track]).
    - Histórico de reprodução (deque[HistoryEntry] com tamanho máximo).
    """
    def __init__(self) -> None:
        self.library: List[Track] = []
        self.playlist: Optional[Playlist[Track]] = None
        self.up_next: deque[Track] = deque()
        # self.history: deque[HistoryEntry] = deque(maxlen=20)
        # self._current_track: Optional[Track] = None

    # Controle da Biblioteca de Faixas
    def library_load(self, file_name: str) -> None:
        """Carrega a biblioteca de faixas a partir de um arquivo JSON.

        Tenta localizar o ficheiro em caminhos relevantes: diretório atual, diretório do
        pacote e raiz do projeto, para funcionar tanto em execução local quanto em
        `python -m mediap`.
        """
        candidates = [
            Path(file_name),
            Path.cwd() / file_name,
            Path(__file__).resolve().parent / file_name,
            Path(__file__).resolve().parent.parent / file_name,
        ]

        library_path = next((path for path in candidates if path.exists()), candidates[2])

        try:
            with library_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Arquivo da biblioteca não encontrado: {file_name}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Arquivo JSON inválido: {file_name}") from exc

        self.library = [Track.from_dict(track_data) for track_data in data]

    def library_list_by(self, sort_by: str = "id") -> List[Track]:
        """Lista as faixas da biblioteca ordenadas por um critério específico."""
        valid_fields = {"id", "title", "artist", "duration", "rating", "data_adicao"}
        if sort_by not in valid_fields:
            raise ValueError(f"Parâmetro de ordenação inválido: {sort_by}")
        return sorted(self.library, key=lambda t: getattr(t, sort_by))

    # Gerenciamento da Playlist

    def playlist_create(self, name: str) -> None:
        """ Cria uma nova playlist com o nome fornecido. """
        self.playlist = Playlist(name)

    def playlist_get_name(self) -> str:
        """ Retorna o nome da playlist atual. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de obter o nome.")
        return self.playlist.name

    def playlist_add_track(self, track_id: list[int]) -> None:
        """ Adiciona uma faixa à playlist atual. """
        for tid in track_id:
            if tid <= 0 or tid > len(self.library):
                raise ValueError(f"ID de faixa inválido: {tid}.")
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de adicionar faixas.")
        for tid in track_id:
            track = self.library[tid - 1]
            self.playlist.add(track)

    def playlist_remove_track_at(self, pos: int) -> Track:
        """ Remove a faixa na posição `pos` da playlist atual. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de remover faixas.")
        return self.playlist.remove_at(pos)

    def playlist_list_tracks(self) -> List[Track]:
        """ Retorna uma lista de todas as faixas na playlist atual. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de listar faixas.")
        return list(self.playlist)

    def playlist_current_track(self) -> Track:
        """ Retorna a faixa atualmente em execução na playlist. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de obter a faixa atual.")
        return self.playlist.current()

    def playlist_reset_cursor(self) -> None:
        """ Reseta o cursor da playlist para a primeira faixa. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de resetar o cursor.")
        self.playlist.reset_cursor()

    def playlist_play_next(self) -> Track:
        """ Avança para a próxima faixa na playlist e retorna a faixa atual. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de avançar faixas.")
        return self.playlist.play_next()

    def playlist_play_prev(self) -> Track:
        """ Retrocede para a faixa anterior na playlist e retorna a faixa atual. """
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de retroceder faixas.")
        return self.playlist.play_prev()

    # Gerenciamento da Up Next Queue

    def up_next_enqueue(self, track_id: list[int]) -> None:
        """ Adiciona faixa(s) à fila Up Next. """
        for tid in track_id:
            if tid <= 0 or tid > len(self.library):
                raise ValueError(f"ID de faixa inválido: {tid}.")

        for tid in track_id:
            track = self.library[tid - 1]
            self.up_next.append(track)

    def up_next_list(self) -> List[Track]:
        """ Retorna uma lista de todas as faixas na fila Up Next. """
        return list(self.up_next)

    def up_next_current(self) -> Optional[Track]:
        """Retorna a primeira faixa da fila Up Next, se houver."""
        return self.up_next[0] if self.up_next else None

    # Controles de Reprodução

    def player_current(self) -> Optional[Track]:
        """Mostar a faixa sob qual o cursor está posicionado"""
        if self.playlist is not None and len(self.playlist) > 0:
            return self.playlist.current()
        if self.up_next:
            return self.up_next[0]
        return None

    def play(self) -> Track:
        """Retorna a faixa atual da reprodução, priorizando a playlist."""
        current = self.player_current()
        if current is not None:
            return current
        raise PlaylistError(
            "Nenhuma faixa disponível para reprodução."
            "\nA playlist está vazia e a fila Up Next também está vazia."
        )

    def play_next(self) -> Track:
        """
        Avança a reprodução. A prioridade é da fila Up Next sobre a playlist.
        """
        if self.up_next:
            return self.up_next.popleft()
        if self.playlist is None or len(self.playlist) == 0:
            raise PlaylistError(
                "Nenhuma faixa disponível para reprodução."
                "\nA playlist está vazia e a fila Up Next também está vazia."
            )
        return self.playlist.play_next()

    def play_prev(self) -> Track:
        """Retrocede a reprodução na playlist (Up Next não afeta prev)."""
        if self.playlist is None or len(self.playlist) == 0:
            raise PlaylistError("Nenhuma faixa disponível para reprodução. A playlist está vazia.")
        return self.playlist.play_prev()

    # # ==========================================
    # # Gerenciamento de Filas e Histórico
    # # ==========================================

    # def add_to_playlist(self, track: Track) -> None:
    #     self.playlist.add(track)

    # def enqueue_up_next(self, track: Track) -> None:
    #     """Adiciona uma música à fila de prioridade Up Next."""
    #     self.up_next.append(track)

    # def _record_history(self, track: Track) -> None:
    #     """Registra a execução no histórico (FIFO gerido pelo maxlen do deque)."""
    #     entry = HistoryEntry(track_id=track.id, timestamp=time.time())
    #     self.history.append(entry)

    # # ==========================================
    # # Smart Shuffle
    # # ==========================================

    # def smart_shuffle(self, n: int, library: List[Track]) -> Playlist[Track]:
    #     """
    #     Gera uma nova playlist baseada em prioridade (Rating alto, Baixa Recência).
    #     """
    #     pq: PriorityQueue[tuple[float, str, Track]] = PriorityQueue()

    #     for track in library:
    #         priority = self._calculate_priority(track)
    #         # A tupla usa (prioridade, id, objeto) para evitar empates quebrem a comparação
    #         pq.put((priority, track.id, track))

    #     nova_playlist = Playlist(f"Smart Shuffle ({n} faixas)")

    #     count = 0
    #     while not pq.empty() and count < n:
    #         _, _, track = pq.get()
    #         nova_playlist.add(track)
    #         count += 1

    #     self.playlist = nova_playlist
    #     return self.playlist

    # def _calculate_priority(self, track: Track) -> float:
    #     """
    #     Fórmula de prioridade: Menores valores saem primeiro na PriorityQueue.
    #     - Rating maior abaixa o valor (maior prioridade).
    #     - Recência no histórico aumenta o valor (penalidade / menor prioridade).
    #     """
    #     # Ex: Rating 5.0 -> Score -500
    #     rating_score = - (track.rating * 100)

    #     recency_penalty = 0
    #     # Inspeciona o histórico do mais recente (direita) para o mais antigo (esquerda)
    #     history_list = list(self.history)
    #     for i, entry in enumerate(reversed(history_list)):
    #         if entry.track_id == track.id:
    #             # Se estiver no histórico, aplica penalidade baseada em quão recente foi.
    #             # Se maxlen é 20 e é a última tocada (i=0), penalidade é 20 * 10 = +200
    #             recency_penalty = (len(history_list) - i) * 10
    #             break

    #     return rating_score + recency_penalty

    # # ==========================================
    # # Persistência JSON
    # # ==========================================

    # def save(self, filepath: str) -> None:
    #     """Salva o estado integral do Player num arquivo JSON."""
    #     data = {
    #         "playlist_name": self.playlist.name,
    #         "playlist_tracks": [asdict(t) for t in self.playlist],
    #         "cursor_index": self.playlist.get_cursor_index(),
    #         "up_next": [asdict(t) for t in self.up_next],
    #         "history": [asdict(h) for h in self.history]
    #     }
    #     with open(filepath, "w", encoding="utf-8") as f:
    #         json.dump(data, f, indent=4)

    # def load(self, filepath: str) -> None:
    #     """Restaura o estado integral do Player a partir do arquivo JSON."""
    #     with open(filepath, "r", encoding="utf-8") as f:
    #         data = json.load(f)

    #     # Restaura Playlist
    #     self.playlist = Playlist(data["playlist_name"])
    #     for track_data in data["playlist_tracks"]:
    #         self.playlist.add(Track.from_dict(track_data))

    #     # Restaura Cursor
    #     self.playlist.set_cursor_by_index(data["cursor_index"])
    #     self._current_track=self.playlist.current() if data["cursor_index"] is not None else None

    #     # Restaura Up Next
    #     self.up_next.clear()
    #     for track_data in data["up_next"]:
    #         self.up_next.append(Track.from_dict(track_data))

    #     # Restaura Histórico
    #     self.history.clear()
    #     for hist_data in data["history"]:
    #         self.history.append(HistoryEntry(**hist_data))
