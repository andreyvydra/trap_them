from pygame.image import load
from settings import *
from sprites import *
from pygame.sprite import Group


class Map:
    def __init__(self, path_map):
        # не нужно указывать размеры поля, программа возьмёт его по размеру файла
        with open('map/map.txt') as map_for_init:
            map_for_init = map_for_init.readlines()
            self.height = len(map_for_init)
            self.width = len(map_for_init[0].split())

        self.path_map = path_map

        self.first_layer = []
        self.second_layer = []

        self.load_map()

    def load_map(self):
        # Подгружаем наши layers
        self.load_floor_layer()
        self.load_characters_layer()

    def load_floor_layer(self):
        with open(self.path_map + '/map.txt') as current_file:
            table = [row.split() for row in current_file]
            for row in range(self.height):
                row_list = []
                for col in range(self.width):
                    row_list.append(int(table[row][col]))
                self.first_layer.append(row_list)

    def load_characters_layer(self):
        with open(self.path_map + '/characters.txt') as current_file:
            table = [row.split() for row in current_file]
            for row in range(self.height):
                row_list = []
                for col in range(self.width):
                    row_list.append(int(table[row][col]))
                self.second_layer.append(row_list)


class Level:
    def __init__(self, level_map):
        self.level_map = level_map
        self.sprites_arr = [[[None, None] for _ in range(self.level_map.width)]
                            for i in range(self.level_map.height)]

        # Начальные x и y для отрисовки карты
        self.x = CENTER_POINT[0] - SCALED_CUBE_WIDTH // 2
        self.y = CENTER_POINT[1] - (self.level_map.height - 1) * SCALED_CUBE_HEIGHT // 4


        # Дельта смещения для отрисовки каждого блока относительно соседних
        self.delta_x = SCALED_CUBE_WIDTH // 2
        self.delta_y = SCALED_TOP_RECT_HEIGHT // 2

        self.all_sprites = Group()
        self.floor = Group()

        self.is_player_turn = True

        self.player = None

        self.font = pygame.font.Font(None, 50)

        self.load_sprites()

    def render(self, screen):
        self.all_sprites.draw(screen)
        self.render_coins(screen)

    def render_coins(self, screen):
        text = self.font.render(f"{self.player.coins}", True, (212, 175, 55))
        screen.blit(text, (20, 20))

    def update(self, *args, **kwargs):
        self.all_sprites.update(*args, **kwargs)

    def load_sprites(self):
        # Подгрузка спрайтов по отдельным layer, соответственно нашей карте
        self.load_sprites_from_first_layer()
        self.load_sprites_from_second_layer()

    def load_sprites_from_first_layer(self):
        for row in range(self.level_map.height):
            for col in range(self.level_map.width):
                x, y = self.get_cords_for_block((col, row))
                current_floor = Floor(col, row, x, y, self.all_sprites, self.floor)
                self.sprites_arr[row][col][0] = current_floor

    def load_sprites_from_second_layer(self):
        for row in range(self.level_map.height):
            for col in range(self.level_map.width):
                sprite_num = self.level_map.second_layer[row][col]
                if sprite_num != 0:
                    current_col, current_row = col + SECOND_LAYER, row + SECOND_LAYER
                    x, y = self.get_cords_for_player((current_col, current_row))
                    if sprite_num == 1:
                        self.player = Player(self, col, row, x, y, self.all_sprites)
                        # так как отрисовка героя требует смещения по row и col на -1, нужно добавить 1
                        self.sprites_arr[row][col][1] = self.player

                    elif sprite_num == 2:
                        new_mob = Mob(self, col, row, x, y, self.all_sprites)

                        self.sprites_arr[row][col][1] = new_mob
                    elif sprite_num == 20:
                        current_col, current_row = col + SECOND_LAYER, row + SECOND_LAYER
                        x, y = self.get_cords_for_block((current_col, current_row))
                        Coin(self, col, row, x, y, self.all_sprites)

    def get_cords_for_player(self, cell):
        # для корректировки спрайта игрока, нужно добавлять MARGIN_WIDTH_PLAYER и MARGIN_HEIGHT_PLAYER
        x, y = self.get_cords_for_block(cell)
        x += MARGIN_LEFT_PLAYER
        y += MARGIN_TOP_PLAYER
        return x, y

    def get_cords_for_block(self, cell):
        col, row = cell
        x = self.x + self.delta_x * (row - col)
        y = self.y + self.delta_y * (row + col)
        return x, y

    def get_cell_for_second_layer(self, cords):
        cell = self.get_cell_for_first_layer(cords)
        if cell is not None:
            return cell[0] + SECOND_LAYER, cell[1] + SECOND_LAYER

    def get_cell_for_first_layer(self, cords):
        for block in self.floor:
            if block.check_collide_top_rect(cords):
                # Не забыть прибавить SECOND_LAYER для корректной отрисовки
                return block.col, block.row
        return None
