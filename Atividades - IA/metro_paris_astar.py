"""
Metrô de Paris — Busca A* (A Estrela)

Formulação do Problema:
  - Estado: estação atual + linha atual (para detectar mudanças de linha)
  - Estado Inicial: estação de origem
  - Operadores: mover para estação vizinha conectada
  - Teste de Meta: estação atual == estação destino
  - Custo do Caminho: tempo em minutos
      * Tempo de deslocamento = distância_km / 30 km/h * 60 min
      * Penalidade de mudança de linha = +5 min por troca
  - Heurística h(n): distância em linha reta até o destino / 30 km/h * 60 min
    (admissível: nunca superestima, pois linha reta é sempre ≤ caminho real)
"""

import heapq
from itertools import combinations

# ── Grafo: arestas com (vizinho, distância_km, linha) ────────────────────────
# Linhas inferidas do mapa (cada cor = uma linha)
# Linha A (azul):  E1-E2-E3-E4-E5-E6
# Linha B (verde): E2-E10, E10-E3, E3-E9-E8-E12
# Linha C (vermelha): E4-E8-E5-E7, E5-E6
# Linha D (amarela): E9-E11, E9-E2, E3-E13-E14, E4-E13

LINES = {
    "A": ["E1","E2","E3","E4","E5","E6"],
    "B": ["E2","E10","E3","E9","E8","E12"],
    "C": ["E4","E8","E5","E7","E5","E6"],
    "D": ["E2","E9","E11","E3","E13","E14","E4"],
}

# Conexões reais com distância (km) e linha
# Formato: (estação1, estação2, distância, linha)
EDGES_RAW = [
    ("E1",  "E2",  11, "A"),
    ("E2",  "E3",  9,  "A"),
    ("E3",  "E4",  7,  "A"),
    ("E4",  "E5",  14, "A"),
    ("E5",  "E6",  3,  "A"),
    ("E2",  "E10", 4,  "B"),
    ("E2",  "E9",  11, "B"),
    ("E3",  "E9",  10, "B"),
    ("E8",  "E9",  10, "B"),
    ("E8",  "E12", 7,  "B"),
    ("E4",  "E8",  16, "C"),
    ("E5",  "E8",  33, "C"),
    ("E5",  "E7",  2,  "C"),
    ("E3",  "E13", 19, "D"),
    ("E4",  "E13", 12, "D"),
    ("E9",  "E11", 14, "D"),
    ("E13", "E14", 5,  "D"),
]

# Monta grafo de adjacência
# graph[e] = [(vizinho, distância, linha), ...]
graph = {f"E{i}": [] for i in range(1, 15)}
for e1, e2, dist, line in EDGES_RAW:
    graph[e1].append((e2, dist, line))
    graph[e2].append((e1, dist, line))

# ── Heurística: distância em linha reta (km) → minutos ───────────────────────
# Tabela fornecida no PDF
HEURISTIC_KM = {
    ("E1","E1"):0,  ("E1","E2"):11, ("E1","E3"):20, ("E1","E4"):27,
    ("E1","E5"):40, ("E1","E6"):43, ("E1","E7"):39, ("E1","E8"):28,
    ("E1","E9"):18, ("E1","E10"):10,("E1","E11"):18,("E1","E12"):30,
    ("E1","E13"):30,("E1","E14"):32,
    ("E2","E2"):0,  ("E2","E3"):9,  ("E2","E4"):16, ("E2","E5"):29,
    ("E2","E6"):32, ("E2","E7"):28, ("E2","E8"):19, ("E2","E9"):11,
    ("E2","E10"):4, ("E2","E11"):17,("E2","E12"):23,("E2","E13"):21,
    ("E2","E14"):24,
    ("E3","E3"):0,  ("E3","E4"):7,  ("E3","E5"):20, ("E3","E6"):22,
    ("E3","E7"):19, ("E3","E8"):15, ("E3","E9"):10, ("E3","E10"):11,
    ("E3","E11"):21,("E3","E12"):21,("E3","E13"):13,("E3","E14"):18,
    ("E4","E4"):0,  ("E4","E5"):13, ("E4","E6"):16, ("E4","E7"):12,
    ("E4","E8"):13, ("E4","E9"):13, ("E4","E10"):18,("E4","E11"):26,
    ("E4","E12"):21,("E4","E13"):11,("E4","E14"):17,
    ("E5","E5"):0,  ("E5","E6"):3,  ("E5","E7"):2,  ("E5","E8"):21,
    ("E5","E9"):25, ("E5","E10"):31,("E5","E11"):38,("E5","E12"):27,
    ("E5","E13"):16,("E5","E14"):20,
    ("E6","E6"):0,  ("E6","E7"):4,  ("E6","E8"):23, ("E6","E9"):28,
    ("E6","E10"):33,("E6","E11"):41,("E6","E12"):30,("E6","E13"):17,
    ("E6","E14"):20,
    ("E7","E7"):0,  ("E7","E8"):22, ("E7","E9"):25, ("E7","E10"):29,
    ("E7","E11"):38,("E7","E12"):28,("E7","E13"):13,("E7","E14"):17,
    ("E8","E8"):0,  ("E8","E9"):9,  ("E8","E10"):22,("E8","E11"):18,
    ("E8","E12"):7, ("E8","E13"):25,("E8","E14"):30,
    ("E9","E9"):0,  ("E9","E10"):13,("E9","E11"):12,("E9","E12"):12,
    ("E9","E13"):23,("E9","E14"):28,
    ("E10","E10"):0,("E10","E11"):20,("E10","E12"):27,("E10","E13"):20,
    ("E10","E14"):23,
    ("E11","E11"):0,("E11","E12"):15,("E11","E13"):35,("E11","E14"):39,
    ("E12","E12"):0,("E12","E13"):31,("E12","E14"):37,
    ("E13","E13"):0,("E13","E14"):5,
    ("E14","E14"):0,
}

