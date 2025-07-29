from pysat.solvers import Solver
from generator import generateCNF, is_connected

def solve_pysat(grid):
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