def possible(grid, x, y, n):
    
    """

    grid: Tablero del Sudoku
    x : Indice de Fila [0-8]
    y : Indice de Columna [0-8]
    n : Numero a colocar en el tablero [1-9] 
      
    Returns: True si es posible colocar n en la posicion (x,y) del tablero

    """

    # Verifica que n no pertenece a la fila x
    for i in range(0,9):
        if grid[x][i] == n:
            return False

    # Verifica que n no pertenece a la fila y
    for i in range(0,9):
        if grid[i][y] == n:
            return False

    # Verifica que n no pertenece a la submatriz de 3x3 que le corresponde
    xo = (x//3) * 3
    yo = (y//3) * 3
    for i in range(0, 3):
        for j in range(0, 3):
            if grid[xo+i][yo+j] == n:
                return False

    return True


def is_full(grid):
    
    """

    grid: Tablero de 9x9      
    Returns: True si el sudoku esta lleno
    
    """

    for i in range(9):
        for j in range(9):
            if(grid[i][j] == 0):
                return False
    return True


def find_empty_cell(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j


def print_sudoku(grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("---------------------")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            print(grid[i][j], end=" ")
        print()


def solve(grid):

    """
    Resuelve un sudoku de 9x9.

    Args:
        grid: Tablero de 9x9. Las casillas vacias se representan con 0.

    Returns:
        grid: El tablero resuelto.

    """

    if is_full(grid):
        return grid

    x, y = find_empty_cell(grid)
   
    for num in range(1, 10):
        if possible(grid, x, y, num):
            grid[x][y] = num

            if solve(grid):
                return grid

            grid[x][y] = 0

    return None


grid = [
[5, 3, 0, 0, 7, 0, 0, 0, 0],
[6, 0, 0, 1, 9, 5, 0, 0, 0],
[0, 9, 8, 0, 0, 0, 0, 6, 0],
[8, 0, 0, 0, 6, 0, 0, 0, 3],
[4, 0, 0, 8, 0, 3, 0, 0, 1],
[7, 0, 0, 0, 2, 0, 0, 0, 6],
[0, 6, 0, 0, 0, 0, 2, 8, 0],
[0, 0, 0, 4, 1, 9, 0, 0, 5],
[0, 0, 0, 0, 8, 0, 0, 7, 9]]

solve = solve(grid)
print_sudoku(solve)

