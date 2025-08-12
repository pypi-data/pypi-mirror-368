from argparse import Namespace
import argparse

class Cli:
    def __init__(self, version: str) -> None:
        self.version = version


    def setup(self) -> Namespace:
        parser = argparse.ArgumentParser(prog="pff", description="a fuzzy finder for files and diretories")
        parser.add_argument("-v", "--version", action="version", version=f"%(prog)s v{self.version}")
        parser.add_argument("dir", type=str, help="the directory to search in")
        parser.add_argument("pattern", type=str, help="the pattern to search for in the file name")
        parser.add_argument("-f", "--filter", type=str, help="filter on wether you want to see fiels only or dirs only", required=False, default="")
        parser.add_argument("-H", "--hidden", action="store_true", help="show the hidden files as well", required=False)

        return parser.parse_args()
