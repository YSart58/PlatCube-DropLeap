TEXTS = {
    "en": {
        "settings_title": "SETTINGS",
        "controls": "Controls:",
        "ctrl_pc": "Keyboard (PC)",
        "ctrl_touch": "Touch Buttons",
        "language": "Language:",
        "lang_en": "English",
        "lang_ru": "Russian",
        "music_vol": "Music Volume:",
        "back": "Back",
        "level_select": "Select Level",
        "level": "Level {n}",
        
        # Editor
        "editor_tools": {"grass": "Grass", "dirt": "Dirt", "spike": "Spike", "exit": "Exit"},
        "editor_hud1": "EDITOR [{tool}]  Grid: {grid}  Target: {target} (F1-F5)",
        "editor_hud2": "LMB place  RMB erase  S save  Ctrl+Z undo  Del reset  G grid",
        "editor_hud3": "Arrows or A D - camera.  C or Esc - exit",
        "editor_on": "ON",
        "editor_off": "OFF",
        "editor_msg_saved": "Saved L{n}: {file}",
        "editor_msg_save_err": "Save error: {err}",
        "editor_msg_reset": "Reset to default",
        "editor_msg_undo": "Undone",
        "editor_msg_undo_empty": "Nothing to undo",
        "editor_msg_grid": "Grid: {state}",
        "editor_msg_tool": "Tool: {tool}",
        "editor_msg_target": "Target: level{n}.json"
    },
    "ru": {
        "settings_title": "НАСТРОЙКИ",
        "controls": "Управление:",
        "ctrl_pc": "Клавиатура (ПК)",
        "ctrl_touch": "Экранные кнопки",
        "language": "Язык:",
        "lang_en": "Английский",
        "lang_ru": "Русский",
        "music_vol": "Громкость музыки:",
        "back": "Назад",
        "level_select": "Выбор уровня",
        "level": "Уровень {n}",
        
        # Editor
        "editor_tools": {"grass": "Трава", "dirt": "Земля", "spike": "Шип", "exit": "Портал"},
        "editor_hud1": "РЕДАКТОР [{tool}]  Сетка: {grid}  Цель: {target} (F1-F5)",
        "editor_hud2": "ЛКМ поставить  ПКМ стереть  S сохранить  Ctrl+Z отмена  Del сброс  G сетка",
        "editor_hud3": "Стрелки или A D - камера.  C или Esc - выход",
        "editor_on": "ВКЛ",
        "editor_off": "ВЫКЛ",
        "editor_msg_saved": "Сохранено L{n}: {file}",
        "editor_msg_save_err": "Ошибка сохранения: {err}",
        "editor_msg_reset": "Сброс на дефолт",
        "editor_msg_undo": "Отменено",
        "editor_msg_undo_empty": "Нечего отменять",
        "editor_msg_grid": "Сетка: {state}",
        "editor_msg_tool": "Инструмент: {tool}",
        "editor_msg_target": "Цель сохранения: level{n}.json"
    }
}

def get_text(key, lang, **kwargs):
    """Возвращает переведенный текст с подстановкой переменных."""
    lang_dict = TEXTS.get(lang, TEXTS["en"])
    text = lang_dict.get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def get_tool_name(tool_key, lang):
    """Отдельная функция для получения названия инструмента редактора."""
    lang_dict = TEXTS.get(lang, TEXTS["en"])
    return lang_dict.get("editor_tools", {}).get(tool_key, tool_key)