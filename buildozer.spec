[app]
title = PlatCube DL
package.name = platcube
package.domain = org.platcube
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .venv,bin,build,.buildozer,__pycache__,.git,venv
version = 0.1

# ✅ ВОЗВРАЩАЕМ pygame-ce и ФИКСИРУЕМ версии Python/Cython
requirements = python3==3.11.9, kivy==2.3.0, hostpython3==3.11.9, pygame-ce
p4a.bootstrap = sdl2

orientation = landscape
fullscreen = 1
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
