"""
Problema das 8 Rainhas - Busca em Profundidade (DFS)

Formulação do Problema:
  - Estado: configuração do tabuleiro (lista de 8 posições, uma por coluna)
  - Estado Inicial: tabuleiro vazio ou com rainhas pré-posicionadas
  - Operadores: colocar uma rainha na próxima coluna livre, em uma linha válida
  - Teste de Meta: 8 rainhas colocadas sem conflitos
  - Custo do Caminho: não relevante (buscamos qualquer solução)
"""

import sys


def is_safe(board, col, row):
    """
    Verifica se uma rainha na posição (row, col) não entra em conflito
    com as rainhas já posicionadas nas colunas 0..col-1.
    """
    for c in range(col):
        r = board[c]
        if r == row:
            return False
        if abs(r - row) == abs(c - col):
            return False
    return True


def dfs_8queens(initial_board=None):
    """
    Busca em Profundidade (DFS) para o Problema das 8 Rainhas.

    Parâmetros:
        initial_board: lista com posições iniciais (None = vazio, -1 = coluna livre)
                       Exemplo: [-1, -1, -1, -1, -1, -1, -1, -1] (vazio)
                       Exemplo: [0, -1, -1, -1, -1, -1, -1, -1]  (rainha na col 0, linha 0)

    Retorna:
        (solução, nós_criados) ou (None, nós_criados) se não houver solução
    """
    N = 8

    if initial_board is None:
        initial_board = [-1] * N

    # Determina a primeira coluna livre
    start_col = 0
    for i, v in enumerate(initial_board):
        if v != -1:
            start_col = i + 1
        else:
            break

    # Verifica conflitos nas rainhas pré-posicionadas
    for c in range(start_col):
        for c2 in range(c):
            r, r2 = initial_board[c], initial_board[c2]
            if r == r2 or abs(r - r2) == abs(c - c2):
                raise ValueError(
                    f"Configuração inicial inválida: rainhas em ({r},{c}) e ({r2},{c2}) estão em conflito."
                )

    nodes_created = 0

    # Pilha DFS: cada elemento é (board_state, next_col)
    # board_state: lista de tamanho N com posições atuais
    initial_state = list(initial_board)
    stack = [(initial_state, start_col)]
    nodes_created += 1

    while stack:
        board, col = stack.pop()
        if col == N:
            return board, nodes_created

        # Iterar de N-1 a 0 para que a pilha processe linha 0 primeiro (LIFO)
        for row in range(N - 1, -1, -1):
            if is_safe(board, col, row):
                new_board = list(board)
                new_board[col] = row
                stack.append((new_board, col + 1))
                nodes_created += 1

    return None, nodes_created


def print_board(board):
    """Imprime o tabuleiro de forma visual."""
    N = 8
    print("  " + " ".join(str(i) for i in range(N)))
    print("  " + "-" * (N * 2 - 1))
    for row in range(N):
        line = f"{row}|"
        for col in range(N):
            if board[col] == row:
                line += "Q "
            else:
                line += ". "
        print(line)
    print()


def run_test(label, initial_board):
    """Executa e exibe os resultados de um caso de teste."""
    print("=" * 50)
    print(f"TESTE: {label}")
    print("=" * 50)
    print("Tabuleiro inicial:")
    print_board(initial_board)

    solution, nodes = dfs_8queens(initial_board)

    print(f"Nós criados: {nodes}")
    if solution:
        print("Solução encontrada!")
        print("Tabuleiro solução:")
        print_board(solution)
        print(f"Posições (coluna -> linha): {solution}")
    else:
        print("Nenhuma solução encontrada.")
    print()


if __name__ == "__main__":

    # ── Tabuleiro 1: Vazio ────────────────────────────────────────────────────
    board_vazio = [-1, -1, -1, -1, -1, -1, -1, -1]
    run_test("Tabuleiro Vazio", board_vazio)

    # ── Tabuleiro 2: 1 rainha (coluna 0, linha 3) ────────────────────────────
    board_1_rainha = [3, -1, -1, -1, -1, -1, -1, -1]
    run_test("1 Rainha: col 0 → linha 3", board_1_rainha)

    # ── Tabuleiro 3: 2 rainhas ───────────────────────────────────────────────
    board_2_rainhas = [1, 4, -1, -1, -1, -1, -1, -1]
    run_test("2 Rainhas: col 0 → linha 1 | col 1 → linha 4", board_2_rainhas)

    # ── Tabuleiro 4: 3 rainhas ───────────────────────────────────────────────
    board_3_rainhas = [0, 4, 7, -1, -1, -1, -1, -1]
    run_test("3 Rainhas: col 0 → linha 0 | col 1 → linha 4 | col 2 → linha 7", board_3_rainhas)
