import pygame, sys, time
from pygame.locals import QUIT
import numpy as np
from pygame.math import Vector2
from pygame.locals import MOUSEBUTTONDOWN
from random import choice
import pandas as pd

board_size = 20


def judgment() -> pd.DataFrame:
    # 한 줄씩 따로 생각한다.
    # 각 줄마다 alpha, beta, charlie, delta 및 각각의 마킹에 원형, blanked, blocked의 변형 위치를 기록
    
    index = pd.MultiIndex.from_product([[i for i in range(board_size)]] * 2, names=['x', 'y'])
    columns = ['x', 'y', 'xy', '-xy']
    full_markers = pd.DataFrame(0, index=index, columns=columns)

    for i, (line, decide_index) in enumerate(line_range()):
        i %= board_size
        if line.size == 0:
            continue
        line_markers = marking(line)

        dir = ''
        for j in range(line_markers.shape[0]):

            match decide_index:
                case 'x':
                    index = (i, j)
                    dir = 'x'
                case 'y':
                    index = (j, i)
                    dir = 'y'
                case 'xy1':
                    index = (j, board_size + j - (i + 1))
                    dir = 'xy'
                case 'xy2':
                    index = (i + j + 1, j)
                    dir = 'xy'
                case '-xy1':
                    index = (j, i - j)
                    dir = '-xy'
                case '-xy2':
                    index = (i + j + 1, board_size - (j + 1))
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
    
    return full_markers
