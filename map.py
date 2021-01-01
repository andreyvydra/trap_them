import pygame
from settings import *
from sprites import *


class Map:
    def __init__(self, path_map, first_layer=None, second_layer=None):
        # не нужно указывать размеры поля, программа возьмёт его по размеру файла
        with open(path_map + '/map.txt') as map_for_init:
            map_for_init = map_for_init.readlines()
            self.height = len(map_for_init)
            self.width = len(map_for_init[0].split())

        self.path_map = path_map

        if first_layer is None:
            self.first_layer = []
        else:
            self.first_layer = first_layer

        if second_layer is None:
            self.second_layer = []
        else:
            self.second_layer = second_layer

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
                            for _ in range(self.level_map.height)]

        # Начальные x и y для отрисовки карты
        self.x = CENTER_POINT[0] - SCALED_CUBE_WIDTH // 2
        self.y = CENTER_POINT[1] - (self.level_map.height - 1) * SCALED_CUBE_HEIGHT // 4

        # Дельта смещения для отрисовки каждого блока относительно соседних
        self.delta_x = SCALED_CUBE_WIDTH // 2
        self.delta_y = SCALED_TOP_RECT_HEIGHT // 2

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.floor = pygame.sprite.Group()
        self.cages = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        self.is_player_turn = True
        self.game_over = False
        self.player = None

        self.font = pygame.font.Font(None, 50)

    def render(self, screen):
        self.floor.draw(screen)
        if not self.game_over:
            screen.blit(self.player.image, self.player.rect)
        self.enemies.draw(screen)
        self.coins.draw(screen)
        self.cages.draw(screen)
        self.render_number_of_coins(screen)
        self.render_players_moves(screen)

    def render_number_of_coins(self, screen):
        text = self.font.render(f"{self.player.coins}", True, (212, 175, 55))
        screen.blit(text, (20, 20))

    def render_players_moves(self, screen):
        radius = 7
        x = [-1, 0, 0, 1]
        y = [0, -1, 1, 0]
        for col, row in zip(x, y):
            if 0 <= self.player.col + col < self.level_map.width and \
                    0 <= self.player.row + row < self.level_map.height:
                if not isinstance(self.sprites_arr[self.player.row + row][self.player.col + col][1], Mob):
                    cur_x, cur_y = self.get_cords_for_movement_circles((self.player.col + col,
                                                                        self.player.row + row))
                    pygame.draw.circle(screen, (255, 255, 0), (cur_x, cur_y), radius)

    def update(self, *args, **kwargs):
        self.all_sprites.update(*args, **kwargs)

    def load_sprites(self):
        # Подгрузка спрайтов по отдельным layer, соответственно нашей карте
        self.load_sprites_from_first_layer()
        self.load_sprites_from_second_layer()

    def load_data(self, data):
        # Поочрёдно загрузить все типы объектов из даты сохранения
        self.load_floor(data['floor'])
        self.load_enemies(data['enemies'])
        self.load_coins(data['coins'])
        self.load_cages(data['cages'])

    def load_player(self, data):
        col, row = data['col'], data['row']
        x, y = data['x'], data['y']
        coins, steps = data['coins'], data['steps']
        self.player = Player(self, col, row, x, y, self.all_sprites, steps=steps, coins=coins)
        self.sprites_arr[row][col][1] = self.player

    def load_coins(self, coins):
        for coin in coins:
            col, row = coin['col'], coin['row']
            x, y = coin['x'], coin['y']
            coin = Coin(self, col, row, x, y,
                        self.all_sprites, self.coins)
            self.sprites_arr[row][col][0] = coin

    def load_cages(self, cages):
        for cage in cages:
            col, row = cage['col'], cage['row']
            x, y = cage['x'], cage['y']
            current_cages = Cage(self, col, row, x, y,
                                 self.all_sprites, self.floor)
            self.sprites_arr[row][col][0] = current_cages

    def load_enemies(self, enemies):
        for enemy in enemies:
            col, row = enemy['col'], enemy['row']
            x, y = enemy['x'], enemy['y']
            coins, step = enemy['coins'], enemy['step']
            new_mob = Mob(self, col, row, x, y,
                          self.all_sprites, self.enemies, coins=coins, step=step)
            self.sprites_arr[row][col][1] = new_mob

    def load_floor(self, floor):
        for block in floor:
            col, row = block['col'], block['row']
            x, y = block['x'], block['y']
            current_floor = Floor(col, row, x, y,
                                  self.all_sprites, self.floor)
            self.sprites_arr[row][col][0] = current_floor

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
                        self.sprites_arr[row][col][1] = self.player

                    elif sprite_num == 2:
                        new_mob = Mob(self, col, row, x, y, self.all_sprites, self.enemies)

                        self.sprites_arr[row][col][1] = new_mob
                    elif sprite_num == 20:
                        current_col, current_row = col + SECOND_LAYER, row + SECOND_LAYER
                        x, y = self.get_cords_for_block((current_col, current_row))
                        Coin(self, col, row, x, y, self.all_sprites, self.coins)

    def get_cords_for_movement_circles(self, cell):
        x, y = self.get_cords_for_block((cell[0], cell[1]))
        x += SCALED_TOP_RECT_WIDTH // 2
        y += SCALED_TOP_RECT_HEIGHT // 2
        return x, y

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
