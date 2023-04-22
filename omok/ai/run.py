from .. import ai, board
import numpy as np
import pandas as pd

def decision():
    full_markers = judgment()
    # full_markers = cythonfn.judgent()
    ai.color *= -1
    e_full_markers = judgment()
    ai.color *= -1
    ai.final["my"] = full_markers.stack()
    ai.final["e"] = e_full_markers.stack()

    def apply2(x):
        if x["e"] < 300 - ai.penelty["empty"]:
            x["e"] *= ai.penelty["combine"]
            x["e"] //= 2
            if ai.leading_color[-ai.color] == True:
                x["my"] *= ai.penelty["combine"]
        else:
            if ai.leading_color[-ai.color] == True:
                x["my"] *= ai.penelty["combine"]
            else:
                if x["my"] >= x["e"]:
                    x["e"] *= ai.penelty["combine"]
                else:
                    x["my"] *= ai.penelty["combine"]
        return int(x.sum())
                
    ai.final = ai.final.apply(apply2, axis=1).unstack()
    coors = np.where(ai.final == ai.final.max().max())

    result = []
    for x, y in zip(*coors):
        result.append([x, y])
                
    return result

def print():
    visualized = board.stone_info.copy().astype(str)
    visualized[visualized == '-1'] = '○'
    visualized[visualized == '1'] = '●'
    visualized[visualized == '0'] = '\''

    if ai.color == 1:
        print("Black")
    else:
        print("White")
    # for y in range(board.size_of_board):
    #     for x in range(board.size_of_board):
    #         print(visualized[x, y], end=' ')
    #     print()
    print(pd.DataFrame(visualized).T)
    print()
        
    if ai.color == ai.BLACK:
        print("Black full markers")
    else:
        print("White full markers")
    print(ai.full_markers.T)
    # print(ai.full_markers.T.loc[6, 1])
    # print(ai.full_markers.T.loc[6, 5])
    print()

def judgment() -> pd.DataFrame:
    # 한 줄씩 따로 생각한다.
    # 각 줄마다 alpha, beta, charlie, delta 및 각각의 마킹에 원형, blanked, blocked의 변형 위치를 기록
    
    index = pd.MultiIndex.from_product([[i for i in range(board.size)]] * 2, names=['x', 'y'])
    columns = ['x', 'y', 'xy', '-xy']
    full_markers = pd.DataFrame(0, index=index, columns=columns)

    for i, (line, decide_index) in enumerate(line_range()):
        i %= board.size
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
                    index = (j, board.size + j - (i + 1))
                    dir = 'xy'
                case 'xy2':
                    index = (i + j + 1, j)
                    dir = 'xy'
                case '-xy1':
                    index = (j, i - j)
                    dir = '-xy'
                case '-xy2':
                    index = (i + j + 1, board.size - (j + 1))
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
            if ai.leading_color[-ai.color] == True:
                if line_markers.loc[j, "score level"] >= 4:
                    if line_markers.loc[j, "empty level"] != 0:
                        continue
                    full_markers.loc[index, dir] += 100 * line_markers.loc[j, "score level"]
                continue
            # 점수
            full_markers.loc[index, dir] += 100 * line_markers.loc[j, "score level"]
            # empty penelty
            full_markers.loc[index, dir] -= line_markers.loc[j, "empty level"] * ai.penelty["empty"]
            # blocked penelty
            full_markers.loc[index, dir] -= int(line_markers.loc[j, "is blocked"]) * ai.penelty["blocked"]

    def apply1(x):
        if np.count_nonzero(x) <= 1:
            return x.sum()
        else: # 가장 큰 값 제외하고 결합 페널티 부여
            leaders = x[x >= 300 - ai.penelty["empty"]] # 주도권 공격에 추가점 부여
            if leaders.size != 0:
                ai.leading_color[ai.color] = True
            else:
                ai.leading_color[ai.color] = False
            mx = x[x == x.max()]
            idx = np.where(x == x.max())[0][0]
            x = pd.concat([x.iloc[:idx], x.iloc[idx + 1:]])
            x = x.apply(lambda i : max(i - ai.penelty["connect"], int(ai.penelty["connect%"] * i)))
            return x.sum() + mx[0] + leaders.size * ai.leading_adv

    full_markers = full_markers.apply(apply1, axis=1).unstack()
