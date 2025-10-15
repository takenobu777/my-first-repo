import curses
import random
import time

# Dimensions
HEIGHT = 20
WIDTH = 10

# Shapes with rotations
SHAPES = {
    'I': [[(0, 0), (1, 0), (2, 0), (3, 0)],
          [(1, -1), (1, 0), (1, 1), (1, 2)]],
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    'T': [[(0, 0), (1, -1), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (2, 0), (1, 1)],
          [(1, -1), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (1, 0), (2, 0), (1, -1)]],
    'S': [[(0, 0), (0, 1), (1, -1), (1, 0)],
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
    'Z': [[(0, -1), (0, 0), (1, 0), (1, 1)],
          [(0, 1), (1, 0), (1, 1), (2, 0)]],
    'J': [[(0, -1), (1, -1), (1, 0), (1, 1)],
          [(0, 0), (0, 1), (1, 0), (2, 0)],
          [(1, -1), (1, 0), (1, 1), (2, 1)],
          [(0, 0), (1, 0), (2, 0), (2, -1)]],
    'L': [[(0, 1), (1, -1), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (2, 0), (2, 1)],
          [(1, -1), (1, 0), (1, 1), (2, -1)],
          [(0, -1), (0, 0), (1, 0), (2, 0)]]
}


class PieceBag:
    """Random generator that mimics the modern Tetris 7-bag system."""

    def __init__(self):
        self._bag = []

    def next(self):
        if not self._bag:
            self._bag = list(SHAPES.keys())
            random.shuffle(self._bag)
        return self._bag.pop()


def get_piece_cells(name, rotation):
    return SHAPES[name][rotation % len(SHAPES[name])]


def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def draw_board(stdscr, board, score, current_piece=None, offset=None, next_piece=None):
    stdscr.clear()

    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            stdscr.addstr(y, x * 2, '[]' if cell else '  ')

    if current_piece is not None and offset is not None:
        off_y, off_x = offset
        for y, x in current_piece:
            draw_y, draw_x = y + off_y, x + off_x
            if draw_y >= 0:
                stdscr.addstr(draw_y, draw_x * 2, '[]')

    stdscr.addstr(0, WIDTH * 2 + 2, f"Score: {score}")

    if next_piece:
        stdscr.addstr(2, WIDTH * 2 + 2, "Next:")
        min_y = min(y for y, _ in next_piece)
        min_x = min(x for _, x in next_piece)
        for y, x in next_piece:
            draw_y = 3 + (y - min_y)
            draw_x = WIDTH * 2 + 2 + (x - min_x) * 2
            stdscr.addstr(draw_y, draw_x, '[]')

    stdscr.addstr(HEIGHT + 1, 0,
                  "Controls: ← → move, ↑ rotate, ↓ soft drop, q quit")
    stdscr.refresh()


def check_collision(board, piece, offset):
    off_y, off_x = offset
    for y, x in piece:
        new_y, new_x = y + off_y, x + off_x
        if new_x < 0 or new_x >= WIDTH or new_y >= HEIGHT:
            return True
        if new_y >= 0 and board[new_y][new_x]:
            return True
    return False


def merge_piece(board, piece, offset):
    off_y, off_x = offset
    for y, x in piece:
        if y + off_y >= 0:
            board[y + off_y][x + off_x] = 1


def clear_lines(board):
    new_board = [row for row in board if not all(row)]
    cleared = HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0 for _ in range(WIDTH)])
    return new_board, cleared


def rotate(name, rotation):
    return get_piece_cells(name, rotation)


def tetris(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    board = create_board()
    score = 0
    bag = PieceBag()
    piece_name = bag.next()
    rotation = 0
    piece = get_piece_cells(piece_name, rotation)
    next_piece_name = bag.next()
    next_piece = get_piece_cells(next_piece_name, 0)
    offset = [-2, WIDTH // 2 - 1]
    drop_time = time.time()
    fall_interval = 0.5
    soft_drop_interval = 0.05

    while True:
        draw_board(stdscr, board, score, piece, offset, next_piece)
        key = stdscr.getch()
        lock_piece = False
        soft_drop = False

        if key == curses.KEY_LEFT and not check_collision(board, piece, (offset[0], offset[1] - 1)):
            offset[1] -= 1
        elif key == curses.KEY_RIGHT and not check_collision(board, piece, (offset[0], offset[1] + 1)):
            offset[1] += 1
        elif key == curses.KEY_DOWN:
            soft_drop = True
            if not check_collision(board, piece, (offset[0] + 1, offset[1])):
                offset[0] += 1
                drop_time = time.time()
            else:
                lock_piece = True
        elif key == curses.KEY_UP:
            new_rot = (rotation + 1) % len(SHAPES[piece_name])
            new_piece = rotate(piece_name, new_rot)
            if not check_collision(board, new_piece, offset):
                rotation = new_rot
                piece = new_piece
        elif key == ord('q'):
            break

        interval = soft_drop_interval if soft_drop else fall_interval
        if time.time() - drop_time > interval and not lock_piece:
            drop_time = time.time()
            if not check_collision(board, piece, (offset[0] + 1, offset[1])):
                offset[0] += 1
            else:
                lock_piece = True

        if lock_piece:
            merge_piece(board, piece, offset)
            board, cleared = clear_lines(board)
            score += cleared * 100
            piece_name = next_piece_name
            rotation = 0
            piece = get_piece_cells(piece_name, rotation)
            next_piece_name = bag.next()
            next_piece = get_piece_cells(next_piece_name, 0)
            offset = [-2, WIDTH // 2 - 1]

            if check_collision(board, piece, offset):
                draw_board(stdscr, board, score)
                stdscr.addstr(HEIGHT // 2, WIDTH - 4, 'GAME OVER')
                stdscr.refresh()
                stdscr.nodelay(False)
                stdscr.getch()
                break

        time.sleep(0.01)


def main():
    curses.wrapper(tetris)


if __name__ == '__main__':
    main()
