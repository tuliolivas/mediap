"""Modelo de dados de uma faixa musical."""

from typing import Any

class Track:
    """Representa uma faixa e valida os valores atribuídos às propriedades.

    `from_dict` e `to_dict` mantêm a conversão para o formato usado nos JSONs.
    """
    def __init__(self, track_id: int, title: str, artist: str,
                 duration: int, rating: int, data_adicao: str) -> None:
        self.id = track_id
        self.title = title
        self.artist = artist
        self.duration = duration
        self.rating = rating
        self.data_adicao = data_adicao

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, valor_id: int) -> None:
        if not isinstance(valor_id, int): # type: ignore
            raise TypeError("O id precisa ser do tipo inteiro.")
        if valor_id < 0:
            raise ValueError("O id não pode ser negativo.")
        self.__id = valor_id

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, valor_title: str) -> None:
        if not isinstance(valor_title, str): # type: ignore
            raise TypeError("O título precisa ser do tipo string.")
        if len(valor_title) == 0:
            raise ValueError("O título precisa ser um valor não vazio.")
        self.__title = valor_title

    @property
    def artist(self) -> str:
        return self.__artist

    @artist.setter
    def artist(self, valor_artist: str) -> None:
        if not isinstance(valor_artist, str): # type: ignore
            raise TypeError("O artista precisa ser do tipo string.")
        if len(valor_artist) == 0:
            raise ValueError("O artista precisa ser um valor não vazio.")
        self.__artist = valor_artist

    @property
    def duration(self) -> int:
        return self.__duration

    @duration.setter
    def duration(self, valor_duration: int) -> None:
        if not isinstance(valor_duration, int): # type: ignore
            raise TypeError("A duração precisa ser do tipo inteiro.")
        if valor_duration < 0:
            raise ValueError("A duração não pode ser negativa.")
        self.__duration = valor_duration

    @property
    def rating(self) -> int:
        return self.__rating

    @rating.setter
    def rating(self, valor_rating: int) -> None:
        if not isinstance(valor_rating, int): # type: ignore
            raise TypeError("A nota precisa ser do tipo inteiro.")
        if not 1 <= valor_rating <= 5:
            raise ValueError("A nota precisa ser um valor entre 1 e 5.")
        self.__rating = valor_rating

    @property
    def data_adicao(self) -> str:
        return self.__data_adicao

    @data_adicao.setter
    def data_adicao(self, valor_data_adicao: str) -> None:
        if not isinstance(valor_data_adicao, str): # type: ignore
            raise TypeError("A data de adição precisa ser do tipo string.")
        self.__data_adicao = valor_data_adicao

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Track':
        """
        Cria uma instância de Track a partir de um dicionário.
        Espera que o dicionário contenha as chaves:
        'id', 'title', 'artist', 'duration', 'rating', 'data_adicao'.
        """
        return cls(
            track_id=data['id'],
            title=data['title'],
            artist=data['artist'],
            duration=data['duration'],
            rating=data['rating'],
            data_adicao=data['data_adicao']
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Converte a instância de Track em um dicionário.
        Retorna um dicionário com as chaves:
        'id', 'title', 'artist', 'duration', 'rating', 'data_adicao'.
        """
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'duration': self.duration,
            'rating': self.rating,
            'data_adicao': self.data_adicao
        }
