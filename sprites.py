import pygame
from collections import deque
from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(*groups)
        self.image = image.copy()
        self.row = row
        self.col = col
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(Sprite):
    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(image, col, row, x, y, *groups)


class Floor(Block):
    images = {0: pygame.image.load('sprites/floor/floor-0-0.png'),
              1: pygame.image.load('sprites/floor/floor-1-0.png'),
              2: pygame.image.load('sprites/floor/floor-2-0.png'),
              3: pygame.image.load('sprites/floor/floor-3-0.png')
              }

    def __init__(self, col, row, x, y, *groups, type_of_block=0):
        super().__init__(Floor.images[type_of_block], col, row, x, y, *groups)
        self.type_of_block = type_of_block
        self.top_rect = pygame.rect.Rect(x, y, SCALED_TOP_RECT_WIDTH,
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
    img = pygame.image.load('sprites/gg_sprites.png')

    def __init__(self, level, col, row, x, y, *groups,
                 coins=5, steps=2, health=5, max_health=5, max_steps=2):
        super().__init__(Player.img, col, row, x, y, *groups)
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.coins = coins
        self.steps = steps
        self.max_steps = max_steps
        self.flag = True
        self.selected = False
        self.health = health
        self.max_health = max_health
        self.abilities = []
        self.is_pressed_end_move_btn = False
        # call_down для кнопки мыши, иначе несколько event за одно нажатие передаётся
        # тк игрок немоментально отпускает кнопку
        self.call_down = 200
        self.last_click = 0

    def change_cords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def change_col_and_row(self, cell):
        self.col = cell[0]
        self.row = cell[1]
        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER

    def update(self, *args, **kwargs):
        if self.steps == 0:
            self.selected = False
        if self.level.is_player_turn:
            if args and args[0].type == pygame.MOUSEBUTTONDOWN:
                if self.steps != 0:
                    if self.last_click > self.call_down:
                        if args[0].button == 1:
                            cell = self.level.get_cell_for_first_layer(args[0].pos)
                            if cell is not None and cell[0] == self.col and cell[1] == self.row:
                                self.selected = not self.selected
                            elif cell is not None:
                                mobs_count = len(list(filter(lambda x: isinstance(x, Mob),
                                                             self.level.sprites_arr[cell[1]][cell[0]][1])))
                                # SECOND_LAYER не учитываем
                                if cell is not None and abs(cell[0] - self.col) + abs(cell[1] - self.row) == 1 and \
                                        mobs_count == 0 and self.selected:
                                    self.level.sprites_arr[cell[1]][cell[0]][1].append(self)
                                    self.level.sprites_arr[self.row][self.col][1] = list(filter(lambda x: x != self,
                                                                                                [character for character
                                                                                                 in
                                                                                                 self.level.sprites_arr[
                                                                                                     self.row][
                                                                                                     self.col][1]]))
                                    self.steps -= 1
                                    self.move(cell)
                        elif args[0].button == 3 and not self.selected:
                            # cell хранит позицию на поле, а starting_cell служит для эффекта падения клетки
                            cell = self.level.get_cell_for_first_layer(args[0].pos)
                            if cell is not None:
                                staring_cell = cell[0] - 4, cell[1] - 4
                                if cell is not None and self.coins > 0:
                                    self.coins -= 1
                                    self.steps -= 1
                                    Cage(self.level, *cell, *self.level.get_cords_for_block(staring_cell),
                                         self.level.all_sprites, self.level.cages)

                self.last_click = 0

            elif self.is_pressed_end_move_btn:
                self.is_pressed_end_move_btn = False
                self.level.is_player_turn = False
                font = pygame.font.Font(None, 50)
                text = font.render("Enemies' move!", True, (100, 255, 100))
                text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
                text_y = 20
                self.level.screen.blit(text, (text_x, text_y))
                self.level.render()
                pygame.display.flip()
                ping_for_message = 10000000
                while ping_for_message != 0:
                    ping_for_message -= 1

                self.level.screen.fill('#282828')

            else:
                self.last_click += 1000 // FPS

    def move(self, cell):
        self.change_col_and_row(cell)
        x, y = self.level.get_cords_for_player((self.drawing_col, self.drawing_row))
        self.change_cords(x, y)


class Cage(Sprite):
    image = pygame.image.load('sprites/cage.png')
    trap_image = pygame.image.load('sprites/trap.png')

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Cage.image, col, row, x, y, *groups)
        self.level = level
        self.velocity = 60
        self.image = Cage.image

        # Для отслеживания падения клетки
        self.is_fallen = False

        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER

        self.margin_left = (SCALED_CUBE_WIDTH - self.rect.width) // 2

        self.top_rect_height = 60
        self.rect.x += self.margin_left
        self.top_rect_height = self.image.get_height() // 2

    def update(self, *args, **kwargs):
        if not self.is_fallen:
            self.level.cages.add(self)
            self.rect.y -= self.top_rect_height
            if self.level.sprites_arr[self.row][self.col][1]:
                self.rect.y += self.velocity // FPS
                floor = self.level.sprites_arr[self.row][self.col][0]
                if self.rect.colliderect(floor.rect):
                    self.rect.y -= self.velocity // FPS
                    self.is_fallen = True

            else:
                block = self.level.sprites_arr[self.row][self.col][0]
                self.rect.y = block.rect.y - self.image.get_height()
                self.is_fallen = True
                self.kill()
                self.level.traps.add(self)
                self.level.all_sprites.add(self)
                self.image = Cage.trap_image.copy()
                self.level.sprites_arr[self.row][self.col][1].append(self)
            self.rect.y += self.top_rect_height

        elif self.level.sprites_arr[self.row][self.col][1] and \
                (not isinstance(self.level.sprites_arr[self.row][self.col][1][0], Cage) or
                 len(self.level.sprites_arr[self.row][self.col][1]) > 1):
            self.image = Cage.image.copy()
            trapped_characters = self.level.sprites_arr[self.row][self.col][1]
            # для проигрывания анимации нужно выбрать один из спрайтов
            # все остальные просто убираются
            character_for_animation = None
            if trapped_characters:
                for trapped_character in trapped_characters:
                    if not isinstance(trapped_character, Cage):
                        if not character_for_animation:
                            character_for_animation = trapped_character
                            self.level.player.coins += character_for_animation.coins
                            continue
                        trapped_character.kill()
                        if isinstance(trapped_character, Mob):
                            self.level.player.coins += trapped_character.coins

                timer = 0
                alpha_channel = 255
                while alpha_channel > 0:
                    if timer % FPS == 0:
                        self.level.screen.fill('#282828')
                        alpha_channel -= 10
                        self.image.set_alpha(alpha_channel)
                        character_for_animation.image.set_alpha(alpha_channel)
                        self.level.render()
                        pygame.display.flip()
                    timer += 1
                character_for_animation.kill()
                self.kill()
                row, col = character_for_animation.row, character_for_animation.col
                self.level.sprites_arr[row][col][1] = []