#     sns.heatmap(full_markers.T, cmap=sns.light_palette(
# "gray", as_cmap=True), annot=True, fmt="d")
#     plt.show()
    
    return full_markers

def marking(line) -> pd.DataFrame:
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
        if line_markers.loc[i, "info"] == -1 * ai.color:
            for dir in [-1, 1]:
                spreading_blocked(line_markers, i, dir)

    stack = 0
    for i in range(line_markers.shape[0]):
        if line_markers.loc[i, "info"] == ai.color:
            stack += 1
        elif stack != 0:
            is_blocked = line_markers.loc[i-1, "is blocked"]
            spreading_level(line_markers, i, stack, is_blocked)
            stack = 0

    return line_markers.iloc[:-1].copy()

def spreading_level(line_markers, i, stack, is_blocked, dir=0, blank_entry=0):
    # turn에 해당하는 칸 앞뒤 두칸씩 score level을 stack만큼 올립니다.
    # 이때 turn에 해당하는 칸과 score level을 올리는 칸 사이 거리만큼 empty level을 올립니다.
    # 또한 score level을 올리기 전 BLOCKED를 만나면 그 칸을 포함해 그 방향으로는 모든 level을 올리지 않으며
    # turn을 만나면 그 칸을 건너뛰고 다음 칸의 level을 올립니다.
    # ex) __OO_OX__에 대해 score level : 23OO3X__, empty level : 11OO_OX__

    for blank in range(2):
        idx = i + blank
        if dir == -1:
            break
        if blank_entry > blank:
            continue
        if i + blank >= line_markers.shape[0]:
            break
        if line_markers.loc[idx, "info"] == -1 * ai.color:
            break
        if line_markers.loc[idx, "info"] == ai.color:
            spreading_level(line_markers, i + 1, stack, is_blocked, dir=1, blank_entry=blank)
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
        if line_markers.loc[idx, "info"] == -1 * ai.color:
            break
        if line_markers.loc[idx, "info"] == ai.color:
            spreading_level(line_markers, i - 1, stack, is_blocked, dir=-1, blank_entry=blank)
        line_markers.loc[idx, "empty level"] += blank
        line_markers.loc[idx, "score level"] += stack
        if is_blocked == True:
            line_markers.loc[idx, "is blocked"] = True

def spreading_blocked(line_markers, i, dir):
    if i + dir < 0 or i + dir >= line_markers.shape[0]:
        return
    if line_markers.loc[i + dir, "info"] != ai.color:
        return   
    line_markers.loc[i + dir, "is blocked"] = True
    spreading_blocked(line_markers, i + dir, dir)

def line_range() -> np.ndarray:
    size = board.size
    for v in board.stone_info:
        yield v, 'x'
    
    for v in board.stone_info.T:
        yield v, 'y'

    for i in np.arange(0, size):
        yield board.stone_info[0:1+i, size-1-i:size].diagonal(), "xy1"
    for i in np.arange(size-2, -1, -1):
        yield board.stone_info.T[0:1+i, size-1-i:size].diagonal(), "xy2"
    yield np.array([]), ''
        
    for i in np.arange(0, size):
        yield board.stone_info[:,::-1][0:1+i, size-1-i:size].diagonal(), "-xy1"
    for i in np.arange(size-2, -1, -1):
        yield board.stone_info.T[::-1][0:1+i, size-1-i:size].diagonal(), "-xy2"
    yield np.array([]), ''

def change_turn(*colors):
    if len(colors) == 0:
        ai.color *= -1
    else:
        ai.color = colors[0]