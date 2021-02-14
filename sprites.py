import sys

import pygame
from collections import deque
from settings import *
from tools import *


class Sprite(pygame.sprite.Sprite):
    """
    Класс спрайтов.

    Attributes:
        image(pygame.image): изображение спрайта
        row(int): ряд спрайта
        col(int): столбик спрайта
        rect(pygame.rect.Rect): прямоугольник, на котором располагается спрайт
    """

    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(*groups)
        self.image = image.copy()
        self.row = row
        self.col = col
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Block(Sprite):
    """Класс блоков."""

    def __init__(self, image, col, row, x, y, *groups):
        super().__init__(image, col, row, x, y, *groups)


class Floor(Block):
    """
    Класс спрайтов пола.

    Attributes:
        images(dict): словарь значений для каждого числа поля
        type_of_block(int): номер блока в словаре
        top_rect(pygame.rect.Rect): верхний прямоугольник спрайта пола

    Methods:
        check_collide_rop_rect(mouse_pos): проверка позиции мыши
         на пересечение с верхним прямоугольником спрайта пола
    """
    print(make_path('sprites/floor/floor-0-0.png'))
    images = {
        0: pygame.image.load(make_path('sprites/floor/floor-0-0.png')),
        1: pygame.image.load(make_path('sprites/floor/floor-1-0.png')),
        2: pygame.image.load(make_path('sprites/floor/floor-2-0.png')),
        3: pygame.image.load(make_path('sprites/floor/floor-3-0.png'))
    }

    def __init__(self, col, row, x, y, *groups, type_of_block=0):
        super().__init__(Floor.images[type_of_block], col, row, x, y, *groups)
        self.type_of_block = type_of_block
        self.top_rect = pygame.rect.Rect(x, y, SCALED_TOP_RECT_WIDTH,
                                         SCALED_TOP_RECT_HEIGHT)

    def check_collide_top_rect(self, mouse_pos):
        """
        Проверка позиции мыши на
         пересечение с верхним прямоугольником спрайта пола.

        Arguments:
            mouse_pos: позиция мыши

        Return:
            result(bool): возвращает True,
             если точка лежит в верхнем прямоугольнике, иначе False
        """

        x, y = abs(self.top_rect.centerx - mouse_pos[0]), \
               abs(self.top_rect.centery - mouse_pos[1])
        b = self.top_rect.height / 2
        a = self.top_rect.width / 2
        # Если y <= -b / a * x + b, то точка лежит в верхнем прямоугольнике
        if y <= -b / a * x + b:
            return True
        return False


