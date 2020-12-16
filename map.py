import pytmx
from pygame.image import load

from settings import *
from sprites import *
from pygame.sprite import Group
from pygame import transform


class Map:
    def __init__(self, path):
        self.tmxdata = pytmx.load_pygame(path, pixelalpha=True)
        self.height = self.tmxdata.height
        self.width = self.tmxdata.width

        # Начальные x и y для отрисовки карты
        self.x = CENTER_POINT[0] - SCALED_CUBE_WIDTH // 2
        self.y = CENTER_POINT[1] - self.height * SCALED_CUBE_HEIGHT // 4 - SCALED_CUBE_HEIGHT // 4 + 100

        # Дельта смещения для отрисовки каждого спрайта относительно соседних
        self.delta_x = SCALED_TOP_RECT_WIDTH // 2
        self.delta_y = SCALED_TOP_RECT_HEIGHT // 2

        self.sprites = Group()
        self.floor = Group()
        self.load_sprites()

    def load_sprites(self):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for col, row, gid, in layer:
                    sprite = ti(gid)
                    if sprite is not None:
                        if layer.name == 'player':
                            # Для того, чтобы отображать игрока выше, чем землю
                            # надо уменьшить row и col на -1 или прибавить SECOND_LAYER
                            col += SECOND_LAYER
                            row += SECOND_LAYER
                            x, y = self.get_cords_for_player(col, row)
                            img = load('sprites/gg1.png')
                            Player(self, img, col, row, x, y, self.sprites)
                        else:
                            x, y = self.get_cords_for_block(col, row)
                            img = load('sprites/floor.png')
                            Floor(img, col, row, x, y, self.sprites, self.floor)

    def get_cords_for_player(self, col, row):
        x = self.x + self.delta_x * (col - row) + MARGIN_LEFT_PLAYER
        y = self.y + self.delta_y * (col + row) + MARGIN_TOP_PLAYER
        return x, y

    def get_cords_for_block(self, col, row):
        x = self.x + self.delta_x * (col - row)
        y = self.y + self.delta_y * (col + row)
        return x, y

    def get_cell_for_player(self, cords):
        for block in self.floor:
            if block.check_collide_top_rect(cords):
                # Не забыть прибавить SECOND_LAYER для корректной отрисовки
                return block.col + SECOND_LAYER, block.row + SECOND_LAYER
        return None

    def get_sprites(self):
        return self.sprites
