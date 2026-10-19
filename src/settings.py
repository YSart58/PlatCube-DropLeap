import os
import sys


def _project_dir():
    """Где лежат .py файлы. На Android — внутри APK (read-only)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _is_android():
    return "ANDROID_PRIVATE" in os.environ


def _user_data_dir():
    """Куда писать данные пользователя (progress). НЕ в папке с игрой."""
    if _is_android():
        return os.environ["ANDROID_PRIVATE"]
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PlatCubeDL")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/PlatCubeDL")
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, "PlatCubeDL")


BASE_DIR   = _project_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ---- Пользовательские данные (progress.json) ----
USER_DIR      = _user_data_dir()
PROGRESS_PATH = os.path.join(USER_DIR, "progress.json")

# ---- Уровни ----
# Бандл (что внутри APK / лежит в проекте): всегда BASE_DIR/levels
LEVELS_DIR_BUNDLED = os.path.join(BASE_DIR, "levels")

# Writable (куда сохраняет редактор):
#   Android  → USER_DIR/levels   (read-only APK → копируем оттуда)
#   Desktop  → BASE_DIR/levels   (правишь прямо в проекте)
if _is_android():
    LEVELS_DIR_WRITABLE = os.path.join(USER_DIR, "levels")
else:
    LEVELS_DIR_WRITABLE = LEVELS_DIR_BUNDLED


def level_path(idx):
    """Путь для чтения/записи уровня (writable)."""
    return os.path.join(LEVELS_DIR_WRITABLE, f"level{idx + 1}.json")


def bundled_level_path(idx):
    """Путь к уровню в бандле (только чтение). На десктопе совпадает с level_path."""
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