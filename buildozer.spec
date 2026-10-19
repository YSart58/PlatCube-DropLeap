[app]
title = PlatCube DL
package.name = platcube
package.domain = org.platcube
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .venv,bin,build,.buildozer,__pycache__,.git,venv
version = 0.1

# Kivy нужен для работы сборщика, pygame-ce - для самой игры
requirements = python3, kivy==2.3.0, pygame-ce
p4a.bootstrap = sdl2

# NDK 23b - самая стабильная версия для pygame
android.ndk = 23b
android.accept_sdk_license = True

orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1
