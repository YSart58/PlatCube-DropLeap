import sys
import traceback
import os

print("=" * 60)
print("PlatCube DL — диагностический запуск")
print("=" * 60)
print(f"Python: {sys.version}")
print(f"CWD:    {os.getcwd()}")
print(f"Файл:   {os.path.abspath(__file__)}")
print("-" * 60)

try:
    import pygame
    print(f"pygame: {pygame.version.ver}")
except Exception as e:
    print(f"[ОШИБКА] import pygame: {e}")
    input("Enter для выхода...")
    sys.exit(1)

# Проверка всех файлов
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
LEVELS = os.path.join(BASE, "levels")

needed_assets = [
    "bg.png", "player.png", "b_grass.png", "b_dirt.png",
    "spike.png", "exit.png",
    "c_left.png", "c_right.png", "c_up.png",
    "pcdl_logo.png", "menu_play.png", "menu_exit.png",
    "l1.png", "l2.png", "l3.png", "l4.png", "l5.png",
]
print(f"\n[Проверка] assets: {ASSETS}")
missing = []
for f in needed_assets:
    p = os.path.join(ASSETS, f)
    if os.path.exists(p):
        print(f"  ✓ {f}")
    else:
        print(f"  ✗ {f}  ОТСУТСТВУЕТ")
        missing.append(f)

if missing:
    print(f"\n[ВНИМАНИЕ] Не хватает {len(missing)} картинок — игра упадёт на них.")
    print(f"          Отсутствуют: {', '.join(missing)}")

print(f"\n[Проверка] levels: {LEVELS}")
if os.path.isdir(LEVELS):
    print(f"  папка существует, файлов: {len(os.listdir(LEVELS))}")
else:
    print(f"  папка не существует — создастся при первом запуске")

print("\n" + "=" * 60)
print("Запуск main.py...")
print("=" * 60 + "\n")

try:
    from main import main
    main()
    print("\n[main] завершился нормально (без ошибок)")
except SystemExit as e:
    print(f"\n[main] SystemExit({e.code}) — нормальный выход")
except Exception as e:
    print("\n" + "!" * 60)
    print("ОШИБКА:")
    print("!" * 60)
    traceback.print_exc()
    print("!" * 60)

input("\nНажми Enter, чтобы закрыть...")