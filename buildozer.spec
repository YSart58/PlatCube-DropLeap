[app]
title = PlatCube DL
package.name = platcube
package.domain = org.platcube
source.dir = .
source.include_exts = py,png,json
source.exclude_dirs = .venv,bin,build,.buildozer,__pycache__,.git,venv
version = 0.1

# Оставляем только pygame-ce, без лишнего kivy
requirements = python3,pygame-ce

orientation = landscape
fullscreen = 1
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
