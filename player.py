"""
Módulo: player.py
Implementa a classe Player, que gerencia a reprodução musical, incluindo:
- Playlist principal (baseada em lista duplamente encadeada).
- Fila FIFO "Up Next" (deque).
- Histórico de reprodução (deque com tamanho máximo).
Também fornece funcionalidades de Smart Shuffle, persistência em JSON e controle de reprodução.
"""

import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import PriorityQueue
from typing import List, Optional

from .models import Track
from .playlist import Playlist, PlaylistError


@dataclass
class HistoryEntry:
    """Uma execução registrada com ID da faixa e horário de início."""

    track_id: int
    timestamp: str


class Player:
    """
    Gerenciador de reprodução musical, incluindo:
    - Biblioteca de faixas (lista de objetos Track).
    - Playlist principal (Playlist[Track]).
    - Fila FIFO "Up Next" (deque[Track]).
    - Histórico de reprodução (deque[HistoryEntry] com tamanho máximo).
    """
    def __init__(self) -> None:
        self.library: List[Track] = []
        self.playlist: Optional[Playlist[Track]] = None
        self.up_next: deque[Track] = deque()
        self.history: deque[HistoryEntry] = deque(maxlen=30)

    # Controle da Biblioteca de Faixas
    def _data_path(self, file_name: str) -> Path:
        """Resolve nomes relativos a partir da pasta do pacote mediap."""
        return Path(__file__).resolve().parent / file_name

    def library_load(self, file_name: str) -> None:
        """Carrega a biblioteca JSON localizada na pasta do pacote."""
        library_path = self._data_path(file_name)

        try:
            with library_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Arquivo da biblioteca não encontrado: {file_name}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Arquivo JSON inválido: {file_name}") from exc

        tracks = [Track.from_dict(track_data) for track_data in data]
        if len({track.id for track in tracks}) != len(tracks):
            raise ValueError("A biblioteca contém IDs de faixa repetidos.")
        self.library = tracks

    def _track_by_id(self, track_id: int) -> Track:
        """Busca pelo ID informado, sem presumir que IDs sejam posições."""
        for track in self.library:
            if track.id == track_id:
                return track
        raise ValueError(f"ID de faixa inválido: {track_id}.")

    def _record_playback(self, track: Track) -> None:
        """Guarda no máximo 30 execuções, com timestamp ISO legível."""
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        self.history.append(HistoryEntry(track.id, timestamp))

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
        if self.playlist is None:
            raise PlaylistError("Nenhuma playlist ativa. Crie uma antes de adicionar faixas.")
        tracks = [self._track_by_id(tid) for tid in track_id]
        for track in tracks:
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

    # Gerenciamento da Up Next Queue

    def up_next_enqueue(self, track_id: list[int]) -> None:
        """ Adiciona faixa(s) à fila Up Next. """
        tracks = [self._track_by_id(tid) for tid in track_id]
        self.up_next.extend(tracks)

    def up_next_list(self) -> List[Track]:
        """ Retorna uma lista de todas as faixas na fila Up Next. """
        return list(self.up_next)

    # Controles de Reprodução

    def player_current(self) -> Optional[Track]:
        """Retorna a faixa indicada pelo cursor da playlist, se houver."""
        if self.playlist is not None and len(self.playlist) > 0:
            return self.playlist.current()
        return None

    def play(self) -> Track:
        """Inicia ou retoma a faixa do cursor e registra a execução."""
        current = self.player_current()
        if current is not None:
            self._record_playback(current)
            return current
        raise PlaylistError(
            "Nenhuma faixa disponível para reprodução."
            "\nA playlist está vazia."
        )

    def play_next(self) -> Track:
        """
        Avança a reprodução. A prioridade é da fila Up Next sobre a playlist.
        """
        if self.up_next:
            track = self.up_next.popleft()
        elif self.playlist is not None and len(self.playlist) > 0:
            track = self.playlist.play_next()
        else:
            raise PlaylistError(
                "Nenhuma faixa disponível para reprodução."
                "\nA playlist está vazia e a fila Up Next também está vazia."
            )
        self._record_playback(track)
        return track

    def play_prev(self) -> Track:
        """Retrocede a reprodução na playlist (Up Next não afeta prev)."""
        if self.playlist is None or len(self.playlist) == 0:
            raise PlaylistError("Nenhuma faixa disponível para reprodução. A playlist está vazia.")
        track = self.playlist.play_prev()
        self._record_playback(track)
        return track

    def smart_shuffle(self, count: int) -> Playlist[Track]:
        """Cria uma playlist priorizando rating e penalizando execuções recentes.

        O score é -10 vezes o rating, mais uma penalidade de 5 a 1 para
        faixas nas cinco posições mais recentes do histórico. A fila recebe
        (score, ID) para desempatar de modo previsível sem comparar objetos.
        Não há repetição; pedir mais faixas do que a biblioteca possui é erro.
        """
        if count <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if count > len(self.library):
            raise ValueError(
                f"Quantidade solicitada ({count}) maior que a biblioteca "
                f"({len(self.library)} faixas)."
            )

        recent_positions: dict[int, int] = {}
        for position, entry in enumerate(reversed(self.history)):
            if entry.track_id not in recent_positions:
                recent_positions[entry.track_id] = position

        priorities: PriorityQueue[tuple[int, int, Track]] = PriorityQueue()
        for track in self.library:
            position = recent_positions.get(track.id)
            penalty = 5 - position if position is not None and position < 5 else 0
            score = -10 * track.rating + penalty
            priorities.put((score, track.id, track))

        new_playlist = Playlist(f"Smart Shuffle ({count} faixas)")
        for _ in range(count):
            _, _, track = priorities.get()
            new_playlist.add(track)
        self.playlist = new_playlist
        return new_playlist

    def history_list(self) -> list[tuple[HistoryEntry, Track]]:
        """Retorna as execuções mais recentes primeiro, junto às faixas."""
        tracks_by_id = {track.id: track for track in self.library}
        return [
            (entry, tracks_by_id[entry.track_id])
            for entry in reversed(self.history)
        ]

    def save(self, file_name: str) -> None:
        """Salva biblioteca e estado do player em JSON autossuficiente."""
        playlist_data = None
        if self.playlist is not None:
            playlist_data = {
                "name": self.playlist.name,
                "track_ids": [track.id for track in self.playlist],
                "cursor_index": self.playlist.get_cursor_index(),
            }

        data = {
            "library": [track.to_dict() for track in self.library],
            "playlist": playlist_data,
            "up_next": [track.id for track in self.up_next],
            "history": [
                {"track_id": entry.track_id, "timestamp": entry.timestamp}
                for entry in self.history
            ],
        }
        self._data_path(file_name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self, file_name: str) -> None:
        """Restaura o player; os dados da biblioteca viajam no próprio arquivo."""
        try:
            data = json.loads(self._data_path(file_name).read_text(encoding="utf-8"))
            library = [Track.from_dict(item) for item in data["library"]]
            tracks_by_id = {track.id: track for track in library}
            if len(tracks_by_id) != len(library):
                raise ValueError("O estado contém IDs de faixa repetidos.")

            playlist_data = data["playlist"]
            playlist = None
            if playlist_data is not None:
                playlist = Playlist(playlist_data["name"])
                for track_id in playlist_data["track_ids"]:
                    playlist.add(tracks_by_id[track_id])
                playlist.set_cursor_by_index(playlist_data["cursor_index"])

            up_next = deque(tracks_by_id[track_id] for track_id in data["up_next"])
            history = deque(
                (
                    HistoryEntry(item["track_id"], item["timestamp"])
                    for item in data["history"]
                ),
                maxlen=30,
            )
            if any(entry.track_id not in tracks_by_id for entry in history):
                raise ValueError("O histórico referencia uma faixa inexistente.")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Arquivo JSON inválido: {file_name}") from exc
        except (KeyError, IndexError, TypeError, ValueError, PlaylistError) as exc:
            raise ValueError(f"Estado inválido em '{file_name}': {exc}") from exc

        self.library = library
        self.playlist = playlist
        self.up_next = up_next
        self.history = history
