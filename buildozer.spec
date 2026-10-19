[app]
title = PlatCube DL
package.name = platcube
package.domain = org.platcube
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .venv,bin,build,.buildozer,__pycache__,.git,venv
version = 0.1

# Фиксируем стабильный Python 3.10 (3.12 ломает сборку Cython) и современный pygame-ce
requirements = python3==3.10.12, hostpython3==3.10.12, pygame-ce
p4a.bootstrap = sdl2

# Принудительно ставим NDK 23b (на новых версиях ломается компилятор clang)
android.ndk = 23b

orientation = landscape
fullscreen = 1
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
