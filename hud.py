import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, LINE_WIDTH


def _life_icon(x: float, y: float, size: float = 10) -> list[tuple[float, float]]:
    return [(x, y - size), (x - size * 0.66, y + size), (x + size * 0.66, y + size)]


def draw_hud(screen: pygame.Surface, font: pygame.font.Font, score: int, player) -> None:
    screen.blit(font.render(f"SCORE  {score}", True, "white"), (20, 16))

    for i in range(player.lives):
        pygame.draw.polygon(screen, "white", _life_icon(30 + i * 24, 66), LINE_WIDTH)

    lines = [
        (f"WEAPON  {player.weapon.name}  [1-3]", player.weapon.color),
        (f"BOMBS  {player.bombs}  [B]", "red" if player.bombs else "gray"),
    ]
    if player.shield_timer > 0:
        lines.append((f"SHIELD  {player.shield_timer:.1f}s", "deepskyblue"))
    if player.speed_timer > 0:
        lines.append((f"SPEED  {player.speed_timer:.1f}s", "gold"))

    for i, (text, color) in enumerate(lines):
        label = font.render(text, True, color)
        screen.blit(label, (SCREEN_WIDTH - label.get_width() - 20, 16 + i * 28))


def draw_game_over(screen: pygame.Surface, big_font: pygame.font.Font,
                   font: pygame.font.Font, score: int) -> None:
    shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 140))
    screen.blit(shade, (0, 0))

    center = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    for surf, offset in (
        (big_font.render("GAME OVER", True, "white"), -50),
        (font.render(f"Final score: {score}", True, "white"), 20),
        (font.render("Press R to play again or Esc to quit", True, "gray"), 60),
    ):
        screen.blit(surf, surf.get_rect(center=center + (0, offset)))
