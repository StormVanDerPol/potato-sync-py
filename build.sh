rm -rf dist && rm -rf build && rm -rf __pycache__ && pyinstaller --onefile ./src/main.py && mv ./dist/main.exe ./dist/potato-sync.exe