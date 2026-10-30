import random
import pygame
from circleshape import CircleShape
from constants import POWERUP_RADIUS, POWERUP_LIFETIME_SECONDS

SHIELD = "shield"
SPEED = "speed"

_STYLES = {
    SHIELD: ("deepskyblue", "S"),
    SPEED: ("gold", "F"),
}


class PowerUp(CircleShape):
    _font: pygame.font.Font | None = None

    def __init__(self, x: float, y: float, kind: str | None = None):
        super().__init__(x, y, POWERUP_RADIUS)
        self.kind = kind or random.choice(list(_STYLES))
        self.lifetime = POWERUP_LIFETIME_SECONDS
        self.velocity = pygame.Vector2(0, random.uniform(15, 35)).rotate(
            random.uniform(0, 360))

    def draw(self, screen: pygame.Surface):
        # Blink during the last couple of seconds before vanishing
        if self.lifetime < 2 and int(self.lifetime * 8) % 2 == 0:
            return
        if PowerUp._font is None:
            PowerUp._font = pygame.font.Font(None, 24)

        color, letter = _STYLES[self.kind]
        pygame.draw.circle(screen, color, self.position, self.radius, 2)
        label = PowerUp._font.render(letter, True, color)
        screen.blit(label, label.get_rect(center=self.position))

    def update(self, dt: float):
        self.position += self.velocity * dt
        self.wrap()
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
