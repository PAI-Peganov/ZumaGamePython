from src.spiral_trajectory import SpiralTrajectory
from src.zigzag_trajectory import ZigZagTrajectory


class TrajectoryFactory:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def build(self, cfg: dict) -> list[tuple[float, float]]:
        t = cfg["path"]
        match t:
            case "spiral":
                return SpiralTrajectory(
                    self.width, self.height,
                    turns=cfg["turns"],
                    r_start=cfg["r_start"],
                    r_end=cfg["r_end"],
                ).build_points()
            case "zigzag":
                return ZigZagTrajectory(self.width, self.height).build_points()
        return ZigZagTrajectory(self.width, self.height).build_points()
