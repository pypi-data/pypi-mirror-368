import sys
import os
from colorama import Fore

def fuzzy_search(dir: str, pattern: str, filter_by: str, hidden: bool) -> list[str]:
    if not os.path.exists(dir) or os.path.isfile(dir):
        print(Fore.RED + f"{dir} is invalid", file=sys.stderr)
        sys.exit(1)
    
    matches = []
    entries = os.listdir(dir)

    if filter_by == "files":
        entries = filter(lambda entry: os.path.isfile(os.path.join(dir, entry)), entries)
    elif filter_by == "dirs":
        entries = filter(lambda entry: os.path.isdir(os.path.join(dir, entry)), entries)
    elif filter_by != "":
        print(Fore.RED + f"invalid option for filter", file=sys.stderr)
        sys.exit(1)

    for entry in entries:
        if entry.startswith(".") and not hidden:
            continue
        if pattern in entry:
            matches.append(entry)
    
    return matches