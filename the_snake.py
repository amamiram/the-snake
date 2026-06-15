from random import randint

import pygame

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
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует игровой объект."""
        if position is None:
            # Центр экрана с шагом GRID_SIZE
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self):
        """Абстрактный метод отрисовки (переопределяется в дочерних класах)."""
        pass


class Apple(GameObject):
    """Класс яблока, которое съедает змейка."""

    def __init__(self):
        """Инициализирует яблоко с случайной позицией и красным цветом."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
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
            # Если координаты змейки не переданы
            # или яблоко не на змейке - выходим
            if snake_positions is None or self.position not in snake_positions:
                break

    def draw(self):
        """Рисует яблоко на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки, которая движется и растёт."""

    def __init__(self):
        """Инициализирует змейку с начальной позицией и направлением."""
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет текущее направление после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку в текущем направлении."""
        head = self.get_head_position()
        x, y = head
        dx, dy = self.direction

        # Новая позиция головы с проходом сквозь стены
        new_head = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Сохраняем последний сегмент перед возможным удалением
        self.last = (
            self.positions[-1] if len(self.positions) > self.length else None
        )

        # Удаляем хвост, если длина превышает текущую
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Рисует змейку на экране."""
        # Рисуем тело (все сегменты кроме головы)
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Рисуем голову
        if self.positions:
            head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, head_rect)
            pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затираем последний сегмент
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    pygame.init()

    # Создаём объекты игры
    snake = Snake()
    apple = Apple()

    # Основной игровой цикл
    while True:
        clock.tick(SPEED)

        # Обработка событий клавиатуры и выхода
        handle_keys(snake)

        # Обновляем направление змейки
        snake.update_direction()

        # Двигаем змейку
        snake.move()

        # Проверка: съела ли змейка яблоко?
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Проверка: столкновение с собой
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            # Очищаем экран
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
