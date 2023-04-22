import pygame, sys
from pygame.locals import QUIT
import numpy as np
import pandas as pd
from pygame.math import Vector2
from pygame.locals import MOUSEBUTTONDOWN
from random import choice

from . import board, ai
from .grid import Grid
from . import screen_size, GRAY, BLACK, WHITE, BROWN, BGREEN, RED

def main():
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    board.put_stone((board.size // 2, board.size // 2))
    board.change_turn(board.WHITE)
    pygame.display.set_caption("Omok")

    while True:
        if board.turn == 1:
            selection = choice(ai.decision())
            board.put_stone(selection)
            board.change_turn()
        #else:
            #selection = choice(ai2.decision())
            #board.put_stone(selection)
            #board.change_turn()
            
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
            elif event.type == MOUSEBUTTONDOWN and board.turn == -1:
                board.put_stone(Grid(event.pos - Vector2(pos) - Vector2(edge)).grid_pos)
                board.change_turn()
        
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