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
    print("=== Hashiwokakero Solver ===")
    print("Welcome to the Hashiwokakero puzzle solver!")
    
    while True:
        # First prompt: Select input file
        print("\n" + "="*40)
        print("Available input files: 1-10")
        try:
            input_choice = input("Please select an input file (1-10) or 'q' to quit: ").strip()
            
            if input_choice.lower() == 'q':
                print("Goodbye!")
                break
                
            input_num = int(input_choice)
            if input_num < 1 or input_num > 10:
                print("Invalid input! Please enter a number between 1 and 10.")
                continue
                
        except ValueError:
            print("Invalid input! Please enter a valid number between 1 and 10.")
            continue
        
        # Second prompt: Select solving method
        print("\n" + "="*40)
        print("Available solving methods:")
        print("1. pySAT")
        print("2. Brute Force")
        print("3. Backtracking")
        print("4. A*")
        print("5. Exit")
        
        try:
            method_choice = input("Please select a solving method (1-5): ").strip()
            
            if method_choice == '5':
                print("Goodbye!")
                break
                
            method_num = int(method_choice)
            if method_num < 1 or method_num > 4:
                print("Invalid choice! Please enter a number between 1 and 4.")
                continue
                
        except ValueError:
            print("Invalid input! Please enter a valid number between 1 and 4.")
            continue
        
        # Process the selected input and method
        input_file = f"Inputs/input-{input_num:02}.txt"
        output_file = f"Outputs/output-{input_num:02}.txt"
        
        print(f"\nProcessing input file: {input_file}")
        print(f"Using method: {['pySAT', 'Brute Force', 'Backtracking', 'A*'][method_num-1]}")
        
        grid = read_input(input_file)
        if not grid:
            with open(output_file, 'w') as f:
                f.write("Invalid or empty input.\n")
            print("Error: Invalid or empty input file.")
            continue
        
        # Solve using selected method
        edges = None
        if method_num == 1:
            edges = solve_pysat(grid)
        elif method_num == 2:
            edges = solve_bruteforce(grid)
        elif method_num == 3:
            edges = solve_backtracking(grid)
        elif method_num == 4:
            edges = solve_astar(grid)
        
        if edges is not None:
            write_solution(grid, edges, output_file)
            print(f"Solution found and saved to: {output_file}")
        else:
            with open(output_file, 'w') as f:
                f.write("No solution found\n")
            print("No solution found for this puzzle.")
        
        print("\n" + "="*40)