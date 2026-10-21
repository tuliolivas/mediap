"""
Módulo models.py
Define a classe Track, que representa uma faixa de música.
"""

from typing import Any

class Track:
    """
    Classe Track
    Define como uma faixa é representada no sistema:
    - ID: Identificador único da faixa.
    - Título: Nome da faixa.
    - Artista: Nome do artista ou banda.
    - Duração: Duração da faixa em segundos.
    - Nota: Avaliação da faixa, de 1 a 5.
    - Data de Adição: Data em que a faixa foi adicionada à biblioteca.
    Também fornece métodos para criar uma instância a partir de um dicionário
    e para converter uma instância em um dicionário.
    """
    def __init__(self, id: int, title: str, artist: str,
                 duration: int, rating: int, data_adicao: str) -> None:
        self.id = id
        self.title = title
        self.artist = artist
        self.duration = duration
        self.rating = rating
        self.data_adicao = data_adicao

    def __str__(self) -> str:
        """Representação em texto formatada da faixa."""
        return f"[{self.id}] {self.title} - {self.artist} ({self.duration}s) | {self.rating}"

    @property
    def id(self) -> int:
        """get para o id"""
        return self.__id

    @id.setter
    def id(self, valor_id: int) -> None:
        """set para o id"""
        if not isinstance(valor_id, int): # type: ignore
            raise TypeError("O id precisa ser do tipo inteiro.")
        if valor_id < 0:
            raise ValueError("O id precisa ser um valor positivo.")
        self.__id = valor_id

    @property
    def title(self) -> str:
        """get para o título"""
        return self.__title

    @title.setter
    def title(self, valor_title: str) -> None:
        """set para o título"""
        if not isinstance(valor_title, str): # type: ignore
            raise TypeError("O título precisa ser do tipo string.")
        if len(valor_title) == 0:
            raise ValueError("O título precisa ser um valor não vazio.")
        self.__title = valor_title

    @property
    def artist(self) -> str:
        """get para o artista"""
        return self.__artist

    @artist.setter
    def artist(self, valor_artist: str) -> None:
        """set para o artista"""
        if not isinstance(valor_artist, str): # type: ignore
            raise TypeError("O artista precisa ser do tipo string.")
        if len(valor_artist) == 0:
            raise ValueError("O artista precisa ser um valor não vazio.")
        self.__artist = valor_artist

    @property
    def duration(self) -> int:
        """get para a duração"""
        return self.__duration

    @duration.setter
    def duration(self, valor_duration: int) -> None:
        """set para a duração"""
        if not isinstance(valor_duration, int): # type: ignore
            raise TypeError("A duração precisa ser do tipo inteiro.")
        if valor_duration < 0:
            raise ValueError("A duração precisa ser um valor positivo.")
        self.__duration = valor_duration

    @property
    def rating(self) -> int:
        """get para a nota"""
        return self.__rating

    @rating.setter
    def rating(self, valor_rating: int) -> None:
        """set para a nota"""
        if not isinstance(valor_rating, int): # type: ignore
            raise TypeError("A nota precisa ser do tipo inteiro.")
        if not 1 <= valor_rating <= 5:
            raise ValueError("A nota precisa ser um valor entre 1 e 5.")
        self.__rating = valor_rating

    @property
    def data_adicao(self) -> str:
        """get para a data de adição"""
        return self.__data_adicao

    @data_adicao.setter
    def data_adicao(self, valor_data_adicao: str) -> None:
        """set para a data de adição"""
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
            id=data['id'],
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
