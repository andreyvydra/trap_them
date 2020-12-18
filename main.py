import pygame
from map import *
from settings import *

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("'КУБЫ!'")
    screen = pygame.display.set_mode(SCREEN_SIZE)

    level_map = Map('map')
    level = Level(level_map)

    running = True

    while running:
        screen.fill('#282828')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        level.render(screen)
        level.update(event)

        # Отрисовка сетки
        # for rect in level_map.floor:
        #    pygame.draw.rect(screen, (255, 255, 255), rect.top_rect, 1)

        pygame.display.flip()
