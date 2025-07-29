from pysat.card import CardEnc
from pysat.formula import IDPool
from collections import defaultdict, deque

# Kiểm tra 2 cạnh cắt nhau
def edges_cross(e1, e2):
    (x1, y1, x2, y2) = e1
    (a1, b1, a2, b2) = e2
    if x1 == x2 and b1 == b2:     # e1 ngang, e2 dọc
        return (min(y1, y2) < b1 < max(y1, y2)) and (min(a1, a2) < x1 < max(a1, a2))
    if a1 == a2 and y1 == y2:     # e1 dọc, e2 ngang
        return (min(b1, b2) < y1 < max(b1, b2)) and (min(x1, x2) < a1 < max(x1, x2))
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
                if grid[x][dy] == 0: continue
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
                if grid[dx][y] == 0: continue
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
                cnf.extend([[-v1, -u1], [-v1, -u2], [-v2, -u1], [-v2, -u2]])


    # Ràng buộc hạn chế cô lập
    for (x1, y1, x2, y2), (v1, v2) in edge_vars.items():
        if island_map.get((x1, y1)) == 1 and island_map.get((x2, y2)) == 1:
            cnf.extend([[-v1], [-v2]])
        if island_map.get((x1, y1)) == 2 and island_map.get((x2, y2)) == 2:
            cnf.append([-v2])
    # Đặt 4 cầu đôi ở đảo 8
    for (x, y), total in island_map.items():
        if total != 8: continue
        for (a, b, c, d), (v1, v2) in edge_vars.items():
            if (a, b) == (x, y) or (c, d) == (x, y):
                cnf.append([v1])
                cnf.append([v2])

    return {
        'cnf': cnf,
        'edge_vars': edge_vars,
        'reverse_map': reverse_map,
        'island_map': island_map,
        'vpool': vpool
    }

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