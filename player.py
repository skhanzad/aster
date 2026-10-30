from circleshape import CircleShape
from constants import *
import pygame
from shot import Shot
from bomb import Bomb
from powerup import SHIELD, SPEED
from weapons import WEAPONS


def _point_in_triangle(p, a, b, c) -> bool:
    def sign(p1, p2, p3):
        return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

    d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def _distance_to_segment(p, a, b) -> float:
    ab = b - a
    if ab.length_squared() == 0:
        return p.distance_to(a)
    t = max(0, min(1, (p - a).dot(ab) / ab.length_squared()))
    return p.distance_to(a + ab * t)


class Player(CircleShape):
    rotation: int = 0
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.spawn_point = pygame.Vector2(x, y)
        self.rotation = 0
        self.shoot_timer = 0
        self.thrusting = False

        self.lives = PLAYER_LIVES
        self.bombs = BOMB_START_COUNT
        self.weapon_index = 0

        self.respawn_timer = 0.0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS
        self.shield_timer = 0.0
        self.speed_timer = 0.0

    # --- state ---------------------------------------------------------------

    @property
    def weapon(self):
        return WEAPONS[self.weapon_index]

    @property
    def is_dead(self) -> bool:
        return self.lives <= 0 or self.respawn_timer > 0

    @property
    def is_vulnerable(self) -> bool:
        return not self.is_dead and self.invulnerable_timer <= 0

    @property
    def shield_radius(self) -> float:
        return self.radius * 1.6

    def hit(self) -> bool:
        """Handle an asteroid hit. Returns True if the ship was destroyed."""
        if self.shield_timer > 0:
            self.shield_timer = 0
            self.invulnerable_timer = 1.0
            return False

        self.lives -= 1
        self.velocity = pygame.Vector2(0, 0)
        if self.lives > 0:
            self.respawn_timer = PLAYER_RESPAWN_DELAY_SECONDS
        return True

    def respawn(self):
        self.position = pygame.Vector2(self.spawn_point)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.speed_timer = 0
        self.shield_timer = 0
        self.invulnerable_timer = PLAYER_INVULNERABLE_SECONDS

    def apply_powerup(self, kind: str):
        if kind == SHIELD:
            self.shield_timer = SHIELD_DURATION_SECONDS
        elif kind == SPEED:
            self.speed_timer = SPEED_BOOST_DURATION_SECONDS

    # --- geometry ------------------------------------------------------------

    def triangle(self) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def collides_with(self, other: CircleShape) -> bool:
        # The shield is round; the bare ship uses its actual triangle
        if self.shield_timer > 0:
            return self.position.distance_to(other.position) <= self.shield_radius + other.radius

        a, b, c = self.triangle()
        center, r = other.position, other.radius
        if _point_in_triangle(center, a, b, c):
            return True
        return any(_distance_to_segment(center, p, q) <= r
                   for p, q in ((a, b), (b, c), (c, a)))

    # --- drawing -------------------------------------------------------------

    def draw(self, screen):
        if self.is_dead:
            return
        # Blink while invulnerable after respawning
        if self.invulnerable_timer > 0 and int(self.invulnerable_timer * 10) % 2 == 0:
            return

        tri = self.triangle()
        if self.thrusting:
            back = (tri[1] + tri[2]) / 2
            backward = pygame.Vector2(0, -1).rotate(self.rotation)
            flame_len = self.radius * (0.8 if self.speed_timer <= 0 else 1.4)
            flame = [tri[1].lerp(back, 0.4), back + backward * flame_len, tri[2].lerp(back, 0.4)]
            color = "orange" if self.speed_timer <= 0 else "gold"
            pygame.draw.polygon(screen, color, flame, LINE_WIDTH)

        pygame.draw.polygon(screen, "white", tri, LINE_WIDTH)

        if self.shield_timer > 0:
            # Flicker when the shield is about to run out
            if self.shield_timer > 2 or int(self.shield_timer * 8) % 2 == 0:
                pygame.draw.circle(screen, "deepskyblue", self.position, self.shield_radius, 2)

    # --- movement & actions --------------------------------------------------

    def rotate(self, dt: float):
        self.rotation += PLAYER_TURN_SPEED  * dt

    def accelerate(self, dt: float):
        boost = SPEED_BOOST_MULTIPLIER if self.speed_timer > 0 else 1
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.velocity += forward * PLAYER_ACCELERATION * boost * dt

    def update(self, dt: float) -> None:
        if self.lives <= 0:
            return
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn()
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)

        self.thrusting = keys[pygame.K_w]
        if keys[pygame.K_w]:
            self.accelerate(dt)
        if keys[pygame.K_s]:
            self.accelerate(-dt / 2)  # reverse thrusters are weaker
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.velocity *= max(0, 1 - PLAYER_DRAG * dt)

        boost = SPEED_BOOST_MULTIPLIER if self.speed_timer > 0 else 1
        if self.velocity.length() > PLAYER_MAX_SPEED * boost:
            self.velocity.scale_to_length(PLAYER_MAX_SPEED * boost)

        self.position += self.velocity * dt
        self.wrap()

        for i, key in enumerate((pygame.K_1, pygame.K_2, pygame.K_3)):
            if keys[key] and i < len(WEAPONS):
                self.weapon_index = i
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.shoot_timer -= dt
        self.invulnerable_timer = max(0, self.invulnerable_timer - dt)
        self.shield_timer = max(0, self.shield_timer - dt)
        self.speed_timer = max(0, self.speed_timer - dt)

    def shoot(self):
        if self.shoot_timer > 0:
            return

        weapon = self.weapon
        self.shoot_timer = weapon.cooldown

        nose = self.triangle()[0]
        for angle in weapon.angles:
            shot = Shot(nose.x, nose.y, weapon.radius, weapon.color, weapon.lifetime)
            shot.velocity = (pygame.Vector2(0, 1).rotate(self.rotation + angle) * weapon.speed
                             + self.velocity)

    def drop_bomb(self):
        if self.is_dead or self.bombs <= 0:
            return
        self.bombs -= 1
        Bomb(self.position.x, self.position.y)
