[app]
title = PlatCube DL
package.name = platcube
package.domain = org.platcube
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .venv,bin,build,.buildozer,__pycache__,.git,venv
version = 0.1

# Чистый pygame. Без Kivy и без pygame-ce — это самая стабильная связка
requirements = python3,pygame

orientation = landscape
fullscreen = 1
android.accept_sdk_license = True
