def print_grid(cells):
    print("---------")
    for i in range(0, 9, 3):
        print(f"| {' '.join(cells[i:i+3])} |")
    print("---------")

def get_cell_index(row, col):
    # Converts 2D coordinates (1-based) to a 1D index (0-based)
    return (row - 1) * 3 + (col - 1)

def is_valid_coordinates(row, col):
    return 1 <= row <= 3 and 1 <= col <= 3

def check_winner(cells, player):
    win_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    return any(all(cells[i] == player for i in line) for line in win_lines)

def board_full(cells):
    return all(c in "XO" for c in cells)

def main():
    cells = ['_' for _ in range(9)]
    print_grid(cells)
    current_player = 'X'

    while True:
        while True:
            coords = input(f"Player {current_player}, enter the coordinates: ").split()
            if len(coords) != 2 or not all(item.isdigit() for item in coords):
                print("You should enter numbers!")
                continue
            row, col = map(int, coords)
            if not is_valid_coordinates(row, col):
                print("Coordinates should be from 1 to 3!")
                continue
            idx = get_cell_index(row, col)
            if cells[idx] != '_':
                print("This cell is occupied! Choose another one!")
                continue
            cells[idx] = current_player
            break

        print_grid(cells)

        if check_winner(cells, current_player):
            print(f"{current_player} wins")
            break
        elif board_full(cells):
            print("Draw")
            break

        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'

if __name__ == "__main__":
    main()
