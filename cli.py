"""
Módulo cli.py
Implementa a interface de linha de comando (CLI) para interação com o reprodutor musical.
Fornece comandos para gerenciar a biblioteca, playlists, fila de prioridade, histórico e reprodução.
"""

import sys
from typing import List

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
  play                      - Mostra a faixa atual da reprodução
  next                      - Avança para a próxima música (Up Next tem precedência)
  prev                      - Retrocede para a música anterior
  current                   - Exibe a música atual em execução

[Sistema]
  help                      - Exibe este menu de ajuda
  exit / quit               - Encerra o programa
"""
    print(help_text)


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
        # print(f"Comando recebido: {user_input}")
        # print(f"Partes do comando: {parts}")

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
                    print(f"Biblioteca '{parts[2]}' carregada com sucesso.")

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
                            print(f" {track}")
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
                    for idx, track in enumerate(tracks):
                        if track == player.playlist_current_track():
                            print(f" > [{idx + 1}] {track}")
                        else:
                            print(f"   [{idx + 1}] {track}")
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
                            if track == player.up_next_current():
                                print(f" > [{idx + 1}] {track}")
                            else:
                                print(f"   [{idx + 1}] {track}")
                        print()
                else:
                    print(f"Erro: Subcomando '{subcmd}' de queue desconhecido.")

            # Comandos de Reprodução

            elif cmd == "play":
                track = player.play()
                print(f"Tocando: {track}")

            elif cmd == "next":
                track = player.play_next()
                print(f"Avançou para: {track}")

            elif cmd == "prev":
                track = player.play_prev()
                print(f"Retrocedeu para: {track}")

            elif cmd == "current":
                current = player.player_current()
                if current is None:
                    print("Nenhuma música a tocar no momento.")
                else:
                    print(f"A tocar agora: {current}")

            # # ==========================================
            # # Fila Up Next
            # # ==========================================
            # elif cmd == "upnext":
            #     if len(parts) < 2:
            #         print("Erro: Especifique a ação (add, show).")
            #         continue

            #     subcmd = parts[1].lower()

            #     if subcmd == "add":
            #         if len(parts) < 3:
            #             print("Erro: Especifique o ID (ex: upnext add track_01).")
            #             continue
            #         player.add_to_up_next(parts[2])
            #         print(f"Faixa '{parts[2]}' adicionada à fila Up Next.")

            #     elif subcmd == "show":
            #         if not player.up_next_queue:
            #             print("A fila Up Next está vazia.")
            #         else:
            #             print("\n--- Fila Up Next ---")
            #             for i, track in enumerate(player.up_next_queue):
            #                 print(f" [{i}] {track}")
            #             print()

            #     else:
            #         print(f"Erro: Subcomando '{subcmd}' de upnext desconhecido.")

            # # ==========================================
            # # Histórico e Smart Shuffle
            # # ==========================================
            # elif cmd == "history":
            #     if not player.history:
            #         print("O histórico de reprodução está vazio.")
            #     else:
            #         print(f"\n--- Histórico de Reprodução (Últimas {player.history.maxlen}) ---")
            #         # Inverte para exibir a mais recente no topo
            #         for idx, entry in enumerate(reversed(player.history), start=1):
            #             print(f" {idx:02d}. [{entry['timestamp']}] ID: {entry['id']} \
            #                   - {entry['track_str']}")
            #         print()

            # elif cmd == "smart-shuffle":
            #     if len(parts) != 2 or not parts[1].isdigit():
            #         print("Erro: Forneça a quantidade (ex: smart-shuffle 10).")
            #         continue
            #     n = int(parts[1])
            #     if n <= 0:
            #         print("Erro: A quantidade deve ser superior a zero.")
            #         continue

            #     player.generate_smart_shuffle(n)
            #     print(f"Playlist 'Smart Shuffle' gerada com {n} faixas e definida como ativa.")
            #     print("Use 'playlist show' para visualizá-la ou 'play' para iniciar a reprodução.")

            # # ==========================================
            # # Comandos de Reprodução
            # # ==========================================
            # elif cmd == "current":
            #     current = player.current_track()
            #     if current:
            #         print(f"A tocar agora: {current}")
            #     else:
            #         print("Nenhuma música a tocar no momento.")

            # elif cmd == "play":
            #     track = player.play()
            #     print(f"A tocar: {track}")

            # elif cmd == "next":
            #     track = player.play_next()
            #     print(f"Avançou para: {track}")

            # elif cmd == "prev":
            #     track = player.play_prev()
            #     print(f"Retrocedeu para: {track}")

            else:
                print(f"Comando desconhecido: '{cmd}'. Digite 'help' para ver os comandos.")

        except (PlaylistError, ValueError, KeyError, IndexError, FileNotFoundError) as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
#   playlist reset               - Reinicializa o cursor na primeira música

# Gerais:
#   help                         - Exibe esta mensagem de ajuda
#   quit                         - Encerra o reprodutor MediaP

# """
#     print(help_text)


# def run_cli() -> None:
#     """Executa a interface de linha de comando (CLI) para o MediaP."""
#     print("MediaP - Reprodutor de Música")
#     print("Digite 'help' para listar os comandos disponíveis.\n")

#     player = Player()

#     while True:
#         try:
#             line = input("mediap> ").strip()
#             if not line:
#                 continue

#             parts = line.split()
#             cmd = parts[0].lower()

