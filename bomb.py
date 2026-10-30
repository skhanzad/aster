import pygame
from circleshape import CircleShape
from constants import BOMB_RADIUS, BOMB_FUSE_SECONDS


class Bomb(CircleShape):
    """Dropped in place; main.py detonates it once `fuse` runs out."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, BOMB_RADIUS)
        self.fuse = BOMB_FUSE_SECONDS

    @property
    def ready_to_detonate(self) -> bool:
        return self.fuse <= 0

    def draw(self, screen: pygame.Surface):
        # Blink faster as the fuse burns down
        blink_rate = 4 + 12 * (1 - self.fuse / BOMB_FUSE_SECONDS)
        lit = int(self.fuse * blink_rate) % 2 == 0
        pygame.draw.circle(screen, "red" if lit else "darkred", self.position, self.radius)
        pygame.draw.circle(screen, "white", self.position, self.radius, 1)

    def update(self, dt: float):
        self.fuse -= dt
