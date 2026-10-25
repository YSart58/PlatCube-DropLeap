import os
import json
import shutil
from .settings import PROGRESS_PATH, BASE_DIR, LEVEL_COUNT


class Progress:
    def __init__(self, path=PROGRESS_PATH):
        self.path      = path
        self.completed = [False] * LEVEL_COUNT
        
        # --- НАСТРОЙКИ ---
        self.control_mode = "pc"
        self.volume       = 0.5
        self.language     = "en"  # По умолчанию английский
        
        self._ensure_dir()
        self._migrate_legacy()
        self.load()
        self.save()

    def _ensure_dir(self):
        d = os.path.dirname(self.path)
        if d and not os.path.isdir(d):
            try: os.makedirs(d, exist_ok=True)
            except OSError as e: print(f"[progress] не удалось создать {d}: {e}")

    def _migrate_legacy(self):
        if os.path.exists(self.path): return
        legacy = os.path.join(BASE_DIR, "progress.json")
        if os.path.exists(legacy) and os.path.abspath(legacy) != os.path.abspath(self.path):
            try: shutil.copy2(legacy, self.path)
            except OSError as e: print(f"[progress] не удалось мигрировать: {e}")

    def load(self):
        if not os.path.exists(self.path): return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            done = data.get("completed", [])
            for i in range(LEVEL_COUNT):
                self.completed[i] = bool(done[i]) if i < len(done) else False
                
            self.control_mode = data.get("control_mode", "pc")
            self.volume       = data.get("volume", 0.5)
            self.language     = data.get("language", "en")
            
            print(f"[progress] загружен {self.path}: {self.completed}")
        except Exception as e:
            print(f"[progress] ошибка загрузки: {e}")

    def save(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({
                    "completed": self.completed,
                    "control_mode": self.control_mode,
                    "volume": self.volume,
                    "language": self.language
                }, f, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"[progress] ошибка сохранения: {e}")

    def is_unlocked(self, idx):
        if idx == 0: return True
        return self.completed[idx - 1]

    def mark_completed(self, idx):
        if 0 <= idx < LEVEL_COUNT:
            self.completed[idx] = True
            self.save()
            print(f"[progress] уровень {idx + 1} пройден")