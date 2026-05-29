"""
Puzzle de 8 Peças — Busca em Largura (BFS) com Poda de Estados Visitados

Formulação do Problema:
  - Estado: tupla de 9 elementos representando o tabuleiro 3x3
             índice 0=canto superior esquerdo, 8=canto inferior direito
             0 (zero) representa o espaço em branco X
  - Estado Inicial: configuração fornecida
  - Operadores: mover o espaço em branco nas 4 direções (UP, DOWN, LEFT, RIGHT)
  - Teste de Meta: estado == (1, 2, 3, 4, 5, 6, 7, 8, 0)
  - Custo do Caminho: número de movimentos (cada ação custa 1)

Pseudo-código aplicado (Busca em Largura com poda):
  listOrd = estadoInicial
  listaV = {}  // hash
  achou = false
  do {
    no = listOrd.removeFirst()
    if (!listaV.contains(no)) {
      listaV.add(no)
      if (ehObjetivo(no)) { achou = true; break }
      else { listOrd.add(no.criarFilhos()) }   // sem sort → FIFO → BFS
    }
  } while (!achou && !listOrd.empty())
"""

from collections import deque


# ── Constante de meta ─────────────────────────────────────────────────────────
GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Deltas de posição para cada movimento do espaço em branco
MOVES = {
    'UP':    -3,
    'DOWN':  +3,
    'LEFT':  -1,
    'RIGHT': +1,
}

# Restrições de borda (impede salto inválido entre colunas)
INVALID = {
    'LEFT':  {0, 3, 6},
    'RIGHT': {2, 5, 8},
}

ACAO_PT = {'UP': 'CIMA', 'DOWN': 'BAIXO', 'LEFT': 'ESQUERDA', 'RIGHT': 'DIREITA'}
ACAO_DESC = {
    'UP':    'espaço sobe   → peça desce',
    'DOWN':  'espaço desce  → peça sobe',
    'LEFT':  'espaço ←      → peça →',
    'RIGHT': 'espaço →      → peça ←',
}


# ── Nó da árvore de busca ─────────────────────────────────────────────────────
class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state  = state
        self.parent = parent
        self.action = action
        self.depth  = depth

    def criar_filhos(self):
        filhos = []
        pos_zero = self.state.index(0)
        for action, delta in MOVES.items():
            if action in INVALID and pos_zero in INVALID[action]:
                continue
            nova_pos = pos_zero + delta
            if 0 <= nova_pos <= 8:
                s = list(self.state)
                s[pos_zero], s[nova_pos] = s[nova_pos], s[pos_zero]
                filhos.append(Node(tuple(s), self, action, self.depth + 1))
        return filhos


# ── BFS com poda de estados visitados ─────────────────────────────────────────
def bfs(estado_inicial):
    no_inicial = Node(state=tuple(estado_inicial))
    if no_inicial.state == GOAL:
        return no_inicial, 1, 0

    list_ord = deque([no_inicial])   # FIFO → BFS (listOrd)
    lista_v  = set()                  # hash de estados visitados
    nos_criados    = 1
    nos_expandidos = 0
    achou = False
    no    = None

    while not achou and list_ord:
        no = list_ord.popleft()                  # removeFirst()
        if no.state not in lista_v:              # !listaV.contains(no)
            lista_v.add(no.state)                # listaV.add(no)
            nos_expandidos += 1
            if no.state == GOAL:                 # ehObjetivo(no)
                achou = True
                break
            else:
                filhos = no.criar_filhos()       # criarFilhos()
                nos_criados += len(filhos)
                list_ord.extend(filhos)          # listOrd.add(filhos)

    return (no, nos_criados, nos_expandidos) if achou else (None, nos_criados, nos_expandidos)


# ── Verifica se um puzzle tem solução (paridade de inversões) ─────────────────
def tem_solucao(estado):
    """
    Um puzzle 8 é solúvel se e somente se o número de inversões for par.
    Inversão: par (i, j) onde i < j mas estado[i] > estado[j] (ignorando 0).
    """
    s = [x for x in estado if x != 0]
    inv = sum(1 for i in range(len(s)) for j in range(i+1, len(s)) if s[i] > s[j])
    return inv % 2 == 0


