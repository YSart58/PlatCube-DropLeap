import pygame
import os
from .settings import ASSETS_DIR, LOGICAL_WIDTH, LOGICAL_HEIGHT


def _load_layer(name):
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        print(f"[ПАРАЛЛАКС] ОШИБКА: Файл {name} не найден в {ASSETS_DIR}!")
        # Возвращаем ярко-розовый экран, чтобы сразу было видно, что файла нет
        surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        surf.fill((255, 0, 255))
        return surf
    
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    
    # Подгоняем высоту под экран (1024x576), сохраняя пропорции
    if h != LOGICAL_HEIGHT:
        scale = LOGICAL_HEIGHT / h
        img = pygame.transform.scale(img, (int(w * scale), LOGICAL_HEIGHT))
        
    print(f"[ПАРАЛЛАКС] Загружен {name}, размер: {img.get_width()}x{img.get_height()}")
    return img


class ParallaxLayer:
    def __init__(self, image, speed_x=0.0, auto_speed=0.0):
        self.image = image
        self.speed_x = speed_x       # Влияние камеры (0 = стоит, 0.5 = движется в 2 раза медленнее)
        self.auto_speed = auto_speed # Автоматическая скорость (плюс = вправо, минус = влево)
        self.auto_offset = 0.0       # Накопленное смещение от автодвижения

    def update(self, dt):
        # Облака плывут слева направо (offset растет)
        self.auto_offset += self.auto_speed * dt

    def draw(self, surface, cam_x=0, is_menu=False):
        w = self.image.get_width()
        if w == 0: return
        
        # Если это игра, камера движет фон влево (поэтому минус)
        cam_offset = 0 if is_menu else (cam_x * self.speed_x)
        
        # Итоговое смещение
        total_offset = self.auto_offset - cam_offset
        
        # Магия зацикливания
        start_x = total_offset % w
        if start_x > 0:
            start_x -= w
            
        x = start_x
        while x < surface.get_width():
            surface.blit(self.image, (x, 0))
            x += w


class ParallaxBackground:
    def __init__(self):
        # Небо стоит на месте
        self.sky = ParallaxLayer(_load_layer("bg_sky.png"), speed_x=0.0, auto_speed=0.0)
        
        # Облака: auto_speed=20 (плывут вправо сами), speed_x=0.3 (в игре камера их сдвигает влево)
        self.clouds = ParallaxLayer(_load_layer("bg_clouds.png"), speed_x=0.3, auto_speed=20.0)

    def update(self, dt):
        self.sky.update(dt)
        self.clouds.update(dt)

    def draw(self, surface, cam_x=0, is_menu=False):
        self.sky.draw(surface, cam_x, is_menu)
        self.clouds.draw(surface, cam_x, is_menu)