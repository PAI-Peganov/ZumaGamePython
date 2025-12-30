from __future__ import annotations
import random
import pygame

from settings import (
    WIDTH, HEIGHT, FPS, BG_COLOR,
    BALL_RADIUS, PROJECTILE_RADIUS, CHAIN_SPACING,
    COLORS, POWERUP_DROP_CHANCE, BOMB_REMOVE_RADIUS,
    START_LIVES, LIFE_COST_COINS, LEVELS
)
from utils import safe_normalize
from ball_path import BallPath
from trajectory_factory import TrajectoryFactory
from level_manager import LevelManager
from chain import BallChain
from projectile import Projectile
from frog import Frog
from skull import Skull
from pop_effect import PopEffect
from powerup_pickup import PowerUpPickup
from powerup_manager import PowerUpManager
from audio_manager import AudioManager
from save_manager import SaveManager
from cheat_manager import CheatManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zuma OOP (criteria)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.big = pygame.font.SysFont("arial", 44)

        self.rect = self.screen.get_rect()

        self.levels = LevelManager()
        self.factory = TrajectoryFactory(WIDTH, HEIGHT)

        self.frog = Frog((WIDTH // 2, HEIGHT - 80))
        self.aim_dir = pygame.Vector2(1, 0)

        self.audio = AudioManager()
        self.save = SaveManager()
        self.cheats = CheatManager()

        self.state = "MENU"  # MENU | PLAY | PAUSE | GAMEOVER | WIN
        self.score = 0
        self.coins = 0
        self.lives = START_LIVES

        self.power = PowerUpManager()
        self.pickups: list[PowerUpPickup] = []
        self.effects: list[PopEffect] = []
        self.projectiles: list[Projectile] = []

        self.pending_burst: list[float] = []  # таймеры выстрелов очереди
        self._load_level()

        self.audio.play_music()

    def _level_cfg(self) -> dict:
        return LEVELS[self.levels.index]

    def _build_path(self) -> BallPath:
        pts = self.factory.build(self._level_cfg())
        return BallPath(pts)

    def _load_level(self) -> None:
        cfg = self._level_cfg()
        self.time_left = float(cfg["time"])
        self.path = self._build_path()
        self.skull = Skull(tuple(map(int, self.path.pos_at(self.path.length).xy)))
        color_count = int(cfg["colors"])
        self.active_colors = COLORS[:color_count]

        self.chain = BallChain(
            path=self.path,
            colors=self.active_colors,
            ball_radius=BALL_RADIUS,
            spacing=CHAIN_SPACING,
            speed=float(cfg["speed"]),
            count=int(cfg["balls"]),
        )
        # стартуем так, чтобы цепочка была "в начале" и не сразу у черепа
        self.chain.set_head_start(0.0)

        self.pickups.clear()
        self.effects.clear()
        self.projectiles.clear()
        self.pending_burst.clear()
        self.power = PowerUpManager()

        # 2 шара в лягушке
        self.cur_color = random.choice(self.active_colors)
        self.next_color = random.choice(self.active_colors)

    def _swap_colors(self) -> None:
        self.cur_color, self.next_color = self.next_color, self.cur_color

    def _consume_color(self) -> tuple[int, int, int]:
        c = self.cur_color
        self.cur_color = self.next_color
        self.next_color = random.choice(self.active_colors)
        return c

    def _spawn_projectile(self, kind: str = "NORMAL") -> None:
        d = self.aim_dir
        if d.length_squared() < 1e-9:
            d = pygame.Vector2(1, 0)
        d = d.normalize()
        start = self.frog.mouth_pos(d)

        color = self._consume_color()
        speed = 560.0 * self.power.projectile_speed_mult()
        p = Projectile(start, d, speed, color, PROJECTILE_RADIUS, kind=kind)
        self.projectiles.append(p)
        self.audio.sfx("shoot")

    def _shoot(self) -> None:
        if self.state != "PLAY":
            return

        # взрывной выстрел при наличии "BOMB"
        if self.power.next_shot_bomb:
            self.power.next_shot_bomb = False
            self._spawn_projectile(kind="BOMB")
            return

        # очередь
        if self.power.burst_enabled():
            self.pending_burst = [0.0, 0.10, 0.20]
            return

        self._spawn_projectile(kind="NORMAL")

    def _add_pop_effects(self, removed_fx) -> None:
        if removed_fx:
            self.audio.sfx("pop")
        for pos, col, rad in removed_fx:
            self.effects.append(PopEffect(pos, col, rad))

    def _maybe_drop_powerup(self, removed_fx) -> None:
        if not removed_fx:
            return
        if random.random() > POWERUP_DROP_CHANCE:
            return

        # точка дропа = среднее удалённых
        sx = sum(p.x for p, _, _ in removed_fx) / len(removed_fx)
        sy = sum(p.y for p, _, _ in removed_fx) / len(removed_fx)
        kind = random.choice(["SLOW", "REVERSE", "SHOT_FAST", "BOMB", "BURST"])
        self.pickups.append(PowerUpPickup(pygame.Vector2(sx, sy), kind))

    def _lose_life(self) -> None:
        self.lives -= 1
        self.audio.sfx("lose")
        if self.lives <= 0:
            self.state = "GAMEOVER"
        else:
            self._load_level()
            self.state = "PLAY"

    def _win_level(self) -> None:
        ok = self.levels.next_level()
        if not ok:
            self.state = "WIN"
        else:
            self._load_level()
            self.state = "PLAY"

    def _handle_cheats(self, key: int) -> None:
        # F1..F6
        if key == pygame.K_F1:
            self.cheats.infinite_time = not self.cheats.infinite_time
        elif key == pygame.K_F2:
            self.score += 1000
        elif key == pygame.K_F3:
            self._win_level()
        elif key == pygame.K_F4:
            self.power.add(random.choice(["SLOW","REVERSE","SHOT_FAST","BOMB","BURST"]))
        elif key == pygame.K_F5:
            self.audio.toggle_music()
        elif key == pygame.K_F6:
            self.lives += 1

    def _konami_feed(self, key: int) -> None:
        mapping = {
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_a: "A",
            pygame.K_b: "B",
        }
        name = mapping.get(key)
        if name and self.cheats.feed_konami(name):
            # party режим: бонусы всегда доступны (упрощенно: добавим BURST+SHOT_FAST)
            self.power.add("BURST")
            self.power.add("SHOT_FAST")

    def _snapshot(self) -> dict:
        # Сохраняем только то, что реально нужно восстановить
        def c2i(c): return COLORS.index(c) if c in COLORS else 0

        return {
            "level": self.levels.index,
            "state": self.state,
            "score": self.score,
            "coins": self.coins,
            "lives": self.lives,
            "time_left": self.time_left,
            "head_s": self.chain.head_s,
            "balls": [c2i(b.color) for b in self.chain.balls],
            "cur": c2i(self.cur_color),
            "next": c2i(self.next_color),
            "effects": {k: e.time_left for k, e in self.power.effects.items()},
            "next_shot_bomb": self.power.next_shot_bomb,
            "inf_time": self.cheats.infinite_time,
            "party": self.cheats.party,
        }

    def _apply_snapshot(self, data: dict) -> None:
        def i2c(i): return COLORS[max(0, min(len(COLORS)-1, int(i)))]

        self.levels.set_index(int(data.get("level", 0)))
        self.state = data.get("state", "PLAY")
        self.score = int(data.get("score", 0))
        self.coins = int(data.get("coins", 0))
        self.lives = int(data.get("lives", START_LIVES))

        self._load_level()
        self.time_left = float(data.get("time_left", self.time_left))
        self.chain.head_s = float(data.get("head_s", 0.0))

        balls = data.get("balls", [])
        self.chain.balls = []
        for i in balls:
            from ball import Ball
            b = Ball(i2c(i), BALL_RADIUS)
            self.chain.balls.append(b)
        self.chain._recalc_positions()

        self.cur_color = i2c(data.get("cur", 0))
        self.next_color = i2c(data.get("next", 1))

        self.power = PowerUpManager()
        eff = data.get("effects", {})
        for k, t in eff.items():
            try:
                from active_effect import ActiveEffect
                self.power.effects[k] = ActiveEffect(k, float(t))
            except Exception:
                pass
        self.power.next_shot_bomb = bool(data.get("next_shot_bomb", False))

        self.cheats.infinite_time = bool(data.get("inf_time", False))
        self.cheats.party = bool(data.get("party", False))

    def handle_events(self) -> bool:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False

            if e.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if e.key == pygame.K_ESCAPE:
                    if self.state == "MENU":
                        return False
                    if self.state == "PLAY":
                        self.state = "PAUSE"
                    elif self.state == "PAUSE":
                        self.state = "PLAY"

                if e.key == pygame.K_RETURN and self.state == "MENU":
                    self.state = "PLAY"

                if e.key == pygame.K_p and self.state in ("PLAY", "PAUSE"):
                    self.state = "PLAY" if self.state == "PAUSE" else "PAUSE"

                if e.key == pygame.K_r and self.state in ("PLAY", "PAUSE"):
                    self._load_level()
                    self.state = "PLAY"

                if e.key == pygame.K_SPACE and self.state == "PLAY":
                    self._swap_colors()

                if e.key == pygame.K_b and self.state == "PLAY":
                    if self.coins >= LIFE_COST_COINS:
                        self.coins -= LIFE_COST_COINS
                        self.lives += 1

                # save/load
                if (mods & pygame.KMOD_CTRL) and e.key == pygame.K_s:
                    self.save.save(self._snapshot())
                if (mods & pygame.KMOD_CTRL) and e.key == pygame.K_l:
                    data = self.save.load()
                    if data:
                        self._apply_snapshot(data)

                self._handle_cheats(e.key)
                self._konami_feed(e.key)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == "MENU":
                    self.state = "PLAY"
                else:
                    self._shoot()

        return True

    def update(self, dt: float) -> None:
        # aim
        m = pygame.mouse.get_pos()
        self.aim_dir = safe_normalize(pygame.Vector2(m) - self.frog.pos)
        if self.aim_dir.length_squared() < 1e-9:
            self.aim_dir = pygame.Vector2(1, 0)

        if self.state != "PLAY":
            return

        # время
        if not self.cheats.infinite_time:
            self.time_left -= dt
            if self.time_left <= 0:
                self._lose_life()
                return

        # бонусы
        self.power.update(dt)

        # очередь
        if self.pending_burst:
            self.pending_burst = [t - dt for t in self.pending_burst]
            while self.pending_burst and self.pending_burst[0] <= 0:
                self.pending_burst.pop(0)
                self._spawn_projectile(kind="NORMAL")

        # цепочка
        self.chain.update(dt, self.power.chain_speed_mult(), self.power.chain_dir())

        # снаряды
        for p in self.projectiles:
            p.update(dt, self.rect)

        # столкновения
        for p in self.projectiles:
            if not p.alive:
                continue
            idx = self.chain.try_insert(p.pos, p.radius, p.color)
            if idx is None:
                continue

            p.alive = False

            if p.kind == "BOMB":
                removed_fx = self.chain.bomb_remove(idx, BOMB_REMOVE_RADIUS)
                self.audio.sfx("bomb")
            else:
                removed_fx = self.chain.pop_color_group(idx)

            if removed_fx:
                self.score += len(removed_fx) * 10
                self.coins += self.chain.coins_for_removed(len(removed_fx))
                self._add_pop_effects(removed_fx)
                self._maybe_drop_powerup(removed_fx)

        self.projectiles = [p for p in self.projectiles if p.alive]

        # эффекты
        for fx in self.effects:
            fx.update(dt)
        self.effects = [fx for fx in self.effects if fx.alive]

        # бонус-пикапы
        for pu in self.pickups:
            pu.update(dt, self.frog.pos)
            if not pu.alive:
                self.power.add(pu.kind)
                self.audio.sfx("powerup")
        self.pickups = [pu for pu in self.pickups if pu.alive]

        # проигрыш у черепа
        if self.chain.head_reached_end():
            self._lose_life()
            return

        # победа по уровню
        if not self.chain.balls:
            self._win_level()

    def draw(self) -> None:
        if self.cheats.party:
            self.screen.fill((18, 10, 30))
        else:
            self.screen.fill(BG_COLOR)

        # путь
        pygame.draw.lines(self.screen, (80, 80, 95), False, [(int(x), int(y)) for x, y in self.path.points], 4)

        # череп
        self.skull.draw(self.screen)

        # шары цепи
        for b in self.chain.balls:
            pygame.draw.circle(self.screen, b.color, (int(b.pos.x), int(b.pos.y)), b.radius)

        # эффекты удаления
        for fx in self.effects:
            fx.draw(self.screen)

        # пикапы бонусов
        for pu in self.pickups:
            pu.draw(self.screen)

        # снаряды
        for p in self.projectiles:
            pygame.draw.circle(self.screen, p.color, (int(p.pos.x), int(p.pos.y)), p.radius)
            if p.kind == "BOMB":
                pygame.draw.circle(self.screen, (255, 255, 255), (int(p.pos.x), int(p.pos.y)), p.radius, 2)

        # лягушка
        self.frog.draw(self.screen, self.aim_dir)

        # 2 шара в лягушке
        aim = self.aim_dir.normalize()
        side = pygame.Vector2(-aim.y, aim.x)
        mouth = self.frog.mouth_pos(aim)
        cur_pos = mouth - aim * 16
        next_pos = self.frog.pos - side * 22 + aim * 6
        pygame.draw.circle(self.screen, self.cur_color, (int(cur_pos.x), int(cur_pos.y)), 12)
        pygame.draw.circle(self.screen, self.next_color, (int(next_pos.x), int(next_pos.y)), 10)

        # HUD
        lvl = self.levels.index + 1
        hud1 = f"Level {lvl}/{len(LEVELS)}  Score:{self.score}  Coins:{self.coins}  Lives:{self.lives}"
        hud2 = f"Time:{max(0,int(self.time_left))}  Effects:{self.power.debug_effects_str()}"
        if self.cheats.infinite_time:
            hud2 += "  [INF_TIME]"
        if self.cheats.party:
            hud2 += "  [PARTY]"

        self.screen.blit(self.font.render(hud1, True, (235, 235, 245)), (16, 14))
        self.screen.blit(self.font.render(hud2, True, (235, 235, 245)), (16, 40))
        self.screen.blit(self.font.render("LMB shoot | Space swap | P pause | Ctrl+S/L save/load | B buy life", True, (210,210,220)), (16, HEIGHT-28))

        # overlays
        if self.state == "MENU":
            t = self.big.render("ZUMA", True, (240, 240, 250))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 190))
            s = self.font.render("Enter / LMB to start. Esc to quit. Konami: ↑↑↓↓←→←→BA", True, (220,220,235))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 260))
        elif self.state == "PAUSE":
            t = self.big.render("PAUSE", True, (255, 240, 200))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
        elif self.state == "GAMEOVER":
            t = self.big.render("GAME OVER", True, (255, 170, 170))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
            s = self.font.render("Press R to restart, Esc to menu", True, (235,235,245))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 300))
        elif self.state == "WIN":
            t = self.big.render("YOU WIN!", True, (170, 255, 170))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
            s = self.font.render("Esc to menu", True, (235,235,245))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 300))

        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
