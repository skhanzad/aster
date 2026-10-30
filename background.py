import os
import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

BACKGROUND_IMAGE = os.path.join(os.path.dirname(__file__), "assets", "background.png")


def load_background() -> pygame.Surface:
    """Use assets/background.png if present, otherwise generate a starfield."""
    if os.path.exists(BACKGROUND_IMAGE):
        image = pygame.image.load(BACKGROUND_IMAGE).convert()
        return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    return _starfield()


def _starfield() -> pygame.Surface:
    rng = random.Random(42)  # same sky every run
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Vertical gradient from deep navy to black
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        surface.fill((int(10 * (1 - t)), int(8 * (1 - t)), int(30 * (1 - t)) + 4),
                     (0, y, SCREEN_WIDTH, 1))

    # A few faint nebula blobs
    nebula = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for _ in range(6):
        center = (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT))
        color = rng.choice([(80, 40, 120), (30, 60, 120), (100, 30, 60)])
        for r in range(220, 0, -20):
            pygame.draw.circle(nebula, (*color, 3), center, r)
    surface.blit(nebula, (0, 0))

    # Stars of varying brightness
    for _ in range(350):
        pos = (rng.randint(0, SCREEN_WIDTH - 1), rng.randint(0, SCREEN_HEIGHT - 1))
        b = rng.randint(70, 255)
        if rng.random() < 0.08:
            pygame.draw.circle(surface, (b, b, b), pos, 1)
        else:
            surface.set_at(pos, (b, b, min(255, b + 20)))

    return surface
