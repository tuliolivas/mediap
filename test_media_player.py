"""Testes da lista, playlist, player e interface de terminal."""

import unittest
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from .cli import format_duration, run_cli
from .player import HistoryEntry, Player
from .playlist import Playlist, PlaylistEmptyError, PlaylistLimitError


class TestPlaylistEstrutura(unittest.TestCase):
    """Testa a lista duplamente encadeada e o cursor da playlist."""

    def setUp(self):
        """ 
        Método setUp é executado ANTES de cada teste.
        Obs.: Ele cria o cenário padrão para cada teste não interferir no outro.
        """
        self.playlist_vazia: Playlist[str] = Playlist("Vazia")
        self.playlist_cheia: Playlist[str] = Playlist("Cheia")
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
        self.assertEqual(self.player.playlist_current_track().id, 1)
        self.assertEqual(len(self.player.up_next), 0)
        self.assertEqual(self.player.history[-1].track_id, 3)

    def test_current_retorna_faixa_ativa(self):
        self.assertEqual(self.player.player_current().id, 1)
        self.player.play_next()
        self.assertEqual(self.player.player_current().id, 2)

    def test_historico_limita_30_e_descarta_os_mais_antigos(self):
        played_ids = [(index % 3) + 1 for index in range(35)]
        self.player.up_next_enqueue(played_ids)
        for _ in played_ids:
            self.player.play_next()

        self.assertEqual(self.player.history.maxlen, 30)
        self.assertEqual(len(self.player.history), 30)
        self.assertEqual(
            [entry.track_id for entry in self.player.history], played_ids[-30:]
        )

    def test_smart_shuffle_prioriza_rating_e_penaliza_recencia(self):
        self.player.history.append(HistoryEntry(3, "2026-10-25T12:00:00+00:00"))
        shuffled = self.player.smart_shuffle(len(self.player.library))
        tracks = list(shuffled)
        ratings = [track.rating for track in tracks]

        self.assertEqual(ratings, sorted(ratings, reverse=True))
        track_ids = [track.id for track in tracks]
        self.assertGreater(track_ids.index(3), track_ids.index(4))
        with self.assertRaises(ValueError):
            self.player.smart_shuffle(len(self.player.library) + 1)

    def test_save_load_restaura_estado_sem_carregar_biblioteca(self):
        self.player.play_next()
        self.player.up_next_enqueue([6, 4])
        self.player.play_next()

        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            self.player.save(str(state_path))

            restored = Player()
            restored.load(str(state_path))

        self.assertEqual(
            [track.id for track in restored.playlist],
            [track.id for track in self.player.playlist],
        )
        self.assertEqual(
            restored.playlist.get_cursor_index(),
            self.player.playlist.get_cursor_index(),
        )
        self.assertEqual(
            [track.id for track in restored.up_next],
            [track.id for track in self.player.up_next],
        )
        self.assertEqual(
            [(entry.track_id, entry.timestamp) for entry in restored.history],
            [(entry.track_id, entry.timestamp) for entry in self.player.history],
        )
        self.assertEqual(len(restored.library), len(self.player.library))

    def test_arquivo_de_estado_relativo_fica_na_pasta_do_pacote(self):
        package_dir = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=package_dir) as temporary_dir:
            relative_dir = Path(temporary_dir).name
            state_name = f"{relative_dir}/state.json"
            state_path = package_dir / state_name

            self.player.save(state_name)
            self.assertTrue(state_path.exists())

            restored = Player()
            restored.load(state_name)
            self.assertEqual(len(restored.library), len(self.player.library))


class TestCLI(unittest.TestCase):
    """Testa uma sessão de ponta a ponta sem exigir entrada interativa."""

    def test_formatacao_e_comandos_da_sessao(self):
        self.assertEqual(format_duration(212), "3:32")

        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "estado.json"
            commands = [
                "library load library.json",
                "library list rating",
                "playlist new Favoritas",
                "playlist add 3 4",
                "playlist show",
                "playlist reset",
                "playlist remove 2",
                "play",
                "enqueue 8",
                "queue show",
                "next",
                "prev",
                "current",
                "history",
                "smart-shuffle 2",
                "save " + str(state_path),
                "load " + str(state_path),
                "upnext 8",
                "exit",
                "library load arquivo-inexistente.json",
                "unknown-command",
                "quit",
            ]
            with patch("builtins.input", side_effect=commands):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    with self.assertRaises(SystemExit):
                        run_cli()

        session_output = output.getvalue()
        self.assertIn('>>> Tocando: "Ghost of Perdition" — Opeth (10:29)', session_output)
        self.assertIn('>>> Tocando: "Homage for Satan" — Deicide (3:59)', session_output)
        self.assertIn(
            'Faixa removida da playlist: "The Drapery Falls" — Opeth (10:54)',
            session_output,
        )
        self.assertIn('Faixa no cursor da playlist: "Ghost of Perdition" — Opeth (10:29)', session_output)
        self.assertIn("Estado carregado de", session_output)
        self.assertIn("Arquivo da biblioteca não encontrado", session_output)
        self.assertIn("Comando desconhecido: 'upnext'", session_output)
        self.assertIn("Comando desconhecido: 'exit'", session_output)
        self.assertIn('1. "Homage for Satan" — Deicide (3:59) [', session_output)
        self.assertIn("Comando desconhecido", session_output)

if __name__ == '__main__':
    unittest.main()
