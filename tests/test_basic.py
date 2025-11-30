from __future__ import annotations

from cosmic_corridor.game import Bullet, Enemy, Player


def test_player_moves_right():
    player = Player(100, 100)
    # dt = 1.0, sağa tam hız
    player.x = 100.0
    player.update(0.0, keys=FakeKeys())  # önce hiçbir tuş yok
    assert player.x == 100.0

    keys = FakeKeys(right=True)
    player.update(1.0, keys)
    assert player.x > 100.0


def test_bullet_moves_up():
    bullet = Bullet(50, 50)
    y_start = bullet.y
    bullet.update(0.5)
    assert bullet.y < y_start


def test_enemy_offscreen():
    enemy = Enemy(100, 700, 40, 20, vy=100.0)
    assert enemy.is_offscreen() is True


class FakeKeys:
    """Basit sahte key-objesi, sadece test için."""

    def __init__(self, right: bool = False) -> None:
        self._right = right

    def __getitem__(self, key: int) -> bool:  # type: ignore[override]
        import pygame

        if key in (pygame.K_RIGHT, pygame.K_d):
            return self._right
        return False
