import pygame
import pygame_gui
import pickle
from map import *
from settings import *
from menu import *
from save import *


def game():
    # Если в меню была нажата кнопка продолжить игру, то
    # level_map и level просто подгружается, а если нет, то
    # создание карты по дефолту
    if msg == 'continue':
        level_map, level = save.get_level_and_map()
    else:
        level_map = Map('map')
        level_map.load_map()
        level = Level(level_map)
        level.load_sprites()

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
                level_map, level = save.get_level_and_map()
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


def pause(level):
    pause_surface = pygame.surface.Surface(SCREEN_SIZE)
    pause_surface.set_alpha(100)
    pause_manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    menu = Menu(pause_manager, continue_btn=True, back_to_menu_btn=True,
                quit_btn=True, save_btn=True, load_btn=True)
    running = True

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


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("'КУБЫ!'")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    main_menu = Menu(manager, continue_btn=True, new_game_btn=True)
    save = Save('saves/save.pickle')

    is_button_game_pressed = False

    mainloop = True
    msg = ''
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
                    if event.ui_element == main_menu.continue_btn:
                        is_button_game_pressed = True
                        msg = 'continue'
                    if event.ui_element == main_menu.new_game_btn:
                        is_button_game_pressed = True
                        msg = 'new_game'

            manager.process_events(event)

        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()
