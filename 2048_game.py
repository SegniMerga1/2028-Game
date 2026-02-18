import os
import random
import sys

GRID_SIZE = 4
NEW_TILE_VALUES = [2, 2, 2, 4]

ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_DIM = "\x1b[2m"

COLOR_MAP = {
    2: "\x1b[38;5;230m",
    4: "\x1b[38;5;223m",
    8: "\x1b[38;5;215m",
    16: "\x1b[38;5;208m",
    32: "\x1b[38;5;203m",
    64: "\x1b[38;5;196m",
    128: "\x1b[38;5;135m",
    256: "\x1b[38;5;129m",
    512: "\x1b[38;5;93m",
    1024: "\x1b[38;5;99m",
    2048: "\x1b[38;5;105m",
}
DEFAULT_TILE_COLOR = "\x1b[38;5;111m"
PROMPT_COLOR = "\x1b[38;5;45m"
BACKGROUND_COLOR = "\x1b[48;5;17m"
HEADER_COLOR = "\x1b[38;5;226m"


def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def enable_ansi_colors():
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        pass


def init_grid():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    add_new_tile(grid)
    add_new_tile(grid)
    return grid


def add_new_tile(grid):
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if not empty_cells:
        return False
    r, c = random.choice(empty_cells)
    grid[r][c] = random.choice(NEW_TILE_VALUES)
    return True


def format_cell(value, width):
    if value == 0:
        padded = ".".rjust(width)
        return f"{ANSI_DIM}{padded}{ANSI_RESET}"

    color = COLOR_MAP.get(value, DEFAULT_TILE_COLOR)
    padded = str(value).rjust(width)
    return f"{ANSI_BOLD}{color}{padded}{ANSI_RESET}"


def display_grid(grid, score):
    clear_screen()
    total_sum = sum(sum(row) for row in grid)
    print(f"{BACKGROUND_COLOR}{HEADER_COLOR}2048 - Console Version{ANSI_RESET}")
    print(f"{BACKGROUND_COLOR}{HEADER_COLOR}Score: {score} | Sum: {total_sum}{ANSI_RESET}")
    print()

    max_value = max(max(row) for row in grid)
    cell_width = max(6, len(str(max_value)) + 2)

    horizontal_line = "+" + "+".join(["-" * cell_width] * GRID_SIZE) + "+"
    for row in grid:
        print(f"{BACKGROUND_COLOR}{horizontal_line}{ANSI_RESET}")
        row_values = "|" + "|".join(format_cell(value, cell_width) for value in row) + "|"
        print(f"{BACKGROUND_COLOR}{row_values}{ANSI_RESET}")
    print(f"{BACKGROUND_COLOR}{horizontal_line}{ANSI_RESET}")
    print()
    print("Controls: W/A/S/D or Arrow Keys (WASD for fallback), Q to quit")



def compress_row_left(row):
    new_row = [value for value in row if value != 0]
    new_row.extend([0] * (GRID_SIZE - len(new_row)))
    return new_row


def merge_row_left(row):
    score_gain = 0
    for idx in range(GRID_SIZE - 1):
        if row[idx] != 0 and row[idx] == row[idx + 1]:
            row[idx] *= 2
            row[idx + 1] = 0
            score_gain += row[idx]
    return row, score_gain


def move_left(grid):
    moved = False
    score_gain = 0
    new_grid = []
    for row in grid:
        compressed = compress_row_left(row)
        merged, gained = merge_row_left(compressed)
        compressed_again = compress_row_left(merged)
        if compressed_again != row:
            moved = True
        new_grid.append(compressed_again)
        score_gain += gained
    return new_grid, moved, score_gain


def reverse_grid_rows(grid):
    return [list(reversed(row)) for row in grid]


def transpose_grid(grid):
    return [list(row) for row in zip(*grid)]


def move_right(grid):
    reversed_grid = reverse_grid_rows(grid)
    new_grid, moved, score_gain = move_left(reversed_grid)
    return reverse_grid_rows(new_grid), moved, score_gain


def move_up(grid):
    transposed = transpose_grid(grid)
    new_grid, moved, score_gain = move_left(transposed)
    return transpose_grid(new_grid), moved, score_gain


def move_down(grid):
    transposed = transpose_grid(grid)
    new_grid, moved, score_gain = move_right(transposed)
    return transpose_grid(new_grid), moved, score_gain


def can_move(grid):
    for row in grid:
        if 0 in row:
            return True
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r][c + 1]:
                return True
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r + 1][c]:
                return True
    return False


if os.name == "nt":
    import msvcrt

    def get_input_key():
        key = msvcrt.getch()
        if key in (b"\x00", b"\xe0"):
            key = msvcrt.getch()
            return {
                b"H": "UP",
                b"P": "DOWN",
                b"K": "LEFT",
                b"M": "RIGHT",
            }.get(key)
        try:
            return key.decode("utf-8").upper()
        except UnicodeDecodeError:
            return None
else:
    import termios
    import tty

    def get_input_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            if key == "\x1b":
                key += sys.stdin.read(2)
                return {
                    "\x1b[A": "UP",
                    "\x1b[B": "DOWN",
                    "\x1b[D": "LEFT",
                    "\x1b[C": "RIGHT",
                }.get(key)
            return key.upper()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


MOVE_MAP = {
    "LEFT": move_left,
    "RIGHT": move_right,
    "UP": move_up,
    "DOWN": move_down,
    "A": move_left,
    "D": move_right,
    "W": move_up,
    "S": move_down,
}


def main():
    enable_ansi_colors()
    grid = init_grid()
    score = 0

    clear_screen()
    print("Welcome to 2048!")
    print("Combine tiles with the same number to reach 2048.")
    print("Do you want to play? (Y/N)")
    while True:
        choice = get_input_key()
        if choice is None:
            continue
        if choice in ("Y", "N"):
            break
    if choice == "N":
        print("Maybe next time!")
        return
    print("Press any key to start...")
    get_input_key()

    while True:
        display_grid(grid, score)
        if not can_move(grid):
            print("Game over! No more moves available.")
            print(f"{PROMPT_COLOR}Play again? (Y/N){ANSI_RESET}")
            while True:
                choice = get_input_key()
                if choice in ("Y", "N"):
                    break
            if choice == "Y":
                grid = init_grid()
                score = 0
                continue
            print("Thanks for playing!")
            break

        key = get_input_key()
        if key is None:
            continue
        if key in ("Q", "\x03"):
            print(f"{PROMPT_COLOR}Do you want to quit? (Y/N){ANSI_RESET}")
            while True:
                choice = get_input_key()
                if choice in ("Y", "N"):
                    break
            if choice == "Y":
                print("Thanks for playing!")
                break
            continue
        if key not in MOVE_MAP:
            continue

        new_grid, moved, score_gain = MOVE_MAP[key](grid)
        if moved:
            grid = new_grid
            score += score_gain
            add_new_tile(grid)


if __name__ == "__main__":
    main()
