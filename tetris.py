import curses
import random
import time

# Dimensions
HEIGHT = 20
WIDTH = 10

# Shapes with rotations
SHAPES = {
    'I': [[(0,0), (1,0), (2,0), (3,0)],
          [(1,-1), (1,0), (1,1), (1,2)]],
    'O': [[(0,0), (0,1), (1,0), (1,1)]],
    'T': [[(0,0), (1,-1), (1,0), (1,1)],
          [(0,0), (1,0), (2,0), (1,1)],
          [(1,-1), (1,0), (1,1), (2,0)],
          [(0,0), (1,0), (2,0), (1,-1)]],
    'S': [[(0,0), (0,1), (1,-1), (1,0)],
          [(0,0), (1,0), (1,1), (2,1)]],
    'Z': [[(0,-1), (0,0), (1,0), (1,1)],
          [(0,1), (1,0), (1,1), (2,0)]],
    'J': [[(0,-1), (1,-1), (1,0), (1,1)],
          [(0,0), (0,1), (1,0), (2,0)],
          [(1,-1), (1,0), (1,1), (2,1)],
          [(0,0), (1,0), (2,0), (2,-1)]],
    'L': [[(0,1), (1,-1), (1,0), (1,1)],
          [(0,0), (1,0), (2,0), (2,1)],
          [(1,-1), (1,0), (1,1), (2,-1)],
          [(0,-1), (0,0), (1,0), (2,0)]]
}


def create_board():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def draw_board(stdscr, board, score):
    stdscr.clear()
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            char = '#'
            if cell:
                stdscr.addstr(y, x * 2, '[]')
            else:
                stdscr.addstr(y, x * 2, '  ')
    stdscr.addstr(0, WIDTH * 2 + 2, f"Score: {score}")
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


def rotate(piece, rotation):
    return SHAPES[piece[0]][rotation]


def choose_piece():
    name = random.choice(list(SHAPES.keys()))
    rotation = 0
    shape = SHAPES[name][rotation]
    return (name, rotation, shape)


def tetris(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    board = create_board()
    score = 0
    piece_name, rotation, piece = choose_piece()
    offset = [-2, WIDTH // 2 - 1]
    drop_time = time.time()
    speed = 0.5

    while True:
        draw_board(stdscr, board, score)
        key = stdscr.getch()
        if key == curses.KEY_LEFT and not check_collision(board, piece, (offset[0], offset[1]-1)):
            offset[1] -= 1
        elif key == curses.KEY_RIGHT and not check_collision(board, piece, (offset[0], offset[1]+1)):
            offset[1] += 1
        elif key == curses.KEY_DOWN:
            speed = 0.05
        elif key == curses.KEY_UP:
            new_rot = (rotation + 1) % len(SHAPES[piece_name])
            new_piece = SHAPES[piece_name][new_rot]
            if not check_collision(board, new_piece, offset):
                rotation = new_rot
                piece = new_piece
        elif key == ord('q'):
            break

        if time.time() - drop_time > speed:
            drop_time = time.time()
            if not check_collision(board, piece, (offset[0] + 1, offset[1])):
                offset[0] += 1
            else:
                merge_piece(board, piece, offset)
                board, cleared = clear_lines(board)
                score += cleared * 100
                piece_name, rotation, piece = choose_piece()
                offset = [-2, WIDTH // 2 - 1]
                speed = 0.5
                if check_collision(board, piece, offset):
                    stdscr.addstr(HEIGHT//2, WIDTH-4, 'GAME OVER')
                    stdscr.refresh()
                    stdscr.nodelay(False)
                    stdscr.getch()
                    break

        for y, x in piece:
            if y + offset[0] >= 0:
                stdscr.addstr(y + offset[0], (x + offset[1]) * 2, '[]')
        stdscr.refresh()


def main():
    curses.wrapper(tetris)


if __name__ == '__main__':
    main()
