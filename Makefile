
PYTHON = python

.DEFAULT_GOAL = help

help:
	@echo "-------------------------------"
	@echo "make run > run the cli from src"
	@echo "make build > build windows binary (check /dist)"
	@echo "make install > installs required modules (Make sure you got a venv going on for your sanity)"
	@echo "-------------------------------"

run:
	${PYTHON} ./src/main.py
build:
	pyinstaller ./src/main.py --icon=icon-192.ico --onefile --add-data "potato-python\Lib\site-packages\pyfiglet;./pyfiglet" --exclude-module=_lzma --exclude-module=_bz2 --exclude-module _hashlib --exclude-module pyinstaller --exclude-module pyinstaller-hooks-contrib
install:
	pip install -r requirements.txt