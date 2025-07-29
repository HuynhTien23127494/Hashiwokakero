import heapq
from collections import defaultdict
from generator import generateCNF, is_connected

def unit_propagation(clauses, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        if not unit_clauses:
            break
        for clause in unit_clauses:
            literal = clause[0]
            var = abs(literal)
            value = literal > 0
            if var in assignment:
                if assignment[var] != value:
                    return False, clauses  # conflict
                continue
            assignment[var] = value
            changed = True
            new_clauses = []
            for c in clauses:
                if literal in c:
                    continue  # clause is satisfied
                if -literal in c:
                    reduced = [l for l in c if l != -literal]
                    if not reduced:
                        return False, clauses  # conflict
                    new_clauses.append(reduced)
                else:
                    new_clauses.append(c)
            clauses = new_clauses
    return True, clauses

def pure_literal_elimination(clauses, assignment):
    literal_count = defaultdict(int)
    for clause in clauses:
        for lit in clause:
            literal_count[lit] += 1
    assigned_vars = set(assignment.keys())
    pure_literals = set()
    for lit in literal_count:
        if -lit not in literal_count and abs(lit) not in assigned_vars:
            pure_literals.add(lit)

    new_clauses = []
    for clause in clauses:
        if any(lit in pure_literals for lit in clause):
            continue  # satisfied
        new_clauses.append(clause)

    for lit in pure_literals:
        assignment[abs(lit)] = lit > 0
    return new_clauses

def heuristic(clauses, assignment, total_vars):
    unassigned = total_vars - len(assignment)
    clause_penalty = sum(1 for c in clauses if not any((abs(l) in assignment and assignment[abs(l)] == (l > 0)) for l in c))
    return unassigned + clause_penalty

def solve_cnf_astar(data):
    clauses = data['cnf']
    total_vars = max(abs(lit) for clause in clauses for lit in clause)
    initial_assignment = {}
    clauses = pure_literal_elimination(clauses, initial_assignment)
    ok, clauses = unit_propagation(clauses, initial_assignment)
    if not ok:
        return None

    heap = []
    g = 0
    h = heuristic(clauses, initial_assignment, total_vars)
    heapq.heappush(heap, (g + h, g, initial_assignment, clauses))
    closed_set = set()

    while heap:
        f, g, assignment, clauses = heapq.heappop(heap)
        frozen = (frozenset(assignment.items()), len(assignment))
        if frozen in closed_set:
            continue
        closed_set.add(frozen)

        if not clauses:
            return assignment

        unassigned_vars = [v for v in range(1, total_vars + 1) if v not in assignment]
        if not unassigned_vars:
            continue

        next_var = unassigned_vars[0]
        for value in [True, False]:
            new_assign = assignment.copy()
            new_assign[next_var] = value
            new_clauses = [clause[:] for clause in clauses]  # deep copy
            lit = next_var if value else -next_var
            new_clauses = [[l for l in c if l != -lit] for c in new_clauses if lit not in c]

            new_clauses = pure_literal_elimination(new_clauses, new_assign)
            ok, new_clauses = unit_propagation(new_clauses, new_assign)
            if not ok:
                continue

            h = heuristic(new_clauses, new_assign, total_vars)
            heapq.heappush(heap, (g + 1 + h, g + 1, new_assign, new_clauses))

    return None

def solve_astar(grid):
    if not grid or not grid[0]:
        print("Empty or invalid grid.")
        return None

    data = generateCNF(grid)
    assignment = solve_cnf_astar(data)
    if not assignment:
        return None

    active_edges = []
    for var, val in assignment.items():
        if val and var in data['reverse_map']:
            edge = data['reverse_map'][var]
            active_edges.append(edge)

    if is_connected(active_edges, data['island_map']):
        return active_edges
    else:
        return None
    