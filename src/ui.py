import os
import pygame
from .settings import (ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       BUTTON_ALPHA)


def _load_btn(name, size):
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 200, 200, BUTTON_ALPHA), (0, 0, size, size))
        return surf
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, (size, size))
    img.set_alpha(BUTTON_ALPHA)
    return img


def draw_text_outlined(surface, text, font, text_color, pos, outline_color=(0, 0, 0), center=False):
    """Рисует текст с черным контуром (обводкой) в 8 направлениях."""
    text_surf = font.render(text, True, text_color)
    outline_surf = font.render(text, True, outline_color)
    
    rect = text_surf.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
        
    surface.blit(outline_surf, (rect.x - 2, rect.y))
    surface.blit(outline_surf, (rect.x + 2, rect.y))
    surface.blit(outline_surf, (rect.x, rect.y - 2))
    surface.blit(outline_surf, (rect.x, rect.y + 2))
    surface.blit(outline_surf, (rect.x - 2, rect.y - 2))
    surface.blit(outline_surf, (rect.x + 2, rect.y - 2))
    surface.blit(outline_surf, (rect.x - 2, rect.y + 2))
    surface.blit(outline_surf, (rect.x + 2, rect.y + 2))
    surface.blit(text_surf, rect)


class TouchButton:
    __slots__ = ("rect", "image", "mouse_buttons", "finger_ids")

    def __init__(self, x, y, size, image):
        self.rect          = pygame.Rect(x, y, size, size)
        self.image         = image
        self.mouse_buttons = set()
        self.finger_ids    = set()

    @property
    def active(self):
        return bool(self.mouse_buttons) or bool(self.finger_ids)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.mouse_buttons.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons.discard(event.button)
        elif event.type == pygame.FINGERDOWN:
            px = int(event.x * LOGICAL_WIDTH)
            py = int(event.y * LOGICAL_HEIGHT)
            if self.rect.collidepoint(px, py):
                self.finger_ids.add(event.finger_id)
        elif event.type == pygame.FINGERUP:
            self.finger_ids.discard(event.finger_id)
        elif event.type == pygame.FINGERMOTION:
            px = int(event.x * LOGICAL_WIDTH)
            py = int(event.y * LOGICAL_HEIGHT)
            if self.rect.collidepoint(px, py):
                self.finger_ids.add(event.finger_id)
            else:
                self.finger_ids.discard(event.finger_id)

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        if self.active:
            ov = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            ov.fill((255, 255, 255, 80))
            surf.blit(ov, self.rect)


class Controls:
    def __init__(self):
        self.visible = False
        size   = 128
        margin = 30
        y_btn  = LOGICAL_HEIGHT - margin - size
        
        self.left  = TouchButton(margin,                         y_btn, size, _load_btn("c_left.png",  size))
        self.right = TouchButton(margin + size + 20,             y_btn, size, _load_btn("c_right.png", size))
        self.up    = TouchButton(LOGICAL_WIDTH - margin - size,  y_btn, size, _load_btn("c_up.png",    size))
        self.buttons = (self.left, self.right, self.up)

    def state(self):
        if not self.visible:
            return {"left": False, "right": False, "up": False}
        return {
            "left":  self.left.active,
            "right": self.right.active,
            "up":    self.up.active,
        }

    def handle_event(self, event):
        if not self.visible:
            return
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, surf):
        if not self.visible:
            return
        for b in self.buttons:
            b.draw(surf)


class Slider:
    def __init__(self, x, y, w, h, initial_value=0.5):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = initial_value
        self.dragging = False
        
        # Загрузка текстуры ручки
        knob_path = os.path.join(ASSETS_DIR, "slider_knob.png")
        if os.path.exists(knob_path):
            self.knob_img = pygame.image.load(knob_path).convert_alpha()
        else:
            self.knob_img = None
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_from_mouse(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_from_mouse(event.pos)

    def _update_from_mouse(self, pos):
        rel_x = pos[0] - self.rect.x
        self.value = max(0.0, min(1.0, rel_x / self.rect.width))

    def draw(self, surf):
        # 1. Фон шкалы (#323232)
        pygame.draw.rect(surf, (50, 50, 50), self.rect, border_radius=10)
        
        # 2. Заполненная часть (#FFC866)
        filled_w = int(self.rect.width * self.value)
        if filled_w > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_w, self.rect.height)
            pygame.draw.rect(surf, (255, 200, 102), filled_rect, border_radius=10)
        
        # 3. Белая обводка (как у кнопок выше)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2, border_radius=10)
        
        # 4. Отрисовка ручки
        handle_x = self.rect.x + int(self.rect.width * self.value)
        handle_y = self.rect.centery
        
        if self.knob_img:
            img_rect = self.knob_img.get_rect(center=(handle_x, handle_y))
            surf.blit(self.knob_img, img_rect)
        else:
            handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
            pygame.draw.rect(surf, (255, 255, 255), handle_rect, border_radius=5)