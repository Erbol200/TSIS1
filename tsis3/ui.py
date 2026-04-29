import pygame
class Button:
    def __init__(self, text, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
    def draw(self, screen, font):
        pygame.draw.rect(screen, self.color, self.rect)
        label = font.render(self.text, True, (255,255,255))
        screen.blit(label, (self.rect.x + 10, self.rect.y + 10))
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)