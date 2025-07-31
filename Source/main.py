import sys
sys.stdout.reconfigure(encoding='utf-8')
from pySAT_solver import solve_pysat
from astar_solver import solve_astar
from backtracking_solver import solve_backtracking
from brute_force_solver import solve_bruteforce

def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        if not lines:
            print(f"Warning: {filename} is empty or invalid format.")
            return []
        return [list(map(int, line.split(','))) for line in lines]

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

if __name__ == '__main__':
    for i in range(1, 11): 
        input_file = f"Inputs/input-{i:02}.txt"
        output_file = f"Outputs/output-{i:02}.txt"
        grid = read_input(input_file)
        if not grid:
            with open(output_file, 'w') as f:
                f.write("Invalid or empty input.\n")
            continue
        edges = solve_backtracking(grid)
        if edges is not None:
            write_solution(grid, edges, output_file)
        else:
            with open(output_file, 'w') as f:
                f.write("No solution found\n")