class Coin(Sprite):
    image = pygame.image.load('sprites/coin.png')

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Coin.image, col, row, x, y, *groups)
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.level = level
        self.pick_up_sound = pygame.mixer.Sound('sounds/coin/pick_up.ogg')
        self.pick_up_sound.set_volume(0.05)

    def update(self, *args, **kwargs):
        if self.level.player.col == self.col and self.level.player.row == self.row:
            self.pick_up_sound.play()
            self.level.player.coins += 1
            self.kill()
        for enemy in self.level.enemies:
            if enemy.col == self.col and enemy.row == self.row:
                self.kill()


class Mob(Sprite):
    # пока как заглушка спрайт гг
    img = pygame.image.load('sprites/mob.png')

    def __init__(self, level, col, row, x, y, *groups, coins=1, step=1, damage=1):
        super().__init__(Mob.img, col, row, x, y, *groups)
        self.flag = False
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col
        self.drawing_row = row
        self.damage = damage

        # self.coins отвечает за вознаграждение за поимку
        self.coins = coins
        self.step = step

    def update(self, *args, **kwargs):
        # стандартно просто идёт навстречу, позже можно использовать алгоритм Дейкстры
        # функция min исключает вариант > step, а max исключает вариант при отрицательном перемещении
        path = []
        if not self.level.is_player_turn:
            self.target = self.level.player
            if self.level.level_map.difficulty == 2:
                path = self.voln(self.row, self.col, self.target.row, self.target.col)
                # пропускаем первую ячейку, откуда начинаетсся движение
                cells = path[1:1 + self.step]
            # если добраться до игрока невозможно мобы работают как на первом уровне
            if self.level.difficulty == 1 or not path:
                delta_row, delta_col = (max(min(self.target.row - self.row, self.step),
                                            -self.step) if self.target.row != self.row else 0,
                                        max(min(self.level.player.col - self.col, self.step),
                                            -self.step) if self.level.player.col != self.col else 0)

                # также на мирном уровне сложности delta_row обнуляется, при разнице в обеих координатах
                if abs(delta_col) + abs(delta_row) > 1:
                    delta_row = 0

                # далее проверяем получившиеся row и col, max исключает ход леве9е/ниже первой ячейки, а
                # min исключает ход правее/выше последней ячейк
                row = min(max(self.row + delta_row, 0), self.level.level_map.height - 1)
                col = min(max(self.col + delta_col, 0), self.level.level_map.width - 1)

                cells = [(col, row)]

            self.level.sprites_arr[self.row][self.col][1] = list(filter(lambda x: x != self,
                                                                        [character for character in
                                                                         self.level.sprites_arr[self.row][self.col][
                                                                             1]]))
            for cell in cells:
                self.move(cell)

            # в этом случае SECOND_LAYER не нужно учитывать
            self.level.sprites_arr[self.row][self.col][1].append(self)
            block = self.level.sprites_arr[self.row][self.col][0]
            if (block.col == self.level.player.col
                    and block.row == self.level.player.row):
                self.level.player.health = max(self.level.player.health - self.damage, 0)
                if self.level.player.health == 0:
                    self.level.game_over = True
                self.kill()
                self.level.sprites_arr[self.row][self.col][1] = list(filter(lambda x: x != self,
                                                                            [character for character in
                                                                             self.level.sprites_arr[self.row][self.col][
                                                                                 1]]))
                return

    def voln(self, x, y, x1, y1):
        path = []
        board = []
        for row in range(self.level.level_map.height):
            board.append([])
            for col in range(self.level.level_map.width):
                board[row].append([-1, (row, col)] if self.level.sprites_arr[row][col][1] and
                                                      isinstance(self.level.sprites_arr[row][col][1][0], Cage) else
                                  [1000, (row, col)])
            # так как у нас координаты заданы по-другому в загрузке карты
            board[row] = board[row]
        queue = deque()
        queue.append((x, y))
        board[x][y][0] = 1
        self.get_to_all_neighbors(x, y, board, queue)
        end_cur = board[x1][y1][0]
        while 0 < end_cur < 1000:
            # использем связный список, чтобы находить, откуда мы пришли в ячейку
            path.append((y1, x1))
            x1, y1 = board[x1][y1][1]
            end_cur -= 1
        return path[::-1]

    def get_to_all_neighbors(self, row, col, board, queue):
        # пока работает за O(n^4)
        # board - список, [расстояние от моба, (координаты предыдущей ячейки)]
        if board[row][col][0] == -1 or row == self.level.level_map.height - 1 and \
                col == self.level.level_map.width - 1:
            return board
        delta_x = [-1, 0, 0, 1]
        delta_y = [0, -1, 1, 0]
        while queue:
            previous = row, col
            row, col = queue.pop()
            for delta_row, delta_col in zip(delta_y, delta_x):
                if 0 <= delta_row + row < self.level.level_map.height and \
                        0 <= delta_col + col < self.level.level_map.width:
                    if board[row + delta_row][col + delta_col][0] > board[row][col][0] + 1 and \
                            (board[row + delta_row][col + delta_col][0] != -1):
                        # сохраняем предыдущую ячейку, вместе с расстоянием
                        board[row + delta_row][col + delta_col] = [board[row][col][0] + 1,
                                                                   (row, col)]
                        queue.append((row + delta_row, col + delta_col))
        return board

    def move(self, cell):
        self.change_col_and_row(cell)
        x, y = self.level.get_cords_for_player((self.drawing_col, self.drawing_row))
        self.change_cords(x, y)

    def change_cords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def change_col_and_row(self, cell):
        self.col = cell[0]
        self.row = cell[1]
        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER
