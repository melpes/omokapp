from pygame.math import Vector2

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
