#!/usr/bin/env python3
#
from __future__ import annotations
from typing import List, Dict
from pip._internal.cli.main import main as pip_main


PACKAGES: Dict[str, str] = {
    'pandas': 'https://github.com/pandas-dev/pandas/archive/refs/heads/main.zip',
    'fitz': 'https://github.com/pymupdf/PyMuPDF/archive/refs/heads/main.zip',
    'pytesseract': 'https://github.com/madmaze/pytesseract/archive/refs/heads/master.zip',
}

STATUS: Dict[str, bool] = {}


def install_packages(ignore_items: List[str] = []):

    for name, url in PACKAGES.items():
        if name in ignore_items:
            continue
        print('---------------------------------')
        print(name, url)
        try:
            pip_main(['install', url])
        except Exception as e:
            print(e)
            print()


def main():
    install_packages()


if __name__ == '__main__':
    main()


