# Основные настройки игры

# Настройки игрового окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650
SCREEN_SIZE = [SCREEN_WIDTH, SCREEN_HEIGHT]
CENTER_POINT = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Настройки кубов
SCALE_COEFFICIENT = 1
STANDARD_CUBE_WIDTH = 104
STANDARD_CUBE_HEIGHT = 134
SCALED_CUBE_WIDTH = STANDARD_CUBE_WIDTH * SCALE_COEFFICIENT
SCALED_CUBE_HEIGHT = STANDARD_CUBE_HEIGHT * SCALE_COEFFICIENT
SCALED_TOP_RECT_HEIGHT = 60
SCALED_TOP_RECT_WIDTH = SCALED_CUBE_WIDTH

# Настройка слоёв
DELTA_LAYER = -1
# Предметы, лежащие на слое выше будут уменьшать свой row, col на -1
SECOND_LAYER = 0 + DELTA_LAYER

# Игрок
HEIGHT_PLAYER = 200
WIDTH_PLAYER = 79
# Спрайт игрока по Y меньше на 17px, чем спрайт куба
# (значение используется для отрисовки и подсчёта координаты на экране)
# Отступы для корректной отрисовки игрока
MARGIN_TOP_PLAYER = -SCALED_CUBE_HEIGHT + SCALED_TOP_RECT_HEIGHT // 2
MARGIN_LEFT_PLAYER = (SCALED_CUBE_WIDTH - WIDTH_PLAYER) // 2