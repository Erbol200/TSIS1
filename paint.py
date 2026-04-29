import pygame
import datetime
import collections
from tools import draw_rectangle, draw_circle, draw_rhombus

pygame.init()
screen = pygame.display.set_mode((800, 600))
canvas = pygame.Surface((800, 600))
canvas.fill((255, 255, 255))

# Состояния
brush_size, color = 2, (0, 0, 0)
tool, is_drawing, start_pos = "pencil", False, (0, 0)
text_mode, text_input, font = False, "", pygame.font.SysFont("Arial", 24)

def flood_fill(surf, x, y, new_color):
    w, h = surf.get_size()
    old_color = surf.get_at((x, y))
    if old_color == new_color: return
    q = collections.deque([(x, y)])
    while q:
        cx, cy = q.popleft()
        if surf.get_at((cx, cy)) == old_color:
            surf.set_at((cx, cy), new_color)
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h: q.append((nx, ny))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.KEYDOWN:
            # Сейв
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                pygame.image.save(canvas, f"art_{datetime.datetime.now().strftime('%H%M%S')}.png")
            # Размеры: 1, 2, 3
            if event.key == pygame.K_1: brush_size = 2
            if event.key == pygame.K_2: brush_size = 5
            if event.key == pygame.K_3: brush_size = 10
            # Выбор цвета: R-красный, G-зеленый, B-синий, K-черный
            if event.key == pygame.K_r: color = (255,0,0)
            if event.key == pygame.K_g: color = (0,255,0)
            if event.key == pygame.K_b: color = (0,0,255)
            if event.key == pygame.K_k: color = (0,0,0)
            # Выбор инструмента: P-карандаш, L-линия, T-текст, F-заливка, Q-прямоугольник, C-круг
            if event.key == pygame.K_p: tool = "pencil"
            if event.key == pygame.K_l: tool = "line"
            if event.key == pygame.K_t: tool = "text"
            if event.key == pygame.K_f: tool = "fill"
            if event.key == pygame.K_q: tool = "rect"
            if event.key == pygame.K_c: tool = "circle"
            
            # Ввод текста
            if text_mode:
                if event.key == pygame.K_RETURN: canvas.blit(font.render(text_input, True, color), start_pos); text_mode = False; text_input = ""
                elif event.key == pygame.K_ESCAPE: text_mode = False; text_input = ""
                elif event.key == pygame.K_BACKSPACE: text_input = text_input[:-1]
                else: text_input += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = event.pos
            if tool == "fill": flood_fill(canvas, event.pos[0], event.pos[1], color)
            elif tool == "text": text_mode = True
            else: is_drawing = True

        if event.type == pygame.MOUSEBUTTONUP and is_drawing:
            if tool == "line": pygame.draw.line(canvas, color, start_pos, event.pos, brush_size)
            elif tool == "rect": draw_rectangle(canvas, color, start_pos, event.pos, brush_size)
            elif tool == "circle": draw_circle(canvas, color, start_pos, event.pos, brush_size)
            is_drawing = False

    screen.blit(canvas, (0, 0))
    if is_drawing and tool == "pencil":
        pygame.draw.line(canvas, color, start_pos, pygame.mouse.get_pos(), brush_size)
        start_pos = pygame.mouse.get_pos()
    
    if text_mode: screen.blit(font.render(text_input, True, color), start_pos)
    pygame.display.flip()
pygame.quit()