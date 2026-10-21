# MediaP

Aplicação CLI de reprodutor musical em Python.

## Visão geral

O projeto gestiona:
- biblioteca de faixas em JSON
- criação e navegação de playlists
- fila Up Next
- reprodução atual e avanço/retrocesso
- lista encadeada duplamente ligada como estrutura principal

## Como executar

No diretório pai do projeto:

```bash
PYTHONPATH=/workspaces python -m mediap
```

Ou, a partir da pasta do projeto:

```bash
cd /workspaces/mediap
python -m mediap
```

> Se o módulo não for encontrado, use `PYTHONPATH` apontando para o diretório que contém a pasta `mediap`.

## Comandos principais

```text
library load library.json
library list id
playlist new Rock
playlist add 1 2
playlist show
play
next
prev
current
enqueue 3
queue show
exit
```

## Estrutura do projeto

- `models.py`: representação da faixa `Track`
- `doubly_linked_list.py`: estrutura de dados genérica
- `playlist.py`: playlist com cursor e regras de navegação
- `player.py`: regras de reprodução e biblioteca
- `cli.py`: interface de linha de comando
- `library.json`: base inicial de dados

## Observação

O projeto está em evolução e a camada de reprodução foi validada por testes automatizados, mas ainda é uma CLI funcional simples, sem interface gráfica nem persistência avançada de playlists.