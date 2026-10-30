from __future__ import annotations
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(*self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: pygame.Surface) -> None:
        # must override
        pass

    def update(self, dt: float) -> None:
        # must override
        pass

    def wrap(self) -> None:
        # Once fully off one edge, reappear just off the opposite edge
        r = self.radius
        if self.position.x < -r:
            self.position.x = SCREEN_WIDTH + r
        elif self.position.x > SCREEN_WIDTH + r:
            self.position.x = -r
        if self.position.y < -r:
            self.position.y = SCREEN_HEIGHT + r
        elif self.position.y > SCREEN_HEIGHT + r:
            self.position.y = -r

    def collides_with(self, other: CircleShape) -> bool:
        return self.position.distance_to(other.position) <= self.radius + other.radius
