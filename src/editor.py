import os
import pygame
from .settings import (TILE_SIZE, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       LEVEL_COUNT, level_path)
from . import level as level_module

TOOLS = [
    ("grass", "Трава"),
    ("dirt",  "Земля"),
    ("spike", "Шип"),
    ("exit",  "Портал"),
]


class Editor:
    def __init__(self, game):
        self.game          = game
        self.grid_on       = True
        self.tool_idx      = 0
        self.save_target   = 0       # 0..LEVEL_COUNT-1
        self.cam_x         = 0
        self.mouse_pos     = (0, 0)
        self.undo_stack    = []
        self._msg          = ""
        self._msg_timer    = 0.0
        self._font         = pygame.font.SysFont("Arial", 18, bold=True)
        self._font_small   = pygame.font.SysFont("Arial", 14, bold=True)
        self._drag_start   = None

        self._grid_tile = pygame.Surface(
            (TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.line(self._grid_tile, (255, 255, 255, 55),
                         (0, 0), (TILE_SIZE, 0))
        pygame.draw.line(self._grid_tile, (255, 255, 255, 55),
                         (0, 0), (0, TILE_SIZE))

    # ---------- служебное ----------
    def _notify(self, msg):
        self._msg = msg
        self._msg_timer = 2.0
        print(f"[editor] {msg}")

    def _snap(self, wx, wy):
        if self.grid_on:
            return ((wx // TILE_SIZE) * TILE_SIZE,
                    (wy // TILE_SIZE) * TILE_SIZE)
        return (int(wx), int(wy))

    def _world_pos(self):
        lx, ly = self.mouse_pos
        return lx + self.cam_x, ly

    def _push_undo(self):
        self.undo_stack.append(self.game.level.serialize())
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)

    def _undo(self):
        if not self.undo_stack:
            self._notify("Нечего отменять")
            return
        self.game.level.deserialize(self.undo_stack.pop())
        self._notify("Отменено")

    # ---------- действия ----------
    def _place(self, wx, wy):
        level = self.game.level
        gx, gy = self._snap(wx, wy)
        rect = pygame.Rect(gx, gy, TILE_SIZE, TILE_SIZE)

        if any(b.rect.colliderect(rect) for b in level.blocks):
            return
        if any(s.rect.colliderect(rect) for s in level.spikes):
            return
        if level.exit and level.exit.rect.colliderect(rect):
            return

        self._push_undo()
        tool = TOOLS[self.tool_idx][0]
        if tool == "grass":
            level.blocks.append(
                level_module.Block(gx, gy, level.grass_img, "grass"))
        elif tool == "dirt":
            level.blocks.append(
                level_module.Block(gx, gy, level.dirt_img, "dirt"))
        elif tool == "spike":
            level.spikes.append(
                level_module.Block(gx, gy, level.spike_img, "spike"))
        elif tool == "exit":
            level.exit = level_module.Block(
                gx, gy, level.exit_img, "exit")

    def _erase(self, wx, wy):
        level = self.game.level
        gx, gy = self._snap(wx, wy)
        rect = pygame.Rect(gx, gy, TILE_SIZE, TILE_SIZE)

        will = (any(b.rect.colliderect(rect) for b in level.blocks)
                or any(s.rect.colliderect(rect) for s in level.spikes)
                or (level.exit and level.exit.rect.colliderect(rect)))
        if not will:
            return

        self._push_undo()
        level.blocks = [b for b in level.blocks
                        if not b.rect.colliderect(rect)]
        level.spikes = [s for s in level.spikes
                        if not s.rect.colliderect(rect)]
        if level.exit and level.exit.rect.colliderect(rect):
            level.exit = None

    def _save(self):
        path = level_path(self.save_target)
        try:
            self.game.level.save_json(path)
            self._notify(
                f"Сохранено L{self.save_target + 1}: {os.path.basename(path)}")
        except Exception as e:
            self._notify(f"Ошибка сохранения: {e}")

    def _reset_default(self):
        self._push_undo()
        self.game.level.reset()
        if os.path.exists(level_path(self.save_target)):
            try:
                os.remove(level_path(self.save_target))
            except OSError:
                pass
        self._notify("Сброс на дефолт")

    # ---------- события ----------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_g:
                self.grid_on = not self.grid_on
                self._notify(f"Сетка: {'ВКЛ' if self.grid_on else 'ВЫКЛ'}")
            elif k == pygame.K_s:
                self._save()
            elif k == pygame.K_DELETE:
                self._reset_default()
            elif k == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
                self._undo()
            elif k == pygame.K_TAB:
                self.tool_idx = (self.tool_idx + 1) % len(TOOLS)
                self._notify(f"Инструмент: {TOOLS[self.tool_idx][1]}")
            elif k in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.tool_idx = k - pygame.K_1
                self._notify(f"Инструмент: {TOOLS[self.tool_idx][1]}")
            # F1-F5: цель сохранения
            elif k in (pygame.K_F1, pygame.K_F2, pygame.K_F3,
                       pygame.K_F4, pygame.K_F5):
                idx = k - pygame.K_F1
                if idx < LEVEL_COUNT:
                    self.save_target = idx
                    self._notify(f"Цель сохранения: level{idx + 1}.json")

        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            if self._drag_start and event.buttons[1]:  # СКМ
                dx = event.pos[0] - self._drag_start[0]
                self.cam_x = self._drag_start[1] - dx
                max_cam = max(0,
                              self.game.level.level_width - LOGICAL_WIDTH)
                self.cam_x = max(0, min(max_cam, self.cam_x))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_pos = event.pos
            if event.button == 2:
                self._drag_start = (event.pos[0], self.cam_x)
            elif event.button == 1:
                wx, wy = self._world_pos()
                self._place(wx, wy)
            elif event.button == 3:
                wx, wy = self._world_pos()
                self._erase(wx, wy)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                self._drag_start = None

    # ---------- update ----------
    def update(self, dt):
        if self._msg_timer > 0:
            self._msg_timer -= dt
        keys = pygame.key.get_pressed()
        speed = 8
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.cam_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.cam_x += speed
        max_cam = max(0, self.game.level.level_width - LOGICAL_WIDTH)
        self.cam_x = max(0, min(max_cam, self.cam_x))

    # ---------- draw ----------
    def draw(self, surf, cam_x):
        if self.grid_on:
            off_x = -(cam_x % TILE_SIZE)
            for y in range(0, LOGICAL_HEIGHT + TILE_SIZE, TILE_SIZE):
                for x in range(off_x - TILE_SIZE,
                               LOGICAL_WIDTH + TILE_SIZE, TILE_SIZE):
                    surf.blit(self._grid_tile, (x, y))

        # превью
        lx, ly = self.mouse_pos
        wx, wy = lx + cam_x, ly
        gx, gy = self._snap(wx, wy)
        sx, sy = gx - cam_x, gy
        tool = TOOLS[self.tool_idx][0]
        color = {"grass": (100, 255, 100, 90),
                 "dirt":  (200, 150, 90, 90),
                 "spike": (255, 100, 100, 90),
                 "exit":  (100, 200, 255, 90)}[tool]
        prev = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        prev.fill(color)
        pygame.draw.rect(prev, (255, 255, 255, 200),
                         prev.get_rect(), 1)
        surf.blit(prev, (sx, sy))

        # панель подсказок
        target = f"L{self.save_target + 1}"
        lines = [
            f"РЕДАКТОР  [{TOOLS[self.tool_idx][1]}]  "
            f"Сетка: {'ВКЛ' if self.grid_on else 'ВЫКЛ'}  "
            f"Сохранить в: {target} (F1-F5)",
            "ЛКМ поставить  ПКМ стереть  S сохранить  Ctrl+Z отмена  "
            "Del сброс  G сетка",
            "←→/A D камера   C/Esc выход",
        ]
        box_h = len(lines) * 22 + 12
        box = pygame.Surface((LOGICAL_WIDTH, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        surf.blit(box, (0, 0))
        for i, line in enumerate(lines):
            txt = self._font_small.render(line, True, (255, 255, 180))
            surf.blit(txt, (12, 6 + i * 22))

        if self._msg_timer > 0:
            a = int(min(1.0, self._msg_timer) * 255)
            txt = self._font.render(self._msg, True, (255, 255, 100))
            txt.set_alpha(a)
            x = (LOGICAL_WIDTH - txt.get_width()) // 2
            surf.blit(txt, (x, LOGICAL_HEIGHT - 50))