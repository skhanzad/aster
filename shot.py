
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, SHOT_LIFETIME_SECONDS


class Shot(CircleShape):
    def __init__(self, x: float, y: float, radius: float = SHOT_RADIUS,
                 color: str = "white", lifetime: float = SHOT_LIFETIME_SECONDS):
        super().__init__(x, y, radius)
        self.color = color
        self.lifetime = lifetime

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.position, self.radius, 2)

    def update(self, dt: float):
        self.position += self.velocity * dt
        self.wrap()

        # Shots wrap too, so they need to expire on their own
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