class Player(Sprite):
    """
    Класс игрока.

    Attributes:
        img(pygame.image): спрайт игрока
        level(Level): текущий уровень
        drawing_row(int): ряд для рисования игрока на поле
        drawing_col(int): столбец для рисования игрока на поле
        coins(int): текущее количество монет
        steps(int): количество отсавшихся действий
        max_steps(int): максимальное количество действий
        selected(bool): флаг, показывающий выбран ли герой
        health(int): количество оставшегося здоровья
        max_health(int): максимальное количество единиц здоровья
        call_down(int): ограничение на количество обрабатываемых нажатий
        last_click(int): последнее нажатие мыши
        cage_distance(int): максимальное расстояние,
         на которое можно ставить клетке

    Methods:
        change_cords(x, y): изменить координаты спрайта
        change_col_and_row(cell): изменить col, row игрока
        update(*args, **kwargs): update игрока
        move(cell): перемещение в клетку cell
    """

    img = pygame.image.load(make_path('sprites/gg_sprites.png'))

    def __init__(self, level, col, row, x, y, *groups,
                 coins=5, steps=2, health=5, max_health=5, max_steps=2,
                 cage_distance=2):
        super().__init__(Player.img, col, row, x, y, *groups)
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.coins = coins
        self.steps = steps
        self.max_steps = max_steps
        self.selected = False
        self.health = health
        self.max_health = max_health
        # call_down для кнопки мыши,
        # иначе несколько event за одно нажатие передаётся
        # тк игрок немоментально отпускает кнопку
        self.call_down = 100
        self.last_click = 0
        self.cage_distance = cage_distance

    def change_cords(self, x, y):
        """
        Изменение координат спрайта.

        Arguments:
            x: координата по x
            y: координата по y
        """

        self.rect.x = x
        self.rect.y = y

    def change_col_and_row(self, cell):
        """
        Изменяет col, row, drawing_col, drawing_row спрайта.

        Arguments:
            cell(tuple(int, int)): кортеж с координатами x и y
        """

        self.col = cell[0]
        self.row = cell[1]
        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER

    def update(self, *args, **kwargs):
        """Update спрайта игрока."""

        if self.steps == 0:
            self.selected = False
        if self.level.is_player_turn:
            if args and args[0].type == pygame.MOUSEBUTTONDOWN:
                if self.steps != 0:
                    if self.last_click > self.call_down:
                        if args[0].button == 1:
                            cell = \
                                self.level.get_cell_for_first_layer(args[0].pos)
                            if cell is not None and \
                                    cell[0] == self.col and \
                                    cell[1] == self.row:
                                self.selected = not self.selected
                            elif cell is not None:
                                mobs_count = len(list(filter(
                                    lambda x: isinstance(x, Mob),
                                    self.level.sprites_arr[cell[1]]
                                    [cell[0]][1])))
                                # SECOND_LAYER не учитываем
                                if cell is not None and \
                                        abs(cell[0] - self.col) \
                                        + abs(cell[1] - self.row) == 1 and \
                                        mobs_count == 0 and self.selected:
                                    s_arr = self.level.sprites_arr
                                    s_arr[cell[1]][cell[0]][1].append(self)
                                    s_arr[self.row][self.col][1] = \
                                        list(filter(lambda x: x != self,
                                                    [character for character in
                                                     s_arr[self.row][self.col][1]]))
                                    self.steps -= 1
                                    self.move(cell)
                                    self.level.events['done_moves'] += 1

                        elif args[0].button == 3 and not self.selected:
                            # cell хранит позицию на поле,
                            # а starting_cell для эффекта падения клетки
                            cell = \
                                self.level.get_cell_for_first_layer(args[0].pos)
                            # расстояние рассматривается по количеству кругов,
                            # поэтому учитываем диагонали
                            row_check = (cell[1] - self.row) ** 2
                            col_check = (cell[0] - self.col) ** 2
                            check_cage_dist = 2 * self.cage_distance ** 2
                            chosen_cell = \
                                self.level.sprites_arr[cell[1]][cell[0]]
                            if (cell is not None and
                                    row_check + col_check <= check_cage_dist and
                                    row_check + col_check > 2 and
                                    all(list(map(lambda x: not isinstance(x, Cage),
                                                 chosen_cell[1])))):
                                staring_cell = cell[0] - 4, cell[1] - 4
                                if self.coins > 0:
                                    self.coins -= 1
                                    self.steps -= 1
                                    Cage(self.level, *cell,
                                         *self.level.get_cords_for_block(staring_cell),
                                         self.level.all_sprites,
                                         self.level.cages)
                                    self.level.events['used_traps'] += 1

                self.last_click = 0

            else:
                self.last_click += 1000 // FPS

    def move(self, cell):
        """
        Перемещение спрайта игрока.

        Arguments:
            cell(tuple(int, int)): кортеж с координатами клетки
        """
        self.change_col_and_row(cell)
        x, y = self.level.get_cords_for_player((self.drawing_col,
                                                self.drawing_row))
        self.change_cords(x, y)


