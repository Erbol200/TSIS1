import pygame
import sys

pygame.init()
keys = pygame.key.get_pressed()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

radius = 25
x = WIDTH // 2
y = HEIGHT // 2
speed = 20

clock = pygame.time.Clock()

running = True

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        if x - speed - radius >= 0:
            x -= speed

    if keys[pygame.K_RIGHT]:
        if x + speed + radius <= WIDTH:
            x += speed

    if keys[pygame.K_UP]:
        if y - speed - radius >= 0:
            y -= speed

    if keys[pygame.K_DOWN]:
        if y + speed + radius <= HEIGHT:
            y += speed

    pygame.draw.circle(screen, RED, (x, y), radius)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()