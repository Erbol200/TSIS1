import pygame
from pygame.locals import *
import random

pygame.init()

# размеры окна
width = 300
height = 600

screen = pygame.display.set_mode((width,height))

running = True


# ---------------- PLAYER ----------------
class player_car(pygame.sprite.Sprite):
    def __init__(self, path="player_car.png"):
        super().__init__()
        imported_image = pygame.image.load(path)
        self.image = pygame.transform.scale(imported_image,(width//4,height//4))
        self.rect = self.image.get_rect()
        self.rect.center = (47,525)
    
    def move(self):
        button = pygame.key.get_pressed()

        # движение влево / вправо
        if button[K_a]:
            self.rect.centerx -= 5
        elif button[K_d]:
            self.rect.centerx += 5

        # границы дороги
        if self.rect.centerx < 47:
            self.rect.centerx = 47
        if self.rect.centerx > 253:
            self.rect.centerx = 253


# ---------------- ENEMY ----------------
class red_car(pygame.sprite.Sprite):
    def __init__(self, path="enemy_car.png"):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(path),(width//4,height//4))
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(47,253)
        self.rect.centery = -75
        self.score = 0

    def move(self, speed=10):
        self.rect.centery += speed

        # если враг вышел за экран — появляется сверху
        if self.rect.centery > 675:
            self.rect.centery = -75
            self.rect.centerx = random.randint(47,253)
            self.score += 10


# ---------------- COIN ----------------
class coin(pygame.sprite.Sprite):
    def __init__(self, path="coin.png"):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(path),(40,40))
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        # случайная позиция сверху дороги
        self.rect.centerx = random.randint(47,253)
        self.rect.centery = random.randint(-300,-50)

    def move(self):
        self.rect.centery += 5

        # если монета ушла вниз — появляется снова
        if self.rect.centery > 650:
            self.spawn()


# ---------------- BACKGROUND ----------------
class background:
    def __init__(self, path="road.png"):
        imported_image = pygame.image.load(path)
        self.image = pygame.transform.scale(imported_image,(width,height//2))

        rect1 = self.image.get_rect()
        rect2 = self.image.get_rect()
        rect3 = self.image.get_rect()

        rect2.centery += height//2
        rect3.centery += height

        self.rectangles = [rect1, rect2, rect3]

    def draw(self):
        for rectangle in self.rectangles:
            screen.blit(self.image,rectangle)

    def move(self):
        for rectangle in self.rectangles:
            if rectangle.centery > 750:
                rectangle.centery = -150
            rectangle.centery += 3


# ---------------- OBJECTS ----------------
bcg = background()
pc = player_car()
enemy = red_car()

# создаём несколько монет
coins = pygame.sprite.Group()
for i in range(3):
    coins.add(coin())

cars = pygame.sprite.Group()
cars.add(pc)
cars.add(enemy)

enemies = pygame.sprite.Group()
enemies.add(enemy)

coin_count = 0  # счётчик монет


# ---------------- GAME LOOP ----------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # фон
    bcg.draw()
    bcg.move()

    # машины
    for car in cars:
        screen.blit(car.image,car.rect)
        car.move()

    # монеты
    for c in coins:
        screen.blit(c.image, c.rect)
        c.move()

    # проверка сбора монет
    collected = pygame.sprite.spritecollide(pc, coins, False)
    for c in collected:
        coin_count += 1
        c.spawn()

    # ---------------- UI ----------------
    font = pygame.font.SysFont("arial",18)

    # счёт (слева)
    score_text = font.render("Score: "+str(enemy.score), True, (0,0,0))
    screen.blit(score_text,(5,5))

    # монеты (справа сверху)
    coin_text = font.render("Coins: "+str(coin_count), True, (0,0,0))
    coin_rect = coin_text.get_rect(topright=(width-5,5))
    screen.blit(coin_text, coin_rect)

    # ---------------- COLLISION ----------------
    if pygame.sprite.spritecollideany(pc,enemies):
        screen.fill((125,20,20))

        go_font = pygame.font.SysFont("times new roman",18)

        game_over_text = go_font.render(
            "Game Over! Score: "+str(enemy.score)+" Coins: "+str(coin_count),
            True, (20,200,200)
        )

        go_rect = game_over_text.get_rect(center=(width//2,height//2))
        screen.blit(game_over_text,go_rect)

        pygame.display.update()
        pygame.time.delay(4000)
        running = False

    pygame.time.Clock().tick(60)
    pygame.display.flip()