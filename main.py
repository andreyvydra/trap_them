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
        level_map, level = save.get_level_and_map(screen)
    else:
        level_map = Map('map')
        level_map.create_map()
        level_map.load_map()
        level = Level(level_map, screen)
        level.load_sprites()

    running = True
    is_pressed_escape = False

    while running:
        if level.game_over:
            game_over_res = game_over()
            if game_over_res == 'load_game':
                level_map, level = save.get_level_and_map(screen)
            if game_over_res == 'quit':
                return 'quit'
            elif game_over_res == 'quit_to_menu':
                return

        if is_pressed_escape:
            pause_res = pause(level)
            if pause_res == 'quit':
                return 'quit'
            elif pause_res == 'quit_to_menu':
                return
            elif pause_res == 'continue':
                is_pressed_escape = False
            elif pause_res == 'load_game':
                level_map, level = save.get_level_and_map(screen)
                is_pressed_escape = False
        if level.level_is_clear():
            upgrades_res = upgrades(level)
            max_health, health, max_steps, abilities, coins = level.player.max_health, \
                                         level.player.health,\
                                         level.player.max_steps,\
                                         level.player.abilities, \
                                         level.player.coins
            if upgrades_res == 'first':
                if health == max_health:
                    health += 1
                max_health += 1
            elif upgrades_res == 'second':
                max_steps += 1
            elif upgrades_res == 'third':
                pass
            level_map = Map('map')
            level_map.create_map()
            level_map.load_map()
            level = Level(level_map, screen)
            level.load_sprites()
            level.player.max_health = max_health
            level.player.health = health
            level.player.max_steps = max_steps
            level.player.abilities = abilities
            level.player.coins = coins
            level.player.steps = max_steps

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
        level.render()

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


def game_over():
    game_over_surface = pygame.surface.Surface(SCREEN_SIZE)
    game_over_surface.set_alpha(100)
    game_over_manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    menu = Menu(game_over_manager, back_to_menu_btn=True,
                quit_btn=True, load_btn=True)
    running = True

    while running:
        game_over_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

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


def upgrades(level):
    upgrades_surface = pygame.surface.Surface(SCREEN_SIZE)
    upgrades_surface.set_alpha(100)
    upgrades_manager = pygame_gui.UIManager(SCREEN_SIZE, 'themes/theme.json')
    menu = UpgradeMenu(upgrades_manager, first_upg_btn=True, second_upg_btn=True,
                quit_btn=True, third_upg_btn=True, back_to_menu_btn=True)
    running = True

    while running:
        upgrades_surface.fill('#282828')
        td = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'continue'

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == menu.first_upg_btn:
                        return 'first'
                    if event.ui_element == menu.back_to_menu_btn:
                        return 'quit_to_menu'
                    if event.ui_element == menu.quit_btn:
                        return 'quit'
                    if event.ui_element == menu.save_btn:
                        save.save_game(level)
                    if event.ui_element == menu.second_upg_btn:
                        return 'second'
                    if event.ui_element == menu.third_upg_btn:
                        return 'third'

            upgrades_manager.process_events(event)

        upgrades_manager.update(td)
        upgrades_manager.draw_ui(upgrades_surface)
        screen.blit(upgrades_surface, (0, 0))
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
            res = game()
            if res == 'quit':
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