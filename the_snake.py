from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10
MIN_SPEED = 5
MAX_SPEED = 30

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption(
    f'Змейка (стрелки - управление, +/- скорость: {SPEED} FPS)'
)

# Настройка времени:
clock = pg.time.Clock()

# Словарь для определения нового направления
DIRECTION_MAP = {
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
}


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует игровой объект."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод отрисовки
        (переопределяется в дочерних классах).
        """
        raise NotImplementedError("Метод draw должен быть переопределён")

    def draw_cell(self, position, color, border_color=None):
        """Рисует одну ячейку на игровом поле.

        Args:
            position: Координаты ячейки (x, y)
            color: Цвет заливки
            border_color: Цвет границы (если None, граница не рисуется)
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Класс яблока, которое съедает змейка."""

    def __init__(self, snake_positions=None):
        """Инициализирует яблоко с случайной позицией и красным цветом.

        Args:
            snake_positions: Список координат змейки (обязателен для игры,
                           но может быть None для тестов)
        """
        super().__init__(body_color=APPLE_COLOR)
        if snake_positions is None:
            snake_positions = []
        self.randomize_position(snake_positions)

    def randomize_position(self, snake_positions):
        """Устанавливает случайную позицию яблока на игровом поле.

        Args:
            snake_positions: Список координат змейки,
            чтобы яблоко не появилось на ней.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in snake_positions:
                break

    def draw(self):
        """Рисует яблоко на экране."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


class Snake(GameObject):
    """Класс змейки, которая движется и растёт."""

    def __init__(self):
        """Инициализирует змейку с начальной позицией и направлением."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения (для совместимости с тестами)."""
        # Направление обновляется через set_direction в handle_keys
        pass

    def set_direction(self, new_direction):
        """Устанавливает новое направление движения.

        Args:
            new_direction: Новое направление (UP, DOWN, LEFT, RIGHT)
        """
        if new_direction:
            opposite_directions = {
                UP: DOWN,
                DOWN: UP,
                LEFT: RIGHT,
                RIGHT: LEFT
            }
            if self.direction != opposite_directions.get(new_direction):
                self.direction = new_direction

    def move(self):
        """Перемещает змейку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Новая позиция головы с проходом сквозь стены
        self.position = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        # Добавляем новую голову
        self.positions.insert(0, self.position)

        # Сохраняем последний сегмент перед возможным удалением
        if len(self.positions) > self.length:
            self.last = self.positions[-1]
        else:
            self.last = None

        # Удаляем хвост, если длина превышает текущую
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Рисует змейку на экране."""
        # Рисуем тело (все сегменты кроме головы)
        for position in self.positions[1:]:
            self.draw_cell(position, self.body_color, BORDER_COLOR)

        # Рисуем голову
        self.draw_cell(self.get_head_position(), self.body_color, BORDER_COLOR)

        # Затираем последний сегмент
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой.

    Returns:
        str: 'speed_up' если нажата клавиша '+',
             'speed_down' если нажата клавиша '-',
             None в остальных случаях
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            # Изменение скорости
            if event.key == pg.K_EQUALS or event.key == pg.K_PLUS:
                return 'speed_up'
            if event.key == pg.K_MINUS:
                return 'speed_down'

            # Изменение направления через словарь
            current_direction = snake.direction
            new_direction = DIRECTION_MAP.get((current_direction, event.key))
            if new_direction:
                snake.set_direction(new_direction)
    return None


def update_speed(action):
    """Обновляет скорость игры.

    Args:
        action: 'speed_up' или 'speed_down'

    Returns:
        int: Новая скорость
    """
    global SPEED
    if action == 'speed_up':
        SPEED = min(SPEED + 1, MAX_SPEED)
    elif action == 'speed_down':
        SPEED = max(SPEED - 1, MIN_SPEED)
    # Обновляем заголовок окна
    pg.display.set_caption(
        f'Змейка (стрелки - управление, +/- скорость: {SPEED} FPS)'
    )
    return SPEED


def main():
    """Основной игровой цикл."""
    pg.init()

    # Создаём объекты игры
    snake = Snake()
    apple = Apple(snake.positions)

    # Основной игровой цикл
    while True:
        clock.tick(SPEED)

        # Обработка событий клавиатуры и выхода
        action = handle_keys(snake)
        if action in ('speed_up', 'speed_down'):
            update_speed(action)

        # Обновляем направление (для совместимости с тестами)
        snake.update_direction()

        # Двигаем змейку
        snake.move()

        # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        # Отрисовка
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
