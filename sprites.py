from pygame import sprite, Rect
from settings import *


class Sprite(sprite.Sprite):
    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(*groups)
        self.image = image
        self.row = row
        self.col = col
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(Sprite):
    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(image, col, row, x, y, *groups)


class Floor(Block):
    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(image, col, row, x, y, *groups)
        self.top_rect = Rect(x, y, SCALED_TOP_RECT_WIDTH,
                             SCALED_TOP_RECT_HEIGHT)

    def check_collide_top_rect(self, mouse_pos):
        x, y = abs(self.top_rect.centerx - mouse_pos[0]), abs(self.top_rect.centery - mouse_pos[1])
        b = self.top_rect.height / 2
        a = self.top_rect.width / 2
        # Если y <= -b / a * x + b, то точка лежит в верхнем прямоугольнике
        if y <= -b / a * x + b:
            return True
        return False


class Player(Sprite):
    def __init__(self, map, image, col, row, x, y, *groups):
        super().__init__(image, col, row, x, y, *groups)
        self.map = map
        self.on_target = False

    def change_cords(self, x, y, cell):
        self.col = cell[0]
        self.row = cell[1]
        self.rect.x = x
        self.rect.y = y

    def update(self, *args, **kwargs):
        mouse_buttons, cords = args
        if mouse_buttons[0]:
            cell = self.map.get_cell_for_player(cords)
            if cell is not None:
                x, y = self.map.get_cords_for_player(cell[0], cell[1])
                self.change_cords(x, y, cell)