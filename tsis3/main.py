import pygame

import random
from tsis3.racer import Player, Enemy

pygame.init()
screen = pygame.display.set_mode((400, 600))
clock = pygame.time.Clock()

# Загрузка фона
bg = pygame.transform.scale(pygame.image.load("assets/road.png"), (400, 600))
bg_y = 0

player = Player()
enemies = pygame.sprite.Group()

running = True
while running:
    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

    # 2. Логика движения фона
    bg_y += 5
    if bg_y >= 600: 
        bg_y = 0

    # 3. Отрисовка фона
    screen.blit(bg, (0, bg_y))
    screen.blit(bg, (0, bg_y - 600))

    # 4. Спавн и обновление врагов
    if random.randint(1, 40) == 1: 
        enemies.add(Enemy(5))
    enemies.update()

    # 5. Движение игрока (клавиши)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.update(-5)
    if keys[pygame.K_RIGHT]: player.update(5)

    # 6. Отрисовка объектов
    screen.blit(player.image, player.rect)
    enemies.draw(screen)

    # 7. Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()