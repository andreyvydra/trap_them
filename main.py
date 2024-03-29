import sqlite3
import sys

from menu import *
from save import *
from tools import *


def game():
    """
    Функция игры, где происходит обновление и рендеринг
    уровня, и обработка некоторых событий.

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
    """

    # Если в меню была нажата кнопка продолжить игру, то
    # level_map и level просто подгружается, а если нет, то
    # создание карты по дефолту
    game_music = pygame.mixer.Sound(make_path('songs/gameplay.ogg'))
    if msg_for_starting == 'continue':
        level_map, level = save.get_level_and_map(screen)
    else:
        level_map = Map(make_path('map'), difficulty=data_of_game[0])
        level_map.load_map()
        level = Level(level_map, screen)
        level.load_sprites()

    # Добавление кнопки 'закончить ход' в менеджер уровня
    game_manager = pygame_gui.UIManager(SCREEN_SIZE, make_path('themes/theme.json'))
    end_move_btn = pygame_gui.elements. \
        UIButton(relative_rect=pygame.rect.Rect((19, 80),
                                                BUTTON_SIZE_2),
                 text='End turn',
                 manager=game_manager)
    level.manager = game_manager

    running = True
    is_pressed_escape = False
    game_music.set_volume(0.25)
    game_music.play(-1, 0, 10000)

    while running:
        cpu_delay = clock.tick(FPS)
        td = cpu_delay / 1000

        # Проверки на состояние уровня
        if level.game_over and not level.player.alive():
            game_music.stop()
            game_over_res = game_over()
            if game_over_res == 'load_game':
                level_map, level = save.get_level_and_map(screen)
                level.manager = game_manager
            if game_over_res == 'quit':
                update_db(level)
                return 'quit'
            elif game_over_res == 'quit_to_menu':
                update_db(level)
                return
            game_music.play(-1, 0, 10000)

        elif level.game_over and level.level_number != 10:
            update_db(level, level_complete=True)

            font = pygame.font.Font(None, 50)
            text = font.render(f"Level {level.level_number} is clear",
                               True, (255, 255, 255))
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
            text_y = 100
            level.screen.blit(text, (text_x, text_y))
            level.render()
            pygame.display.flip()
            ping_for_message = 10000000
            while ping_for_message != 0:
                ping_for_message -= 1
            level.screen.fill('#282828')

            number_of_level = level.level_number
            upgrades_res = upgrades()
            max_health = level.player.max_health
            health = level.player.health
            max_steps = level.player.max_steps
            coins = level.player.coins
            cage_dis = level.player.cage_distance

            if upgrades_res == 'first':
                health += 1
                max_health += 1
            elif upgrades_res == 'second':
                max_steps += 1
            elif upgrades_res == 'third':
                cage_dis += 1

            level_map = Map(make_path('map'))
            level_map.load_map()
            level = Level(level_map, screen, number_of_level + 1)
            level.load_sprites()
            level.player.max_health = max_health
            level.player.health = health
            level.player.max_steps = max_steps
            level.player.coins = coins
            level.player.steps = max_steps
            level.player.cage_distance = cage_dis
            level.manager = game_manager
            save.save_game(level)

        elif level.game_over and level.level_number == 10:
            update_db(level, level_complete=True)
            ending()

        # Обработка нажатия на escape
        if is_pressed_escape:
            game_music.stop()
            pause_res = pause(level)
            if pause_res == 'quit':
                update_db(level)
                return 'quit'
            elif pause_res == 'quit_to_menu':
                update_db(level)
                return
            elif pause_res == 'continue':
                is_pressed_escape = False
            elif pause_res == 'load_game':
                level_map, level = save.get_level_and_map(screen)
                level.manager = game_manager
                is_pressed_escape = False
            game_music.play(-1, 0, 10000)

        screen.fill('#282828')
        event = pygame.event.Event(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_pressed_escape = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                level.player.update(event)
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    # В проверке присутствует проверка на падение клетки для
                    # того, чтобы исключить возможность делать ходы,
                    # до того как клетка упадёт на моба
                    if event.ui_element == end_move_btn and \
                            all(map(lambda x: x.is_fallen, level.cages)):
                        level.is_pressed_end_move_btn = True

            game_manager.process_events(event)

        level.update(event, td, clock.get_fps())
        level.render()
        show_fps(screen, clock.get_fps())

        # Отрисовка сетки
        # for rect in level_map.floor:
        #    pygame.draw.rect(screen, (255, 255, 255), rect.top_rect, 1)

        pygame.display.flip()


def update_db(level, level_complete=False):
    """
    Функция обновления статистики в базе данных

    Arguments:
        level (Level): уровень, в котором был основной gameplay
        level_complete (bool): флаг, указывающий на конец уровня

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
    """

    events = level.get_events()
    if level_complete:
        events['level_complete'] += 1
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['locked_up_mafia']}
                    WHERE id=1''').fetchall()
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['picked_up_coins']}
                    WHERE id=2''').fetchall()
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['health_down']}
                    WHERE id=3''').fetchall()
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['done_moves']}
                    WHERE id=4''').fetchall()
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['level_complete']}
                    WHERE id=5''').fetchall()
    cur.execute(f'''UPDATE statistic
                    SET value = value + {events['used_traps']}
                    WHERE id=6''').fetchall()
    con.commit()


def pre_game_menu():
    """
    Функция предигрового меню с выбором сложности

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
        data (list): Данные, собранные из этого игрового меню
    """
    pre_game_manager = pygame_gui.UIManager(SCREEN_SIZE,
                                            make_path('themes/theme.json'))
    btn_width, btn_height = 150, 50

    # Алгоритм по созданию прямоугольников под сетку (elements)
    elements = [None, [None, None]]
    y = len(elements) / 2 * btn_height
    for i, elem in enumerate(elements):
        if elem.__class__ == list:
            x = len(elem) / 2 * btn_width
            for j, item in enumerate(elem):
                cur_x = CENTER_POINT[0] - x + j * btn_width
                cur_y = CENTER_POINT[1] - y + i * btn_height
                rect = pygame.Rect((cur_x, cur_y), (btn_width, btn_height))
                elements[i][j] = rect
        else:
            cur_x = CENTER_POINT[0] - btn_width
            cur_y = CENTER_POINT[1] - y + i * btn_height
            rect = pygame.Rect((cur_x, cur_y), (btn_width * 2, btn_height))
            elements[i] = rect

    difficulty_menu = pygame_gui.elements.ui_drop_down_menu. \
        UIDropDownMenu(options_list=['Низкий', 'Средний'],
                       starting_option='Низкий',
                       relative_rect=elements[0],
                       manager=pre_game_manager,
                       )

    start_game_btn = pygame_gui.elements.ui_button. \
        UIButton(manager=pre_game_manager,
                 relative_rect=elements[1][1],
                 text='Начать игру')

    back_to_menu_btn = pygame_gui.elements.ui_button. \
        UIButton(manager=pre_game_manager,
                 relative_rect=elements[1][0],
                 text='Выйти в меню')

    running = True
    difficulties = {'Низкий': 1,
                    'Средний': 2}
    difficulty = difficulties['Низкий']
    data_of_game.clear()

    while running:
        screen.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == difficulty_menu:
                        difficulty = difficulties[event.text]
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_game_btn:
                        # В будущем вместо [difficulty] будет список
                        # с данными, которые будут собираться из этого меню
                        return [difficulty]
                    if event.ui_element == back_to_menu_btn:
                        return 'quit_to_menu'

            pre_game_manager.process_events(event)

        pre_game_manager.update(td)
        pre_game_manager.draw_ui(screen)
        screen.blit(screen, (0, 0))
        pygame.display.flip()


def pause(level):
    """
    Функция меню паузы

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
    """
    pause_surface = pygame.surface.Surface(SCREEN_SIZE)
    # Устанавливаем альфа канал на 100 для прозрачности
    pause_surface.set_alpha(100)
    pause_manager = pygame_gui.UIManager(SCREEN_SIZE, make_path('themes/theme.json'))
    menu = Menu(pause_manager, continue_btn=True, back_to_menu_btn=True,
                quit_btn=True, save_btn=True, load_btn=True)
    running = True

    while running:
        pause_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == menu.continue_btn:
                        return 'continue'
                    if event.ui_element == menu.back_to_menu_btn:
                        return 'quit_to_menu'
                    if event.ui_element == menu.quit_btn:
                        return 'quit'
                    if event.ui_element == menu.save_btn:
                        save.save_game(level)
                    if event.ui_element == menu.load_btn:
                        return 'load_game'

            pause_manager.process_events(event)

        pause_manager.update(td)
        pause_manager.draw_ui(pause_surface)
        screen.blit(pause_surface, (0, 0))
        pygame.display.flip()


def ending():
    """Функция отображения финального экрана"""

    font = pygame.font.Font(None, 70)
    text = font.render('Вы прошли нашу игру, спасибо!', True, (255, 0, 255))
    text_w = text.get_width()
    text_h = text.get_height()
    x, y = CENTER_POINT[0] - text_w // 2, CENTER_POINT[1] - text_h // 2
    running = True
    while running:
        screen.fill('#282828')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(text, (x, y))

        pygame.display.flip()


def game_over():
    """
    Функция отображения экрана при проигрыше

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
    """

    game_over_surface = pygame.surface.Surface(SCREEN_SIZE)
    game_over_surface.set_alpha(100)
    game_over_manager = pygame_gui.UIManager(SCREEN_SIZE,
                                             make_path('themes/theme.json'))
    menu = Menu(game_over_manager, back_to_menu_btn=True,
                quit_btn=True, load_btn=True)
    running = True

    while running:
        game_over_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == menu.back_to_menu_btn:
                        return 'quit_to_menu'
                    if event.ui_element == menu.quit_btn:
                        return 'quit'
                    if event.ui_element == menu.load_btn:
                        return 'load_game'

            game_over_manager.process_events(event)

        game_over_manager.update(td)
        game_over_manager.draw_ui(game_over_surface)
        screen.blit(game_over_surface, (0, 0))
        pygame.display.flip()


def upgrades():
    """
    Функция для отображения апгрейдов и их выбора игроком

    Return:
        signal (str or None): Сигнал-сообщение для обработки эвента
    """
    upgrades_surface = pygame.surface.Surface(SCREEN_SIZE)
    upgrades_surface.set_alpha(100)
    upgrades_manager = pygame_gui.UIManager(SCREEN_SIZE,
                                            make_path('themes/theme.json'))
    menu = UpgradeMenu(upgrades_manager, first_upg_btn=True,
                       second_upg_btn=True, third_upg_btn=True)
    running = True

    while running:
        upgrades_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == menu.first_upg_btn:
                        return 'first'
                    if event.ui_element == menu.second_upg_btn:
                        return 'second'
                    if event.ui_element == menu.third_upg_btn:
                        return 'third'

            upgrades_manager.process_events(event)

        upgrades_manager.update(td)
        upgrades_manager.draw_ui(upgrades_surface)
        screen.blit(upgrades_surface, (0, 0))
        pygame.display.flip()


def show_statistic():
    """
    Функция для отображения статистики игры
    """

    running = True

    show_stat_manager = pygame_gui. \
        UIManager(SCREEN_SIZE, make_path('themes/theme.json'))

    back_rect = pygame.Rect((20, 20), BUTTON_SIZE)

    back_btn = pygame_gui.elements.ui_button. \
        UIButton(relative_rect=back_rect,
                 manager=show_stat_manager,
                 text='Назад')

    stat_data = cur.execute('''SELECT title,
                                value from statistic''').fetchall()

    font = pygame.font.Font(None, 40)
    # Высота текста в px
    height_px = 28
    margin = 20
    strings = pygame.sprite.Group()

    y = SCREEN_SIZE[1] // 2 - len(stat_data) / 2 * \
        height_px - len(stat_data) / 2 * margin

    for i, stat in enumerate(stat_data):
        text = font.render(f'{stat[0]}: {str(stat[1])}',
                           True, (153, 102, 0))
        text_w, text_h = text.get_width(), text.get_height()
        cur_x = SCREEN_SIZE[0] // 2 - text.get_width() // 2
        cur_y = y + i * text.get_height() + (margin * i)

        sprite = pygame.sprite.Sprite(strings)
        sprite.image = text
        sprite.rect = pygame.Rect((cur_x, cur_y), (text_w, text_h))

    while running:
        screen.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == back_btn:
                        return

            show_stat_manager.process_events(event)

        show_stat_manager.update(td)
        show_stat_manager.draw_ui(screen)

        strings.draw(screen)

        pygame.display.flip()


def start_game():
    """Функция для запуска игры"""
    music.stop()
    result = game()
    # Выход из игры
    if result == 'quit':
        sys.exit()
    music.play(-1, 0, 10000)


def make_db():
    """Функция создания базы данных"""
    try:
        cur.execute('''CREATE TABLE statistic (
                       id    INTEGER PRIMARY KEY AUTOINCREMENT
                                     UNIQUE
                                      NOT NULL,
                       title STRING  NOT NULL,
                       value INTEGER NOT NULL
                    );''')
        cur.execute('''INSERT INTO statistic(title, value)
                       VALUES ("Поймано членов мафии", 0),
                       ("Собрано монет", 0),
                       ("Потрачено здоровья", 0),
                       ("Совершено действий", 0),
                       ("Мест зачищено", 0),
                       ("Использовано ловушек", 0)''')
        con.commit()
    except sqlite3.Error:
        print('DB is done')


if __name__ == '__main__':
    # Инициализация всего и вся
    pygame.mixer.init()
    pygame.init()

    music = pygame.mixer.Sound(make_path('songs/main_menu.ogg'))
    music.set_volume(0.25)
    music.play(-1, 0, 10000)

    pygame.display.set_caption("'КУБЫ!'")
    screen = pygame.display.set_mode(SCREEN_SIZE)

    clock = pygame.time.Clock()

    manager = pygame_gui.UIManager(SCREEN_SIZE, make_path('themes/theme.json'))
    main_menu = Menu(manager, continue_btn=True, new_game_btn=True,
                     quit_btn=True, stat_btn=True)

    save = Save(make_path('saves/save.pickle'))

    bg = pygame.image.load(make_path('bgs/menu_bg.png'))
    bg = pygame.transform.scale(bg, SCREEN_SIZE)

    is_button_game_pressed = False
    is_button_new_game_pressed = False
    mainloop = True

    msg_for_starting = ''
    data_of_game = []
    con = sqlite3.connect('statistic.db')
    cur = con.cursor()
    make_db()

    while mainloop:
        time_delta = clock.tick(FPS) / 1000.0

        if is_button_game_pressed:
            start_game()
        if is_button_new_game_pressed:
            res = pre_game_menu()
            if res != 'quit_to_menu':
                data_of_game = res
                start_game()

        is_button_game_pressed = False
        is_button_new_game_pressed = False

        screen.fill('#282828')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == main_menu.continue_btn:
                        is_button_game_pressed = True
                        msg_for_starting = 'continue'
                    if event.ui_element == main_menu.new_game_btn:
                        is_button_new_game_pressed = True
                        msg_for_starting = 'new_game'
                    if event.ui_element == main_menu.quit_btn:
                        sys.exit()
                    if event.ui_element == main_menu.stat_btn:
                        show_statistic()

            manager.process_events(event)
        screen.blit(bg, (0, 0))
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
