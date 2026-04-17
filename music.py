import pygame


class Track:
    def __init__(self, title, path):
        self.title = title
        self.path = path


class Playlist:
    def __init__(self, tracks):
        if not tracks:
            raise ValueError("Playlist cannot be empty")

        self.tracks = tracks
        self.index = 0

    def current(self):
        return self.tracks[self.index]

    def next(self):
        self.index = (self.index + 1) % len(self.tracks)
        return self.current()

    def previous(self):
        self.index = (self.index - 1) % len(self.tracks)
        return self.current()


class MusicPlayer:
    def __init__(self, playlist):
        self.playlist = playlist
        pygame.mixer.init()
        self.is_playing = False

    def load_current(self):
        track = self.playlist.current()
        pygame.mixer.music.load(track.path)

    def play(self):
        self.load_current()
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def resume(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def next(self):
        self.playlist.next()
        self.play()

    def previous(self):
        self.playlist.previous()
        self.play()

    def get_current_title(self):
        return self.playlist.current().title