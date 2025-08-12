from argparse import Namespace

from .cli.cli import Cli
from .fuzzy_search.fuzzy_search import fuzzy_search
from .util.show_entries import show_entries
from . import __version__

def main():
    cli: Cli = Cli(version=__version__)
    args: Namespace = cli.setup()
    matches = fuzzy_search(args.dir, args.pattern, args.filter, args.hidden)
    show_entries(matches, args.dir)


if __name__ == "__main__":
    main()
