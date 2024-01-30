from random import randint

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

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10
MIN_SPEED = 5
MAX_SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption(
    'Змейка - Управление: Стрелки, '
    'Выход: ESC, '
    'Скорость: +/-, '
    'Пауза: P'
)
clock = pg.time.Clock()

# Создание словаря направлений:
DIRECTION_MAP = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (0, pg.K_p): (0, 0)
}


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=(0, 0), body_color=None):
        """Инициализирует игровой объект."""
        self.position = position
        self.body_color = body_color

    def draw(self, surface, position, fill_color, border_color=BORDER_COLOR):
        """Отрисовывает ячейку на поверхности."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, fill_color, rect)
        pg.draw.rect(surface, border_color, rect, 1)


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self, occupied_positions=[]):
        """Инициализирует яблоко."""
        super().__init__(body_color=APPLE_COLOR)
        self.occupied_positions = occupied_positions
        self.randomize_position(self.occupied_positions)

    def randomize_position(self, occupied_positions):
        """Случайным образом изменяет позицию яблока на поле."""
        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if new_position not in self.occupied_positions:
                break
        self.position = new_position
        self.occupied_positions = occupied_positions

    def draw(self, surface):
        """Отрисовывает яблоко на указанной поверхности."""
        super().draw(surface, self.position, self.body_color)


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        """Инициализация змейки."""
        super().__init__(body_color=SNAKE_COLOR)
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.reset()
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновление направления движения змейки после нажатия на клавишу."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку в новую позицию."""
        head_position = self.get_head_position()
        x, y = self.direction
        new = (
            ((head_position[0] + (x * GRID_SIZE)) % SCREEN_WIDTH),
            ((head_position[1] + (y * GRID_SIZE)) % SCREEN_HEIGHT)
        )
        self.positions.insert(0, new)
        self.last = self.positions.pop() \
            if len(self.positions) > self.length else None

    def check_collisions(self, apple):
        """Проверяет столкновение змейки с яблоком."""
        return self.positions[0] == apple.position

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT

    def draw(self, surface):
        """Отрисовывает змейку на указанной поверхности."""
        for position in self.positions[1:]:
            super().draw(surface, position, self.body_color)

        # Отрисовка головы змейки
        super().draw(surface, self.positions[0], self.body_color, BORDER_COLOR)

        # Затирание последнего сегмента
        if self.last:
            super().draw(
                surface,
                self.last,
                BOARD_BACKGROUND_COLOR,
                BOARD_BACKGROUND_COLOR
            )


def handle_keys(snake):
    """Обрабатывает пользовательский ввод."""
    global SPEED, running, paused
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_PLUS or event.key == pg.K_EQUALS:
                SPEED = min(MAX_SPEED, SPEED + 1)
            elif event.key == pg.K_MINUS:
                SPEED = max(MIN_SPEED, SPEED - 1)
            elif event.key == pg.K_p:
                paused = not paused
            else:
                direction_key = (0, event.key) if event.key == pg.K_p else \
                    (snake.direction, event.key)
                new_direct = DIRECTION_MAP.get(direction_key, snake.direction)
                if (new_direct[0] * -1, new_direct[1] * -1) != snake.direction:
                    snake.next_direction = new_direct
    return True


def main():
    """Основная функция для запуска игры."""
    global running, paused
    pg.init()

    snake = Snake()
    apple = Apple()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    running = True
    paused = False

    while running:
        clock.tick(SPEED)
        handle_keys(snake)
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        pg.display.update()

        if not paused:
            snake.update_direction()
            snake.move()
            if snake.get_head_position() in snake.positions[1:]:
                snake.reset()
            elif snake.check_collisions(apple):
                apple.randomize_position(occupied_positions=snake.positions)
                snake.length += 1

    pg.quit()


if __name__ == '__main__':
    main()
