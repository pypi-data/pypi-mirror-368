# pff
a fuzzy finder for files and diretories

[![PyPI Version](https://img.shields.io/pypi/v/pff)](https://pypi.org/project/pff)

> [!NOTE]
> *this app is only available on Linux and MacOS*

## searching:
to start the fuzzy search use the `pff` command it takes two arguments a directory to search in it's contents
and a pattern to search with, example

    pff . gi

> [!NOTE]
> *the '.' in the first argument is the directory it stands for current working directory, use it to search within the directory you are*
> *running the tool from*

in this example it loops through all the contents of the given directory '.' (current working directory) and searches
for entries that start with the given pattern 'gi' if it finds any file or directory with this pattern in their name
it will be printed to the console

> [!NOTE]
> *by default the application doesn't search through hidden entries as well, if you want it to search through hidden entries*
> *use the [hidden](#hidden-flag) flag*

## hidden flag:
the hidden flag allows you to see through hidden entries as well as non-hidden entries, example

    pff . gi --hidden/-H

in this example it will search through all the entries in the given directory and any entry that has 'gi' in its
name will be printed to the console, but because we included the `--hidden` flag it will also print hidden
entries that have 'gi' in their name

> [!TIP]
> *if you want to look through files only or through directories only use the [filter](#filter-option) option*

## filter option:
the filter option allows you to filter your search for files only or directories only it takes in one of two
options `files` to search through files only or `dirs` to search through directories only, example

    pff . gi --filter/-f files

in this example it will search through all the entries in the given directory, and check if the given pattern
is in the name of the entry, but it will only search through files because we used the filter option with `files`
so no directories will be taken account of

> [!TIP]
> *this option is helpful if you are looking for a specific file or directory, but not both and don't know the exact name*
> *because it allows you to get less results that may be irrelevant*

## installation:
the tool is available on PyPI to install it run

    pipx install pff

> [!TIP]
> *you can install the tool with pip and not pipx, but it is not recommended as pip is usually used for libraries*
> *to help with projects while this is a cli tool and not a library*
