import time
import tracemalloc
import itertools

import sys
sys.stdout.reconfigure(encoding='utf-8')

from pysat.card import CardEnc
from pysat.formula import IDPool
from pysat.solvers import Solver
from collections import defaultdict, deque

# Đọc file input
def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        if not lines:
            print(f"Warning: {filename} is empty or invalid format.")
            return []
        return [list(map(int, line.split(','))) for line in lines]

# Ghi output ra file
def write_solution(grid, edges, output_file):
    rows, cols = len(grid), len(grid[0])
    board = [[str(cell) if cell != 0 else '0' for cell in row] for row in grid]

    for x1, y1, x2, y2, w in edges:
        if x1 == x2:
            for y in range(min(y1, y2) + 1, max(y1, y2)):
                board[x1][y] = '=' if w == 2 else '-'
        elif y1 == y2: 
            for x in range(min(x1, x2) + 1, max(x1, x2)):
                board[x][y1] = '$' if w == 2 else '|'

    with open(output_file, 'w') as f:
        for row in board:
            f.write('[ ' + ' , '.join(f'"{cell}"' for cell in row) + ' ]\n')

# Kiểm tra 2 cạnh cắt nhau
def edges_cross(e1, e2):
    (x1, y1, x2, y2) = e1
    (a1, b1, a2, b2) = e2

    if x1 == x2 and b1 == b2:  # e1 ngang, e2 dọc
        if (min(y1, y2) < b1 < max(y1, y2)) and (min(a1, a2) < x1 < max(a1, a2)):
            return True
    if a1 == a2 and y1 == y2:  # e1 dọc, e2 ngang
        if (min(b1, b2) < y1 < max(b1, b2)) and (min(x1, x2) < a1 < max(x1, x2)):
            return True
    return False

def generateCNF(grid):
    rows, cols = len(grid), len(grid[0])
    vpool = IDPool()
    cnf = []
    edge_vars = {}
    reverse_map = {}
    island_map = {}

    # Tạo biến & ràng buộc tối đa 2 cầu
    for x in range(rows):
        for y in range(cols):
            if grid[x][y] == 0:
                continue
            island_map[(x, y)] = grid[x][y]

            # sang phải
            for dy in range(y + 1, cols):
                if grid[x][dy] == 0:
                    continue
                if all(grid[x][k] == 0 for k in range(y + 1, dy)):
                    v1 = vpool.id(f"B_{x}_{y}_{x}_{dy}_1")
                    v2 = vpool.id(f"B_{x}_{y}_{x}_{dy}_2")
                    edge_vars[(x, y, x, dy)] = (v1, v2)
                    reverse_map[v1] = (x, y, x, dy, 1)
                    reverse_map[v2] = (x, y, x, dy, 2)
                    cnf.append([-v1, -v2])
                break

            # xuống dưới
            for dx in range(x + 1, rows):
                if grid[dx][y] == 0:
                    continue
                if all(grid[k][y] == 0 for k in range(x + 1, dx)):
                    v1 = vpool.id(f"B_{x}_{y}_{dx}_{y}_1")
                    v2 = vpool.id(f"B_{x}_{y}_{dx}_{y}_2")
                    edge_vars[(x, y, dx, y)] = (v1, v2)
                    reverse_map[v1] = (x, y, dx, y, 1)
                    reverse_map[v2] = (x, y, dx, y, 2)
                    cnf.append([-v1, -v2])
                break

    # Tổng số cầu mỗi đảo
    for (x, y), total in island_map.items():
        vars_for_island = []
        for (a, b, c, d), (v1, v2) in edge_vars.items():
            if (a, b) == (x, y) or (c, d) == (x, y):
                vars_for_island.append((v1, 1))
                vars_for_island.append((v2, 2))
        expanded = []
        for var, weight in vars_for_island:
            expanded.extend([var] * weight)
        if expanded:
            card = CardEnc.equals(lits=expanded, bound=total, vpool=vpool, encoding=1)
            cnf.extend(card.clauses)

    # Ràng buộc không cắt nhau
    edges = list(edge_vars.keys())
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            if edges_cross(edges[i], edges[j]):
                v1, v2 = edge_vars[edges[i]]
                u1, u2 = edge_vars[edges[j]]
                cnf.append([-v1, -u1])
                cnf.append([-v1, -u2])
                cnf.append([-v2, -u1])
                cnf.append([-v2, -u2])

    return {
        'cnf': cnf,
        'edge_vars': edge_vars,
        'reverse_map': reverse_map,
        'island_map': island_map,
        'vpool': vpool
    }

# Kiểm tra liên thông
def is_connected(edges, islands):
    graph = defaultdict(list)
    for x1, y1, x2, y2, _ in edges:
        graph[(x1, y1)].append((x2, y2))
        graph[(x2, y2)].append((x1, y1))

    start = next(iter(islands))
    visited = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            queue.extend(graph[node])
    return len(visited) == len(islands)

# Giải pySAT
def solve_hashi(grid):
    if not grid or not grid[0]:
        print("Empty or invalid grid.")
        return None

    data = generateCNF(grid)
    cnf = data['cnf']
    solver = Solver(name='glucose3')
    for clause in cnf:
        solver.add_clause(clause)

    while solver.solve():
        model = solver.get_model()
        active_edges = []
        blocking_clause = []

        for lit in model:
            if lit > 0 and lit in data['reverse_map']:
                edge = data['reverse_map'][lit]
                active_edges.append(edge)
                blocking_clause.append(-lit)

        if is_connected(active_edges, data['island_map']):
            return active_edges
        else:
            solver.add_clause(blocking_clause)

    return None

