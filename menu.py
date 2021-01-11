import pygame_gui
from settings import *
import pygame


class Menu:
    """
    Класс, который упрощает работу с интерфейсами меню

    Attributes:
        manager(pygame_gui.UIManager): менеджер
        continue_btn(pygame_gui.elements.UIButton): кнопка продолжения
        new_game_btn(pygame_gui.elements.UIButton): кнопка новой игры
        save_btn(pygame_gui.elements.UIButton): сохранение игры
        load_btn(pygame_gui.elements.UIButton): загрузка игры
        back_to_menu_btn(pygame_gui.elements.UIButton:
            вернуться в главное меню
        quit_btn(pygame_gui.elements.UIButton): выход из игры
        buttons(arr): массив со всеми кнопками

    Methods:
        set_coordinates_for_buttons(): установка координат кнопок
        add_continue_btn(): добавление кнопки продолжения
        add_new_game_btn(): добавление кнопки новой игры
        add_save_btn(): добавление кнопки сохранения
        add_load_btn(): добавление кнопки загрузки
        add_back_to_menu_btn(): добавление кнопки возврата в главное меню
        add_quit_btn(): добавление кнопки выхода из игры
        """

    def __init__(self, manager, continue_btn=False, new_game_btn=False,
                 save_btn=False, load_btn=False,
                 back_to_menu_btn=False, quit_btn=False,
                 stat_btn=False):

        self.manager = manager
        self.continue_btn = None
        self.new_game_btn = None
        self.save_btn = None
        self.load_btn = None
        self.back_to_menu_btn = None
        self.quit_btn = None
        self.stat_btn = None

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
        if stat_btn:
            self.add_stat_btn()

        self.buttons = [self.continue_btn, self.new_game_btn,
                        self.save_btn, self.load_btn, self.stat_btn,
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
        continue_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                    text='Продолжить',
                                                    manager=self.manager)
        self.continue_btn = continue_btn

    def add_new_game_btn(self):
        new_game_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                    text='Новая игра',
                                                    manager=self.manager)
        self.new_game_btn = new_game_btn

    def add_save_btn(self):
        save_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                text='Сохранить игру',
                                                manager=self.manager)
        self.save_btn = save_btn

    def add_load_button(self):
        load_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                text='Загрузить игру',
                                                manager=self.manager)
        self.load_btn = load_btn

    def add_back_to_menu_btn(self):
        back_to_menu_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                           text='Главное меню',
                                                           manager=self.manager)
        self.back_to_menu_btn = back_to_menu_button

    def add_quit_btn(self):
        quit_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                text='Выйти из игры',
                                                manager=self.manager)
        self.quit_btn = quit_btn

    def add_stat_btn(self):
        stat_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0),
                                                                          BUTTON_SIZE),
                                                text='Статистика',
                                                manager=self.manager)
        self.stat_btn = stat_btn


class UpgradeMenu:
    '''
    Класс выбора улучшения

    Attributes:
        manager(pygame_gui.UIManager): менеджер
        first_upg_btn(pygame_gui.elements.UIButton): кнопка первого улучшения
        second_upg_btn(pygame_gui.elements.UIButton): кнопка второго улучшения
        third_upg_btn(pygame_gui.elements.UIButton): кнопка третьего улучшения
        first_upg_image(pygame_gui.elements.UIImage): изображение первого
            улучшения
        second_upg_image(pygame_gui.elements.UIImage): изображение второго
            улучшения
        third_upg_image(pygame_gui.elements.UIImage): изображение третьего
            улучшения
        buttons(arr): массив со всеми кнопками

    Methods:
        set_coordinates_for_buttons(): установка координат кнопок
        set_coordinates_for_upg_images(): установка координат для изображений
        add_first_upg_btn(): добавление кнопки выбора первого улучшения
        add_second_upg_btn(): добавление кнопки выбора второго улучшения
        add_third_upg_btn(): добавление кнопки выбора третьего улучшения
    '''
    def __init__(self, manager, first_upg_btn=False,
                 second_upg_btn=False, third_upg_btn=False):

        self.manager = manager
        self.first_upg_btn = None
        self.second_upg_btn = None
        self.third_upg_btn = None
        self.first_upg_image = None
        self.second_upg_image = None
        self.third_upg_image = None

        if first_upg_btn:
            self.add_first_upg_btn()
        if second_upg_btn:
            self.add_second_upg_btn()
        if third_upg_btn:
            self.add_third_upg_btn()

        self.buttons = [self.first_upg_btn, self.second_upg_btn,
                        self.third_upg_btn]

        self.set_coordinates_for_upg_btns()
        self.set_coordinates_for_upg_images()

    def set_coordinates_for_upg_images(self):
        images = [self.first_upg_image, self.second_upg_image,
                  self.third_upg_image]
        x = len(images) * UPGRADE_IMAGE_SIZE[1] // 2
        for i, img in enumerate(images):
            img.rect.x = CENTER_POINT[0] - x + i * BUTTON_SIZE[0]
            img.rect.y = \
                CENTER_POINT[1] - MARGIN_BOTTOM_IMAGE + MARGIN_TOP_BUTTON
            img.rebuild()

    def set_coordinates_for_upg_btns(self):
        active_buttons = [self.first_upg_btn, self.second_upg_btn,
                          self.third_upg_btn]
        x = len(active_buttons) / 2 * BUTTON_SIZE[0]
        for i, btn in enumerate(active_buttons):
            btn.rect.x = CENTER_POINT[0] - x + i * BUTTON_SIZE[0]
            btn.rect.y = CENTER_POINT[1] + MARGIN_TOP_BUTTON
            btn.rebuild()

    def add_first_upg_btn(self):
        first_upg_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                     text='Увеличить hp на 1',
                                                     manager=self.manager)

        first_upg_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), UPGRADE_IMAGE_SIZE),
            image_surface=pygame.image.load('sprites/+hp.png'),
            manager=self.manager)
        self.first_upg_btn = first_upg_btn
        self.first_upg_image = first_upg_image

    def add_second_upg_btn(self):
        second_upg_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
                                                      text='Увеличить mp на 1',
                                                      manager=self.manager)

        second_upg_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), UPGRADE_IMAGE_SIZE),
            image_surface=pygame.image.load('sprites/+mp.png'),
            manager=self.manager)

        self.second_upg_btn = second_upg_btn
        self.second_upg_image = second_upg_image

    def add_third_upg_btn(self):
        third_upg_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 0), BUTTON_SIZE),
            text='Увеличить cage_dis на 1',
                                                      manager=self.manager)
        third_upg_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((0, 0), UPGRADE_IMAGE_SIZE),
            image_surface=pygame.image.load('sprites/+cage_distance.png'),
                                                       manager=self.manager)
        self.third_upg_btn = third_upg_btn
        self.third_upg_image = third_upg_image