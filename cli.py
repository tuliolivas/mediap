"""
Módulo cli.py
Implementa a interface de linha de comando (CLI) para interação com o reprodutor musical.
Fornece comandos para gerenciar a biblioteca, playlists, fila de prioridade, histórico e reprodução.
"""

import sys
from datetime import datetime
from typing import List

from .models import Track
from .playlist import PlaylistError
from .player import Player


def print_help() -> None:
    """Exibe a lista de comandos disponíveis no sistema."""
    help_text = """
Comandos Disponíveis:
---------------------
[Biblioteca]
  library load <arquivo>    - Carrega a biblioteca a partir de um ficheiro JSON
  library list [atributo]   - Lista as músicas (padrão: id)

[Playlist]
  playlist new <nome>       - Cria uma nova playlist e define-a como ativa
  playlist add <id> ...     - Adiciona uma ou mais faixas à playlist ativa
  playlist remove <pos>     - Remove a faixa na posição indicada
  playlist show             - Exibe as faixas da playlist ativa
  playlist reset            - Reinicia o cursor para a primeira música

[Up Next]
  enqueue <id> ...          - Adiciona faixas à fila Up Next
  queue show                - Exibe a fila Up Next
  upnext <id> ...           - Alias de enqueue

[Reprodução]
    play                      - Inicia ou retoma a faixa atual
  next                      - Avança para a próxima música (Up Next tem precedência)
  prev                      - Retrocede para a música anterior
  current                   - Exibe a música atual em execução

[Histórico e Shuffle]
    history                   - Exibe as últimas 30 execuções
    smart-shuffle <n>         - Gera uma playlist ordenada por prioridade

[Estado]
    save <arquivo>            - Salva o estado completo em JSON
    load <arquivo>            - Restaura o estado de um JSON

[Sistema]
  help                      - Exibe este menu de ajuda
  exit / quit               - Encerra o programa
"""
    print(help_text)


def format_duration(seconds: int) -> str:
    """Formata a duração em minutos e segundos, sem depender de áudio real."""
    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{minutes}:{remaining_seconds:02d}"


def format_track(track: Track) -> str:
    """Usa uma apresentação consistente nas listas e na reprodução."""
    duration = format_duration(track.duration)
    return f'"{track.title}" — {track.artist} ({duration})'