#             if cmd == "quit":
#                 print("Encerrando o MediaP...")
#                 break

#             if cmd == "help":
#                 print_help()
#                 continue

#             # Comandos diretos de reprodução
#             if cmd == "play":
#                 try:
#                     track = player.play()
#                     print(f"Tocando agora: {track}")
#                 except LibraryError as err:
#                     print(f"Erro: {err}")

#             elif cmd in ("next", "play_next"):
#                 try:
#                     track = player.play_next()
#                     if track:
#                         print(f"Tocando agora: {track}")
#                 except LibraryError as err:
#                     print(f"Erro: {err}")

#             elif cmd in ("prev", "play_prev"):
#                 try:
#                     track = player.play_prev()
#                     if track:
#                         print(f"Tocando agora: {track}")
#                 except LibraryError as err:
#                     print(f"Erro: {err}")

#             # Comandos com Library
#             elif cmd == "library":
#                 if len(parts) == 1:
#                     print("Erro: Esse comando precisa de um argumento. Use 'help'.")
#                     continue

#                 subcmd = parts[1].lower()

#                 if subcmd == "load":
#                     if len(parts) == 2:
#                         print("Erro: Nome do arquivo JSON não fornecido.")
#                         continue
#                     filename = parts[2]
#                     try:
#                         player.load_library(filename)
#                         print(f"Biblioteca carregada: {len(player.tracks)} faixas.")
#                     except (FileNotFoundError, LibraryError, ValueError) as err:
#                         print(f"Erro ao carregar biblioteca: {err}")

#                 elif subcmd == "save":
#                     if len(parts) == 2:
#                         print("Erro: Nome do arquivo JSON não fornecido.")
#                         continue
#                     filename = parts[2]
#                     try:
#                         player.save_data(filename)
#                         print(f"Biblioteca salva em '{filename}'.")
#                     except LibraryError as err:
#                         print(f"Erro ao salvar biblioteca: {err}")

#                 elif subcmd == "list":
#                     sort_by = parts[2] if len(parts) > 2 else "id"
#                     try:
#                         tracks = player.list_tracks(by=sort_by)
#                      dict[str, Any]   if not tracks:
#                             print("A biblioteca está vazia.")
#                         else:
#                             print(f"\nFaixas na biblioteca (ordenadas por {sort_by}):")
#                             for track in tracks:
#                                 print(f"  {track}")
#                             print()
#                     except LibraryError as err:
#                         print(f"Erro: {err}")

#                 else:
#                     print(f"Subcomando 'library {subcmd}' inválido.")

#             # Comandos com Playlist
#             elif cmd == "playlist":
#                 if len(parts) == 1:
#                     print("Erro: Esse comando precisa de um argumento. Use 'help'.")
#                     continue

#                 subcmd = parts[1].lower()

#                 if subcmd == "new":
#                     if len(parts) == 2:
#                         print("Erro: Nome da playlist não fornecido.")
#                         continue
#                     name = parts[2]
#                     try:
#                         player.create_playlist(name)
#                         print(f"Playlist '{name}' criada e definida como atual.")
#                     except (LibraryError, ValueError) as err:
#                         print(f"Erro ao criar playlist: {err}")

#                 elif subcmd == "add":
#                     if len(parts) == 2:
#                         print("Erro: ID da faixa não fornecido.")
#                         continue
#                     track_id = parts[2]
#                     try:
#                         player.add_to_playlist(track_id)
#                         print(f"Faixa '{track_id}' adicionada à playlist.")
#                     except (LibraryError, ValueError, KeyError) as err:
#                         print(f"Erro ao adicionar faixa: {err}")

#                 elif subcmd == "remove":
#                     if len(parts) == 2 or not parts[2].isdigit():
#                         print("Erro: Posição numérica não fornecida ou inválida.")
#                         continue
#                     pos = int(parts[2])
#                     try:
#                         removed = player.remove_from_playlist(pos)
#                         print(f"Faixa '{removed}' removida da posição {pos}.")
#                     except (LibraryError, ValueError, IndexError) as err:
#                         print(f"Erro ao remover faixa: {err}")

#                 elif subcmd == "show":
#                     try:
#                         player.show_playlist()
#                     except (LibraryError, ValueError) as err:
#                         print(f"Erro: {err}")

#                 elif subcmd in ("next", "play_next"):
#                     try:
#                         track = player.play_next()
#                         if track:
#                             print(f" Tocando agora: {track}")
#                     except LibraryError as err:
#                         print(f"Erro: {err}")

#                 elif subcmd in ("prev", "play_prev"):
#                     try:
#                         track = player.play_prev()
#                         if track:
#                             print(f"Tocando agora: {track}")
#                     except LibraryError as err:
#                         print(f"Erro: {err}")

#                 elif subcmd == "current":
#                     try:
#                         track = player.current_track()
#                         if track:
#                             print(f"Faixa em execução: {track}")
#                     except LibraryError as err:
#                         print(f"Erro: {err}")

#                 elif subcmd == "reset":
#                     try:
#                         player.reset_playlist_cursor()
#                         print("Cursor reinicializado na primeira música da playlist.")
#                     except LibraryError as err:
#                         print(f"Erro: {err}")

#                 else:
#                     print(f"Subcomando 'playlist {subcmd}' inválido.")

#             else:
#                 print("Erro: comando inválido. Digite 'help' para ajuda.")

#         except Exception as err:
#             print(f"Erro no processamento do comando: {err}")
