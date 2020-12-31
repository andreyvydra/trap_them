import pygame_gui
from settings import *
import pygame


class Menu:
    """Класс, который упрощает работу с интерфейсами меню"""
    def __init__(self, manager, continue_btn=False, new_game_btn=False,
                 save_btn=False, load_btn=False,
                 back_to_menu_btn=False, quit_btn=False):

        self.manager = manager
        self.continue_btn = None
        self.new_game_btn = None
        self.save_btn = None
        self.load_btn = None
        self.back_to_menu_btn = None
        self.quit_btn = None

        if continue_btn:
            self.add_continue_btn()
        if new_game_btn:
            self.add_new_game_btn()
        if save_btn:
            self.add_save_btn()
        if load_btn:
            self.add_load_button()
        if back_to_menu_btn:
            self.add_back_to_menu_btn()
        if quit_btn:
            self.add_quit_btn()

        self.buttons = [self.continue_btn, self.new_game_btn,
                        self.save_btn, self.load_btn,
                        self.back_to_menu_btn, self.quit_btn]

        self.set_coordinates_for_buttons()

    def set_coordinates_for_buttons(self):
        active_buttons = list(filter(lambda x: x is not None, self.buttons))
        y = len(active_buttons) / 2 * BUTTON_SIZE[1]
        for i, btn in enumerate(active_buttons):
            btn.rect.x = CENTER_POINT[0] + MARGIN_LEFT_BUTTON
            btn.rect.y = CENTER_POINT[1] - y + i * BUTTON_SIZE[1]
            btn.rebuild()

    def add_continue_btn(self):
        continue_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                              BUTTON_SIZE),
                                                    text='Продолжить',
                                                    manager=self.manager)
        self.continue_btn = continue_btn

    def add_new_game_btn(self):
        new_game_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                              BUTTON_SIZE),
                                                    text='Новая игра',
                                                    manager=self.manager)
        self.new_game_btn = new_game_btn

    def add_save_btn(self):
        save_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                          BUTTON_SIZE),
                                                text='Сохранить игру',
                                                manager=self.manager)
        self.save_btn = save_btn

    def add_load_button(self):
        load_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                          BUTTON_SIZE),
                                                text='Загрузить игру',
                                                manager=self.manager)
        self.load_btn = load_btn

    def add_back_to_menu_btn(self):
        back_to_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                                     BUTTON_SIZE),
                                                           text='Главное меню',
                                                           manager=self.manager)
        self.back_to_menu_btn = back_to_menu_button

    def add_quit_btn(self):
        quit_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                          BUTTON_SIZE),
                                                text='Выйти из игры',
                                                manager=self.manager)
        self.quit_btn = quit_btn