class Cage(Sprite):
    """
    Класс клетки.

    Attributes:
        image(pygame.image): изображение клетки
        level(Level): текущий уровень
        velocity(int): скорость падение клетки
        is_fallen(bool): проверка упала ли клетка
        drawing_col(int): столбец для рисования клетки
        drawing_row(int): ряд для рисования клетки
        margin_left(int): отступ для клетки для помещения в центр
        top_rect_height(int): верхний прямоугольник изображения клетки

    Methods:
        update(): update клетки
    """

    image = pygame.image.load(make_path('sprites/cage.png'))
    trap_image = pygame.image.load(make_path('sprites/trap.png'))

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Cage.image, col, row, x, y, *groups)
        self.level = level

        # Для подстроховки)
        self.velocity = 60
        self.image = Cage.image

        # Служит для подсчёта остатоков при делении нацело при перемещении
        self.delta_remainder = 0

        # Для отслеживания падения клетки
        self.is_fallen = False

        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER

        self.margin_left = (SCALED_CUBE_WIDTH - self.rect.width) // 2

        self.rect.x += self.margin_left
        self.top_rect_height = self.image.get_height() // 2

    def update(self, *args, **kwargs):
        """Update спрайта клетки"""
        fps = args[2]
        trapped_characters_cell = \
            self.level.sprites_arr[self.row][self.col]
        if not self.is_fallen:
            self.level.cages.add(self)
            self.rect.y -= self.top_rect_height
            if trapped_characters_cell[1]:

                delta = self.velocity / fps
                # Остатки от деления будут сохраняться для того,
                # в дальнейшем всё коррекнто отрисовывалось
                self.delta_remainder += delta - round(delta)

                if self.delta_remainder >= 1:
                    self.rect.y += round(delta) + self.delta_remainder
                    self.delta_remainder -= round(self.delta_remainder)
                elif 0 <= round(self.delta_remainder + delta) <= 1:
                    # Здесь приходится 'взять взаймы' у delta_remainder
                    # если он не дотягивает до одного пикселя, то он
                    # примет отрицательное значение
                    self.rect.y += 1
                    self.delta_remainder = self.delta_remainder + delta -\
                                           round(self.delta_remainder + delta)
                else:
                    self.rect.y += round(delta)

                floor = trapped_characters_cell[0]
                if self.rect.bottomright[1] >= floor.rect.y:
                    self.rect.y -= round(delta)
                    self.is_fallen = True

            else:
                block = trapped_characters_cell[0]
                self.rect.y = block.rect.y - self.image.get_height()
                self.is_fallen = True
                self.kill()
                self.level.traps.add(self)
                self.level.all_sprites.add(self)
                self.image = Cage.trap_image.copy()
                trapped_characters_cell[1].append(self)
            self.rect.y += self.top_rect_height

        elif (trapped_characters_cell[1] and
              (not isinstance(trapped_characters_cell[1][0], Cage) or
               len(trapped_characters_cell[1]) > 1)):

            self.image = Cage.image.copy()
            # для дальнейшей прорисовки нужно убрать клетку из массива
            self.level.sprites_arr[self.row][self.col][1] = \
                list(filter(lambda x: not isinstance(x, Cage),
                            self.level.sprites_arr[self.row][self.col][1]))
            trapped_characters = self.level.sprites_arr[self.row][self.col][1]
            # для проигрывания анимации нужно выбрать один из спрайтов
            # все остальные просто убираются
            character_for_animation = None
            if trapped_characters and len(trapped_characters) >= 1:
                for trapped_character in trapped_characters:
                    # для проигрывания анимации нужно выбрать один из спрайтов
                    # все остальные просто убираются
                    if not isinstance(trapped_character, Cage):
                        # выбираем для анимации один спрайт
                        if not character_for_animation:
                            character_for_animation = trapped_character
                            self.level.player.coins += \
                                character_for_animation.coins
                            continue
                        # остальные спрайты просто убиваем
                        trapped_character.kill()
                        if isinstance(trapped_character, Mob):
                            self.level.player.coins += trapped_character.coins
                            self.level.events['locked_up_mafia'] += 1

                timer = 0
                alpha_channel = 255
                # анимация посмтепенного исчезновения
                while alpha_channel > 0:
                    if timer % FPS == 0:
                        self.level.screen.fill('#282828')
                        alpha_channel -= 10
                        self.image.set_alpha(alpha_channel)
                        character_for_animation.image.set_alpha(alpha_channel)
                        self.level.render()
                        pygame.display.flip()
                    timer += 1
                row, col = character_for_animation.row, \
                           character_for_animation.col
                self.level.sprites_arr[row][col][1] = []
                # так как игрок может быть один на клетке,
                # можно проверять только спрайт для анимации
                if isinstance(character_for_animation, Player):
                    self.level.player.health = 0
                    self.level.game_over = True
                else:
                    self.level.events['locked_up_mafia'] += 1

                character_for_animation.kill()
                self.kill()


