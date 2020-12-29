import pygame

from settings import *


class Sprite(pygame.sprite.Sprite):
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
    img = pygame.image.load('sprites/floor.png')

    def __init__(self, col, row, x, y, *groups):
        super().__init__(Floor.img, col, row, x, y, *groups)
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
    img = pygame.image.load('sprites/gg_sprite.png')

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Player.img, col, row, x, y, *groups)
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.coins = 5
        self.flag = True

        # call_down для кнопки мыши, иначе несколько event за одно нажатие передаётся
        # тк игрок немоментально отпускает кнопку
        self.call_down = 300
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
        if self.level.is_player_turn:
            if args and args[0].type == pygame.MOUSEBUTTONDOWN:
                if self.last_click > self.call_down:
                    if args[0].button == 1:
                        cell = self.level.get_cell_for_first_layer(args[0].pos)
                        # SECOND_LAYER не учитываем
                        if cell is not None and abs(cell[0] - self.col) + abs(cell[1] - self.row) == 1 and not \
                                isinstance(self.level.sprites_arr[cell[1]][cell[0]][1], Mob):
                            self.level.sprites_arr[cell[1]][cell[0]][1] = self
                            self.level.sprites_arr[self.row][self.col][1] = None
                            self.move(cell)
                    elif args[0].button == 3:
                        # cell хранит позицию на поле, а starting_cell служит для эффекта падения клетки
                        cell = self.level.get_cell_for_first_layer(args[0].pos)
                        if cell is not None:
                            staring_cell = cell[0] - 4, cell[1] - 4
                            if cell is not None and self.coins > 0:
                                self.coins -= 1
                                Cage(self.level, *cell, *self.level.get_cords_for_block(staring_cell),
                                     self.level.all_sprites)
                    # на колёсико мыши конец хода игрока
                    if args[0].button == 2:
                        self.level.is_player_turn = False
                    self.last_click = 0
            else:
                self.last_click += 1000 // FPS

    def move(self, cell):
        self.change_col_and_row(cell)
        x, y = self.level.get_cords_for_player((self.drawing_col, self.drawing_row))
        self.change_cords(x, y)


class Cage(Sprite):
    image = pygame.image.load('sprites/cage.png')

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Cage.image, col, row, x, y, *groups)
        self.level = level
        self.velocity = 60

        # Для отслеживания падения клетки
        self.is_fallen = False

        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER

        self.margin_left = (SCALED_CUBE_WIDTH - self.rect.width) // 2

        self.top_rect_height = 60
        self.rect.x += self.margin_left
        self.top_rect_height = self.image.get_height() // 2

    def update(self, *args, **kwargs):
        self.rect.y -= self.top_rect_height

        if not self.is_fallen:
            self.rect.y += self.velocity // FPS
            for floor in self.level.floor:
                if floor.col == self.col and floor.row == self.row:
                    if self.rect.colliderect(floor.rect):
                        self.rect.y -= self.velocity // FPS
                        self.is_fallen = True
                    break

        else:
            trapped_character = self.level.sprites_arr[self.row][self.col][1]
            if trapped_character and trapped_character:
                # kill потом заменю на смену непрозрачности до 0, за определённое время
                self.level.sprites_arr[self.row][self.col][1] = None
                if trapped_character.__class__ == Mob:
                    self.level.player.coins += trapped_character.coins
                trapped_character.kill()
            self.kill()
        self.rect.y += self.top_rect_height


class Coin(Sprite):
    image = pygame.image.load('sprites/coin.png')

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Coin.image, col, row, x, y, *groups)
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.level = level

    def update(self, *args, **kwargs):
        if self.level.player.col == self.col and self.level.player.row == self.row:
            self.level.player.coins += 1
            self.kill()


class Mob(Sprite):
    # пока как заглушка спрайт гг
    img = pygame.image.load('sprites/gg_sprite.png')

    def __init__(self, level, col, row, x, y, *groups, coins=1, step=1):
        super().__init__(Mob.img, col, row, x, y, *groups)
        self.flag = False
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col
        self.drawing_row = row

        # self.coins отвечает за вознаграждение за поимку
        self.coins = coins
        self.step = step

    def update(self, *args, **kwargs):
        # стандартно просто идёт навстречу, позже можно использовать алгоритм Дейкстры
        # оставлю комменты, так что можно текст считать читаемым
        # функция min исключает вариант > step, а max исключает вариант при отрицательном перемещении
        if not self.level.is_player_turn:
            delta_row, delta_col = (max(min(self.level.player.row - self.row, self.step),
                                        -self.step) if self.level.player.row != self.row else 0,
                                    max(min(self.level.player.col - self.col, self.step),
                                        -self.step) if self.level.player.col != self.col else 0)
            if abs(delta_col) + abs(delta_row) > 1:
                delta_row = 0

            # далее проверяем получившиеся row и col, max исключает ход левее/ниже первой ячейки, а
            # min исключает ход правее/выше последней ячейк
            row = min(max(self.row + delta_row, 0), self.level.level_map.height - 1)
            col = min(max(self.col + delta_col, 0), self.level.level_map.width - 1)


            # в этом случае SECOND_LAYER не нужно учитывать
            self.level.sprites_arr[row][col][1] = self
            self.level.sprites_arr[self.row][self.col][1] = None
            block = self.level.sprites_arr[row][col][0]
            self.move((block.col, block.row))
            self.level.is_player_turn = True

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
