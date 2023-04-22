from omok import board
import numpy as np

BLANK, BLACK, WHITE, BLOCKED = 0, 1, -1, 2
color_dict = {
    BLANK: "BLANK",
    BLACK: "BLACK",
    WHITE: "WHITE",
    BLOCKED: "BLOCKED"
}
n_of_board = 0

size = 20
stone_info = np.zeros([size] * 2, dtype=int)
turn = BLACK
last = None

def put_stone(pos: tuple) -> None:
    pos = tuple(map(int, pos))
    for i in range(len(pos)):
        assert board.size > pos[i] and pos[i] >= 0, "pos : index error"
    assert board.stone_info[pos] == board.BLANK, "돌을 놓으려는 위치가 빈칸이 아닙니다!"
    board.stone_info[pos] = board.turn
    board.last = pos

def check_winner() -> int:
    for color in (board.BLACK, board.WHITE):
        for line in line_range():
            line = np.concatenate([line, [0]])
            stack = 0
            for space in line:
                if space == color:
                    stack += 1
                else:
                    if stack == 5:
                        print(f"{board.color_dict[color]} WIN!")
                        return color
                    stack = 0
        if stack == 5:
            print(f"{board.color_dict[color]} WIN!")
            return color
    return board.BLANK

def change_turn(*colors) -> None:
    if len(colors) == 0:
        board.turn *= -1
    else:
        board.turn = colors[0]

def make_turn(color):
    assert color == 1 or color == -1, f"올바른 color값이 아닙니다. color는 1 또는 -1이어야 합니다. color type : {type(color)}, color value : {color}"
    board.turn = color

def line_range() -> list:
    size = board.size
    for v in board.stone_info:
        yield v

    for v in board.stone_info.T:
        yield v

    for i in np.arange(0, size):
        yield board.stone_info[0:1 + i, size - (1 + i):size].diagonal()
    for i in np.arange(size - 2, -1, -1):
        yield board.stone_info.T[0:1 + i, size - (1 + i):size].diagonal()

    for i in np.arange(0, size):
        yield board.stone_info[:, ::-1][0:1 + i, size - (1 + i):size].diagonal()
    for i in np.arange(size - 2, -1, -1):
        yield board.stone_info.T[::-1][0:1 + i, size - (1 + i):size].diagonal()

def board_print() -> None:
    visualized = board.stone_info.copy().astype(str)
    visualized[np.where(visualized == '-1')] = '○'
    visualized[np.where(visualized == '1')] = '●'
    visualized[np.where(visualized == '0')] = '`'
    # print(pd.DataFrame(visualized).T)
    for y in range(board.size):
        for x in range(board.size):
            print(visualized[x, y], end=' ')
        print()
    print()
