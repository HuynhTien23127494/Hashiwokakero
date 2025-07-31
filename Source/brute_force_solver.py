from generator import generateCNF, is_connected
import itertools
import time

def solve_cnf_bruteforce(data):
    clauses = data['cnf']
    reverse_map = data['reverse_map']
    island_map = data['island_map']
    
    all_vars = sorted(set(abs(lit) for clause in clauses for lit in clause))
    n = len(all_vars)
    
    for k in range(0, n+1):
        for combo in itertools.combinations(all_vars, k):
            assignment = {}
            for var in all_vars:
                assignment[var] = var in combo
            
            satisfied = True
            for clause in clauses:
                clause_satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if (lit > 0 and assignment.get(var, False)) or (lit < 0 and not assignment.get(var, False)):
                        clause_satisfied = True
                        break
                if not clause_satisfied:
                    satisfied = False
                    break
            
            if satisfied:
                active_edges = []
                for var in all_vars:
                    if assignment.get(var, False) and var in reverse_map:
                        active_edges.append(reverse_map[var])
                
                if is_connected(active_edges, island_map):
                    return active_edges
    
    return None

def solve_bruteforce(grid):
    if not grid or not grid[0]:
        print("Empty or invalid grid.")
        return None
    
    start_time = time.perf_counter()
    
    data = generateCNF(grid)
    solution = solve_cnf_bruteforce(data)
    
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"[Brute-force] Solved in {elapsed:.4f} seconds")
    
    return solution

