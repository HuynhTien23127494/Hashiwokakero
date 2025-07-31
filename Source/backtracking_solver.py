from generator import generateCNF, is_connected
import copy
import time

def unit_propagate(clauses, assignment):
    changed = True
    new_assignment = assignment.copy()
    new_clauses = copy.deepcopy(clauses)

    while changed:
        changed = False
        updated_clauses = []
        for clause in new_clauses:
            unassigned_lits = []
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in new_assignment:
                    if (lit > 0 and new_assignment[var]) or (
                        lit < 0 and not new_assignment[var]
                    ):
                        satisfied = True
                        break
                else:
                    unassigned_lits.append(lit)
            if satisfied:
                continue
            if not unassigned_lits:
                return None, None  # Xung đột
            if len(unassigned_lits) == 1:
                unit_lit = unassigned_lits[0]
                var = abs(unit_lit)
                val = unit_lit > 0
                if var in new_assignment and new_assignment[var] != val:
                    return None, None  # Xung đột
                if var not in new_assignment:
                    new_assignment[var] = val
                    changed = True
            updated_clauses.append(unassigned_lits)
        new_clauses = updated_clauses
    return new_clauses, new_assignment


def dpll(clauses, assignment):
    new_clauses, new_assignment = unit_propagate(clauses, assignment)
    if new_clauses is None:
        return None

    literal_polarity = {}
    for clause in new_clauses:
        for lit in clause:
            var = abs(lit)
            if var in new_assignment:
                continue
            if var not in literal_polarity:
                literal_polarity[var] = lit > 0
            elif literal_polarity[var] != (lit > 0):
                literal_polarity[var] = None

    for var, val in literal_polarity.items():
        if val is not None and var not in new_assignment:
            new_assignment[var] = val

    all_satisfied = all(
        any((lit > 0 and new_assignment.get(abs(lit), False)) or
            (lit < 0 and not new_assignment.get(abs(lit), False))
            for lit in clause)
        for clause in new_clauses
    )
    if all_satisfied:
        return new_assignment

    all_vars = set(abs(lit) for clause in new_clauses for lit in clause)
    unassigned = list(all_vars - set(new_assignment.keys()))
    if not unassigned:
        return new_assignment

    var = min(unassigned)
    for val in [True, False]:
        trial = new_assignment.copy()
        trial[var] = val
        result = dpll(new_clauses, trial)
        if result is not None:
            return result
    return None


def solve_cnf_backtracking(data):
    clauses = data['cnf']
    reverse_map = data['reverse_map']
    island_map = data['island_map']

    all_vars = sorted(set(abs(lit) for clause in clauses for lit in clause))

    while True:
        model = dpll(clauses, {})
        if model is None:
            return None

        active_edges = []
        for var in all_vars:
            if model.get(var, False) and var in reverse_map:
                active_edges.append(reverse_map[var])

        if is_connected(active_edges, island_map):
            return active_edges
        else:
            blocking_clause = [-var if model.get(var, False) else var for var in all_vars]
            clauses.append(blocking_clause)

def solve_backtracking(grid):
    if not grid or not grid[0]:
        print("Empty or invalid grid.")
        return None
    
    start_time = time.perf_counter()

    data = generateCNF(grid)
    solution = solve_cnf_backtracking(data)

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[Backtracking] Solved in {elapsed:.4f} seconds")

    return solution