def run_cli() -> None:
    """Ciclo principal de execução da interface de linha de comando."""
    print("=== Bem-vindo ao Reprodutor Musical CLI ===")
    print("Digite 'help' para ver os comandos disponíveis.\n")

    player = Player()

    while True:
        try:
            user_input = input("mediap> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nA encerrar...")
            sys.exit(0)

        if not user_input:
            continue

        parts: List[str] = user_input.split()
        cmd: str = parts[0].lower()

        try:
            # Comandos de Sistema

            if cmd in ("exit", "quit"):
                print("A encerrar o reprodutor. Até logo!")
                sys.exit(0)

            elif cmd == "help":
                print_help()

            # Comandos de Biblioteca

            elif cmd == "library":

                if len(parts) < 2:
                    print("Erro: Especifique a ação (load, list).")
                    continue

                subcmd = parts[1].lower()

                if subcmd == "load":
                    if len(parts) < 3:
                        print("Erro: Especifique o ficheiro (ex: library load data.json).")
                        continue
                    player.library_load(parts[2])
                    print(f"Biblioteca carregada: {len(player.library)} faixas.")

                elif subcmd == "list":
                    if len(parts) < 3:
                        by = "id"
                    else:
                        by = parts[2].lower()
                    tracks = player.library_list_by(sort_by=by)
                    if not tracks:
                        print("A biblioteca está vazia.")
                    else:
                        print(f"\n--- Biblioteca (Ordenada por: {by}) ---")
                        for track in tracks:
                            print(f" [{track.id}] {format_track(track)} | rating {track.rating}")
                        print()

                else:
                    print(f"Erro: Subcomando '{subcmd}' de library desconhecido.")

            # Comandos de Playlist

            elif cmd == "playlist":
                if len(parts) < 2:
                    print("Erro: Especifique a ação (new, add, remove, show, reset).")
                    continue

                subcmd = parts[1].lower()

                if subcmd == "new":
                    if len(parts) < 3:
                        print("Erro: Especifique o nome (ex: playlist new Rock).")
                        continue
                    name = " ".join(parts[2:])
                    player.playlist_create(name)
                    print(f"Playlist '{name}' criada e definida como ativa.")

                elif subcmd == "add":
                    if len(parts) < 3:
                        print("Erro: Especifique o ID (ex: playlist add 1).")
                        continue
                    player.playlist_add_track([int(tid) for tid in parts[2:]])
                    print(f"Faixa(s) ID: {', '.join(parts[2:])} adicionada à playlist.")

                elif subcmd == "remove":
                    if len(parts) < 3 or not parts[2].isdigit():
                        print("Erro: Especifique uma posição numérica válida \
                              ex: playlist remove 2).")
                        continue
                    pos = int(parts[2])
                    removed = player.playlist_remove_track_at(pos)
                    print(f"Faixa removida da playlist: {removed}")

                elif subcmd == "show":
                    tracks = player.playlist_list_tracks()
                    print(f"\n--- Playlist Ativa - {player.playlist_get_name()} ---")
                    if not tracks:
                        print("A playlist está vazia.\n")
                        continue
                    cursor_index = player.playlist.get_cursor_index()
                    for idx, track in enumerate(tracks, start=1):
                        marker = ">" if idx == cursor_index else " "
                        print(f"{marker} {idx}. {format_track(track)}")
                    print()

                elif subcmd == "reset":
                    player.playlist_reset_cursor()
                    print("Cursor da playlist reiniciado para o início.")

                else:
                    print(f"Erro: Subcomando '{subcmd}' de playlist desconhecido.")

            # Comandos de Fila Up Next

            elif cmd in ("enqueue", "upnext"):
                if len(parts) < 2:
                    print("Erro: Especifique o ID da faixa (ex: enqueue 1).")
                    continue
                player.up_next_enqueue([int(tid) for tid in parts[1:]])
                print(f"Faixa(s) ID: {', '.join(parts[1:])} adicionada à fila Up Next.")

            elif cmd == "queue":
                if len(parts) < 2:
                    print("Erro: Especifique a ação (show).")
                    continue

                subcmd = parts[1].lower()

                if subcmd == "show":
                    tracks = player.up_next_list()
                    print("\n--- Fila Up Next ---")
                    if not tracks:
                        print("A fila Up Next está vazia.")
                    else:
                        for idx, track in enumerate(tracks):
                            marker = ">" if idx == 0 else " "
                            print(f"{marker} {idx + 1}. {format_track(track)}")
                        print()
                else:
                    print(f"Erro: Subcomando '{subcmd}' de queue desconhecido.")

            # Comandos de Reprodução

            elif cmd == "play":
                track = player.play()
                print(f">>> Tocando: {format_track(track)}")

            elif cmd == "next":
                track = player.play_next()
                print(f">>> Tocando: {format_track(track)}")

            elif cmd == "prev":
                track = player.play_prev()
                print(f">>> Tocando: {format_track(track)}")

            elif cmd == "current":
                current = player.player_current()
                if current is None:
                    print("Nenhuma música a tocar no momento.")
                else:
                    print(f"Tocando agora: {format_track(current)}")

            elif cmd == "history":
                entries = player.history_list()
                if not entries:
                    print("O histórico de reprodução está vazio.")
                    continue
                print("\n--- Histórico de Reprodução ---")
                for index, (entry, track) in enumerate(entries, start=1):
                    played_at = datetime.fromisoformat(entry.timestamp).strftime("%H:%M:%S")
                    print(f"{index}. {track.title} — {track.artist} [{played_at}]")
                print()

            elif cmd == "smart-shuffle":
                if len(parts) != 2 or not parts[1].isdigit():
                    print("Erro: Forneça uma quantidade inteira (ex: smart-shuffle 10).")
                    continue
                playlist = player.smart_shuffle(int(parts[1]))
                print(f"Playlist '{playlist.name}' criada e definida como ativa.")

            elif cmd in ("save", "load"):
                if len(parts) != 2:
                    print(f"Erro: Use {cmd} <arquivo>.")
                    continue
                if cmd == "save":
                    player.save(parts[1])
                    print(f"Estado salvo em '{parts[1]}'.")
                else:
                    player.load(parts[1])
                    print(f"Estado carregado de '{parts[1]}'.")

            else:
                print(f"Comando desconhecido: '{cmd}'. Digite 'help' para ver os comandos.")

        except (PlaylistError, ValueError, KeyError, IndexError, FileNotFoundError) as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
