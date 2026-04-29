import pygame
import math

def draw_rectangle(surface, color, start, end, width):
    rect = pygame.Rect(min(start[0], end[0]), min(start[1], end[1]), 
                       abs(start[0] - end[0]), abs(start[1] - end[1]))
    pygame.draw.rect(surface, color, rect, width)

def draw_circle(surface, color, start, end, width):
    radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))
    if radius > 0:
        pygame.draw.circle(surface, color, start, radius, width)

def draw_rhombus(surface, color, start, end, width):
    cx, cy = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
    w, h = abs(end[0] - start[0]) // 2, abs(end[1] - start[1]) // 2
    points = [(cx, cy - h), (cx + w, cy), (cx, cy + h), (cx - w, cy)]
    pygame.draw.polygon(surface, color, points, width)