from __future__ import annotations
from spiral_trajectory import SpiralTrajectory
from zigzag_trajectory import ZigZagTrajectory

class TrajectoryFactory:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def build(self, cfg: dict) -> list[tuple[float, float]]:
        t = cfg["path"]
        if t == "spiral":
            traj = SpiralTrajectory(
                self.width, self.height,
                turns=cfg["turns"],
                r_start=cfg["r_start"],
                r_end=cfg["r_end"],
            )
            return traj.build_points()
        if t == "zigzag":
            return ZigZagTrajectory(self.width, self.height).build_points()
        # fallback
        return ZigZagTrajectory(self.width, self.height).build_points()
