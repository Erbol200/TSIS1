import pygame
import datetime
import math

class MickeyClock:
    def __init__(self, screen, center):
        self.screen = screen
        self.center = center
        self.hand_image = pygame.image.load("images/mickey_hand.png")
        self.hand_image = pygame.transform.scale(self.hand_image, (200, 40))

    def draw_hand(self, angle, is_minute=True):
        rotated = pygame.transform.rotate(self.hand_image, angle)
        rect = rotated.get_rect(center=self.center)
        self.screen.blit(rotated, rect)

    def draw(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        minute_angle = - (minutes * 6) + 90
        second_angle = - (seconds * 6) + 90

        self.draw_hand(minute_angle, True)

        self.draw_hand(second_angle, False)