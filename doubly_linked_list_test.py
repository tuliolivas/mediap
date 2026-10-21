"""
Módulo de testes unitários para a classe Playlist e suas funcionalidades.
"""

import unittest
from typing import Optional

from .player import Player
from .playlist import Playlist, PlaylistEmptyError, PlaylistLimitError


# Classe de Testes Unitários

class TestPlaylistEstrutura(unittest.TestCase):
    """ Testes unitários para a classe Playlist e suas funcionalidades. """

    def setUp(self):
        """ 
        Método setUp é executado ANTES de cada teste.
        Obs.: Ele cria o cenário padrão para cada teste não interferir no outro.
        """
        self.playlist_vazia: Playlist[Optional[str]] = Playlist("Vazia")
        self.playlist_cheia: Playlist[Optional[str]] = Playlist("Cheia")
        self.playlist_cheia.add("Música A")
        self.playlist_cheia.add("Música B")
        self.playlist_cheia.add("Música C")

    def test_inicializacao(self):
        """ 1.1. Testes de Inicialização. """
        self.assertEqual(len(self.playlist_vazia), 0)
        self.assertEqual(self.playlist_vazia.name, "Vazia")
        # Verifica se lança a exceção correta ao tentar ler de lista vazia
        with self.assertRaises(PlaylistEmptyError):
            self.playlist_vazia.current()

    def test_insercao_none(self):
        """ 1.2. Testes de Inserção de Elementos Inválidos. """
        with self.assertRaises(ValueError):
            self.playlist_vazia.add(None)

    def test_insercao_e_cursor_inicial(self):
        """ 1.3. Testes de Inserção e Cursor Inicial. """
        self.playlist_vazia.add("Música A")
        self.assertEqual(len(self.playlist_vazia), 1)
        self.assertEqual(self.playlist_vazia.current(), "Música A")
        # Inserir mais faixas não deve mover o cursor da primeira posição
        self.playlist_vazia.add("Música B")
        self.assertEqual(len(self.playlist_vazia), 2)
        self.assertEqual(self.playlist_vazia.current(), "Música A")

    def test_movimentacao_cursor_sucesso(self):
        """ 2.1. Testes de Movimentação do Cursor. """
        # Avança A -> B -> C
        self.assertEqual(self.playlist_cheia.current(), "Música A")
        self.assertEqual(self.playlist_cheia.play_next(), "Música B")
        self.assertEqual(self.playlist_cheia.play_next(), "Música C")
        # Volta C -> B -> A
        self.assertEqual(self.playlist_cheia.play_prev(), "Música B")
        self.assertEqual(self.playlist_cheia.play_prev(), "Música A")

    def test_limites_do_cursor(self):
        """ 2.2. Testes de Limites do Cursor. """
        # Cursor está na A. Tentar voltar deve dar erro.
        with self.assertRaises(PlaylistLimitError):
            self.playlist_cheia.play_prev()
        # Ir até a última
        self.playlist_cheia.play_next() # Vai para B
        self.playlist_cheia.play_next() # Vai para C
        # Tentar avançar além da última deve dar erro
        with self.assertRaises(PlaylistLimitError):
            self.playlist_cheia.play_next()

    def test_reset_cursor(self):
        """ 2.3. Testes de Reset do Cursor. """
        self.playlist_cheia.play_next()
        self.playlist_cheia.play_next()
        self.assertEqual(self.playlist_cheia.current(), "Música C")
        self.playlist_cheia.reset_cursor()
        self.assertEqual(self.playlist_cheia.current(), "Música A")

    def test_indice_1_based_consistente_com_cursor(self):
        """A restauração do cursor e a remoção usam as mesmas posições 1-based."""
        self.playlist_cheia.set_cursor_by_index(1)
        self.assertEqual(self.playlist_cheia.current(), "Música A")
        self.assertEqual(self.playlist_cheia.get_cursor_index(), 1)
        self.playlist_cheia.set_cursor_by_index(2)
        self.assertEqual(self.playlist_cheia.current(), "Música B")
        self.assertEqual(self.playlist_cheia.get_cursor_index(), 2)

    def test_posicao_invalida_nao_altera_playlist(self):
        """Posições fora dos limites falham sem remover nenhuma faixa."""
        for pos in (0, 4):
            with self.subTest(pos=pos), self.assertRaises(IndexError):
                self.playlist_cheia.remove_at(pos)
            self.assertEqual(list(self.playlist_cheia), ["Música A", "Música B", "Música C"])

    def test_remover_faixa_sem_afetar_cursor(self):
        """ 3.1. Testes de Remoção e Reajuste Automático. """
        # Cursor está na "A" (pos 1). Remover a pos 3 ("C")
        removida = self.playlist_cheia.remove_at(3)
        self.assertEqual(removida, "Música C")
        self.assertEqual(len(self.playlist_cheia), 2)
        self.assertEqual(self.playlist_cheia.current(), "Música A")

    def test_remover_faixa_em_execucao_desloca_para_proxima(self):
        """ 3.2. Testes de Remoção e Reajuste Automático. """
        # Cursor na "A" (pos 1). Remover ela mesma.
        removida = self.playlist_cheia.remove_at(1)
        self.assertEqual(removida, "Música A")
        self.assertEqual(self.playlist_cheia.current(), "Música B")
        self.assertEqual(list(self.playlist_cheia), ["Música B", "Música C"])
        self.assertEqual(len(self.playlist_cheia), 2)

    def test_remover_faixa_antes_do_cursor_preserva_faixa_atual(self):
        """A remoção antes do cursor não deve alterar a faixa atualmente ativa."""
        self.playlist_cheia.play_next()
        removida = self.playlist_cheia.remove_at(1)
        self.assertEqual(removida, "Música A")
        self.assertEqual(self.playlist_cheia.current(), "Música B")
        self.assertEqual(list(self.playlist_cheia), ["Música B", "Música C"])

    def test_remover_ultima_faixa_em_execucao_desloca_para_anterior(self):
        """ 3.3. Testes de Remoção e Reajuste Automático. """
        # Ir para a última (C)
        self.playlist_cheia.play_next()
        self.playlist_cheia.play_next()
        # Remover a "C" (pos 3)
        self.playlist_cheia.remove_at(3)
        # Como C era a última, o cursor deve voltar para "B"
        self.assertEqual(self.playlist_cheia.current(), "Música B")

    def test_remover_unica_faixa_esvazia_cursor(self):
        """ 3.4. Testes de Remoção e Reajuste Automático. """
        self.playlist_vazia.add("Única")
        self.playlist_vazia.remove_at(1)
        self.assertEqual(len(self.playlist_vazia), 0)
        with self.assertRaises(PlaylistEmptyError):
            self.playlist_vazia.current()


class TestPlayerReproducao(unittest.TestCase):
    """Testes para o fluxo principal de reprodução do player."""

    def setUp(self):
        self.player = Player()
        self.player.library_load("library.json")
        self.player.playlist_create("Rock")
        self.player.playlist_add_track([1, 2, 3])

    def test_play_e_next_prev_na_playlist(self):
        self.assertEqual(self.player.play().id, 1)
        self.assertEqual(self.player.play_next().id, 2)
        self.assertEqual(self.player.play_prev().id, 1)

    def test_up_next_tem_precedencia_sobre_playlist(self):
        self.player.up_next_enqueue([3])
        self.assertEqual(self.player.play_next().id, 3)

    def test_current_retorna_faixa_ativa(self):
        self.assertEqual(self.player.player_current().id, 1)
        self.player.play_next()
        self.assertEqual(self.player.player_current().id, 2)

if __name__ == '__main__':
    unittest.main()
