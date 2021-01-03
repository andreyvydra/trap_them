from itertools import repeat

from settings import *
from sprites import *
from random import sample, randrange
import pygame


class Map:
    def __init__(self, path_map, difficulty=2, first_layer=None, second_layer=None):

        self.difficulty = difficulty
        self.path_map = path_map

        # не нужно указывать размеры поля, программа возьмёт его по размеру файла
        with open(path_map + '/map.txt') as map_for_init:
            map_for_init = map_for_init.readlines()
            self.height = len(map_for_init)
            self.width = len(map_for_init[0].split())

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

    def create_map(self):
        self.width = randrange(5, 10)
        self.height = randrange(5, 10)
        if self.difficulty == 1:
            num_characters = self.width * self.height // 5 + 1
            num_coins = self.width * self.height // 10
        else:
            num_characters = self.width * self.height // 4 + 1
            num_coins = self.width * self.height // 20
        # матрица, где для каждой ячейки хранится row и col
        matrix = [[0] * self.width for row in range(self.height)]
        result = []
        with open(self.path_map + '/map.txt', 'w') as current_file:
            for row in range(self.height):
                result.append(' '.join(str(i) for i in matrix[row]))
            current_file.writelines('\n'.join(result))
        characters = sample([(row, col) for row in range(self.height) for col in range(self.width)],
                            num_characters)
        coins = sample(characters, num_coins)
        for characters_row, characters_col in characters:
            matrix[characters_row][characters_col] = 2
        for coin_row, coin_col in coins:
            matrix[coin_row][coin_col] = 20
        # последние координаты будут использоваться для задания координаты игрока
        matrix[characters_row][characters_col] = 1
        result = []
        with open(self.path_map + '/characters.txt', 'w') as current_file:
            for row in range(self.height):
                result.append(' '.join(str(i) for i in matrix[row]))
            current_file.writelines('\n'.join(result))


class Level:
    def __init__(self, level_map, screen):
        self.level_map = level_map
        self.sprites_arr = [[[None, None] for _ in range(self.level_map.width)]
                            for _ in range(self.level_map.height)]
        self.screen = screen

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
        self.traps = pygame.sprite.Group()
        self.hearts = pygame.sprite.Group()

        self.is_player_turn = True
        self.game_over = False
        self.player = None

        self.font = pygame.font.Font(None, 50)
        # 1 - мирный, мобы просто идут на игрока,
        # 2 - нормальный, ищет кратчайший путь, но просто так на ловушки не попадается
        self.difficulty = self.level_map.difficulty

    def render(self):
        self.floor.draw(self.screen)
        self.traps.draw(self.screen)
        if not self.game_over:
            self.screen.blit(self.player.image, self.player.rect)
        self.enemies.draw(self.screen)
        self.coins.draw(self.screen)
        self.cages.draw(self.screen)
        self.render_number_of_coins()
        self.render_players_moves()
        self.render_health()
        self.render_mp()

    def render_mp(self):
        for i in range(self.player.max_steps):
            if i + 1 <= self.player.steps:
                pygame.draw.rect(self.screen, (15, 82, 186), (20 + (i * 60), 50, 60, 25))
            pygame.draw.rect(self.screen, (255, 255, 255), (20 + (i * 60), 50, 60, 25), 2)

    def render_number_of_coins(self):
        text = self.font.render(f"{self.player.coins}", True, (212, 175, 55))
        text_w = text.get_width()
        text_x = SCREEN_WIDTH - text_w - 20
        text_y = 20
        self.screen.blit(text, (text_x, text_y))

    def render_health(self):
        for i in range(self.player.max_health):
            if i + 1 <= self.player.health:
                pygame.draw.rect(self.screen, (98, 212, 77), (20 + (i * 60), 20, 60, 25))
            pygame.draw.rect(self.screen, (255, 255, 255), (20 + (i * 60), 20, 60, 25), 2)

    def render_players_moves(self):
        if self.player.alive() and self.player.selected:
            radius = 7
            x = [-1, 0, 0, 1]
            y = [0, -1, 1, 0]
            for col, row in zip(x, y):
                if 0 <= self.player.col + col < self.level_map.width and \
                        0 <= self.player.row + row < self.level_map.height:
                    if not isinstance(self.sprites_arr[self.player.row + row][self.player.col + col][1], Mob):
                        cur_x, cur_y = self.get_cords_for_movement_circles((self.player.col + col,
                                                                            self.player.row + row))
                        pygame.draw.circle(self.screen, (255, 255, 0), (cur_x, cur_y), radius)

    def update(self, *args, **kwargs):
        if self.is_player_turn:
            s = 0
            for sprite in self.all_sprites:
                s += 1 if sprite.__class__ == Player else 0
            print(s)
            self.all_sprites.update(*args, **kwargs)
        else:
            self.enemies.update()
            self.cages.update()
            self.traps.update()
            font = pygame.font.Font(None, 50)
            text = font.render("Your move!", True, (100, 255, 100))
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
            text_y = self.y - text.get_height() - HEIGHT_PLAYER - SCALED_CUBE_HEIGHT // 2
            self.screen.blit(text, (text_x, text_y))
            self.is_player_turn = True
            self.render()
            pygame.display.flip()
            ping_for_message = 10000000
            while ping_for_message != 0:
                ping_for_message -= 1

            self.screen.fill('#282828')
            self.is_player_turn = True
            self.player.steps = self.player.max_steps

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
            self.sprites_arr[row][col][1] = coin

    def load_cages(self, cages):
        for cage in cages:
            col, row = cage['col'], cage['row']
            x, y = cage['x'], cage['y']
            Cage(self, col, row, x, y,
                 self.all_sprites, self.floor)

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
