import pygame
import random
from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_LUMPINESS,
    ASTEROID_SCORES,
    LINE_WIDTH,
)
from logger import log_event


class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-60, 60)

        # Lumpy outline: a ring of vertices at random distances from the centre
        count = random.randint(9, 14)
        self.offsets = []
        for i in range(count):
            angle = 360 / count * i + random.uniform(-10, 10)
            distance = radius * random.uniform(1 - ASTEROID_LUMPINESS, 1.0)
            self.offsets.append(pygame.Vector2(0, distance).rotate(angle))

    @property
    def kind(self) -> int:
        return max(1, round(self.radius / ASTEROID_MIN_RADIUS))

    @property
    def score(self) -> int:
        return ASTEROID_SCORES.get(self.kind, 10)

    def outline(self) -> list[pygame.Vector2]:
        return [self.position + o.rotate(self.rotation) for o in self.offsets]

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.outline(), LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation += self.spin * dt
        self.wrap()

    def split(self):
        # Destroy the current asteroid
        self.kill()

        # Small asteroids don't split
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        # Log the asteroid splitting
        log_event("asteroid_split")

        # Generate a random angle
        angle = random.uniform(20, 50)

        # Rotate the velocity in opposite directions
        velocity1 = self.velocity.rotate(angle)
        velocity2 = self.velocity.rotate(-angle)

        # Calculate the smaller asteroid radius
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        # Create two smaller asteroids
        asteroid1 = Asteroid(
            self.position.x,
            self.position.y,
            new_radius
        )

        asteroid2 = Asteroid(
            self.position.x,
            self.position.y,
            new_radius
        )

        # Make the smaller asteroids move faster
        asteroid1.velocity = velocity1 * 1.2
        asteroid2.velocity = velocity2 * 1.2