class Coin(Sprite):
    """
    Класс монет.

    Attributes:
        image(pygame.image): изображение монеты
        drawing_col(int): столбец для рисования монеты
        drawing_row(int): ряд для рисования монеты
        level(Level): текущий уровень
        pick_up_sound(pygame.mixer,Sound): звук получения монеты

    Methods:
        update(): update спрайта монеты
    """
    image = pygame.image.load(make_path('sprites/coin.png'))

    def __init__(self, level, col, row, x, y, *groups):
        super().__init__(Coin.image, col, row, x, y, *groups)
        self.drawing_col = col + SECOND_LAYER
        self.drawing_row = row + SECOND_LAYER
        self.level = level
        self.pick_up_sound = pygame.mixer\
            .Sound(make_path('sounds/coin/pick_up.ogg'))
        self.pick_up_sound.set_volume(0.05)

    def update(self, *args, **kwargs):
        """Update спрайта монеты"""
        if self.level.player.col == self.col and \
                self.level.player.row == self.row:
            self.pick_up_sound.play()
            self.level.player.coins += 1
            self.level.events['picked_up_coins'] += 1
            self.kill()
        for enemy in self.level.enemies:
            if enemy.col == self.col and enemy.row == self.row:
                self.kill()


class Mob(Sprite):
    """
    Класс мобов.

    Attributes:
        img(pygame.image): изобрвжение спрайта моба
        level(Level): текущий уровень
        drawing_col(int): столбец для рисования спрайта
        drawing_row(int): ряд для рисования спрайта
        damage(int): урон, который наносит моб
        coins(int): количество монет за поимку моба
        step(int): количество шагов
    """
    img = pygame.image.load(make_path('sprites/mob.png'))
    sound_of_move = pygame.mixer.Sound(make_path('sounds/mob/move.ogg'))
    sound_of_hit = pygame.mixer.Sound(make_path('sounds/mob/hit.ogg'))
    sound_of_hit.set_volume(0.2)

    def __init__(self, level, col, row, x, y, *groups,
                 coins=1, step=1, damage=1):
        super().__init__(Mob.img, col, row, x, y, *groups)
        self.level = level
        # col_drawing используется, как переменная для отрисовки
        self.drawing_col = col
        self.drawing_row = row
        self.damage = damage
        self.before_col = None
        self.before_row = None

        # self.coins отвечает за вознаграждение за поимку
        self.coins = coins
        self.step = step

    def update(self, *args, **kwargs):
        """Update мобов"""
        path = []
        if not self.level.ai_turn_is_ended and self.level.is_enemies_turn:
            self.target = self.level.player
            if self.level.level_map.difficulty == 2:
                path = self.voln(self.row, self.col,
                                 self.target.row, self.target.col)
                # пропускаем первую ячейку, откуда начинаетсся движение
                cells = path[1:1 + self.step]
            # если добраться до игрока невозможно,
            # мобы работают как на первом уровне
            # функция min исключает вариант > step,
            # а max исключает вариант при отрицательном перемещении
            # min исключает ход правее/выше последней ячейк
            if self.level.difficulty == 1 or not path:
                delta_row = (max(
                    min(self.target.row - self.row, self.step), -self.step)
                             if self.target.row != self.row else 0)
                delta_col = (max(
                    min(self.target.col - self.col, self.step), -self.step)
                             if self.target.col != self.col else 0)

                # также на мирном уровне сложности delta_row обнуляется,
                # при разнице в обеих координатах
                if abs(delta_col) + abs(delta_row) > 1:
                    delta_row = 0

                new_row = self.row + delta_row
                new_col = self.col + delta_col

                # далее проверяем получившиеся row и col,
                # max исключает ход левее/ниже первой ячейки, а
                row = min(
                    max(new_row, 0), self.level.level_map.height - 1)
                col = min(
                    max(new_col, 0), self.level.level_map.width - 1)

                cells = [(col, row)]

            for cell in cells:
                self.before_col = cell[0]
                self.before_row = cell[1]

            # в этом случае SECOND_LAYER не нужно учитывать
            new_cell = self.level.sprites_arr[cell[1]][cell[0]]
            block = new_cell[0]
            if (block.col == self.level.player.col
                    and block.row == self.level.player.row):
                Mob.sound_of_hit.play()
                self.level.player.health = \
                    max(self.level.player.health - self.damage, 0)
                if self.level.player.health == 0:
                    self.level.game_over = True
                    self.level.player.kill()
                self.kill()
                new_cell = self.level.sprites_arr[self.row][self.col]
                new_cell[1] = \
                    list(filter(lambda x: x != self,
                                [character for character in
                                 new_cell[1]]))
                self.level.events['health_down'] += 1
            else:
                self.level.check_out_list.append(self)

    def voln(self, x, y, x1, y1):
        """
        Алгоритм поиска пути к игроку

        Arguments:
            x(int): начальная координата x
            y(int): начальная координата y
            x1(int): координата x игрока
            y1(int): координата y игрока

        Return:
             path(arr[int, int]): массив с координатами пути
        """
        path = []
        board = []
        # в матрице задаётся начальное расстояние = 1000 для обычных клеток
        # и расстояние = -1 для полей с клеткой
        for row in range(self.level.level_map.height):
            board.append([])
            for col in range(self.level.level_map.width):
                cur_cell = self.level.sprites_arr[row][col]
                board[row].append([-1, (row, col)]
                                  if cur_cell[1] and isinstance(cur_cell[1][0], Cage)
                                  else [1000, (row, col)])
            # так как у нас координаты заданы по-другому в загрузке карты
            board[row] = board[row]
        queue = deque()
        queue.append((x, y))
        board[x][y][0] = 1
        self.get_to_all_neighbors(x, y, board, queue)
        end_cur = board[x1][y1][0]
        while 0 < end_cur < 1000:
            # использем связный список,
            # чтобы находить, откуда мы пришли в ячейку
            path.append((y1, x1))
            x1, y1 = board[x1][y1][1]
            end_cur -= 1
        return path[::-1]

    def get_to_all_neighbors(self, row, col, board, queue):
        """
        Функция перебора всех соседей по очереди

        Arguments:
            row(int): начальный ряд
            col(int): начальный столбец
            board(arr[int, [int, int]]): текущее состояние матрицы
            queue(deque): очередь координат соседей

        Return:
            board(arr[int, [int, int]]): возвращает изменённую матрицу
        """
        # board - список, [расстояние от моба, (координаты предыдущей ячейки)]
        if board[row][col][0] == -1 or \
                row == self.level.level_map.height - 1 and \
                col == self.level.level_map.width - 1:
            return board
        delta_x = [-1, 0, 0, 1]
        delta_y = [0, -1, 1, 0]
        while queue:
            row, col = queue.pop()
            for delta_row, delta_col in zip(delta_y, delta_x):
                if 0 <= delta_row + row < self.level.level_map.height and \
                        0 <= delta_col + col < self.level.level_map.width:
                    next_row = delta_row + row
                    next_col = delta_col + col
                    if (board[next_row][next_col][0] > board[row][col][0] + 1
                            and board[next_row][next_col][0] != -1):
                        # сохраняем предыдущую ячейку, вместе с расстоянием
                        board[next_row][next_col] = [board[row][col][0] + 1,
                                                     (row, col)]
                        # если расстояние для текущй клетки обновлено,
                        # нужно пройти по всем соседей текущей клетки
                        queue.append((next_row, next_col))
        return board

    def move(self, cell):
        """
        Перемещение моба

        Arguments:
            cell(tuple(int, int)): кортеж координат клетки
        """
        self.change_col_and_row(cell)
        x, y = self.level.get_cords_for_player((self.drawing_col,
                                                self.drawing_row))
        self.change_cords(x, y)

    def change_cords(self, x, y):
        """
        Изменение координат спрайта.

        Arguments:
            x: координата по x
            y: координата по y
        """
        self.rect.x = x
        self.rect.y = y

    def change_col_and_row(self, cell):
        """
        Изменяет col, row, drawing_col, drawing_row спрайта.

        Arguments:
            cell(tuple(int, int)): кортеж с координатами x и y
        """
        self.col = cell[0]
        self.row = cell[1]
        self.drawing_col = self.col + SECOND_LAYER
        self.drawing_row = self.row + SECOND_LAYER
