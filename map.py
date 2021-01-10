from itertools import repeat

from settings import *
from sprites import *
from random import sample, randrange, randint
import pygame


class Map:
    def __init__(self, path_map, difficulty=2, first_layer=None, second_layer=None):

        self.difficulty = difficulty
        self.path_map = path_map
        self.create_map()

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
            self.num_characters = self.width * self.height // 5 + 1
            num_coins = self.width * self.height // 10
        else:
            self.num_characters = self.width * self.height // 4 + 1
            num_coins = self.width * self.height // 20
        # матрица, где для каждой ячейки хранится row и col
        type_of_block = randint(0, 3)
        matrix = [[type_of_block] * self.width for row in range(self.height)]
        result = []
        with open(self.path_map + '/map.txt', 'w') as current_file:
            for row in range(self.height):
                result.append(' '.join(str(i) for i in matrix[row]))
            current_file.writelines('\n'.join(result))
        # так как остаются клетки со значением спрайта пола, нужно обнулить все клетки
        matrix = [[0] * self.width for row in range(self.height)]
        characters = sample([(row, col) for row in range(self.height) for col in range(self.width)],
                            self.num_characters)
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
        self.num_characters -= num_coins


class Level:
    def __init__(self, level_map, screen, level_number=1):
        self.level_map = level_map
        self.sprites_arr = [[[None, []] for _ in range(self.level_map.width)]
                            for _ in range(self.level_map.height)]
        self.screen = screen
        self.level_number = level_number
        self.alpha_channel_for_lvl_number = 255

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
        self.is_pressed_end_move_btn = False

        self.manager = None
        self.events = {'picked_up_coins': 0,
                       'locked_up_mafia': 0,
                       'health_down': 0,
                       'done_moves': 0,
                       'used_traps': 0,
                       'level_complete': 0}

        self.is_player_turn = True
        self.game_over = False
        self.player = None

        self.font = pygame.font.Font(None, 50)
        self.level_number_text = self.font.render(f'Level {str(self.level_number)}', True, (255, 255, 255))
        # 1 - мирный, мобы просто идут на игрока,
        # 2 - нормальный, ищет кратчайший путь, но просто так на ловушки не попадается
        self.difficulty = self.level_map.difficulty

    def render(self):

        self.floor.draw(self.screen)
        self.coins.draw(self.screen)
        self.traps.draw(self.screen)

        self.render_cage_cells()
        self.render_players_moves()

        cages = {(cage.col, cage.row): cage for cage in self.cages}

        for row_n, row in enumerate(self.sprites_arr):
            for col_n, cell in enumerate(row):
                enemies = cell[1]
                if len(enemies):
                    if enemies[0].__class__ == Player and not self.game_over:
                        self.screen.blit(enemies[0].image, enemies[0].rect)
                    elif enemies[0].__class__ != Player:
                        self.screen.blit(enemies[0].image, enemies[0].rect)
                        if (enemies[0].col, enemies[0].row) in cages:
                            cage = cages[(enemies[0].col, enemies[0].row)]
                            self.screen.blit(cage.image, cage.rect)
                    elif (row_n, col_n) in cages:
                        cage = cages[(enemies[0].col, enemies[0].row)]
                        self.screen.blit(cage.image, cage.rect)

        self.render_number_of_coins()
        self.render_health()
        self.render_num_characters()
        self.render_mp()
        self.manager.draw_ui(self.screen)
        if self.alpha_channel_for_lvl_number > 0:
            self.level_number_text.set_alpha(self.alpha_channel_for_lvl_number)
            self.alpha_channel_for_lvl_number -= 255 / FPS * 0.5
            x, y = CENTER_POINT[0] - self.level_number_text.get_width() // 2, 20
            self.screen.blit(self.level_number_text, (x, y))

    def render_mp(self):
        for i in range(self.player.max_steps):
            if i + 1 <= self.player.steps:
                pygame.draw.rect(self.screen, (15, 82, 186), (20 + (i * 60), 50, 60, 25))
            pygame.draw.rect(self.screen, (255, 255, 255), (20 + (i * 60), 50, 60, 25), 2)

    def render_cage_cells(self):
        if self.player.alive() and not self.player.selected and self.player.steps:
            x = [-1, -1, 0, -1, 0, 1, 1, 1]
            y = [-1, 0, -1, 1, 1, 0, 1, -1]
            radius = 7
            for col, row in zip(x, y):
                for distance_x in range(1, self.player.cage_distance + 1):
                    for distance_y in range(1, self.player.cage_distance + 1):
                        if 0 <= self.player.col + col * distance_x < self.level_map.width and \
                                0 <= self.player.row + row * distance_y < self.level_map.height and \
                                (col * distance_x) ** 2 + (row * distance_y) ** 2 > 2:
                                cur_x, cur_y = self.get_cords_for_movement_circles((self.player.col + col * distance_x,
                                                                                    self.player.row + row * distance_y))
                                pygame.draw.circle(self.screen, ('#00E5DF'), (cur_x, cur_y), radius)

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
        if self.player.alive() and self.player.selected and self.player.steps:
            radius = 7
            x = [-1, 0, 0, 1]
            y = [0, -1, 1, 0]
            for col, row in zip(x, y):
                if 0 <= self.player.col + col < self.level_map.width and \
                        0 <= self.player.row + row < self.level_map.height:
                    if len(self.sprites_arr[self.player.row + row][self.player.col + col][1]) == 0:
                        cur_x, cur_y = self.get_cords_for_movement_circles((self.player.col + col,
                                                                            self.player.row + row))
                        pygame.draw.circle(self.screen, (255, 255, 0), (cur_x, cur_y), radius)

    def render_num_characters(self):
        for row in range(self.level_map.height):
            for col in range(self.level_map.width):
                if len(self.sprites_arr[row][col][1]) > 1:
                    if self.sprites_arr[row][col][1][0].__class__ == Cage:
                        num = len(self.sprites_arr[row][col][1]) - 1
                    else:
                        num = len(self.sprites_arr[row][col][1])
                    if num > 1:
                        x, y = self.get_cords_for_block((col, row))
                        font = pygame.font.Font(None, 20)
                        text = font.render(f"{num}", True, (255, 255, 255))
                        text_w = text.get_width()
                        text_h = text.get_height()
                        text_x = x + SCALED_TOP_RECT_WIDTH // 2 - text_w // 2
                        text_y = y - SCALED_TOP_RECT_HEIGHT + text_h
                        pygame.draw.rect(self.screen, ('#282828'), (text_x - 5, text_y - 2,
                                                                    text_w + 10, text_h + 5))
                        pygame.draw.rect(self.screen, ('white'), (text_x - 5, text_y - 2,
                                                                  text_w + 10, text_h + 5), 1)
                        self.screen.blit(text, (text_x, text_y))

    def update(self, *args, **kwargs):
        if not any(filter(lambda x: x.alive(), self.enemies)):
            self.game_over = True
        td = args[1]
        self.manager.update(td)
        if self.is_player_turn:
            self.all_sprites.update(*args, **kwargs)
            if self.is_pressed_end_move_btn:
                self.is_pressed_end_move_btn = False
                self.is_player_turn = False
                font = pygame.font.Font(None, 50)
                text = font.render("Enemies' move!", True, (100, 255, 100))
                text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
                text_y = 20
                self.screen.blit(text, (text_x, text_y))
                self.render()
                pygame.display.flip()
                ping_for_message = 10000000
                while ping_for_message != 0:
                    ping_for_message -= 1

                self.screen.fill('#282828')
        else:
            self.enemies.update()
            self.cages.update()
            self.traps.update()
            self.player.steps = self.player.max_steps
            font = pygame.font.Font(None, 50)
            text = font.render("Your move!", True, (100, 255, 100))
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
            text_y = 20
            self.screen.blit(text, (text_x, text_y))
            self.is_player_turn = True
            self.render()
            pygame.display.flip()
            ping_for_message = 10000000
            while ping_for_message != 0:
                ping_for_message -= 1

            self.screen.fill('#282828')
            self.is_player_turn = True
            self.player.is_pressed_end_move_btn = False

    def get_events(self):
        return self.events

    def load_sprites(self):
        # Подгрузка спрайтов по отдельным layer, соответственно нашей карте
        self.load_sprites_from_first_layer()
        self.load_sprites_from_second_layer()

    def load_data(self, data):
        # Поочрёдно загрузить все типы объектов из даты сохранения
        level_data, number_of_level = data[0], data[1]
        self.level_number = number_of_level
        self.update_text_number_of_level()
        self.load_floor(level_data['floor'])
        self.load_enemies(level_data['enemies'])
        self.load_coins(level_data['coins'])
        self.load_cages(level_data['cages'])

    def load_player(self, data):
        col, row = data['col'], data['row']
        drawing_col, drawing_row = col + SECOND_LAYER, row + SECOND_LAYER
        x, y = self.get_cords_for_player((drawing_col, drawing_row))
        coins, steps = data['coins'], data['steps']
        max_steps = data['max_steps']
        health, max_health = data['health'], data['max_health']
        self.player = Player(self, col, row, x, y,
                             self.all_sprites, steps=steps,
                             coins=coins, health=health,
                             max_health=max_health, max_steps=max_steps)
        self.sprites_arr[row][col][1].append(self.player)

    def load_coins(self, coins):
        for coin in coins:
            col, row = coin['col'], coin['row']
            x, y = self.get_cords_for_block((col + SECOND_LAYER, row + SECOND_LAYER))
            x += (SCALED_CUBE_WIDTH - Coin.image.get_width()) // 2
            y += (SCALED_CUBE_HEIGHT - Coin.image.get_height()) - SCALED_TOP_RECT_HEIGHT // 2
            Coin(self, col, row, x, y,
                 self.all_sprites, self.coins)

    def load_cages(self, cages):
        for cage in cages:
            col, row = cage['col'], cage['row']
            drawing_col, drawing_row = col + SECOND_LAYER, row + SECOND_LAYER
            x, y = self.get_cords_for_block((drawing_col, drawing_row))
            Cage(self, col, row, x, y,
                 self.all_sprites, self.floor)

    def load_enemies(self, enemies):
        for enemy in enemies:
            col, row = enemy['col'], enemy['row']
            drawing_col, drawing_row = col + SECOND_LAYER, row + SECOND_LAYER
            x, y = self.get_cords_for_player((drawing_col, drawing_row))
            coins, step = enemy['coins'], enemy['step']
            new_mob = Mob(self, col, row, x, y,
                          self.all_sprites, self.enemies, coins=coins, step=step)
            self.sprites_arr[row][col][1].append(new_mob)

    def load_floor(self, floor):
        for block in floor:
            col, row = block['col'], block['row']
            x, y = self.get_cords_for_block((col, row))
            type_of_block = block['type_of_block']
            current_floor = Floor(col, row, x, y,
                                  self.all_sprites, self.floor, type_of_block=type_of_block)
            self.sprites_arr[row][col][0] = current_floor

    def update_text_number_of_level(self):
        self.level_number_text = self.font.render(f'Level {str(self.level_number)}',
                                                  True, (255, 255, 255))

    def load_sprites_from_first_layer(self):
        for row in range(self.level_map.height):
            for col in range(self.level_map.width):
                x, y = self.get_cords_for_block((col, row))
                current_floor = Floor(col, row, x, y, self.all_sprites, self.floor,
                                      type_of_block=self.level_map.first_layer[row][col])
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
                        self.sprites_arr[row][col][1].append(self.player)

                    elif sprite_num == 2:
                        new_mob = Mob(self, col, row, x, y, self.all_sprites, self.enemies)

                        self.sprites_arr[row][col][1].append(new_mob)
                    elif sprite_num == 20:
                        x, y = self.get_cords_for_block((col + SECOND_LAYER, row + SECOND_LAYER))
                        x += (SCALED_CUBE_WIDTH - Coin.image.get_width()) // 2
                        y += (SCALED_CUBE_HEIGHT - Coin.image.get_height()) - SCALED_TOP_RECT_HEIGHT // 2
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
