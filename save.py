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
        level_map = Map(map_data[0])
        level_map.width = map_data[1]
        level_map.height = map_data[2]
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
                                   'step': sprite.step}
                                  for sprite in level.enemies],

                      'floor': [{'col': sprite.col,
                                 'row': sprite.row,
                                 'type_of_block': sprite.type_of_block}
                                for sprite in level.floor],

                      'cages': [{'col': sprite.col,
                                 'row': sprite.row}
                                for sprite in level.cages],

                      'coins': [{'col': sprite.col,
                                 'row': sprite.row}
                                for sprite in level.coins]}
        return level_data, level.level_number

    def get_map_data(self, level):
        w, h = level.level_map.width, level.level_map.height
        return level.level_map.path_map, w, h

    def get_player_data(self, level):
        player_data = {'coins': level.player.coins,
                       'steps': level.player.steps,
                       'health': level.player.health,
                       'max_health': level.player.max_health,
                       'max_steps': level.player.max_steps,
                       'col': level.player.col,
                       'row': level.player.row}
        return player_data
