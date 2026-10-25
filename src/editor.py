import os
import shutil
import datetime
import pygame
from .settings import (TILE_SIZE, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       LEVEL_COUNT, level_path, FONT_PATH, BASE_DIR)
from . import level as level_module
from .ui import draw_text_outlined
from .localization import get_text, get_tool_name

TOOLS = ["grass", "dirt", "spike", "exit"]

class Editor:
    def __init__(self, game):
        self.game          = game
        self.grid_on       = True
        self.tool_idx      = 0
        self.save_target   = 0
        self.cam_x         = 0
        self.mouse_pos     = (0, 0)
        self.undo_stack    = []
        self._msg          = ""
        self._msg_timer    = 0.0
        
        if os.path.exists(FONT_PATH):
            self._font = pygame.font.Font(FONT_PATH, 20)
            self._font_small = pygame.font.Font(FONT_PATH, 16)
        else:
            self._font = pygame.font.SysFont("Arial", 20, bold=True)
            self._font_small = pygame.font.SysFont("Arial", 16, bold=True)

        self._drag_start   = None
        self._grid_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.line(self._grid_tile, (255, 255, 255, 55), (0, 0), (TILE_SIZE, 0))
        pygame.draw.line(self._grid_tile, (255, 255, 255, 55), (0, 0), (0, TILE_SIZE))

    def _notify(self, msg):
        self._msg = msg
        self._msg_timer = 2.0
        print(f"[editor] {msg}")

    def _snap(self, wx, wy):
        if self.grid_on: return ((wx // TILE_SIZE) * TILE_SIZE, (wy // TILE_SIZE) * TILE_SIZE)
        return (int(wx), int(wy))

    def _world_pos(self):
        lx, ly = self.mouse_pos
        return lx + self.cam_x, ly

    def _push_undo(self):
        self.undo_stack.append(self.game.level.serialize())
        if len(self.undo_stack) > 30: self.undo_stack.pop(0)

    def _undo(self):
        lang = self.game.progress.language
        if not self.undo_stack:
            self._notify(get_text("editor_msg_undo_empty", lang))
            return
        self.game.level.deserialize(self.undo_stack.pop())
        self._notify(get_text("editor_msg_undo", lang))

    def _place(self, wx, wy):
        level = self.game.level
        gx, gy = self._snap(wx, wy)
        rect = pygame.Rect(gx, gy, TILE_SIZE, TILE_SIZE)

        if any(b.rect.colliderect(rect) for b in level.blocks): return
        if any(s.rect.colliderect(rect) for s in level.spikes): return
        if level.exit and level.exit.rect.colliderect(rect): return

        self._push_undo()
        tool = TOOLS[self.tool_idx]
        if tool == "grass": level.blocks.append(level_module.Block(gx, gy, level.grass_img, "grass"))
        elif tool == "dirt": level.blocks.append(level_module.Block(gx, gy, level.dirt_img, "dirt"))
        elif tool == "spike": level.spikes.append(level_module.Block(gx, gy, level.spike_img, "spike"))
        elif tool == "exit": level.exit = level_module.Block(gx, gy, level.exit_img, "exit")

    def _erase(self, wx, wy):
        level = self.game.level
        gx, gy = self._snap(wx, wy)
        rect = pygame.Rect(gx, gy, TILE_SIZE, TILE_SIZE)
        will = (any(b.rect.colliderect(rect) for b in level.blocks) or any(s.rect.colliderect(rect) for s in level.spikes) or (level.exit and level.exit.rect.colliderect(rect)))
        if not will: return

        self._push_undo()
        level.blocks = [b for b in level.blocks if not b.rect.colliderect(rect)]
        level.spikes = [s for s in level.spikes if not s.rect.colliderect(rect)]
        if level.exit and level.exit.rect.colliderect(rect): level.exit = None

    def _save(self):
        lang = self.game.progress.language
        path = level_path(self.save_target)
        
        # --- 🛡️ СОЗДАНИЕ БЭКАПА ПЕРЕД СОХРАНЕНИЕМ ---
        if os.path.exists(path):
            try:
                backup_dir = os.path.join(BASE_DIR, "levels_backup")
                os.makedirs(backup_dir, exist_ok=True)
                
                # Генерируем имя с датой и временем (например: level3_2026-10-25_22-30-15.json)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_name = f"level{self.save_target + 1}_{timestamp}.json"
                backup_path = os.path.join(backup_dir, backup_name)
                
                # Копируем старый файл в папку бэкапов
                shutil.copy2(path, backup_path)
                print(f"[editor] Создан бэкап: {backup_name}")
            except Exception as e:
                print(f"[editor] Не удалось создать бэкап: {e}")
        # ----------------------------------------------

        try:
            self.game.level.save_json(path)
            msg = get_text("editor_msg_saved", lang, n=self.save_target+1, file=os.path.basename(path))
            self._notify(msg)
        except Exception as e: 
            self._notify(get_text("editor_msg_save_err", lang, err=str(e)))

    def _reset_default(self):
        lang = self.game.progress.language
        self._push_undo()
        self.game.level.reset()
        if os.path.exists(level_path(self.save_target)):
            try: os.remove(level_path(self.save_target))
            except OSError: pass
        self._notify(get_text("editor_msg_reset", lang))

    def handle_event(self, event):
        lang = self.game.progress.language
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_g:
                self.grid_on = not self.grid_on
                state = get_text("editor_on" if self.grid_on else "editor_off", lang)
                self._notify(get_text("editor_msg_grid", lang, state=state))
            elif k == pygame.K_s: self._save()
            elif k == pygame.K_DELETE: self._reset_default()
            elif k == pygame.K_z and (event.mod & pygame.KMOD_CTRL): self._undo()
            elif k == pygame.K_TAB:
                self.tool_idx = (self.tool_idx + 1) % len(TOOLS)
                tool_name = get_tool_name(TOOLS[self.tool_idx], lang)
                self._notify(get_text("editor_msg_tool", lang, tool=tool_name))
            elif k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.tool_idx = k - pygame.K_1
                tool_name = get_tool_name(TOOLS[self.tool_idx], lang)
                self._notify(get_text("editor_msg_tool", lang, tool=tool_name))
            elif k in (pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5):
                idx = k - pygame.K_F1
                if idx < LEVEL_COUNT:
                    self.save_target = idx
                    self._notify(get_text("editor_msg_target", lang, n=idx+1))

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            if self._drag_start and event.buttons[1]:
                dx = event.pos[0] - self._drag_start[0]
                self.cam_x = self._drag_start[1] - dx
                max_cam = max(0, self.game.level.level_width - LOGICAL_WIDTH)
                self.cam_x = max(0, min(max_cam, self.cam_x))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = event.pos
            if event.button == 2: self._drag_start = (event.pos[0], self.cam_x)
            elif event.button == 1:
                wx, wy = self._world_pos()
                self._place(wx, wy)
            elif event.button == 3:
                wx, wy = self._world_pos()
                self._erase(wx, wy)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2: self._drag_start = None

    def update(self, dt):
        if self._msg_timer > 0: self._msg_timer -= dt
        keys = pygame.key.get_pressed()
        speed = 8
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.cam_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cam_x += speed
        max_cam = max(0, self.game.level.level_width - LOGICAL_WIDTH)
        self.cam_x = max(0, min(max_cam, self.cam_x))

    def draw(self, surf, cam_x):
        lang = self.game.progress.language
        
        if self.grid_on:
            off_x = -(cam_x % TILE_SIZE)
            for y in range(0, LOGICAL_HEIGHT + TILE_SIZE, TILE_SIZE):
                for x in range(off_x - TILE_SIZE, LOGICAL_WIDTH + TILE_SIZE, TILE_SIZE):
                    surf.blit(self._grid_tile, (x, y))

        lx, ly = self.mouse_pos
        wx, wy = lx + cam_x, ly
        gx, gy = self._snap(wx, wy)
        sx, sy = gx - cam_x, gy
        tool = TOOLS[self.tool_idx]
        color = {"grass": (100, 255, 100, 90), "dirt": (200, 150, 90, 90), "spike": (255, 100, 100, 90), "exit": (100, 200, 255, 90)}[tool]
        prev = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        prev.fill(color)
        pygame.draw.rect(prev, (255, 255, 255, 200), prev.get_rect(), 1)
        surf.blit(prev, (sx, sy))

        target = f"L{self.save_target + 1}"
        grid_state = get_text("editor_on" if self.grid_on else "editor_off", lang)
        tool_name = get_tool_name(tool, lang)
        
        lines = [
            get_text("editor_hud1", lang, tool=tool_name, grid=grid_state, target=target),
            get_text("editor_hud2", lang),
            get_text("editor_hud3", lang),
        ]
        
        box_h = len(lines) * 22 + 12
        box = pygame.Surface((LOGICAL_WIDTH, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        surf.blit(box, (0, 0))
        
        for i, line in enumerate(lines):
            draw_text_outlined(surf, line, self._font_small, (255, 255, 180), (12, 6 + i * 22))

        if self._msg_timer > 0:
            alpha = int(min(1.0, self._msg_timer) * 255)
            text_surf = self._font.render(self._msg, True, (255, 255, 100))
            text_surf.set_alpha(alpha)
            x = (LOGICAL_WIDTH - text_surf.get_width()) // 2
            surf.blit(text_surf, (x, LOGICAL_HEIGHT - 50))