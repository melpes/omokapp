import pygame, sys
from pygame.locals import QUIT
import numpy as np
from pygame.math import Vector2
from pygame.locals import MOUSEBUTTONDOWN
from random import choice
import pandas as pd

# 4/8
if True:
    # 4/8
    # pygame으로 구현
    # 가장 최근에 둔 수 표기 구현
    # 주도권 구현 필요
    # 주도권 : 3을 연속해서 만들 수 있으면 상대는 자신에게 유리한 수가 있어도 두지 못하고 오직 막는 수 중에서만 선택할 수 있게 된다. 이때 우선순위는 자신의 4 > (공)막4 > (공)3 이며 이 수를 제외하고는 주도권을 잃는다고 상정한다.
    # 다만 내가 주도권이 있어도 상대가 더 높은 우선순위의 주도권 공격은 할 수 있다.
    # 아래는 주도권 공격에 대해 상대가 둘 수 있는 수들이다.
    #              방어      /          공격
    #       사이 공간 / 양옆  / (공)3 /  (공)막4  / 4
    # 공3      30O     26O  (160/200) 310/350   400
    # 3         -      300  (160/200) 310/350   400
    # 공막4    350     310  (160/200) (310/350) (400)
    # 막4              350  (160/200) (310/350) (400)
    # 4               400  (160/200) (310/350) (400)
    # 1. 주도권 공격들을 분류한다.
    # 2. 상대에 주도권 공격이 있는지 판단하고 있으면 정해진 대응을 한다.
    # 3. 내 주도권 공격이 가능한지 판단하고 가능하면 주도권 공격을 한다.
    # 4. 점수순으로 수를 둔다
    # 보드에 있는 주도권 공격을 파악하는 법(공격이 가능한 것 말고 이미 이루어진 공격)
    # 점수 : 방어해야 하는 주도권 공격의 최소점은 260점이며 한 가지를 제외하면 전부 300점이 넘는다.
    # 다만 최종 점수는 결합 점수기 때문에 주도권 공격이 아니어도 300점을 넘는 경우가 많다.
    # 따라서 결합 이전 점수를 기준으로 판단해야 한다.
    # 주도권 공격이 있는지 판단하는 self.leading_color 추가.
    # 상대 주도권 공격이 있으면 
    
    pass


