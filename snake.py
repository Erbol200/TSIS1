import pygame
import random

pygame.init()

# --- НАСТРОЙКИ ---
WIDTH, HEIGHT = 600, 400
CELL = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()

# --- ЦВЕТА ---
WHITE = (255,255,255)
GREEN = (50,200,50)
RED = (200,0,0)
ORANGE = (200,120,0)
BLACK = (0,0,0)

# --- ЗМЕЯ ---
snake = [[50,50],[60,50],[70,50]]
direction = "RIGHT"

# --- ЕДА ---
def spawn_food():
    """Создаёт еду в случайном месте (не на змее)"""
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if [x,y] not in snake:
            return [x,y]

food = spawn_food()

# --- ИГРА ---
score = 0
level = 1
speed = 10   # начальная скорость

running = True

while running:

    # --- СОБЫТИЯ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # --- УПРАВЛЕНИЕ ---
    if keys[pygame.K_UP] and direction != "DOWN":
        direction = "UP"
    elif keys[pygame.K_DOWN] and direction != "UP":
        direction = "DOWN"
    elif keys[pygame.K_LEFT] and direction != "RIGHT":
        direction = "LEFT"
    elif keys[pygame.K_RIGHT] and direction != "LEFT":
        direction = "RIGHT"

    # --- ДВИЖЕНИЕ ---
    head = snake[-1].copy()

    if direction == "RIGHT":
        head[0] += CELL
    elif direction == "LEFT":
        head[0] -= CELL
    elif direction == "UP":
        head[1] -= CELL
    elif direction == "DOWN":
        head[1] += CELL

    # --- ПРОВЕРКА СТОЛКНОВЕНИЙ С ГРАНИЦАМИ ---
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        print("Game Over: Wall collision")
        running = False

    # --- ПРОВЕРКА СТОЛКНОВЕНИЯ С СОБОЙ ---
    if head in snake:
        print("Game Over: Self collision")
        running = False

    snake.append(head)

    # --- ПРОВЕРКА ЕДЫ ---
    if head == food:
        score += 1

        # --- УРОВНИ ---
        if score % 3 == 0:   # каждые 3 очка новый уровень
            level += 1
            speed += 2       # увеличение скорости

        food = spawn_food()
    else:
        snake.pop(0)

    # --- ОТРИСОВКА ---
    screen.fill(WHITE)

    # змейка
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL, CELL))

    # еда
    pygame.draw.rect(screen, ORANGE, (food[0], food[1], CELL, CELL))

    # --- ТЕКСТ ---
    font = pygame.font.SysFont("times new roman", 20)

    score_text = font.render(f"Score: {score}", True, BLACK)
    level_text = font.render(f"Level: {level}", True, BLACK)

    screen.blit(score_text, (10,10))
    screen.blit(level_text, (10,30))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()