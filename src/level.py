import os
import json
import math
import pygame
from .settings import ASSETS_DIR, TILE_SIZE


def _load(name, size=(TILE_SIZE, TILE_SIZE)):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
    return pygame.transform.scale(img, size)


class Block:
    __slots__ = ("rect", "image", "tex")
    def __init__(self, x, y, image, tex="grass"):
        self.rect  = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = image
        self.tex   = tex

    def draw(self, surf, cam_x=0):
        surf.blit(self.image, (self.rect.x - cam_x, self.rect.y))


class Level:
    """Уровень. Если path задан и существует — загружает его, иначе дефолт."""

    def __init__(self, path=None):
        self.grass_img = _load("b_grass.png")
        self.dirt_img  = _load("b_dirt.png")
        self.spike_img = _load("spike.png")
        self.exit_img  = _load("exit.png")

        self.blocks = []
        self.spikes = []
        self.exit   = None
        self.player_start = (64, 448)
        self.level_width  = 60 * TILE_SIZE

        loaded = False
        if path and os.path.exists(path):
            try:
                self.load_json(path)
                print(f"[level] загружен {path}")
                loaded = True
            except Exception as e:
                print(f"[level] ошибка загрузки {path}: {e} → дефолт")
        if not loaded:
            self.reset()

    # ---------- дефолт ----------
    def reset(self):
        self.blocks = []
        self.spikes = []
        self.level_width = 60 * TILE_SIZE
        ground_top = 480
        self.player_start = (64, ground_top - TILE_SIZE)

        for row in range(3):
            y = ground_top + row * TILE_SIZE
            if row == 0:
                tex_img, tex_name = self.grass_img, "grass"
            else:
                tex_img, tex_name = self.dirt_img, "dirt"
            for col in range(60):
                self.blocks.append(Block(col * TILE_SIZE, y, tex_img, tex_name))

        for sx in (384, 800, 1216, 1600):
            self.spikes.append(
                Block(sx, ground_top - TILE_SIZE, self.spike_img, "spike"))

        platforms = [
            (160,  384, 3),
            (576,  352, 3),
            (960,  384, 3),
            (1376, 352, 3),
        ]
        for px, py, pw in platforms:
            for i in range(pw):
                self.blocks.append(
                    Block(px + i * TILE_SIZE, py, self.grass_img, "grass"))

        self.exit = Block(1856, ground_top - TILE_SIZE * 2,
                          self.exit_img, "exit")

    # ---------- сериализация ----------
    def serialize(self):
        return {
            "player_start": list(self.player_start),
            "level_width":  self.level_width,
            "blocks": [{"tex": b.tex, "x": b.rect.x, "y": b.rect.y}
                       for b in self.blocks],
            "spikes": [{"x": s.rect.x, "y": s.rect.y} for s in self.spikes],
            "exit":   ({"x": self.exit.rect.x, "y": self.exit.rect.y}
                       if self.exit else None),
        }

    def deserialize(self, data):
        self.player_start = tuple(data.get("player_start", (64, 448)))
        self.level_width  = data.get("level_width", 60 * TILE_SIZE)
        tex_map = {
            "grass": self.grass_img,
            "dirt":  self.dirt_img,
            "spike": self.spike_img,
            "exit":  self.exit_img,
        }
        self.blocks = []
        for b in data.get("blocks", []):
            tex = b.get("tex", "grass")
            self.blocks.append(Block(b["x"], b["y"], tex_map[tex], tex))
        self.spikes = []
        for s in data.get("spikes", []):
            self.spikes.append(
                Block(s["x"], s["y"], self.spike_img, "spike"))
        ex = data.get("exit")
        self.exit = (Block(ex["x"], ex["y"], self.exit_img, "exit")
                     if ex else None)

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self.deserialize(json.load(f))

    def save_json(self, path):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.serialize(), f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)

    # ---------- отрисовка ----------
    def draw(self, surf, cam_x=0):
        for b in self.blocks:
            b.draw(surf, cam_x)
        for s in self.spikes:
            s.draw(surf, cam_x)
        
        if self.exit:
            # 🎯 ПУЛЬСИРУЮЩЕЕ СВЕЧЕНИЕ ПОРТАЛА
            # Берем текущее время в секундах
            time_sec = pygame.time.get_ticks() / 1000.0
            
            # sin() выдает значения от -1 до 1. Превращаем это в пульсацию от 0 до 1
            pulse = (math.sin(time_sec * 5.0) + 1.0) / 2.0
            
            # Настраиваем размер и прозрачность свечения
            glow_radius = 24 + (pulse * 12)  # Радиус меняется от 24 до 36 пикселей
            alpha = int(40 + (pulse * 60))   # Прозрачность меняется от 40 до 100
            
            # Создаем поверхность для свечения
            glow_size = int(glow_radius * 2)
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Рисуем несколько кругов друг на друге для мягкого градиента (светло-желтый)
            pygame.draw.circle(glow_surf, (255, 255, 150, alpha // 3), (glow_radius, glow_radius), glow_radius)
            pygame.draw.circle(glow_surf, (255, 255, 150, alpha // 2), (glow_radius, glow_radius), glow_radius * 0.7)
            pygame.draw.circle(glow_surf, (255, 255, 180, alpha), (glow_radius, glow_radius), glow_radius * 0.4)
            
            # Позиционируем свечение ровно по центру портала
            glow_x = self.exit.rect.centerx - cam_x - glow_radius
            glow_y = self.exit.rect.centery - glow_radius
            
            # Сначала рисуем свечение (оно будет позади), затем сам портал
            surf.blit(glow_surf, (glow_x, glow_y))
            self.exit.draw(surf, cam_x)
