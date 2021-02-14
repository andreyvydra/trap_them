import os
from settings import *
from pygame import Color


font = pygame.font.SysFont("Arial", 30)


def make_path(dest):
    cur_dir = os.getcwd()
    cur_dir += DATA_PATH
    cur_dir += '\\' + dest
    return cur_dir


def show_fps(surface, fps):
    text = font.render('FPS: ' + str(round(fps)), True, Color('coral'))
    surface.blit(text, (SCREEN_WIDTH - text.get_width() - 20, 50))
