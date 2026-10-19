import os
import pygame
from .settings import (ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT,
                       BUTTON_ALPHA)


def _load_btn(name, size):
    img = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
    img = pygame.transform.scale(img, (size, size))
    img.set_alpha(BUTTON_ALPHA)
    return img


class TouchButton:
    __slots__ = ("rect", "image", "mouse_buttons", "finger_ids")

    def __init__(self, x, y, size, image):
        self.rect          = pygame.Rect(x, y, size, size)
        self.image         = image
        self.mouse_buttons = set()   # номера зажатых кнопок мыши
        self.finger_ids    = set()   # id пальцев

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
        size   = 128
        margin = 30
        y_btn  = LOGICAL_HEIGHT - margin - size
        left_img  = _load_btn("c_left.png",  size)
        right_img = _load_btn("c_right.png", size)
        up_img    = _load_btn("c_up.png",    size)

        self.left  = TouchButton(margin,                         y_btn, size, left_img)
        self.right = TouchButton(margin + size + 20,             y_btn, size, right_img)
        self.up    = TouchButton(LOGICAL_WIDTH - margin - size,  y_btn, size, up_img)
        self.buttons = (self.left, self.right, self.up)

    def state(self):
        return {
            "left":  self.left.active,
            "right": self.right.active,
            "up":    self.up.active,
        }

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, surf):
        for b in self.buttons:
            b.draw(surf)