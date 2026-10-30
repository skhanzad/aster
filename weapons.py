from dataclasses import dataclass


@dataclass(frozen=True)
class Weapon:
    name: str
    cooldown: float
    speed: float
    angles: tuple[float, ...]  # one shot per angle, relative to the ship
    radius: float
    color: str
    lifetime: float


WEAPONS = [
    Weapon("Blaster", cooldown=0.3, speed=500, angles=(0,), radius=5,
           color="white", lifetime=1.2),
    Weapon("Spread", cooldown=0.55, speed=450, angles=(-15, 0, 15), radius=4,
           color="orange", lifetime=0.8),
    Weapon("Rapid", cooldown=0.09, speed=700, angles=(0,), radius=3,
           color="cyan", lifetime=0.9),
]
