from .. import board
import numpy as np
import pandas as pd

BLANK, BLACK, WHITE, BLOCKED = 0, 1, -1, 2
color_dict = {
    BLANK : "BLANK",
    BLACK : "BLACK",
    WHITE : "WHITE",
    BLOCKED : "BLOCKED"
}

index = (i for i in range(board.size))
columns = (i for i in range(board.size))
full_markers = pd.DataFrame(0, index=index, columns=columns)
color = board.turn
penelty = {
    "empty"   : 40,
    "blocked" : 50,
    "connect" : 60,
    "connect%": 0.2,
    "combine" : 0.25
}
leading_adv = 50
leading_color = {
    BLACK : False,
    WHITE : False
}

final = pd.DataFrame()