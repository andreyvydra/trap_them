import pygame
import pygame_gui
from map import *
from settings import *


def game():
    level_map = Map('map')
    level = Level(level_map)
    running = True
    is_pressed_escape = False
    while running:
        if is_pressed_escape:
            res = pause()
            if res == 'quit':
                return 'quit'
            elif res == 'quit_to_menu':
                return
            elif res == 'continue':
                is_pressed_escape = False
        screen.fill('#282828')
        event = pygame.event.Event(0)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_pressed_escape = True
            if event.type == pygame.QUIT:
                return 'quit'

        level.update(event)
        level.render(screen)

        # Отрисовка сетки
        # for rect in level_map.floor:
        #    pygame.draw.rect(screen, (255, 255, 255), rect.top_rect, 1)

        clock.tick(FPS)
        pygame.display.flip()


def pause():
    pause_surface = pygame.surface.Surface(SCREEN_SIZE)
    pause_surface.set_alpha(100)
    pause_manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    running = True
    continue_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                              CENTER_POINT[1] - 76),
                                                                             (100, 50)),
                                                   text='Продолжать',
                                                   manager=pause_manager)
    back_to_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                                  CENTER_POINT[1] - 25),
                                                                                 (100, 50)),
                                                       text='Главное меню',
                                                       manager=pause_manager)
    quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                          CENTER_POINT[1] + 26),
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

    start_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((CENTER_POINT[0] - 50,
                                                                                CENTER_POINT[1] - 25),
                                                                               (100, 50)),
                                                     text='Играть',
                                                     manager=manager)
    mainloop = True

    while mainloop:
        time_delta = clock.tick(FPS) / 1000.0
        if is_button_game_pressed:
            if game() == 'quit':
                pygame.quit()
                break

        is_button_game_pressed = False

        screen.fill('#282828')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_game_button:
                        is_button_game_pressed = True

            manager.process_events(event)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