# Xác định các cạnh có thể nối
def generate_possible_edges(grid):
    rows, cols = len(grid), len(grid[0])
    islands = [(x, y, grid[x][y]) for x in range(rows) for y in range(cols) if grid[x][y] > 0]
    edges = []

    for i, (x1, y1, _) in enumerate(islands):
        for j in range(i + 1, len(islands)):
            x2, y2, _ = islands[j]
            if x1 == x2 and all(grid[x1][k] == 0 for k in range(min(y1, y2) + 1, max(y1, y2))):
                edges.append(((x1, y1), (x2, y2)))
            elif y1 == y2 and all(grid[k][y1] == 0 for k in range(min(x1, x2) + 1, max(x1, x2))):
                edges.append(((x1, y1), (x2, y2)))
    return edges

def island_degree(edges, island):
    return sum(w for e1, e2, w in edges if e1 == island or e2 == island)

#Giải brute-force
def solve_brute_force(grid):
    print("Running brute-force...")
    start = time.time()
    tracemalloc.start()

    edges_possible = generate_possible_edges(grid)
    weights = [0, 1, 2]  # 0 = không nối, 1 = 1 cầu, 2 = 2 cầu

    islands = {(x, y): grid[x][y] for x in range(len(grid)) for y in range(len(grid[0])) if grid[x][y] > 0}
    for combination in itertools.product(weights, repeat=len(edges_possible)):
        used_edges = []
        for i, w in enumerate(combination):
            if w > 0:
                used_edges.append((edges_possible[i][0][0], edges_possible[i][0][1],
                                   edges_possible[i][1][0], edges_possible[i][1][1], w))
        if not is_connected(used_edges, islands):
            continue
        degree_check = True
        deg = {k: 0 for k in islands}
        for x1, y1, x2, y2, w in used_edges:
            deg[(x1, y1)] += w
            deg[(x2, y2)] += w
        for pos in islands:
            if deg[pos] != islands[pos]:
                degree_check = False
                break
        if degree_check:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            print(f"Brute-force finished in {time.time() - start:.2f}s, memory: {peak / 1024:.2f} KB")
            return used_edges
    tracemalloc.stop()
    print("Brute-force found no solution")
    return None

#Giải bằng backtracking
def solve_backtracking(grid):
    print("Running backtracking...")
    start = time.time()
    tracemalloc.start()

    edges_possible = generate_possible_edges(grid)
    islands = {(x, y): grid[x][y] for x in range(len(grid)) for y in range(len(grid[0])) if grid[x][y] > 0}

    def backtrack(idx, current_edges, degree):
        if idx == len(edges_possible):
            if all(degree[pos] == islands[pos] for pos in islands) and is_connected(current_edges, islands):
                return current_edges
            return None

        e1, e2 = edges_possible[idx]
        for w in [0, 1, 2]:
            degree_copy = degree.copy()
            if w > 0:
                degree_copy[e1] += w
                degree_copy[e2] += w
                if degree_copy[e1] > islands[e1] or degree_copy[e2] > islands[e2]:
                    continue
                current_edges.append((e1[0], e1[1], e2[0], e2[1], w))
            result = backtrack(idx + 1, current_edges[:], degree_copy)
            if result:
                return result
            if w > 0:
                current_edges.pop()
        return None

    init_degree = {k: 0 for k in islands}
    result = backtrack(0, [], init_degree)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Backtracking finished in {time.time() - start:.2f}s, memory: {peak / 1024:.2f} KB")
    return result

if __name__ == '__main__':
    for i in range(1, 11): 
        input_file = f"Inputs\\input-{i:02}.txt"
        output_file = f"Outputs\\output-{i:02}.txt"
        grid = read_input(input_file)
        if not grid:
            with open(output_file, 'w') as f:
                f.write("Invalid or empty input.\n")
            continue
        edges = solve_hashi(grid)
        if edges is not None:
            write_solution(grid, edges, output_file)
        else:
            with open(output_file, 'w') as f:
                f.write("No solution found\n")

    #Với thuật toán brute-force và backtracking với độ phức tạp thời gian là 0(3^E) E là số cạnh tiềm năng
    #Brute-force nên chạy khi E <= 12 còn backtracking nên chạy khi E <= 18. Vì thế brute chỉ nên chạy chạy đc input-01
    for i in range(1, 3): 
        input_file = f"Source\\Inputs\\input-{i:02}.txt"
        output_file_bf = f"Source\\Outputs\\output_bf-{i:02}.txt"
        output_file_bt = f"Source\\Outputs\\output_bt-{i:02}.txt"
        grid = read_input(input_file)
        if not grid:
            with open(output_file_bf, 'w') as f:
                f.write("Invalid or empty input.\n")
            with open(output_file_bt, 'w') as f:
                f.write("Invalid or empty input.\n")
            continue

        edges = solve_brute_force(grid)
        if edges is not None:
            write_solution(grid, edges, output_file_bf)
        else:
            with open(output_file_bf, 'w') as f:
                f.write("No solution found\n")
        
        edges = solve_backtracking(grid)
        if edges is not None:
            write_solution(grid, edges, output_file_bt)
        else:
            with open(output_file_bt, 'w') as f:
                f.write("No solution found\n")
