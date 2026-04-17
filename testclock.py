import pygame
import datetime
import math
pygame.init()

screen=pygame.display.set_mode((600,600))
pygame.display.set_caption("Mickey Clock")

WIDTH,HEIGHT=600,600
center=(WIDTH//2,HEIGHT//2)

img=pygame.image.load("images/mickey_hand.png").convert_alpha()
img = pygame.transform.scale(img, (600, 450))

running = True

while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    clock = pygame.time.Clock()
    screen.fill((255,255,255))
    rect = img.get_rect(center=center)
    screen.blit(img, rect)
    
    now=datetime.datetime.now()
    seconds=now.second
    minutes = now.minute + now.second / 60
    
    sec_angel=math.radians(seconds*6-90)
    sec_length=180
    sec_x=center[0]+sec_length*math.cos(sec_angel)
    sec_y=center[1]+sec_length*math.sin(sec_angel)
    pygame.draw.line(screen,(255,0,0),center,(sec_x,sec_y),3)
    
    min_angle = math.radians(minutes * 6 - 90)

    min_length = 130
    min_x = center[0] + min_length * math.cos(min_angle)
    min_y = center[1] + min_length * math.sin(min_angle)
    pygame.draw.line(screen, (0, 0, 0), center, (min_x, min_y), 5)
    
    pygame.draw.circle(screen,(255,0,0),center,5)
    pygame.display.flip()
    
    clock.tick(30)
    
    