def heuristic_min(station, goal):
    """Converte distância em linha reta (km) para minutos a 30 km/h."""
    key = (station, goal) if (station, goal) in HEURISTIC_KM else (goal, station)
    km = HEURISTIC_KM.get(key, 0)
    return km / 30 * 60  # minutos

def travel_time_min(dist_km):
    """Converte distância real em minutos a 30 km/h."""
    return dist_km / 30 * 60

def astar(origin, goal):
    """
    Algoritmo A* para encontrar o caminho de menor tempo entre origin e goal.

    Estado: (estação_atual, linha_atual)
    Custo g(n): tempo acumulado em minutos (viagem + penalidades de troca)
    Heurística h(n): distância em linha reta → minutos (admissível)
    f(n) = g(n) + h(n)

    Retorna: (caminho, linhas_usadas, mudanças, tempo_total, nós_expandidos)
    """
    if origin == goal:
        return [origin], [], 0, 0.0, 0

    # Fila de prioridade: (f, g, estação, linha_atual, caminho, linhas_no_caminho)
    # Linha inicial = None (ainda não escolheu linha)
    start = (heuristic_min(origin, goal), 0.0, origin, None, [origin], [])
    heap = [start]
    visited = {}  # (estação, linha) -> melhor g encontrado
    nos_expandidos = 0

    while heap:
        f, g, station, current_line, path, lines_path = heapq.heappop(heap)

        state = (station, current_line)
        if state in visited and visited[state] <= g:
            continue
        visited[state] = g
        nos_expandidos += 1

        if station == goal:
            # Conta mudanças de linha (ignorando None inicial)
            real_lines = [l for l in lines_path if l is not None]
            changes = sum(1 for i in range(1, len(real_lines)) if real_lines[i] != real_lines[i-1])
            return path, lines_path, changes, g, nos_expandidos

        for neighbor, dist, line in graph[station]:
            # Custo de viagem
            travel = travel_time_min(dist)
            # Penalidade de mudança de linha
            penalty = 5.0 if (current_line is not None and line != current_line) else 0.0
            new_g = g + travel + penalty
            new_h = heuristic_min(neighbor, goal)
            new_f = new_g + new_h

            new_state = (neighbor, line)
            if new_state not in visited or visited[new_state] > new_g:
                heapq.heappush(heap, (
                    new_f, new_g, neighbor, line,
                    path + [neighbor], lines_path + [line]
                ))

    return None, None, 0, float('inf'), nos_expandidos


def format_result(origin, goal, path, lines_path, changes, total_time, nos):
    """Formata o resultado de forma legível."""
    lines = []
    lines.append(f"\n{'='*55}")
    lines.append(f"  Origem: {origin}  →  Destino: {goal}")
    lines.append(f"{'='*55}")

    if path is None:
        lines.append("  Sem caminho disponível.")
        return "\n".join(lines)

    if origin == goal:
        lines.append("  Origem e destino são iguais. Tempo: 0 min.")
        return "\n".join(lines)

    # Detalha o percurso
    lines.append("  Percurso:")
    real_lines = [l for l in lines_path if l is not None]
    for i, station in enumerate(path):
        if i == 0:
            line_info = ""
        else:
            line_info = f"  [Linha {real_lines[i-1]}]"
            if i > 1 and real_lines[i-1] != real_lines[i-2]:
                line_info += "  *** TROCA DE LINHA ***"
        lines.append(f"    {station}{line_info}")

    lines.append(f"\n  Mudanças de linha: {changes}")
    lines.append(f"  Tempo de viagem:   {total_time:.1f} min")
    lines.append(f"    (inclui {changes * 5} min de penalidade por troca)")
    lines.append(f"  Nós expandidos:    {nos}")
    return "\n".join(lines)


def run_all_combinations():
    """Executa o A* para todas as combinações de estações."""
    stations = [f"E{i}" for i in range(1, 15)]
    results = []
    for origin, goal in combinations(stations, 2):
        path, lines_path, changes, total_time, nos = astar(origin, goal)
        results.append((origin, goal, path, lines_path, changes, total_time, nos))
    return results


def interactive():
    """Modo interativo: lê origem e destino do usuário."""
    stations = [f"E{i}" for i in range(1, 15)]
    print("\n=== Metrô de Paris — Busca A* ===")
    print(f"Estações disponíveis: {', '.join(stations)}")

    while True:
        print()
        origin = input("Estação de origem (ou 'sair'): ").strip().upper()
        if origin == 'SAIR':
            break
        if origin not in stations:
            print(f"  Estação inválida. Escolha entre {stations}")
            continue

        goal = input("Estação de destino:            ").strip().upper()
        if goal not in stations:
            print(f"  Estação inválida. Escolha entre {stations}")
            continue

        path, lines_path, changes, total_time, nos = astar(origin, goal)
        print(format_result(origin, goal, path, lines_path, changes, total_time, nos))


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        # Uso: python metro_paris_astar.py E1 E14
        origin, goal = sys.argv[1].upper(), sys.argv[2].upper()
        path, lines_path, changes, total_time, nos = astar(origin, goal)
        print(format_result(origin, goal, path, lines_path, changes, total_time, nos))

    elif "--all" in sys.argv:
        print("=== Todas as combinações de estações ===")
        results = run_all_combinations()
        for origin, goal, path, lines_path, changes, total_time, nos in results:
            print(format_result(origin, goal, path, lines_path, changes, total_time, nos))

    else:
        interactive()
