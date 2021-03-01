import os


def clearscreen():
    os.system("cls" if os.name == "nt" else "clear")
