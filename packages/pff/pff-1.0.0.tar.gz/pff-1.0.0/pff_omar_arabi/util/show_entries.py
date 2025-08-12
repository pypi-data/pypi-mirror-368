from colorama import Fore
import os

def show_entries(entries: list[str], dir: str) -> None:
    for entry in entries:
        relative_path = os.path.join(dir, entry)
        if os.path.isfile(relative_path):
            print(Fore.GREEN + f"File: {entry}")
        elif os.path.isdir(relative_path):
            print(Fore.BLUE + f"Dir: {entry}")