import pygame
import pygame_gui
import pickle
from map import *
from settings import *


def game(msg):
    if msg == 'new_game':
        level_map = Map('map')
        level_map.load_map()
        level = Level(level_map)
        level.load_sprites()
    elif msg == 'continue':
        level_map, level = load_game()

    running = True
    is_pressed_escape = False
    while running:
        if is_pressed_escape:
            res = pause(level)
            if res == 'quit':
                return 'quit'
            elif res == 'quit_to_menu':
                return
            elif res == 'continue':
                is_pressed_escape = False
            elif res == 'load_game':
                level_map, level = load_game()
                is_pressed_escape = False

        screen.fill('#282828')
        event = pygame.event.Event(0)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_pressed_escape = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                level.player.update(event)
            if event.type == pygame.QUIT:
                return 'quit'

        level.update(event)
        level.render(screen)

        # Отрисовка сетки
        # for rect in level_map.floor:
        #    pygame.draw.rect(screen, (255, 255, 255), rect.top_rect, 1)

        clock.tick(FPS)
        pygame.display.flip()


def save_game(level):
    with open('saves/save.pickle', 'wb') as file:
        player_data = {'coins': level.player.coins,
                       'steps': level.player.steps,
                       'col': level.player.col,
                       'row': level.player.row,
                       'x': level.player.rect.x,
                       'y': level.player.rect.y}

        level_data = {'enemies': [{'col': sprite.col,
                                   'row': sprite.row,
                                   'coins': sprite.coins,
                                   'step': sprite.step,
                                   'x': sprite.rect.x,
                                   'y': sprite.rect.y}
                                  for sprite in level.enemies],

                      'floor': [{'col': sprite.col,
                                 'row': sprite.row,
                                 'x': sprite.rect.x,
                                 'y': sprite.rect.y}
                                for sprite in level.floor],

                      'cages': [{'col': sprite.col,
                                 'row': sprite.row,
                                 'x': sprite.rect.x,
                                 'y': sprite.rect.y}
                                for sprite in level.cages],
                      'coins': [{'col': sprite.col,
                                 'row': sprite.row,
                                 'x': sprite.rect.x,
                                 'y': sprite.rect.y}
                                for sprite in level.coins]}

        map_data = {'path_map': level.level_map.path_map,
                    'first_layer': level.level_map.first_layer,
                    'second_layer': level.level_map.second_layer}
        pickle.dump([player_data, level_data, map_data], file)


def load_data():
    with open('saves/save.pickle', 'rb') as file:
        return pickle.load(file)


def load_game():
    player_data, level_data, map_data = load_data()
    level_map = Map(map_data['path_map'], map_data['first_layer'], map_data['second_layer'])
    level = Level(level_map)
    level.load_data(level_data)
    level.load_player(player_data)
    return level_map, level


def pause(level):
    pause_surface = pygame.surface.Surface(SCREEN_SIZE)
    pause_surface.set_alpha(100)
    pause_manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    running = True
    continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                              CENTER_POINT[1] - 76),
                                                                             (100, 50)),
                                                   text='Продолжить',
                                                   manager=pause_manager)
    back_to_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                                  CENTER_POINT[1] - 25),
                                                                                 (100, 50)),
                                                       text='Главное меню',
                                                       manager=pause_manager)
    save_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                               CENTER_POINT[1] + 26),
                                                                              (100, 50)),
                                                    text='Сохранить игру',
                                                    manager=pause_manager)
    load_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                               CENTER_POINT[1] + 77),
                                                                              (100, 50)),
                                                    text='Загрузить игру',
                                                    manager=pause_manager)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                          CENTER_POINT[1] + 128),
                                                                         (100, 50)),
                                               text='Выйти',
                                               manager=pause_manager)

    while running:
        pause_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == continue_button:
                        return 'continue'
                    if event.ui_element == back_to_menu_button:
                        return 'quit_to_menu'
                    if event.ui_element == quit_button:
                        return 'quit'
                    if event.ui_element == save_game_button:
                        save_game(level)
                    if event.ui_element == load_game_button:
                        return 'load_game'

            pause_manager.process_events(event)

        pause_manager.update(td)
        pause_manager.draw_ui(pause_surface)
        screen.blit(pause_surface, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("'КУБЫ!'")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')

    is_button_game_pressed = False

    continue_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                                   CENTER_POINT[1] - 25),
                                                                                  (100, 50)),
                                                        text='Продолжить игру',
                                                        manager=manager)
    new_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                              CENTER_POINT[1] + 26),
                                                                             (100, 50)),
                                                   text='Новая игра',
                                                   manager=manager)
    mainloop = True
    msg = ''
    while mainloop:
        time_delta = clock.tick(FPS) / 1000.0

        if is_button_game_pressed:
            if game(msg) == 'quit':
                pygame.quit()
                break

        is_button_game_pressed = False

        screen.fill('#282828')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == continue_game_button:
                        is_button_game_pressed = True
                        msg = 'continue'
                    if event.ui_element == new_game_button:
                        is_button_game_pressed = True
                        msg = 'new_game'

            manager.process_events(event)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
