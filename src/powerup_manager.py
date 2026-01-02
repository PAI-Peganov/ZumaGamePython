from src.active_effect import ActiveEffect
from src.settings import EFFECT_DURATIONS, SHOT_SLOW_MULT, SHOT_FAST_MULT


class PowerUpManager:
    def __init__(self):
        self.effects: dict[str, ActiveEffect] = {}
        self.next_shot_bomb = False

    def add(self, kind: str) -> None:
        if kind == "BOMB":
            self.next_shot_bomb = True
            return
        dur = EFFECT_DURATIONS.get(kind, 4.0)
        self.effects[kind] = ActiveEffect(kind, dur)

    def update(self, dt: float) -> None:
        dead = []
        for k, e in self.effects.items():
            e.update(dt)
            if not e.alive():
                dead.append(k)
        for k in dead:
            del self.effects[k]

    def has(self, kind: str) -> bool:
        return kind in self.effects

    def chain_speed_mult(self) -> float:
        return SHOT_SLOW_MULT if self.has("SLOW") else 1.0

    def chain_dir(self) -> int:
        return -1 if self.has("REVERSE") else 1

    def projectile_speed_mult(self) -> float:
        return SHOT_FAST_MULT if self.has("SHOT_FAST") else 1.0

    def burst_enabled(self) -> bool:
        return self.has("BURST")

    def debug_effects_str(self) -> str:
        parts = []
        for k, e in self.effects.items():
            parts.append(f"{k}:{e.time_left:.0f}")
        if self.next_shot_bomb:
            parts.append("BOMB:1")
        return " ".join(parts)
