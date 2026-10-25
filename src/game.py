import os
import shutil
import pygame
from .settings import (ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       TILE_SIZE, BLACK, WHITE, LEVEL_COUNT,
                       LEVELS_DIR_WRITABLE, FONT_PATH,
                       level_path, bundled_level_path, BASE_DIR)
from .player import Player
from . import level as level_module
from .ui import Controls, draw_text_outlined
from .editor import Editor
from .menu import MainMenu, SettingsMenu
from .level_select import LevelSelect
from .progress import Progress
from .parallax import ParallaxBackground
from .localization import get_text

STATE_PLAY = "play"
STATE_DEAD = "dead"
STATE_WIN  = "win"

_FOCUS_LOST_EVENT = getattr(
    pygame, "WINDOWFOCUSLOST",
    getattr(pygame, "WINDOWEVENT_FOCUS_LOST", -1),
)

class Game:
    def __init__(self, canvas):
        self.canvas = canvas
        
        pygame.font.init()
        self.font = pygame.font.Font(FONT_PATH, 24) if os.path.exists(FONT_PATH) else pygame.font.SysFont("Arial", 24, bold=True)

        self._ensure_levels_exist()
        self.progress = Progress()
        
        self.current_music = None
        self.sfx_win = None
        self.sfx_lose = None

        # --- ИНИЦИАЛИЗАЦИЯ МУЗЫКИ И ЗВУКОВ ---
        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.progress.volume)
            
            sfx_dir = os.path.join(ASSETS_DIR, "sfx")
            
            win_path = os.path.join(sfx_dir, "win.ogg")
            if os.path.exists(win_path):
                self.sfx_win = pygame.mixer.Sound(win_path)
            else:
                print("[game] ВНИМАНИЕ: win.ogg не найден в assets/sfx/")
                
            lose_path = os.path.join(sfx_dir, "lose.ogg")
            if os.path.exists(lose_path):
                self.sfx_lose = pygame.mixer.Sound(lose_path)
            else:
                print("[game] ВНИМАНИЕ: lose.ogg не найден в assets/sfx/")
                
        except Exception as e:
            print(f"[game] Ошибка инициализации звука: {e}")

        self.parallax = ParallaxBackground()

        self.controls   = Controls()
        self.editor     = Editor(self)
        self.menu       = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.level_sel  = LevelSelect(self)

        self.level  = None
        self.player = None
        self.key_state = {"left": False, "right": False, "up": False}
        self._c_held   = False
        self._esc_held = False
        self.state = STATE_PLAY
        self.timer = 0.0
        self.cam_x = 0
        self.current_level_idx = 0
        self.screen = "menu"
        
        self.play_music("awakening.ogg")
        self._running = True

    def play_music(self, track_name):
        if self.current_music == track_name: return
        
        if track_name is None:
            pygame.mixer.music.stop()
            self.current_music = None
            return

        music_path = os.path.join(ASSETS_DIR, track_name)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.progress.volume)
                pygame.mixer.music.play(-1)
                self.current_music = track_name
            except Exception as e:
                print(f"[game] Ошибка загрузки музыки {track_name}: {e}")

    def _ensure_levels_exist(self):
        try: os.makedirs(LEVELS_DIR_WRITABLE, exist_ok=True)
        except OSError: pass

        for i in range(LEVEL_COUNT):
            target = level_path(i)
            if os.path.exists(target): continue
            legacy = os.path.join(BASE_DIR, f"level{i + 1}.json")
            if (os.path.exists(legacy) and os.path.abspath(legacy) != os.path.abspath(target)):
                try: shutil.copy2(legacy, target); continue
                except OSError: pass
            bundled = bundled_level_path(i)
            if (os.path.exists(bundled) and os.path.abspath(bundled) != os.path.abspath(target)):
                try: shutil.copy2(bundled, target); continue
                except OSError: pass
            try:
                lvl = level_module.Level()
                lvl.save_json(target)
            except Exception: pass

    def request_quit(self):
        self._running = False

    def start_level(self, idx):
        self.current_level_idx = idx
        path = level_path(idx)
        if not os.path.exists(path):
            bundled = bundled_level_path(idx)
            if os.path.exists(bundled): path = bundled
        self.level  = level_module.Level(path=path)
        self.player = self._spawn_player_at_start()
        self.controls.visible = (self.progress.control_mode == "mobile")
        self.state  = STATE_PLAY
        self.timer  = 0.0
        self.cam_x  = 0
        self._center_camera_on_player()
        self.screen = "game"
        self.play_music("meadows.ogg")

    def _spawn_player_at_start(self):
        px, py = self.level.player_start
        test = pygame.Rect(px, py, TILE_SIZE, TILE_SIZE)
        for _ in range(30):
            if not any(b.rect.colliderect(test) for b in self.level.blocks): break
            test.y -= TILE_SIZE
        return Player(test.x, test.y)

    def _center_camera_on_player(self):
        target = self.player.rect.centerx - LOGICAL_WIDTH // 2
        self.cam_x = max(0, min(target, self.level.level_width - LOGICAL_WIDTH))

    def _enter_editor(self):
        self.editor.save_target = self.current_level_idx
        self.editor.cam_x       = self.cam_x
        self.key_state = {"left": False, "right": False, "up": False}
        self.screen = "editor"
        self.play_music("reconstruction.ogg")

    def _exit_editor(self):
        self.player = self._spawn_player_at_start()
        self.state  = STATE_PLAY
        self.timer  = 0.0
        self._center_camera_on_player()
        keys = pygame.key.get_pressed()
        self.key_state["left"]  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        self.key_state["right"] = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.key_state["up"]    = (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE])
        self.screen = "game"
        self.play_music("meadows.ogg")

    def handle_event(self, event):
        if self.screen == "menu": self.menu.handle_event(event)
        elif self.screen == "settings": self.settings_menu.handle_event(event)
        elif self.screen == "level_select": self.level_sel.handle_event(event)
        elif self.screen == "editor": self._handle_editor_event(event)
        elif self.screen == "game": self._handle_game_event(event)
        return self._running

    def _handle_editor_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_c, pygame.K_ESCAPE):
            if not self._c_held and not self._esc_held:
                self._c_held = event.key == pygame.K_c
                self._esc_held = event.key == pygame.K_ESCAPE
                self._exit_editor()
                return
        if event.type == pygame.KEYUP and event.key == pygame.K_c: self._c_held = False
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE: self._esc_held = False
        self.editor.handle_event(event)

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            if not self._c_held:
                self._c_held = True
                self._enter_editor()
                return
        elif event.type == pygame.KEYUP and event.key == pygame.K_c:
            self._c_held = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if not self._esc_held:
                self._esc_held = True
                self.screen = "level_select"
                self.state = STATE_PLAY # Сбрасываем стейт
                return
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            self._esc_held = False

        self.controls.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a): self.key_state["left"] = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d): self.key_state["right"] = True
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE): self.key_state["up"] = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a): self.key_state["left"] = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d): self.key_state["right"] = False
            elif event.key in (pygame.K_UP, pygame.K_w, pygame.K_SPACE): self.key_state["up"] = False
        elif event.type == _FOCUS_LOST_EVENT:
            self.key_state = {"left": False, "right": False, "up": False}

    def update(self, dt):
        self.parallax.update(dt)

        # 🎵 ЖЕЛЕЗОБЕТОННАЯ ЛОГИКА МУЗЫКИ
        if self.screen in ("menu", "settings", "level_select"):
            self.play_music("awakening.ogg")
        elif self.screen == "game":
            if self.state == STATE_PLAY:
                self.play_music("meadows.ogg")
        elif self.screen == "editor":
            self.play_music("reconstruction.ogg")

        if self.screen == "menu": self.menu.update(dt)
        elif self.screen == "settings": self.settings_menu.update(dt)
        elif self.screen == "level_select": self.level_sel.update(dt)
        elif self.screen == "editor": self.editor.update(dt)
        elif self.screen == "game": self._update_game(dt)
        return self._running

    def _merged_input(self):
        cs = self.controls.state()
        return {
            "left":  self.key_state["left"]  or cs["left"],
            "right": self.key_state["right"] or cs["right"],
            "up":    self.key_state["up"]    or cs["up"],
        }

    def _update_game(self, dt):
        if self.state == STATE_PLAY:
            self.player.handle_input(self._merged_input(), dt)
            self.player.update(self.level.blocks)

            if self.player.rect.left < 0:
                self.player.rect.left = 0
                if self.player.vel_x < 0: self.player.vel_x = 0
            if self.player.rect.right > self.level.level_width:
                self.player.rect.right = self.level.level_width
                if self.player.vel_x > 0: self.player.vel_x = 0

            # Падение под уровень (смерть)
            if self.player.rect.top > LOGICAL_HEIGHT + TILE_SIZE * 2:
                self.state = STATE_DEAD
                self.timer = 3.0
                self.play_music(None)
                if self.sfx_lose: 
                    self.sfx_lose.set_volume(self.progress.volume)
                    self.sfx_lose.play()
                return

            hit = self.player.hitbox()
            # Шипы (смерть)
            for s in self.level.spikes:
                if hit.colliderect(s.rect):
                    self.state = STATE_DEAD
                    self.timer = 3.0
                    self.play_music(None)
                    if self.sfx_lose: 
                        self.sfx_lose.set_volume(self.progress.volume)
                        self.sfx_lose.play()
                    return
            
            # Портал (победа)
            if self.level.exit and hit.colliderect(self.level.exit.rect):
                self.state = STATE_WIN
                self.timer = 3.0
                self.play_music(None)
                if self.sfx_win: 
                    self.sfx_win.set_volume(self.progress.volume)
                    self.sfx_win.play()
                self.progress.mark_completed(self.current_level_idx)
                return

            self._center_camera_on_player()
        else:
            self.timer -= dt
            if self.timer <= 0:
                if self.state == STATE_DEAD:
                    self.player = self._spawn_player_at_start()
                    self.state  = STATE_PLAY
                    self.timer  = 0.0
                    self._center_camera_on_player()
                elif self.state == STATE_WIN:
                    self.screen = "level_select"
                    self.state = STATE_PLAY # 🎯 СБРАСЫВАЕМ СТЕЙТ, ЧТОБЫ ЗАИГРАЛА МУЗЫКА МЕНЮ

    def draw(self):
        self.canvas.fill((135, 206, 235))

        if self.screen in ("menu", "settings", "level_select"):
            self.parallax.draw(self.canvas, cam_x=0, is_menu=True)
        else:
            current_cam = self.cam_x if self.screen == "game" else self.editor.cam_x
            self.parallax.draw(self.canvas, cam_x=current_cam, is_menu=False)

        if self.screen == "menu": self.menu.draw(self.canvas)
        elif self.screen == "settings": self.settings_menu.draw(self.canvas)
        elif self.screen == "level_select": self.level_sel.draw(self.canvas)
        elif self.screen == "editor": self._draw_editor()
        elif self.screen == "game": self._draw_game()

    def _draw_game(self):
        if self.level: self.level.draw(self.canvas, self.cam_x)
        if self.player: self.player.draw(self.canvas, self.cam_x)
        self.controls.draw(self.canvas)

        if self.level:
            lang = self.progress.language
            lvl_text = get_text("level", lang, n=self.current_level_idx + 1)
            draw_text_outlined(self.canvas, lvl_text, self.font, (255, 255, 255), (10, 10))

        if self.state != STATE_PLAY:
            alpha = int((1.0 - self.timer / 3.0) * 255)
            alpha = max(0, min(255, alpha))
            ov = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
            ov.set_alpha(alpha)
            ov.fill(BLACK if self.state == STATE_DEAD else WHITE)
            self.canvas.blit(ov, (0, 0))

    def _draw_editor(self):
        if self.level:
            self.level.draw(self.canvas, self.editor.cam_x)
            self.editor.draw(self.canvas, self.editor.cam_x)