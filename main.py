"""Точка входа. Запуск: python main.py"""
import os
os.environ.setdefault("SDL_TOUCH_MOUSE_EVENTS", "0")

# --- Windows DPI awareness: убирает "мыло" на экранах 125%/150% ---
if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import sys
import pygame
from src.settings import (LOGICAL_WIDTH, LOGICAL_HEIGHT, FPS,
                          WINDOW_WIDTH, WINDOW_HEIGHT, ASSETS_DIR)
from src.game import Game


def screen_to_logical(px, py, screen_size):
    sw, sh = screen_size
    target_ratio = LOGICAL_WIDTH / LOGICAL_HEIGHT
    screen_ratio = sw / sh

    if abs(screen_ratio - target_ratio) < 0.001:
        return (int(px * LOGICAL_WIDTH / sw),
                int(py * LOGICAL_HEIGHT / sh))

    if screen_ratio > target_ratio:
        new_w, new_h = int(sh * target_ratio), sh
    else:
        new_w, new_h = sw, int(sw / target_ratio)

    x_off = (sw - new_w) / 2
    y_off = (sh - new_h) / 2
    lx = (px - x_off) * LOGICAL_WIDTH  / new_w
    ly = (py - y_off) * LOGICAL_HEIGHT / new_h
    return (int(lx), int(ly))


def scale_to_screen(canvas, screen):
    sw, sh = screen.get_size()
    cw, ch = canvas.get_size()
    if (sw, sh) == (cw, ch):
        screen.blit(canvas, (0, 0))
        return

    ratio = cw / ch
    if sw / sh > ratio:
        nw, nh = int(sh * ratio), sh
    else:
        nw, nh = sw, int(sw / ratio)

    scaled = pygame.transform.scale(canvas, (nw, nh))
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))


def _convert_mouse(event, screen):
    lx, ly = screen_to_logical(event.pos[0], event.pos[1], screen.get_size())
    if event.type == pygame.MOUSEMOTION:
        return pygame.event.Event(event.type, {
            "pos": (lx, ly), "rel": event.rel, "buttons": event.buttons,
        })
    return pygame.event.Event(event.type, {
        "pos": (lx, ly), "button": event.button,
    })


def main():
    pygame.init()
    pygame.display.set_caption("PlatCube DL")

    # 🎯 УСТАНОВКА ИКОНКИ ОКНА
    icon_path = os.path.join(ASSETS_DIR, "icon.png")
    if os.path.exists(icon_path):
        try:
            icon_img = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_img)
        except Exception as e:
            print(f"Не удалось загрузить иконку окна: {e}")

    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h

    # Запуск в полноэкранном режиме
    screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN)

    canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    game   = Game(canvas)
    clock  = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type in (pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP,
                              pygame.MOUSEMOTION):
                event = _convert_mouse(event, screen)
            elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP,
                                pygame.FINGERMOTION):
                lx, ly = screen_to_logical(
                    event.x * screen.get_width(),
                    event.y * screen.get_height(),
                    screen.get_size(),
                )
                event = pygame.event.Event(event.type, {
                    "x": lx / LOGICAL_WIDTH,
                    "y": ly / LOGICAL_HEIGHT,
                    "finger_id": event.finger_id,
                    "touch_id": getattr(event, "touch_id", event.finger_id),
                })

            if not game.handle_event(event):
                running = False
                break

        if not running:
            break

        if not game.update(clock.get_time() / 1000.0):
            running = False
            break

        game.draw()
        scale_to_screen(canvas, screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()