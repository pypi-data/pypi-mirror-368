#!/usr/bin/env python3

# Standard libraries
from pathlib import Path
from re import sub
from typing import Union

# Paths class, pylint: disable=too-few-public-methods
class Paths:

    # Resolve
    @staticmethod
    def resolve(data: Union[Path, str]) -> str:

        # Resolve path
        path: str = str(Path(data).resolve())

        # Result
        return path

    # Slugify
    @staticmethod
    def slugify(text: str) -> str:

        # Variables
        result: str = text.strip().lower()

        # Adapt to file slug
        result = sub(r'[\\/]', '_', result)
        result = sub(r'[^-_\s\w]', '', result)
        result = sub(r'[-\s]+', '-', result)

        # Result
        return result
