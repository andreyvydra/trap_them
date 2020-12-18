import pygame
from map import *
from settings import *

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("'КУБЫ!'")
    screen = pygame.display.set_mode(SCREEN_SIZE)

    level_map = Map()
    all_sprites = pygame.sprite.Group(level_map.get_sprites())

    running = True

    while running:
        screen.fill('#282828')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(pygame.mouse.get_pressed(3), pygame.mouse.get_pos())
        all_sprites.draw(screen)

        # Отрисовка сетки
        # for rect in level_map.floor:
        #    pygame.draw.rect(screen, (255, 255, 255), rect.top_rect, 1)

        pygame.display.flip()
