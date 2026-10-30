
import random
import pygame
from constants import *
from logger import log_state, log_event
from player import Player
from asteroid import Asteroid
from asteroid_field import AsteroidField
from shot import Shot
from bomb import Bomb
from powerup import PowerUp
from explosion import Explosion
from background import load_background
from hud import draw_hud, draw_game_over


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()
    dt = 0.0

    background = load_background()
    font = pygame.font.Font(None, 30)
    big_font = pygame.font.Font(None, 96)

    print("Starting Asteroids")
    print(f"Screen width: {SCREEN_WIDTH}\nScreen height: {SCREEN_HEIGHT}")

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    Bomb.containers = (bombs, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)
    Explosion.containers = (updatable, drawable)

    def new_game():
        for group in (updatable, drawable, asteroids, shots, bombs, powerups):
            group.empty()
        return Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), AsteroidField(asteroids)

    p, a = new_game()
    score = 0
    next_bomb_award = BOMB_AWARD_EVERY_SCORE
    game_over = False

    def destroy_asteroid(asteroid, split=True):
        nonlocal score
        score += asteroid.score
        Explosion(asteroid.position, asteroid.radius)
        if random.random() < POWERUP_DROP_CHANCE:
            PowerUp(asteroid.position.x, asteroid.position.y)
        if split:
            asteroid.split()
        else:
            asteroid.kill()

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_b and not game_over:
                    p.drop_bomb()
                if event.key == pygame.K_r and game_over:
                    p, a = new_game()
                    score = 0
                    next_bomb_award = BOMB_AWARD_EVERY_SCORE
                    game_over = False

        log_state()

        for g in updatable:
            g.update(dt)

        # Bombs wipe out every asteroid in their blast radius
        for bomb in list(bombs):
            if not bomb.ready_to_detonate:
                continue
            log_event("bomb_detonated")
            Explosion(bomb.position, 40, "orange", ring_radius=BOMB_BLAST_RADIUS)
            for asteroid in list(asteroids):
                if bomb.position.distance_to(asteroid.position) <= BOMB_BLAST_RADIUS + asteroid.radius:
                    destroy_asteroid(asteroid, split=False)
            bomb.kill()

        for asteroid in list(asteroids):
            for shot in shots:
                if asteroid.collides_with(shot):
                    log_event("asteroid_shot")
                    destroy_asteroid(asteroid)
                    shot.kill()
                    break

        if p.is_vulnerable:
            for asteroid in list(asteroids):
                if p.collides_with(asteroid):
                    log_event("player_hit")
                    destroy_asteroid(asteroid)
                    if p.hit():
                        Explosion(p.position, 60, "orange")
                        if p.lives <= 0:
                            log_event("game_over", score=score)
                            print(f"Game over! Score: {score}")
                            game_over = True
                    break

        if not p.is_dead:
            for powerup in list(powerups):
                if p.collides_with(powerup):
                    log_event("powerup_collected", kind=powerup.kind)
                    p.apply_powerup(powerup.kind)
                    powerup.kill()

        while score >= next_bomb_award:
            p.bombs += 1
            next_bomb_award += BOMB_AWARD_EVERY_SCORE

        screen.blit(background, (0, 0))

        for g in drawable:
            g.draw(screen)

        draw_hud(screen, font, score, p)
        if game_over:
            draw_game_over(screen, big_font, font, score)

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
