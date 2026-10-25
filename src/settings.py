import os
import sys

def _project_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _is_android():
    return "ANDROID_PRIVATE" in os.environ or "ANDROID_ARGUMENT" in os.environ or sys.platform == "android"

def _user_data_dir():
    if _is_android():
        if "ANDROID_PRIVATE" in os.environ:
            return os.environ["ANDROID_PRIVATE"]
        return os.path.expanduser("~")
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PlatCubeDL")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PlatCubeDL")
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, "PlatCubeDL")

BASE_DIR   = _project_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---- ШРИФТ (поддержка .otf и .ttf) ----
FONT_PATH = os.path.join(ASSETS_DIR, "font.otf")
if not os.path.exists(FONT_PATH):
    FONT_PATH = os.path.join(ASSETS_DIR, "font.ttf")

# ---- Пользовательские данные (progress.json) ----
USER_DIR      = _user_data_dir()
PROGRESS_PATH = os.path.join(USER_DIR, "progress.json")

# ---- Уровни ----
LEVELS_DIR_BUNDLED = os.path.join(BASE_DIR, "levels")

if _is_android():
    LEVELS_DIR_WRITABLE = os.path.join(USER_DIR, "levels")
else:
    LEVELS_DIR_WRITABLE = LEVELS_DIR_BUNDLED

def level_path(idx):
    return os.path.join(LEVELS_DIR_WRITABLE, f"level{idx + 1}.json")

def bundled_level_path(idx):
    return os.path.join(LEVELS_DIR_BUNDLED, f"level{idx + 1}.json")

# ---- Экран ----
LOGICAL_WIDTH  = 1024
LOGICAL_HEIGHT = 576
WINDOW_WIDTH   = 1280
WINDOW_HEIGHT  = 720
FPS            = 60

# ---- Физика ----
TILE_SIZE       = 32
GRAVITY         = 0.9
PLAYER_SPEED    = 4
JUMP_VELOCITY   = -18
MAX_FALL_SPEED  = 20

COYOTE_TIME = 0.1
JUMP_BUFFER = 0.1

BUTTON_ALPHA = 150

LEVEL_COUNT = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)