WIDTH = 900
HEIGHT = 700
FPS = 60

BG_COLOR = (18, 18, 24)

BALL_RADIUS = 14
PROJECTILE_RADIUS = 10
CHAIN_SPACING = BALL_RADIUS * 2 + 2

COLORS = [
    (235, 70, 70),
    (70, 210, 95),
    (70, 140, 235),
    (235, 210, 70),
    (190, 90, 220),
]

ASSETS_DIR = "assets"
MUSIC_FILE = "music.ogg"
SFX = {
    "shoot": "shoot.wav",
    "pop": "pop.wav",
    "powerup": "powerup.wav",
    "bomb": "bomb.wav",
    "lose": "lose.wav",
}

# Бонусы (секунды)
EFFECT_DURATIONS = {
    "SLOW": 5.0,
    "REVERSE": 2.5,
    "SHOT_FAST": 6.0,
    "BURST": 6.0,
}
SLOW_MULT = 0.55
SHOT_FAST_MULT = 1.65

BOMB_REMOVE_RADIUS = 2     # сколько шаров слева/справа выносит бомба
POWERUP_DROP_CHANCE = 0.18

START_LIVES = 3
LIFE_COST_COINS = 35
COINS_PER_BALL = 1

LEVELS = [
    # 1) Спираль, мало цветов, больше времени
    dict(path="spiral", turns=3.2, r_start=520, r_end=30,
         speed=150.0, balls=26, colors=3, time=75),
    # 2) Спираль быстрее, больше цветов
    dict(path="spiral", turns=3.6, r_start=560, r_end=28,
         speed=185.0, balls=30, colors=4, time=70),
    # 3) Змейка-траектория (вариативно)
    dict(path="zigzag", speed=210.0, balls=34, colors=5, time=65),
]
