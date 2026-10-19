import os
import math
import pygame
from .settings import ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT, TILE_SIZE


def _load(name, size=None, smooth=False):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
    if size:
        if smooth:
            img = pygame.transform.smoothscale(img, size)
        else:
            img = pygame.transform.scale(img, size)
    return img


def _load_fit(name, max_w, max_h, smooth=False):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
    w, h = img.get_size()
    scale = min(max_w / w, max_h / h)
    if scale != 1.0:
        if smooth:
            img = pygame.transform.smoothscale(
                img, (int(w * scale), int(h * scale)))
        else:
            img = pygame.transform.scale(
                img, (int(w * scale), int(h * scale)))
    return img


class MenuButton:
    def __init__(self, image, center):
        self.image   = image
        self.rect    = image.get_rect(center=center)
        self.hovered = False
        self.pressed = False

    def handle_event(self, event, pos):
        if pos is None:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(pos)
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.rect.collidepoint(pos):
                self.pressed = True
        elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
            was = self.pressed and self.rect.collidepoint(pos)
            self.pressed = False
            return was
        return False

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        if self.pressed:
            ov = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            ov.fill((255, 255, 255, 60))
            surf.blit(ov, self.rect)
        elif self.hovered:
            ov = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            ov.fill((255, 255, 255, 25))
            surf.blit(ov, self.rect)


class MainMenu:
    def __init__(self, game):
        self.game = game

        # bg — фото-подобный, ему smooth-даунскейл на пользу
        self.bg = _load("bg.png", (LOGICAL_WIDTH, LOGICAL_HEIGHT),
                        smooth=True)

        # Логотип: увеличен, БЕЗ сглаживания (пиксельный стиль)
        self.logo = _load_fit("pcdl_logo.png", 700, 250, smooth=False)

        # Кнопки: тоже пиксельные
        play_img = _load_fit("menu_play.png", 240, 90, smooth=False)
        exit_img = _load_fit("menu_exit.png", 240, 90, smooth=False)

        self.play_btn = MenuButton(play_img, (LOGICAL_WIDTH // 2, 320))
        self.exit_btn = MenuButton(exit_img, (LOGICAL_WIDTH // 2, 430))

        self.logo_rect = self.logo.get_rect(
            center=(LOGICAL_WIDTH // 2, 130))

        # анимация кубика
        self.player_img = _load("player.png", (TILE_SIZE, TILE_SIZE))
        self.grass_img  = _load("b_grass.png", (TILE_SIZE, TILE_SIZE))
        self.dirt_img   = _load("b_dirt.png",  (TILE_SIZE, TILE_SIZE))

        self.cube_ground_y = LOGICAL_HEIGHT - TILE_SIZE * 3
        self.reset_cube()
        self._t = 0.0

    def reset_cube(self):
        self.cube_x          = -TILE_SIZE
        self.cube_y          = float(self.cube_ground_y)
        self.cube_speed      = 110.0
        self.cube_vy         = 0.0
        self.cube_waiting    = False
        self.cube_wait       = 0.0
        self.is_jumping      = False
        self.next_jump_timer = 1.5

    def _pos(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                          pygame.MOUSEMOTION):
            return event.pos
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            return (int(event.x * LOGICAL_WIDTH),
                    int(event.y * LOGICAL_HEIGHT))
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.request_quit()
            return

        pos = self._pos(event)
        if self.play_btn.handle_event(event, pos):
            self.game.screen = "level_select"
            return
        if self.exit_btn.handle_event(event, pos):
            self.game.request_quit()

    def update(self, dt):
        self._t += dt

        if self.cube_waiting:
            self.cube_wait -= dt
            if self.cube_wait <= 0:
                self.reset_cube()
        else:
            self.cube_x += self.cube_speed * dt
            if self.cube_x > LOGICAL_WIDTH:
                self.cube_waiting = True
                self.cube_wait = 2.5
                self.is_jumping = False

            if not self.is_jumping:
                self.next_jump_timer -= dt
                if self.next_jump_timer <= 0:
                    self.is_jumping = True
                    self.cube_vy = -12.0
            else:
                self.cube_vy += 0.6
                self.cube_y += self.cube_vy
                if self.cube_y >= self.cube_ground_y:
                    self.cube_y = float(self.cube_ground_y)
                    self.is_jumping = False
                    self.next_jump_timer = 1.5 + (self._t * 7.3) % 1.5

    def draw(self, surf):
        surf.blit(self.bg, (0, 0))

        for col in range(0, LOGICAL_WIDTH, TILE_SIZE):
            surf.blit(self.grass_img,
                      (col, LOGICAL_HEIGHT - TILE_SIZE * 2))
            surf.blit(self.dirt_img,
                      (col, LOGICAL_HEIGHT - TILE_SIZE))

        surf.blit(self.logo, self.logo_rect)

        # ⬇ Кубик рисуется ДО кнопок, чтобы кнопки были сверху ⬇
        if not self.cube_waiting:
            surf.blit(self.player_img,
                      (int(self.cube_x), int(self.cube_y)))

        # Кнопки поверх кубика
        self.play_btn.draw(surf)
        self.exit_btn.draw(surf)