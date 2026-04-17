import pygame
import sys
from music import Track, Playlist, MusicPlayer


tracks = [
    Track("Song 1", "music/song.mp3"),
    Track("Song 2", "music/song2.mp3"),
    
]

playlist = Playlist(tracks)
player = MusicPlayer(playlist)

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Music Player")

font = pygame.font.Font(None, 36)

running = True

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_p:
                player.play()

            elif event.key == pygame.K_s:
                player.stop()

            elif event.key == pygame.K_n:
                player.next()

            elif event.key == pygame.K_b:
                player.previous()

            elif event.key == pygame.K_q:
                running = False

    text = font.render(
        "Now playing: " + player.get_current_title(),
        True,
        (255, 255, 255)
    )
    screen.blit(text, (50, 150))

    controls = font.render(
        "P-Play S-Stop N-Next B-Back Q-Quit",
        True,
        (180, 180, 180)
    )
    screen.blit(controls, (50, 250))

    pygame.display.flip()

pygame.quit()
sys.exit()