def main():
    # 선언부
    screen_size = (500, 500)
    board = Board(20)
    ai = Ai(board, 1)
    ai2 = Ai(board, -1)

    # color
    GRAY =  (   128,    128,    128)
    BLACK = (     0,      0,      0)
    WHITE = (   255,    255,    255)
    BROWN = (   188,     94,      0)
    BGREEN = (   13,    152,    186)
    RED =   (   255,      0,      0)
    
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    board.put_stone((board.size // 2, board.size // 2))
    board.make_turn(-1)
    pygame.display.set_caption("Omok")

    while True:
        if board.turn == 1:
            selection = choice(ai.decision())
            board.put_stone(selection)
            board.change_turn()
        else:
            selection = choice(ai2.decision())
            board.put_stone(selection)
            board.change_turn()
            
        board_size_p = Grid.cell_size * board.size
        
        screen.fill(WHITE)
        edge = 3
        pos = [screen_size[i] // 2 - board_size_p // 2 - edge for i in range(2)]
        rect = (pos[0], pos[1], board_size_p + 2 * edge, board_size_p + 2 * edge)
        pygame.draw.rect(screen, BGREEN, rect)
        pygame.draw.rect(screen, BLACK, rect, edge)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # elif event.type == MOUSEBUTTONDOWN and board.turn == -1:
            #     board.put_stone(Grid(event.pos - Vector2(pos) - Vector2(edge)).grid_pos)
            #     board.change_turn()
        
        for x in range(board.size):
            for y in range(board.size):
                xy = (x, y)
                if sum(xy) % 2 == 0:
                    cell_pos = [Grid.cell_size * xy[i] - board_size_p // 2 + screen_size[i] // 2 for i in range(2)]
                    rect = (cell_pos[0], cell_pos[1], Grid.cell_size, Grid.cell_size)
                    pygame.draw.rect(screen, BROWN, rect)            

        for x in range(board.size):
            for y in range(board.size):
                xy = (x, y)
                cell_pos = [(xy[i] + 0.5 - board.size // 2) * Grid.cell_size + screen_size[i] // 2 for i in range(2)]
                if board.stone_info[x, y] == 1:
                    pygame.draw.circle(screen, BLACK, cell_pos, Grid.cell_size // 2.5)
                elif board.stone_info[x, y] == -1:
                    pygame.draw.circle(screen, WHITE, cell_pos, Grid.cell_size // 2.5)
        last_pos = [(board.last[i] + 0.5 - board.size // 2) * Grid.cell_size + screen_size[i] // 2 for i in range(2)]
        pygame.draw.circle(screen, RED, last_pos, Grid.cell_size // 10)

        pygame.display.update()

        if board.check_winner() != 0:
            break

class Board:
    BLANK, BLACK, WHITE, BLOCKED = 0, 1, -1, 2
    color_dict = {
        BLANK: "BLANK",
        BLACK: "BLACK",
        WHITE: "WHITE",
        BLOCKED: "BLOCKED"
    }
    n_of_board = 0

    def __init__(self, board_width: int) -> None:
        Board.n_of_board += 1
        self.size = board_width
        self.stone_info = np.zeros([self.size] * 2, dtype=int)
        self.turn = Board.BLACK
        self.last = None

    def put_stone(self, pos: tuple) -> None:
        pos = tuple(map(int, pos))
        for i in range(len(pos)):
            assert self.size > pos[i] and pos[
                i] >= 0, "pos : index error"
        assert self.stone_info[pos] == Board.BLANK, "돌을 놓으려는 위치가 빈칸이 아닙니다!"
        self.stone_info[pos] = self.turn
        self.last = pos

    def check_winner(self) -> int:
        for color in (Board.BLACK, Board.WHITE):
            for line in self.line_range():
                stack = 0
                for space in line:
                    if space == color:
                        stack += 1
                    else:
                        if stack == 5:
                            print(f"{Board.color_dict[color]} WIN!")
                            return color
                        stack = 0
            if stack == 5:
                print(f"{Board.color_dict[color]} WIN!")
                return color
        return Board.BLANK

    def change_turn(self) -> None:
        self.turn *= -1

    def make_turn(self, color):
        assert color == 1 or color == -1, f"올바른 color값이 아닙니다. color는 1 또는 -1이어야 합니다. color type : {type(color)}, color value : {color}"
        self.turn = color

    def line_range(self) -> list:
        size = self.size
        for v in self.stone_info:
            yield v

        for v in self.stone_info.T:
            yield v

        for i in np.arange(0, size):
            yield self.stone_info[0:1 + i, size - (1 + i):size].diagonal()
        for i in np.arange(size - 2, -1, -1):
            yield self.stone_info.T[0:1 + i, size - (1 + i):size].diagonal()

        for i in np.arange(0, size):
            yield self.stone_info[:, ::-1][0:1 + i,
                                           size - (1 + i):size].diagonal()
        for i in np.arange(size - 2, -1, -1):
            yield self.stone_info.T[::-1][0:1 + i,
                                          size - (1 + i):size].diagonal()

    def print(self) -> None:
        visualized = self.stone_info.copy().astype(str)
        visualized[np.where(visualized == '-1')] = '○'
        visualized[np.where(visualized == '1')] = '●'
        visualized[np.where(visualized == '0')] = '`'
        # print(pd.DataFrame(visualized).T)
        for y in range(self.size):
            for x in range(self.size):
                print(visualized[x, y], end=' ')
            print()
        print()


class Grid:
    cell_size = 20

    def __init__(self, *pos: Vector2):
        if len(pos) == 2:
            self.input_coor(Vector2(pos[0], pos[1]))
        elif len(pos) == 1:
            self.input_coor(Vector2(pos[0]))

    def input_coor(self, pos: Vector2):
        pos = Vector2(pos)
        self.coor_pos = pos
        self.grid_pos = pos // Grid.cell_size
        return self

    def input_grid(self, pos: Vector2):
        pos = Vector2(pos)
        self.grid_pos = pos
        self.coor_pos = self.grid_pos * Grid.cell_size
        return self

    def __add__(self, other):
        pos = Grid()
        if hasattr(other, "grid_pos"):
            pos.input_coor(self.grid_pos + other.grid_pos)
        else:
            pos.input_coor(self.grid_pos + other)
        return pos

    def __repr__(self):
        return f"coor_pos{self.coor_pos}, grid_pos{self.grid_pos}"


class Ai:
    BLANK, BLACK, WHITE, BLOCKED = 0, 1, -1, 2
    color_dict = {
        BLANK : "BLANK",
        BLACK : "BLACK",
        WHITE : "WHITE",
        BLOCKED : "BLOCKED"
    }
    def decision(self):
        full_markers = self.judgment()
        self.color *= -1
        e_full_markers = self.judgment()
        self.color *= -1
        final = pd.DataFrame()
        final["my"] = full_markers.stack()
        final["e"] = e_full_markers.stack()

        def apply2(x):
            if x["e"] < 300 - self.penelty["empty"]:
                x["e"] *= self.penelty["combine"]
                x["e"] //= 2
                if self.leading_color[-self.color] == True:
                    x["my"] *= self.penelty["combine"]
            else:
                if self.leading_color[-self.color] == True:
                    x["my"] *= self.penelty["combine"]
                else:
                    if x["my"] >= x["e"]:
                        x["e"] *= self.penelty["combine"]
                    else:
                        x["my"] *= self.penelty["combine"]
            return int(x.sum())
                    
        self.final = final.apply(apply2, axis=1).unstack()
        coors = np.where(self.final == self.final.max().max())

        result = []
        for x, y in zip(*coors):
            result.append([x, y])
        return result

    def __init__(self, board, color) -> None:
        self.board : Board = board
        index = [i for i in range(self.board.size)]
        columns = [i for i in range(self.board.size)]
        self.full_markers = pd.DataFrame(0, index=index, columns=columns)
        self.color = color
        self.penelty = {
            "empty"   : 40,
            "blocked" : 50,
            "connect" : 60,
            "connect%": 0.2,
            "combine" : 0.25
        }
        self.leading_adv = 50
        self.leading_color = {
            1 : False,
            -1 : False
        }

    def print(self):        
        visualized = self.board.stone_info.copy().astype(str)
        visualized[visualized == '-1'] = '○'
        visualized[visualized == '1'] = '●'
        visualized[visualized == '0'] = '\''

        if self.color == 1:
            print("Black")
        else:
            print("White")
        # for y in range(self.board.size_of_board):
        #     for x in range(self.board.size_of_board):
        #         print(visualized[x, y], end=' ')
        #     print()
        print(pd.DataFrame(visualized).T)
        print()
            
        if self.color == Ai.BLACK:
            print("Black full markers")
        else:
            print("White full markers")
        print(self.full_markers.T)
        # print(self.full_markers.T.loc[6, 1])
        # print(self.full_markers.T.loc[6, 5])
        print()

    def judgment(self) -> pd.DataFrame:
        # 한 줄씩 따로 생각한다.
        # 각 줄마다 alpha, beta, charlie, delta 및 각각의 마킹에 원형, blanked, blocked의 변형 위치를 기록

        index = pd.MultiIndex.from_product([[i for i in range(self.board.size)]] * 2, names=['x', 'y'])
        columns = ['x', 'y', 'xy', '-xy']
        full_markers = pd.DataFrame(0, index=index, columns=columns)

        for i, (line, decide_index) in enumerate(self.line_range()):
            i %= self.board.size
            if line.size == 0:
                continue
            line_markers = self.marking(line)

            dir = ''
            for j in range(line_markers.shape[0]):

                if decide_index == 'x':
                    index = (i, j)
                    dir = 'x'
                elif decide_index == 'y':
                    index = (j, i)
                    dir = 'y'
                elif decide_index == 'xy1':
                    index = (j, self.board.size + j - (i + 1))
                    dir = 'xy'
                elif decide_index == 'xy2':
                    index = (i + j + 1, j)
                    dir = 'xy'
                elif decide_index == '-xy1':
                    index = (j, i - j)
                    dir = '-xy'
                elif decide_index == '-xy2':
                    index = (i + j + 1, self.board.size - (j + 1))
                    dir = '-xy'
                if line_markers.loc[j, "score level"] > 4 or line_markers.loc[j, "score level"] == 0:
                    continue

                # 260
                # 4스택 이상은 blank 및 페널티 판단 불필요
                if line_markers.loc[j, "score level"] >= 4:
                    if line_markers.loc[j, "empty level"] != 0:
                        continue
                    full_markers.loc[index, dir] += 100 * line_markers.loc[j, "score level"]
                    continue
                if self.leading_color[-self.color] == True:
                    if line_markers.loc[j, "score level"] >= 4:
                        if line_markers.loc[j, "empty level"] != 0:
                            continue
                        full_markers.loc[index, dir] += 100 * line_markers.loc[j, "score level"]
                    continue
                # 점수
                full_markers.loc[index, dir] += 100 * line_markers.loc[j, "score level"]
                # empty penelty
                full_markers.loc[index, dir] -= line_markers.loc[j, "empty level"] * self.penelty["empty"]
                # blocked penelty
                full_markers.loc[index, dir] -= int(line_markers.loc[j, "is blocked"]) * self.penelty["blocked"]


        def apply1(x):
            if np.count_nonzero(x) <= 1:
                return x.sum()
            else: # 가장 큰 값 제외하고 결합 페널티 부여
                leaders = x[x >= 300 - self.penelty["empty"]] # 주도권 공격에 추가점 부여
                if leaders.size != 0:
                    self.leading_color[self.color] = True
                else:
                    self.leading_color[self.color] = False
                mx = x[x == x.max()]
                idx = np.where(x == x.max())[0][0]
                x = pd.concat([x.iloc[:idx], x.iloc[idx + 1:]])
                x = x.apply(lambda i : max(i - self.penelty["connect"], int(self.penelty["connect%"] * i)))
                return x.sum() + mx[0] + leaders.size * self.leading_adv

        full_markers = full_markers.apply(apply1, axis=1).unstack()
    #     sns.heatmap(full_markers.T, cmap=sns.light_palette(
    # "gray", as_cmap=True), annot=True, fmt="d")
    #     plt.show()

        return full_markers

    def marking(self, line) -> pd.DataFrame:
        line = np.concatenate([line, [0]])
        marker = pd.Series({i:0 for i in range(line.size)})
        df = {
            "info" : line,
            "score level" : marker,
            "empty level" : marker,
            "is blocked" : False
        }
        line_markers = pd.DataFrame(df)

        for i in range(line_markers.shape[0]):
            if line_markers.loc[i, "info"] == -1 * self.color:
                for dir in [-1, 1]:
                    self.spreading_blocked(line_markers, i, dir)

        stack = 0
        for i in range(line_markers.shape[0]):
            if line_markers.loc[i, "info"] == self.color:
                stack += 1
            elif stack != 0:
                is_blocked = line_markers.loc[i-1, "is blocked"]
                self.spreading_level(line_markers, i, stack, is_blocked)
                stack = 0

        return line_markers.iloc[:-1].copy()

    def spreading_level(self, line_markers, i, stack, is_blocked, dir=0, blank_entry=0):
        # self.turn에 해당하는 칸 앞뒤 두칸씩 score level을 stack만큼 올립니다.
        # 이때 self.turn에 해당하는 칸과 score level을 올리는 칸 사이 거리만큼 empty level을 올립니다.
        # 또한 score level을 올리기 전 BLOCKED를 만나면 그 칸을 포함해 그 방향으로는 모든 level을 올리지 않으며
        # self.turn을 만나면 그 칸을 건너뛰고 다음 칸의 level을 올립니다.
        # ex) __OO_OX__에 대해 score level : 23OO3X__, empty level : 11OO_OX__

        for blank in range(2):
            idx = i + blank
            if dir == -1:
                break
            if blank_entry > blank:
                continue
            if i + blank >= line_markers.shape[0]:
                break
            if line_markers.loc[idx, "info"] == -1 * self.color:
                break
            if line_markers.loc[idx, "info"] == self.color:
                self.spreading_level(line_markers, i + 1, stack, is_blocked, dir=1, blank_entry=blank)
            line_markers.loc[idx, "score level"] += stack
            line_markers.loc[idx, "empty level"] += blank
            if is_blocked == True:
                line_markers.loc[idx, "is blocked"] = True

        for blank in range(2):
            idx = (i - 1 - stack) - blank
            if dir == 1:
                break
            if blank_entry > blank:
                continue
            if (i - 1 - stack) - blank < 0:
                break
            if line_markers.loc[idx, "info"] == -1 * self.color:
                break
            if line_markers.loc[idx, "info"] == self.color:
                self.spreading_level(line_markers, i - 1, stack, is_blocked, dir=-1, blank_entry=blank)
            line_markers.loc[idx, "empty level"] += blank
            line_markers.loc[idx, "score level"] += stack
            if is_blocked == True:
                line_markers.loc[idx, "is blocked"] = True

    def spreading_blocked(self, line_markers, i, dir):
        if i + dir < 0 or i + dir >= line_markers.shape[0]:
            return
        if line_markers.loc[i + dir, "info"] != self.color:
            return   
        line_markers.loc[i + dir, "is blocked"] = True
        self.spreading_blocked(line_markers, i + dir, dir)

    def line_range(self) -> np.ndarray:
        size = self.board.size
        for v in self.board.stone_info:
            yield v, 'x'
        
        for v in self.board.stone_info.T:
            yield v, 'y'

        for i in np.arange(0, size):
            yield self.board.stone_info[0:1+i, size-1-i:size].diagonal(), "xy1"
        for i in np.arange(size-2, -1, -1):
            yield self.board.stone_info.T[0:1+i, size-1-i:size].diagonal(), "xy2"
        yield np.array([]), ''
            
        for i in np.arange(0, size):
            yield self.board.stone_info[:,::-1][0:1+i, size-1-i:size].diagonal(), "-xy1"
        for i in np.arange(size-2, -1, -1):
            yield self.board.stone_info.T[::-1][0:1+i, size-1-i:size].diagonal(), "-xy2"
        yield np.array([]), ''

if __name__ == "__main__":
    main()
