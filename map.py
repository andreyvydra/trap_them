from pygame.image import load
from settings import *
from sprites import *
from pygame.sprite import Group


class Map:
    def __init__(self, delta_x=SCALED_CUBE_WIDTH // 2, delta_y=30):
        # не нужно указывать размеры поля, программа возьмёт его по размеру файла
        with open('map/map.txt') as map_for_init:
            map_for_init = map_for_init.readlines()
            self.height = len(map_for_init)
            self.width = len(map_for_init[0].split())
        self.board = [[0] * self.width for _ in range(self.height)]

        # Начальные x и y для отрисовки карты
        self.x = CENTER_POINT[0] - SCALED_CUBE_WIDTH // 2
        self.y = CENTER_POINT[1] - self.height * SCALED_CUBE_HEIGHT // 4 - SCALED_CUBE_HEIGHT // 4

        # Дельта смещения для отрисовки каждого блока относительно соседних
        self.delta_x = delta_x
        self.delta_y = delta_y

        self.sprites = []
        self.floor = Group()
        self.load_sprites()

    def load_sprites(self):
        # как в куче метод нахождения родителей с помощью mod
        # модом для слоя с персонажами является
        current_layer = 0
        for file in ['map/map.txt', 'map/characters.txt']:
            with open(file) as current_file:
                # перевод в список значений для каждой клетки
                table = [row.split() for row in current_file]
                for row in range(self.height):
                    for col in range(self.width):
                        sprite = table[row][col]
                        if current_layer == 1:
                            if int(sprite) == 1:
                                # Для того, чтобы отображать игрока выше, чем землю
                                # надо уменьшить row и col на -1 или прибавить SECOND_LAYER
                                col += SECOND_LAYER
                                row += SECOND_LAYER
                                x = self.x + self.delta_x * (col - row)
                                y = self.y + self.delta_y * (col + row)
                                img = load('sprites/gg_sprite.png')
                                sprite = Player(self, img, row, col, x + MARGIN_LEFT_PLAYER,
                                                y + MARGIN_TOP_PLAYER)
                        else:
                            # при добавлении других спрайтов поля нужно дописать условия
                            img = load('sprites/floor.png')
                            x = self.x + self.delta_x * (col - row)
                            y = self.y + self.delta_y * (col + row)
                            sprite = Floor(img, row, col, x, y)
                            self.floor.add(sprite)
                        if not type(sprite) == str:
                            # проверка, что это спрайт
                            self.sprites.append(sprite)
                current_layer += 1

    def get_cords_for_player(self, col, row):
        # для корректировки спрайта игрока, нужно добавлять MARGIN_WIDTH_PLAYER
        x = self.x + self.delta_x * (row - col) + MARGIN_LEFT_PLAYER
        y = self.y + self.delta_y * (row + col) + MARGIN_TOP_PLAYER
        return x, y

    def get_cell_for_player(self, cords):
        for block in self.floor:
            if block.check_collide_top_rect(cords):
                # Не забыть прибавить SECOND_LAYER для корректной отрисовки
                return block.col + SECOND_LAYER, block.row + SECOND_LAYER
        return None

    def get_sprites(self):
        return self.sprites