import os
import pygame
from .settings import (ASSETS_DIR, TILE_SIZE, GRAVITY,
                       PLAYER_SPEED, JUMP_VELOCITY, MAX_FALL_SPEED,
                       COYOTE_TIME, JUMP_BUFFER)


class Player:
    def __init__(self, x, y):
        path = os.path.join(ASSETS_DIR, "player.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

        # тайминги ввода
        self._coyote = COYOTE_TIME
        self._buffer = 0.0
        self._jump_was_pressed = False

    def hitbox(self):
        return self.rect.inflate(-8, -8)

    def handle_input(self, buttons, dt):
        """Обработка ввода + логика прыжка с буфером и coyote time.
        buttons: dict {"left": bool, "right": bool, "up": bool}
        """
        # ---- движение ----
        self.vel_x = 0
        if buttons.get("left"):
            self.vel_x = -PLAYER_SPEED
        if buttons.get("right"):
            self.vel_x = PLAYER_SPEED

        # ---- буфер прыжка ----
        jump = bool(buttons.get("up"))
        if jump and not self._jump_was_pressed:
            self._buffer = JUMP_BUFFER
        self._jump_was_pressed = jump
        self._buffer = max(0.0, self._buffer - dt)

        # ---- coyote time ----
        if self.on_ground:
            self._coyote = COYOTE_TIME
        else:
            self._coyote = max(0.0, self._coyote - dt)

        # ---- выполняем прыжок ----
        if self._buffer > 0 and self._coyote > 0:
            self.vel_y = JUMP_VELOCITY
            self.on_ground = False
            self._coyote = 0.0
            self._buffer = 0.0

    def update(self, blocks):
        """Только физика — столкновения с блоками."""
        # горизонталь
        self.rect.x += self.vel_x
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.vel_x > 0:
                    self.rect.right = b.rect.left
                elif self.vel_x < 0:
                    self.rect.left = b.rect.right

        # вертикаль
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)
        self.rect.y += self.vel_y
        self.on_ground = False
        for b in blocks:
            if self.rect.colliderect(b.rect):
                if self.vel_y > 0:
                    self.rect.bottom = b.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = b.rect.bottom
                    self.vel_y = 0

    def draw(self, surf, cam_x=0):
        surf.blit(self.image, (self.rect.x - cam_x, self.rect.y))