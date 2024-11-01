import random

import pygame

# Константы
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
BACKGROUND_COLOR = (0, 0, 0)  # Черный фон
ALL_CELLS = set(
    (x * CELL_SIZE, y * CELL_SIZE) for x in range(WINDOW_WIDTH // CELL_SIZE) for y in range(WINDOW_HEIGHT // CELL_SIZE))


class Drawable:
    """Базовый класс для всех объектов, которые могут быть отрисованы."""

    def __init__(self):
        self.position = (0, 0)
        self.color = (255, 255, 255)  # Цвет по умолчанию (белый)

    def render(self, surface):
        """Отрисовка объекта на игровом поле. Должен быть переопределён в дочерних классах."""
        pass

    def draw_square(self, surface):
        """Вспомогательный метод для отрисовки квадратов."""
        rect = pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.color, rect)


class Fruit(Drawable):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self, occupied_positions):
        super().__init__()
        self.color = (255, 0, 0)  # Красный цвет
        self.place_randomly(occupied_positions)

    def place_randomly(self, occupied_positions):
        """Устанавливает случайную позицию для фрукта, избегая занятых позиций."""
        available_positions = ALL_CELLS - occupied_positions
        if available_positions:
            self.position = random.choice(tuple(available_positions))

    def render(self, surface):
        """Отрисовывает фрукт на игровом поле."""
        self.draw_square(surface)


class Serpent(Drawable):
    """Класс, описывающий змейку на игровом поле."""

    def __init__(self):
        super().__init__()
        self.size = 1  # Изначально длина змейки 1
        self.body_segments = [(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)]  # Начальная позиция головы
        self.velocity = (CELL_SIZE, 0)  # Движение вправо
        self.next_velocity = None
        self.color = (0, 255, 0)  # Зеленый цвет
        self.last_segment = None  # Позиция последнего сегмента

    def change_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_velocity and self.next_velocity != (-self.velocity[0], -self.velocity[1]):
            self.velocity = self.next_velocity
        self.next_velocity = None

    def advance(self):
        """Обновляет позиции сегментов змейки."""
        head_x, head_y = self.get_head()
        new_head = (head_x + self.velocity[0], head_y + self.velocity[1])

        # Корректируем позицию при выходе за границы
        new_head = (
            new_head[0] % WINDOW_WIDTH,  # При выходе за правую/левую границу
            new_head[1] % WINDOW_HEIGHT  # При выходе за верхнюю/низнюю границу
        )

        # Проверка на столкновение с собой (только если длина больше 1)
        if self.size > 1 and new_head in self.body_segments[1:]:
            self.reset()
            return

        # Обновление списка позиций
        self.last_segment = self.body_segments[-1] if len(
            self.body_segments) > 1 else None  # Сохраняем позицию последнего сегмента
        self.body_segments.insert(0, new_head)  # Вставляем новую позицию головы
        if len(self.body_segments) > self.size:
            self.body_segments.pop()  # Удаляем последний сегмент, если длина изменилась

    def render(self, surface):
        """Отрисовывает змейку на игровом поле."""
        for segment in self.body_segments:
            self.position = segment
            self.draw_square(surface)

        # Стираем след последнего сегмента, если он есть
        if self.last_segment:
            pygame.draw.rect(surface, BACKGROUND_COLOR,
                             (self.last_segment[0], self.last_segment[1], CELL_SIZE, CELL_SIZE))

    def get_head(self):
        """Возвращает позицию головы змейки."""
        return self.body_segments[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.size = 1
        self.body_segments = [(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)]  # Центр экрана
        self.velocity = (CELL_SIZE, 0)  # Начальное движение вправо
        self.last_segment = None


def process_input(snake):
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Завершение игры при нажатии ESC
                pygame.quit()
                exit()
            elif event.key == pygame.K_UP:
                snake.next_velocity = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN:
                snake.next_velocity = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT:
                snake.next_velocity = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT:
                snake.next_velocity = (CELL_SIZE, 0)


def main_loop():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    clock = pygame.time.Clock()

    snake = Serpent()
    fruit = Fruit(set(snake.body_segments))  # Передаем занятые позиции змейки

    while True:
        process_input(snake)
        snake.change_direction()
        snake.advance()

        # Проверка, съела ли змейка фрукт
        if snake.get_head() == fruit.position:
            snake.size += 1
            fruit.place_randomly(set(snake.body_segments))  # Передаем занятые позиции змейки

        # Отрисовка объектов
        window.fill(BACKGROUND_COLOR)  # Очищаем экран
        snake.render(window)
        fruit.render(window)
        pygame.display.set_caption(f'Snake Game - Score: {snake.size}')  # Заголовок с текущим рекордом
        pygame.display.update()

        clock.tick(10)  # Ограничиваем скорость игры


if __name__ == '__main__':
    main_loop()