# ── Exibição ──────────────────────────────────────────────────────────────────
def fmt_cell(v):
    return 'X' if v == 0 else str(v)

def exibir_tabuleiro(estado, label=""):
    s = estado
    if label:
        print(f"  {label}")
    print("  +-------+")
    print(f"  | {fmt_cell(s[0])} {fmt_cell(s[1])} {fmt_cell(s[2])} |")
    print(f"  | {fmt_cell(s[3])} {fmt_cell(s[4])} {fmt_cell(s[5])} |")
    print(f"  | {fmt_cell(s[6])} {fmt_cell(s[7])} {fmt_cell(s[8])} |")
    print("  +-------+")

def reconstruir_caminho(no_final):
    caminho = []
    atual = no_final
    while atual:
        caminho.append(atual)
        atual = atual.parent
    return list(reversed(caminho))

def exibir_solucao(estado_inicial, label="Puzzle"):
    print(f"\n{'='*58}")
    print(f"  {label}")
    print(f"{'='*58}")

    if not tem_solucao(estado_inicial):
        print("\n  Estado Inicial:")
        exibir_tabuleiro(estado_inicial)
        print("\n  *** SEM SOLUÇÃO: número de inversões é ímpar. ***")
        print("  Metade de todas as configurações do 8-puzzle são insolúveis.")
        return

    no_sol, nos_criados, nos_expandidos = bfs(estado_inicial)

    if no_sol is None:
        print("  Sem solução encontrada pelo BFS.")
        return

    caminho = reconstruir_caminho(no_sol)

    print(f"\n  Estado Inicial:")
    exibir_tabuleiro(estado_inicial)
    print(f"\n  Estado Meta:  | 1 2 3 | 4 5 6 | 7 8 X |")
    print(f"\n  Passos para resolver: {len(caminho)-1}")
    print(f"  Nós criados:          {nos_criados}")
    print(f"  Nós expandidos:       {nos_expandidos}")
    print(f"\n{'─'*58}")
    print("  SEQUÊNCIA DE MOVIMENTOS:")
    print(f"{'─'*58}\n")

    for i, no in enumerate(caminho):
        if i == 0:
            exibir_tabuleiro(no.state, "Passo 0 — Estado Inicial")
        else:
            pt   = ACAO_PT.get(no.action, no.action)
            desc = ACAO_DESC.get(no.action, '')
            exibir_tabuleiro(no.state, f"Passo {i} — {pt}  [{desc}]")
        print()

    print(f"  >>> Resolvido em {len(caminho)-1} passo(s)! <<<")


# ── Casos de teste ────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Puzzle 1 (fornecido) — SEM SOLUÇÃO
    puzzle1 = (4, 6, 2,
               8, 1, 3,
               7, 5, 0)
    exibir_solucao(puzzle1, "Puzzle 1 (fornecido): [4 6 2 / 8 1 3 / 7 5 X]")

    # Puzzle 2 (fornecido) — COM SOLUÇÃO
    puzzle2 = (6, 4, 2,
               8, 1, 3,
               7, 5, 0)
    exibir_solucao(puzzle2, "Puzzle 2 (fornecido): [6 4 2 / 8 1 3 / 7 5 X]")

    # Puzzle 3 (próprio — 8 passos)
    # [4 2 X / 5 1 3 / 7 8 6]
    puzzle3 = (4, 2, 0,
               5, 1, 3,
               7, 8, 6)
    exibir_solucao(puzzle3, "Puzzle 3 (próprio, 8 passos): [4 2 X / 5 1 3 / 7 8 6]")

    # Puzzle 4 (próprio — 6 passos)
    # [1 2 3 / 4 X 8 / 7 6 5]
    puzzle4 = (1, 2, 3,
               4, 0, 8,
               7, 6, 5)
    exibir_solucao(puzzle4, "Puzzle 4 (próprio, 6 passos): [1 2 3 / 4 X 8 / 7 6 5]")
