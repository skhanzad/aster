import random
import pygame
from constants import EXPLOSION_LIFETIME_SECONDS


class Explosion(pygame.sprite.Sprite):
    """A burst of fading particles, with an optional expanding shockwave ring."""

    containers: tuple[pygame.sprite.Group, ...]

    def __init__(self, position: pygame.Vector2, size: float, color="white",
                 ring_radius: float = 0, lifetime: float = EXPLOSION_LIFETIME_SECONDS):
        super().__init__(*self.containers)
        self.position = pygame.Vector2(position)
        self.color = pygame.Color(color)
        self.ring_radius = ring_radius
        self.lifetime = lifetime
        self.age = 0.0

        # Each particle: [position, velocity]
        self.particles = []
        for _ in range(int(8 + size / 2)):
            velocity = pygame.Vector2(0, random.uniform(size, size * 4)).rotate(
                random.uniform(0, 360))
            self.particles.append([pygame.Vector2(position), velocity])

    def update(self, dt: float) -> None:
        self.age += dt
        if self.age >= self.lifetime:
            self.kill()
            return
        for particle in self.particles:
            particle[0] += particle[1] * dt
            particle[1] *= 0.94

    def draw(self, screen: pygame.Surface) -> None:
        fade = max(0.0, 1 - self.age / self.lifetime)
        color = pygame.Color(self.color)
        color.r, color.g, color.b = (int(c * fade) for c in (color.r, color.g, color.b))

        for pos, _ in self.particles:
            pygame.draw.circle(screen, color, pos, max(1, 3 * fade))

        if self.ring_radius:
            radius = self.ring_radius * (self.age / self.lifetime) ** 0.5
            if radius > 2:
                pygame.draw.circle(screen, color, self.position, radius, 3)
