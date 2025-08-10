#!/usr/bin/env python3
from soup_files import __version__


def test():
    from soup_files import (
        File, Directory, UserFileSystem, LibraryDocs, InputFiles
    )
    pass


def main():
    print(f' soup_files - versão: {__version__}')
    test()


if __name__ == '__main__':
    main()
