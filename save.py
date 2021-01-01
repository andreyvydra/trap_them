import pickle
from map import *


class Save:
    """Класс, который занимается всей обработкой данных,
    сохранением и подгрузкой в игру"""

    def __init__(self, path_save):
        self.path_save = path_save

    def get_data(self):
        with open('saves/save.pickle', 'rb') as file:
            return pickle.load(file)

    def get_level_and_map(self, screen):
        player_data, level_data, map_data = self.get_data()
        level_map = Map(map_data)
        level = Level(level_map, screen)
        level.load_data(level_data)
        level.load_player(player_data)
        return level_map, level

    def save_game(self, level):
        player_data = self.get_player_data(level)
        level_data = self.get_level_data(level)
        map_data = self.get_map_data(level)
        with open('saves/save.pickle', 'wb') as file:
            pickle.dump([player_data, level_data, map_data], file)

    def get_level_data(self, level):
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
        return level_data

    def get_map_data(self, level):
        return level.level_map.path_map

    def get_player_data(self, level):
        player_data = {'coins': level.player.coins,
                       'steps': level.player.steps,
                       'col': level.player.col,
                       'row': level.player.row,
                       'x': level.player.rect.x,
                       'y': level.player.rect.y}
        return player_data
