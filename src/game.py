import random
import pygame

from settings import (
    WIDTH, HEIGHT, FPS, BG_COLOR, SHOOT_TIMEOUT, SHOT_BASE_SPEED,
    BALL_RADIUS, PROJECTILE_RADIUS, CHAIN_SPACING,
    COLORS, POWERUP_DROP_CHANCE, BOMB_REMOVE_RADIUS,
    START_LIVES, LIFE_COST_COINS, COINS_PER_BALL, LEVEL_CONFIGS
)
from utils import safe_normalize
from game_path import GamePath
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
        pygame.display.set_caption("Zuma - PAI | little_darkness")
        self.clock = pygame.time.Clock()
        self.font_s = pygame.font.SysFont("arial", 20)
        self.font_h = pygame.font.SysFont("arial", 44)

        self.rect = self.screen.get_rect()

        self.audio = AudioManager()
        self.saver = SaveManager()
        self.cheats = CheatManager()

        self._build_new_game()

    def _build_new_game(self):
        self.level_manager = LevelManager()
        self.traj_factory = TrajectoryFactory(WIDTH, HEIGHT)

        self.frog = Frog((WIDTH // 2, HEIGHT - 80))
        self.aim_dir = pygame.Vector2(1, 0)

        self.state = "MENU"
        self.shoot_timeout = 0.0
        self.score = 0
        self.coins = 0
        self.lives = START_LIVES

        self.power = PowerUpManager()
        self.pickups: list[PowerUpPickup] = []
        self.effects: list[PopEffect] = []
        self.projectiles: list[Projectile] = []

        self.pending_burst: list[float] = []
        self._load_level()

        self.audio.play_ambient_music()

    def _level_cfg(self) -> dict:
        return LEVEL_CONFIGS[self.level_manager.index]

    def _load_level(self) -> None:
        cfg = self._level_cfg()
        self.time_left = float(cfg["time"])
        self.path = GamePath(self.traj_factory.build(cfg))
        self.skull = Skull(self.path.pos_at(self.path.length))
        self.active_colors = COLORS[:int(cfg["colors"])]

        self.chain = BallChain(
            path=self.path,
            colors=self.active_colors,
            ball_radius=BALL_RADIUS,
            spacing=CHAIN_SPACING,
            speed=float(cfg["speed"]),
            count=int(cfg["balls"]),
        )
        self.chain.set_head_start(0.0)

        self.pickups.clear()
        self.effects.clear()
        self.projectiles.clear()
        self.pending_burst.clear()
        self.power = PowerUpManager()

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
        speed = SHOT_BASE_SPEED * self.power.projectile_speed_mult()
        p = Projectile(start, d, speed, color, PROJECTILE_RADIUS, kind=kind)
        self.projectiles.append(p)
        self.audio.sfx("shoot")

    def _shoot(self) -> None:
        if self.state != "PLAY":
            return
        self.shoot_timeout = SHOOT_TIMEOUT

        if self.power.next_shot_bomb:
            self.power.next_shot_bomb = False
            self._spawn_projectile(kind="BOMB")
            return

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
        next_exists = self.level_manager.next_level()
        self.audio.sfx("win")
        if not next_exists:
            self.state = "WIN"
        else:
            self._load_level()
            self.state = "PLAY"

    def _handle_base_cheats(self, key: int) -> None:
        if key == pygame.K_F1:
            self.cheats.infinite_time = not self.cheats.infinite_time
        elif key == pygame.K_F2:
            self.score += 1000
        elif key == pygame.K_F3:
            self._win_level()
        elif key == pygame.K_F4:
            self.power.add(random.choice([
                "SLOW", "REVERSE", "SHOT_FAST", "BOMB", "BURST"
            ]))
        elif key == pygame.K_F5:
            self.audio.toggle_ambient_music()
        elif key == pygame.K_F6:
            self.lives += 1

    def _sequences_feed(self, key: int) -> None:
        mapping = {
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_a: "A",
            pygame.K_b: "B",
        }
        name = mapping.get(key)
        if name and self.cheats.feed_sequences(name):
            self.power.add("BURST")
            self.power.add("SHOT_FAST")

    def _snapshot(self) -> dict:
        def c2i(c): return COLORS.index(c) if c in COLORS else 0

        return {
            "level": self.level_manager.index,
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

        self.level_manager.set_index(int(data.get("level", 0)))
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

    def handle_events(self, events: list[pygame.event.Event]) -> bool:
        for e in events:
            if e.type == pygame.QUIT:
                return False

            if e.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()

                if e.key == pygame.K_ESCAPE:
                    if self.state in ("MENU", "GAMEOVER"):
                        return False
                    if self.state == "PLAY":
                        self.state = "PAUSE"
                    elif self.state == "PAUSE":
                        self.state = "PLAY"
                    elif self.state == "WIN":
                        self._build_new_game()

                if e.key == pygame.K_RETURN and self.state == "MENU":
                    self.state = "PLAY"

                if e.key == pygame.K_p and self.state in ("PLAY", "PAUSE"):
                    self.state = "PLAY" if self.state == "PAUSE" else "PAUSE"

                if e.key == pygame.K_r and self.state in (
                        "PLAY", "PAUSE", "GAMEOVER"
                ):
                    if self.state == "GAMEOVER":
                        self._build_new_game()
                    else:
                        self._load_level()
                    self.state = "PLAY"

                if e.key == pygame.K_SPACE and self.state == "PLAY":
                    self._swap_colors()

                if e.key == pygame.K_b and self.state == "PLAY":
                    if self.coins >= LIFE_COST_COINS:
                        self.coins -= LIFE_COST_COINS
                        self.lives += 1

                if (mods & pygame.KMOD_CTRL) and e.key == pygame.K_s:
                    self.saver.save(self._snapshot())
                if (mods & pygame.KMOD_CTRL) and e.key == pygame.K_l:
                    data = self.saver.load()
                    if data:
                        self._apply_snapshot(data)

                self._handle_base_cheats(e.key)
                self._sequences_feed(e.key)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == "MENU":
                    self.state = "PLAY"
                elif self.shoot_timeout <= 0:
                    self._shoot()
        return True

    def _update_aim(self):
        m = pygame.mouse.get_pos()
        self.aim_dir = safe_normalize(pygame.Vector2(m) - self.frog.pos)
        if self.aim_dir.length_squared() < 1e-9:
            self.aim_dir = pygame.Vector2(1, 0)

    def _update_queue(self, dt: float):
        if self.pending_burst:
            self.pending_burst = [t - dt for t in self.pending_burst]
            while self.pending_burst and self.pending_burst[0] <= 0:
                self.pending_burst.pop(0)
                self._spawn_projectile(kind="NORMAL")

    def _update_projectiles(self, dt: float):
        for p in self.projectiles:
            p.update(dt, self.rect)
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
                self.coins += len(removed_fx) * COINS_PER_BALL
                self._add_pop_effects(removed_fx)
                self._maybe_drop_powerup(removed_fx)
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _update_effects(self, dt: float):
        for fx in self.effects:
            fx.update(dt)
        self.effects = [fx for fx in self.effects if fx.alive]

    def _update_pickups(self, dt: float):
        for pu in self.pickups:
            pu.update(dt, self.frog.pos)
            if not pu.alive:
                self.power.add(pu.kind)
                self.audio.sfx("powerup")
        self.pickups = [pu for pu in self.pickups if pu.alive]

    def update(self, dt: float) -> None:
        self.shoot_timeout -= dt
        self._update_aim()

        if self.state != "PLAY":
            return
        if not self.cheats.infinite_time:
            self.time_left -= dt
            if self.time_left <= 0:
                self._lose_life()
                return

        self.power.update(dt)
        self._update_queue(dt)
        self.chain.update(
            dt, self.power.chain_speed_mult(), self.power.chain_dir()
        )
        self._update_projectiles(dt)
        self._update_effects(dt)
        self._update_pickups(dt)

        if self.chain.head_reached_end():
            self._lose_life()
            return
        if not self.chain.balls:
            self._win_level()

    def _draw_frog(self):
        aim = self.aim_dir.normalize()
        side = pygame.Vector2(-aim.y, aim.x)
        mouth = self.frog.mouth_pos(aim)
        cur_pos = mouth + aim * 2
        next_pos = mouth - side * 16 - aim * 2
        pygame.draw.circle(
            self.screen, self.next_color, (int(next_pos.x), int(next_pos.y)), 8
        )
        pygame.draw.circle(
            self.screen, self.cur_color, (int(cur_pos.x), int(cur_pos.y)), 12
        )
        self.frog.draw(self.screen, self.aim_dir)

    def _draw_hud(self):
        lvl = self.level_manager.index + 1
        hud1 = "Level {}/{}  Score:{}  Coins:{}  Lives:{}".format(
            lvl, len(LEVEL_CONFIGS), self.score, self.coins, self.lives
        )
        hud2 = "Time:{}  Effects:{}".format(
            max(0, int(self.time_left)), self.power.debug_effects_str()
        )
        if self.cheats.infinite_time:
            hud2 += "  [INF_TIME]"
        if self.cheats.party:
            hud2 += "  [PARTY]"

        self.screen.blit(
            self.font_s.render(hud1, True, (235, 235, 245)), (16, 14)
        )
        self.screen.blit(
            self.font_s.render(hud2, True, (235, 235, 245)), (16, 40)
        )
        self.screen.blit(self.font_s.render(
            "LMB shoot | Space swap | P pause | Ctrl+S/L save/load | B buy life",
            True, (210, 210, 220)
        ), (16, HEIGHT - 28))

    def _draw_overlays(self):
        if self.state == "MENU":
            t = self.font_h.render("ZUMA", True, (240, 240, 250))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 190))
            s = self.font_s.render(
                "Enter / LMB to start. Esc to quit. Konami: ↑↑↓↓←→←→BA", True,
                (220, 220, 235)
            )
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 260))
        elif self.state == "PAUSE":
            t = self.font_h.render("PAUSE", True, (255, 240, 200))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
        elif self.state == "GAMEOVER":
            t = self.font_h.render("GAME OVER", True, (255, 170, 170))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
            s = self.font_s.render(
                "Press R to restart, Esc to menu", True, (235, 235, 245)
            )
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 300))
        elif self.state == "WIN":
            t = self.font_h.render("YOU WIN!", True, (170, 255, 170))
            self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 240))
            s = self.font_s.render("Esc to menu", True, (235, 235, 245))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 300))

    def draw(self) -> None:
        if self.cheats.party:
            self.screen.fill((18, 10, 30))
        else:
            self.screen.fill(BG_COLOR)

        pygame.draw.lines(self.screen, (80, 80, 95), False, [
            (int(x), int(y)) for x, y in self.path.points
        ], 4)
        self.skull.draw(self.screen)
        for b in self.chain.balls:
            pygame.draw.circle(
                self.screen, b.color, (int(b.pos.x), int(b.pos.y)), b.radius
            )
        for fx in self.effects:
            fx.draw(self.screen)
        for pu in self.pickups:
            pu.draw(self.screen)
        for p in self.projectiles:
            pygame.draw.circle(
                self.screen, p.color, (int(p.pos.x), int(p.pos.y)), p.radius
            )
            if p.kind == "BOMB":
                pygame.draw.circle(
                    self.screen, (255, 255, 255), (int(p.pos.x), int(p.pos.y)),
                    p.radius, 2
                )
        self._draw_frog()
        self._draw_hud()
        self._draw_overlays()
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events(pygame.event.get())
            self.update(dt)
            self.draw()
        pygame.quit()
