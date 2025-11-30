from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

BG_TOP = (5, 5, 20)
BG_BOTTOM = (10, 5, 40)

PLAYER_COLOR = (230, 230, 250)
PLAYER_OUTLINE = (80, 80, 160)

ENEMY_COLOR = (240, 90, 120)
ENEMY_OUTLINE = (60, 20, 40)

BULLET_COLOR = (180, 240, 255)
POWERUP_COLOR = (80, 220, 120)

TEXT_COLOR = (235, 235, 245)

MAX_LIVES = 3


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Interpolate between two colors."""
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
    )


@dataclass
class Player:
    x: float
    y: float
    w: int = 40
    h: int = 22
    speed: float = 320.0
    fire_cooldown: float = 0.25
    fire_timer: float = 0.0
    powerup_timer: float = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.w / 2),
            int(self.y - self.h / 2),
            self.w,
            self.h,
        )

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1

        self.x += dx * self.speed * dt
        self.x = max(40, min(WIDTH - 40, self.x))

        if self.fire_timer > 0:
            self.fire_timer -= dt

        if self.powerup_timer > 0:
            self.powerup_timer -= dt

    def can_fire(self) -> bool:
        return self.fire_timer <= 0

    def reset_fire(self) -> None:
        if self.powerup_timer > 0:
            self.fire_timer = self.fire_cooldown * 0.45
        else:
            self.fire_timer = self.fire_cooldown

    def has_powerup(self) -> bool:
        return self.powerup_timer > 0


@dataclass
class Bullet:
    x: float
    y: float
    vy: float = -420.0
    w: int = 4
    h: int = 12

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.w / 2),
            int(self.y - self.h / 2),
            self.w,
            self.h,
        )

    def update(self, dt: float) -> None:
        self.y += self.vy * dt


@dataclass
class Enemy:
    x: float
    y: float
    w: int
    h: int
    vy: float
    hp: int = 1

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.w / 2),
            int(self.y - self.h / 2),
            self.w,
            self.h,
        )

    def update(self, dt: float) -> None:
        self.y += self.vy * dt

    def is_offscreen(self) -> bool:
        return self.y - self.h / 2 > HEIGHT + 40

    def take_damage(self, dmg: int) -> None:
        self.hp -= dmg

    def is_dead(self) -> bool:
        return self.hp <= 0


@dataclass
class PowerUp:
    x: float
    y: float
    size: int = 18
    vy: float = 160.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def update(self, dt: float) -> None:
        self.y += self.vy * dt


class CosmicCorridorGame:
    """Main game class for the Cosmic Corridor shooter."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Cosmic Corridor – Arcade Space Shooter")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.SysFont("consolas", 18)
        self.font_medium = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_big = pygame.font.SysFont("consolas", 36, bold=True)

        self.player = Player(WIDTH / 2, HEIGHT - 70)
        self.bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.powerups: list[PowerUp] = []

        self.enemy_timer = 0.0
        self.enemy_interval = 0.8
        self.powerup_timer_spawn = 0.0
        self.powerup_interval = 8.0

        self.time_survived = 0.0
        self.score = 0
        self.lives = MAX_LIVES
        self.game_over = False
        self.running = True

        self.flash_timer = 0.0
        self.tutorial_time = 5.0

        self.starfield = self._create_starfield()

    # ---------- starfield ----------
    def _create_starfield(self) -> list[list[float]]:
        stars: list[list[float]] = []
        for _ in range(120):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            speed = random.uniform(20, 80)
            brightness = random.randint(150, 255)
            stars.append([float(x), float(y), speed, float(brightness)])
        return stars

    def _update_starfield(self, dt: float) -> None:
        for star in self.starfield:
            star[1] += star[2] * dt
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = -10.0
                star[2] = random.uniform(20, 80)
                star[3] = float(random.randint(150, 255))

    def _draw_starfield(self) -> None:
        for x, y, _speed, bright in self.starfield:
            color = (int(bright), int(bright), int(bright))
            self.screen.fill(color, ((int(x), int(y)), (2, 2)))

    # ---------- drawing ----------
    def _draw_background(self) -> None:
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = lerp_color(BG_TOP, BG_BOTTOM, t)
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

    def _draw_player(self) -> None:
        glow = pygame.Surface((80, 70), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (140, 140, 255, 80), (0, 20, 80, 40))
        self.screen.blit(glow, (int(self.player.x - 40), int(self.player.y - 40)))

        pygame.draw.rect(
            self.screen,
            PLAYER_OUTLINE,
            self.player.rect.inflate(4, 4),
            border_radius=8,
        )
        pygame.draw.rect(self.screen, PLAYER_COLOR, self.player.rect, border_radius=8)

        nose = pygame.Rect(self.player.rect.centerx - 4, self.player.rect.top - 8, 8, 10)
        pygame.draw.rect(self.screen, (250, 250, 255), nose, border_radius=4)

        if self.player.has_powerup():
            aura = pygame.Surface((100, 90), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (80, 255, 160, 90), (0, 20, 100, 50))
            self.screen.blit(aura, (int(self.player.x - 50), int(self.player.y - 45)))

    def _draw_bullets(self) -> None:
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, BULLET_COLOR, bullet.rect, border_radius=3)

    def _draw_enemies(self) -> None:
        for enemy in self.enemies:
            pygame.draw.rect(
                self.screen,
                ENEMY_OUTLINE,
                enemy.rect.inflate(4, 4),
                border_radius=6,
            )
            pygame.draw.rect(self.screen, ENEMY_COLOR, enemy.rect, border_radius=6)
            cockpit = pygame.Rect(enemy.rect.centerx - 6, enemy.rect.y + 4, 12, 8)
            pygame.draw.rect(self.screen, (240, 220, 220), cockpit, border_radius=3)

    def _draw_powerups(self) -> None:
        for powerup in self.powerups:
            pygame.draw.rect(
                self.screen,
                (20, 80, 40),
                powerup.rect.inflate(4, 4),
                border_radius=6,
            )
            pygame.draw.rect(self.screen, POWERUP_COLOR, powerup.rect, border_radius=6)

    def _draw_ui(self) -> None:
        bar = pygame.Rect(0, 0, WIDTH, 40)
        pygame.draw.rect(self.screen, (10, 10, 25), bar)
        pygame.draw.line(self.screen, (60, 60, 120), bar.bottomleft, bar.bottomright, 2)

        txt_score = self.font_medium.render(f"SCORE: {self.score}", True, TEXT_COLOR)
        txt_time = self.font_small.render(
            f"TIME: {int(self.time_survived)} s",
            True,
            (210, 210, 230),
        )
        txt_lives = self.font_medium.render("❤" * self.lives, True, (255, 110, 140))

        self.screen.blit(txt_score, (10, 6))
        self.screen.blit(txt_time, (10, 22))
        self.screen.blit(
            txt_lives,
            (WIDTH - txt_lives.get_width() - 16, 6),
        )

        if self.player.has_powerup():
            width = 140
            x = WIDTH // 2 - width // 2
            y = 8
            ratio = max(0.0, min(1.0, self.player.powerup_timer / 6.0))
            pygame.draw.rect(
                self.screen,
                (30, 60, 40),
                (x, y, width, 8),
                border_radius=4,
            )
            pygame.draw.rect(
                self.screen,
                (120, 250, 180),
                (x, y, int(width * ratio), 8),
                border_radius=4,
            )
            label = self.font_small.render("POWER-UP", True, (210, 250, 225))
            self.screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 18))

    def _draw_flash(self) -> None:
        if self.flash_timer <= 0:
            return
        alpha = int(180 * (self.flash_timer / 0.25))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 120, 120, alpha))
        self.screen.blit(overlay, (0, 0))

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        t1 = self.font_big.render("GAME OVER", True, (250, 230, 240))
        t2 = self.font_medium.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        t3 = self.font_small.render(
            "ENTER: play again   |   ESC: quit",
            True,
            TEXT_COLOR,
        )

        self.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 70))
        self.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 - 30))
        self.screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 10))

    # ---------- logic ----------
    def _reset(self) -> None:
        self.player.x = WIDTH / 2
        self.player.y = HEIGHT - 70
        self.bullets.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.enemy_timer = 0.0
        self.powerup_timer_spawn = 0.0
        self.time_survived = 0.0
        self.score = 0
        self.lives = MAX_LIVES
        self.game_over = False
        self.flash_timer = 0.0
        self.tutorial_time = 5.0
        self.player.powerup_timer = 0.0

    def _spawn_enemy(self) -> None:
        x = random.randint(60, WIDTH - 60)
        width = random.randint(32, 46)
        height = random.randint(24, 32)
        base_speed = random.uniform(120, 170)
        extra_speed = self.time_survived * 1.8
        vy = base_speed + extra_speed
        hp = 1 if random.random() < 0.75 else 2
        self.enemies.append(Enemy(x, -height, width, height, vy, hp))

    def _spawn_powerup(self) -> None:
        x = random.randint(80, WIDTH - 80)
        self.powerups.append(PowerUp(x, -20))

    def _update_game(self, dt: float) -> None:
        if self.game_over:
            return

        self.time_survived += dt
        if self.tutorial_time > 0:
            self.tutorial_time -= dt

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        self._update_starfield(dt)

        self.enemy_timer += dt
        self.powerup_timer_spawn += dt

        interval = max(0.35, self.enemy_interval - self.time_survived * 0.01)
        if self.enemy_timer >= interval:
            self.enemy_timer -= interval
            self._spawn_enemy()

        if self.powerup_timer_spawn >= self.powerup_interval:
            self.powerup_timer_spawn = 0.0
            self._spawn_powerup()

        if keys[pygame.K_SPACE] and self.player.can_fire():
            self.player.reset_fire()
            if self.player.has_powerup():
                offset = 12
                self.bullets.append(Bullet(self.player.x - offset, self.player.y - 10))
                self.bullets.append(Bullet(self.player.x + offset, self.player.y - 10))
            else:
                self.bullets.append(Bullet(self.player.x, self.player.y - 10))

        for bullet in self.bullets:
            bullet.update(dt)
        for enemy in self.enemies:
            enemy.update(dt)
        for powerup in self.powerups:
            powerup.update(dt)

        self.bullets = [b for b in self.bullets if b.y + b.h > -20]
        self.enemies = [e for e in self.enemies if not e.is_offscreen()]
        self.powerups = [p for p in self.powerups if p.y - p.size < HEIGHT + 20]

        # bullet vs enemy
        remaining_bullets: list[Bullet] = []
        for bullet in self.bullets:
            hit_any = False
            for enemy in self.enemies:
                if enemy.rect.colliderect(bullet.rect):
                    enemy.take_damage(1)
                    self.score += 10
                    hit_any = True
                    break
            if not hit_any:
                remaining_bullets.append(bullet)
        self.bullets = remaining_bullets
        self.enemies = [e for e in self.enemies if not e.is_dead()]

        # player vs enemy
        remaining_enemies: list[Enemy] = []
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.lives -= 1
                self.flash_timer = 0.25
                if self.lives <= 0:
                    self.game_over = True
            else:
                remaining_enemies.append(enemy)
        self.enemies = remaining_enemies

        # player vs powerup
        remaining_powerups: list[PowerUp] = []
        for powerup in self.powerups:
            if self.player.rect.colliderect(powerup.rect):
                self.player.powerup_timer = 6.0
            else:
                remaining_powerups.append(powerup)
        self.powerups = remaining_powerups

        self.score += int(dt * 4)

        if self.flash_timer > 0:
            self.flash_timer -= dt

    # ---------- public API ----------
    def run(self) -> None:
        """Start the main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if self.game_over and event.key == pygame.K_RETURN:
                        self._reset()

            self._update_game(dt)

            self._draw_background()
            self._draw_starfield()
            self._draw_bullets()
            self._draw_enemies()
            self._draw_powerups()
            self._draw_player()
            self._draw_ui()
            self._draw_flash()

            if self.game_over:
                self._draw_game_over()

            pygame.display.flip()

        pygame.quit()
