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
AMBIENT_MUSIC_FILE = "ambient.mp3"
SFX = {
    "shoot": "kwa_shot.mp3",
    "pop": "red_sign.mp3",
    "powerup": "rdr2_clip.mp3",
    "bomb": "boom.mp3",
    "win": "frog_laugh.mp3",
    "lose": "classic_hurt.mp3",
}

EFFECT_DURATIONS = {
    "SLOW": 5.0,
    "REVERSE": 2.5,
    "SHOT_FAST": 6.0,
    "BURST": 6.0,
}
SHOT_SLOW_MULT = 0.55
SHOT_FAST_MULT = 1.65
SHOT_BASE_SPEED = 700
SHOOT_TIMEOUT = 1.0

BOMB_REMOVE_RADIUS = 2
POWERUP_DROP_CHANCE = 0.18

START_LIVES = 3
LIFE_COST_COINS = 35
COINS_PER_BALL = 1

LEVEL_CONFIGS = [
    dict(
        path="spiral", turns=3.2, r_start=520, r_end=30,
        speed=100.0, balls=26, colors=3, time=75
    ),
    dict(
        path="spiral", turns=3.6, r_start=560, r_end=28,
        speed=185.0, balls=30, colors=4, time=70
    ),
    dict(
        path="zigzag", speed=210.0, balls=34, colors=5, time=65
    ),
]
