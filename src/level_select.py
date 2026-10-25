import os
import pygame
from .settings import (ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       LEVEL_COUNT, FONT_PATH)
from .ui import draw_text_outlined
from .localization import get_text


def _load(name, size):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
    return pygame.transform.scale(img, size)


def _load_locked(idx):
    path = os.path.join(ASSETS_DIR, f"lc{idx + 1}.png")
    if os.path.exists(path):
        return _load(f"lc{idx + 1}.png", (100, 100))
    base = _load(f"l{idx + 1}.png", (100, 100)).copy()
    base.fill((80, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return base


class LevelSelect:
    def __init__(self, game):
        self.game = game

        if os.path.exists(FONT_PATH): self.font = pygame.font.Font(FONT_PATH, 24)
        else: self.font = pygame.font.SysFont("Arial", 24, bold=True)

        self.unlocked_imgs = [_load(f"l{i + 1}.png", (100, 100)) for i in range(LEVEL_COUNT)]
        self.locked_imgs = [None, *[_load_locked(i) for i in range(1, LEVEL_COUNT)]]

        btn_size = 100
        pad_x    = 50
        total_w  = btn_size * LEVEL_COUNT + pad_x * (LEVEL_COUNT - 1)
        start_x  = (LOGICAL_WIDTH - total_w) // 2
        y = LOGICAL_HEIGHT // 2 - 70
        
        self.rects = []
        for i in range(LEVEL_COUNT):
            r = pygame.Rect(start_x + i * (btn_size + pad_x), y, btn_size, btn_size)
            self.rects.append(r)

        self.hover_idx = -1

        self.back_img      = None
        self.back_rect     = pygame.Rect(12, 12, 140, 50)
        self.back_fallback = True
        back_path = os.path.join(ASSETS_DIR, "back_level.png")
        if os.path.exists(back_path):
            try:
                img = pygame.image.load(back_path).convert_alpha()
                w, h = img.get_size()
                sc = min(140 / w, 50 / h)
                if sc != 1.0: img = pygame.transform.scale(img, (int(w * sc), int(h * sc)))
                self.back_img      = img
                self.back_rect     = img.get_rect(topleft=(12, 12))
                self.back_fallback = False
            except pygame.error: pass

    def _pos(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): return event.pos
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP): return (int(event.x * LOGICAL_WIDTH), int(event.y * LOGICAL_HEIGHT))
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.screen = "menu"
            return

        pos = self._pos(event)
        if pos is None: return

        if event.type == pygame.MOUSEMOTION:
            self.hover_idx = -1
            for i, r in enumerate(self.rects):
                if r.collidepoint(pos):
                    self.hover_idx = i
                    break

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.back_rect.collidepoint(pos):
                self.game.screen = "menu"
                return
            for i, r in enumerate(self.rects):
                if r.collidepoint(pos):
                    if self.game.progress.is_unlocked(i): self.game.start_level(i)
                    return

    def update(self, dt): pass

    def draw(self, surf):
        lang = self.game.progress.language
        
        # Перевод заголовка
        draw_text_outlined(surf, get_text("level_select", lang), self.font, (255, 255, 255), 
                           (LOGICAL_WIDTH // 2, 60), center=True)

        for i, r in enumerate(self.rects):
            unlocked = self.game.progress.is_unlocked(i)
            img = self.unlocked_imgs[i] if unlocked else self.locked_imgs[i]
            surf.blit(img, r)

            if unlocked and self.hover_idx == i:
                ov = pygame.Surface(r.size, pygame.SRCALPHA)
                ov.fill((255, 255, 255, 35))
                surf.blit(ov, r)

        if not self.back_fallback:
            surf.blit(self.back_img, self.back_rect)
        else:
            back_bg = pygame.Surface(self.back_rect.size, pygame.SRCALPHA)
            back_bg.fill((0, 0, 0, 140))
            surf.blit(back_bg, self.back_rect)
            
            # Перевод кнопки "Назад"
            draw_text_outlined(surf, get_text("back", lang), self.font, (255, 255, 255), 
                               (self.back_rect.centerx, self.back_rect.centery), center=True)