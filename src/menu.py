import os
import math
import pygame
from .settings import ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT, TILE_SIZE, FONT_PATH
from .ui import Slider, draw_text_outlined
from .localization import get_text


def _load(name, size=None, smooth=False):
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        surf = pygame.Surface(size or (100, 100), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 100))
        return surf
    img = pygame.image.load(path).convert_alpha()
    if size:
        if smooth: img = pygame.transform.smoothscale(img, size)
        else: img = pygame.transform.scale(img, size)
    return img


def _load_fit(name, max_w, max_h, smooth=False):
    path = os.path.join(ASSETS_DIR, name)
    
    # Если файла нет в папке localization, ищем его в корне assets (fallback)
    if not os.path.exists(path) and name.startswith("localization/"):
        fallback_name = name.split("/")[-1][3:] # отрезаем "en_" или "ru_"
        path = os.path.join(ASSETS_DIR, fallback_name)

    if not os.path.exists(path):
        surf = pygame.Surface((100, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 0, 100))
        return surf
        
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    scale = min(max_w / w, max_h / h)
    if scale != 1.0:
        if smooth: img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
        else: img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    return img


class MenuButton:
    def __init__(self, image, center):
        self.image   = image
        self.rect    = image.get_rect(center=center)
        self.hovered = False
        self.pressed = False

    def handle_event(self, event, pos):
        if pos is None: return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(pos)
        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            if self.rect.collidepoint(pos): self.pressed = True
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
        self.logo = _load_fit("pcdl_logo.png", 700, 250, smooth=False)

        self.lang = None
        self.play_btn = None
        self.settings_btn = None
        self.exit_btn = None
        
        # Первоначальная загрузка текстур
        self.update_textures()

        self.logo_rect = self.logo.get_rect(center=(LOGICAL_WIDTH // 2, 130))

        self.player_img = _load("player.png", (TILE_SIZE, TILE_SIZE))
        self.grass_img  = _load("b_grass.png", (TILE_SIZE, TILE_SIZE))
        self.dirt_img   = _load("b_dirt.png",  (TILE_SIZE, TILE_SIZE))

        self.cube_ground_y = LOGICAL_HEIGHT - TILE_SIZE * 3
        self.reset_cube()
        self._t = 0.0

    def update_textures(self):
        """Загружает кнопки в зависимости от выбранного языка."""
        lang = self.game.progress.language
        if self.lang == lang:
            return # Язык не изменился, текстуры уже загружены
        self.lang = lang
        
        btn_w, btn_h = 200, 70
        
        # Загружаем картинки из папки localization
        play_img = _load_fit(f"localization/{lang}_menu_play.png", btn_w, btn_h, smooth=False)
        settings_img = _load_fit(f"localization/{lang}_menu_settings.png", btn_w, btn_h, smooth=False)
        exit_img = _load_fit(f"localization/{lang}_menu_exit.png", btn_w, btn_h, smooth=False) 

        # Сохраняем позиции (если кнопки уже были созданы, берем их координаты)
        c_play = (LOGICAL_WIDTH // 2, 295)
        c_settings = (LOGICAL_WIDTH // 2, 380)
        c_exit = (LOGICAL_WIDTH // 2, 465)

        if self.play_btn:
            c_play = self.play_btn.rect.center
            c_settings = self.settings_btn.rect.center
            c_exit = self.exit_btn.rect.center

        # Пересоздаем кнопки с новыми текстурами
        self.play_btn = MenuButton(play_img, c_play)
        self.settings_btn = MenuButton(settings_img, c_settings)
        self.exit_btn = MenuButton(exit_img, c_exit)

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
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): return event.pos
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP): return (int(event.x * LOGICAL_WIDTH), int(event.y * LOGICAL_HEIGHT))
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.request_quit()
            return

        pos = self._pos(event)
        if self.play_btn.handle_event(event, pos): self.game.screen = "level_select"; return
        if self.settings_btn.handle_event(event, pos): self.game.screen = "settings"; return
        if self.exit_btn.handle_event(event, pos): self.game.request_quit(); return

    def update(self, dt):
        self.update_textures() # Проверяем, не сменил ли игрок язык в настройках
        
        self._t += dt
        if self.cube_waiting:
            self.cube_wait -= dt
            if self.cube_wait <= 0: self.reset_cube()
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
        for col in range(0, LOGICAL_WIDTH, TILE_SIZE):
            surf.blit(self.grass_img, (col, LOGICAL_HEIGHT - TILE_SIZE * 2))
            surf.blit(self.dirt_img, (col, LOGICAL_HEIGHT - TILE_SIZE))
        surf.blit(self.logo, self.logo_rect)
        if not self.cube_waiting:
            surf.blit(self.player_img, (int(self.cube_x), int(self.cube_y)))
        
        self.play_btn.draw(surf)
        self.settings_btn.draw(surf)
        self.exit_btn.draw(surf)


class SettingsMenu:
    def __init__(self, game):
        self.game = game
        lang = self.game.progress.language
        
        if os.path.exists(FONT_PATH):
            self.font = pygame.font.Font(FONT_PATH, 28)
            self.small = pygame.font.Font(FONT_PATH, 22)
        else:
            self.font = pygame.font.SysFont("Arial", 28, bold=True)
            self.small = pygame.font.SysFont("Arial", 22, bold=True)

        back_path = os.path.join(ASSETS_DIR, "back_level.png")
        if os.path.exists(back_path): self.back_img = _load_fit("back_level.png", 140, 50, smooth=False)
        else: self.back_img = _load_fit("menu_exit.png", 140, 50, smooth=False)
            
        self.back_btn = MenuButton(self.back_img, (100, 50))
        
        self.ctrl_rect = pygame.Rect(LOGICAL_WIDTH // 2 - 150, 160, 300, 50)
        self.lang_rect = pygame.Rect(LOGICAL_WIDTH // 2 - 150, 270, 300, 50)
        self.slider = Slider(LOGICAL_WIDTH // 2 - 150, 400, 300, 20, game.progress.volume)

    def _pos(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION): return event.pos
        if event.type in (pygame.FINGERDOWN, pygame.FINGERUP): return (int(event.x * LOGICAL_WIDTH), int(event.y * LOGICAL_HEIGHT))
        return None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.screen = "menu"
            return

        pos = self._pos(event)
        if self.back_btn.handle_event(event, pos):
            self.game.screen = "menu"
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ctrl_rect.collidepoint(event.pos):
                if self.game.progress.control_mode == "pc": self.game.progress.control_mode = "mobile"
                else: self.game.progress.control_mode = "pc"
                self.game.progress.save()
            
            if self.lang_rect.collidepoint(event.pos):
                if self.game.progress.language == "en": self.game.progress.language = "ru"
                else: self.game.progress.language = "en"
                self.game.progress.save()

        old_vol = self.slider.value
        self.slider.handle_event(event)
        if old_vol != self.slider.value:
            self.game.progress.volume = self.slider.value
            self.game.progress.save()
            try: pygame.mixer.music.set_volume(self.slider.value)
            except Exception: pass

    def update(self, dt): pass

    def draw(self, surf):
        lang = self.game.progress.language
        
        draw_text_outlined(surf, get_text("settings_title", lang), self.font, (255, 255, 255), (LOGICAL_WIDTH // 2, 80), center=True)
        
        draw_text_outlined(surf, get_text("controls", lang), self.small, (255, 255, 255), (self.ctrl_rect.x, self.ctrl_rect.y - 25))
        pygame.draw.rect(surf, (50, 50, 50), self.ctrl_rect, border_radius=10)
        pygame.draw.rect(surf, (255, 255, 255), self.ctrl_rect, 2, border_radius=10)
        
        mode_text = get_text("ctrl_pc" if self.game.progress.control_mode == "pc" else "ctrl_touch", lang)
        draw_text_outlined(surf, mode_text, self.small, (255, 255, 255), self.ctrl_rect.center, center=True)

        draw_text_outlined(surf, get_text("language", lang), self.small, (255, 255, 255), (self.lang_rect.x, self.lang_rect.y - 25))
        pygame.draw.rect(surf, (50, 50, 50), self.lang_rect, border_radius=10)
        pygame.draw.rect(surf, (255, 255, 255), self.lang_rect, 2, border_radius=10)
        
        lang_text = get_text("lang_en" if lang == "en" else "lang_ru", lang)
        draw_text_outlined(surf, lang_text, self.small, (255, 255, 255), self.lang_rect.center, center=True)

        draw_text_outlined(surf, get_text("music_vol", lang), self.small, (255, 255, 255), (self.slider.rect.x, self.slider.rect.y - 25))
        self.slider.draw(surf)
        
        self.back_btn.draw(surf)