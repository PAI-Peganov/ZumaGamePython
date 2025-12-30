import pygame

def clamp(x: float, a: float, b: float) -> float:
    return max(a, min(b, x))

def safe_normalize(v: pygame.Vector2) -> pygame.Vector2:
    if v.length_squared() < 1e-9:
        return pygame.Vector2(0, 0)
    return v.normalize()
