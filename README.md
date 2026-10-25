.\.venv\Scripts\python.exe main.py

.\.venv\Scripts\python.exe -m PyInstaller --noconsole --onefile --name "PlatCubeDL" --icon="icon.ico" --add-data "assets;assets" --add-data "levels;levels" main.py
