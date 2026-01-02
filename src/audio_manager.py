import os
import pygame
from settings import ASSETS_DIR, AMBIENT_MUSIC_FILE, SFX


class AudioManager:
    def __init__(self):
        self.enabled = True
        self.ok = False
        try:
            pygame.mixer.init()
            self.ok = True
        except Exception:
            print("Audio not managed")
            self.ok = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._load()

    def _load(self) -> None:
        if not self.ok:
            return
        for name, fn in SFX.items():
            path = os.path.join(ASSETS_DIR, fn)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception:
                    pass

    def play_ambient_music(self) -> None:
        if not self.ok or not self.enabled:
            return
        path = os.path.join(ASSETS_DIR, AMBIENT_MUSIC_FILE)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    def toggle_ambient_music(self) -> None:
        self.enabled = not self.enabled
        if not self.ok:
            return
        try:
            if self.enabled:
                self.play_ambient_music()
            else:
                pygame.mixer.music.stop()
        except Exception:
            pass

    def sfx(self, clip_name: str) -> None:
        if not self.ok or not self.enabled:
            return
        sound_clip = self.sounds.get(clip_name)
        if sound_clip:
            try:
                sound_clip.play()
            except Exception:
                pass
