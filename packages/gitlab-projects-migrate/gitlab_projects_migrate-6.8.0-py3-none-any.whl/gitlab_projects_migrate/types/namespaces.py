#!/usr/bin/env python3

# Standard libraries
from re import sub
from typing import Optional, Tuple

# Namespaces class
class Namespaces:

    # Capitalize
    @staticmethod
    def capitalize(text: str, words: bool = False) -> str:

        # Capitalize words
        if words:
            return ' '.join(
                Namespaces.capitalize(word, words=False) for word in text.split())

        # Capitalize text
        return f'{text[:1].capitalize()}{text[1:]}'

    # Describe
    @staticmethod
    def describe(
        name: str,
        description: str = '',
    ) -> str:

        # Use description
        if description:
            return description

        # Adapt name
        return Namespaces.capitalize(sub(r'[-_]', ' ', name), words=True)

    # Split namespace
    @staticmethod
    def split_namespace(
        path: str,
        relative: bool = False,
    ) -> Tuple[str, str]:
        return (
            # Namespace
            f'/{path[:path.rfind("/")]}' if '/' in path and relative else \
            f'{path[:path.rfind("/")]}' if '/' in path else \
            '',
            # Path
            f'{path[path.rfind("/") + 1:]}' if '/' in path else \
            path,
        )

    # Subpath
    @staticmethod
    def subpath(
        parent_path: str,
        child_path: str,
    ) -> str:

        # Parse relative path
        if child_path.startswith(f'{parent_path}/'):
            return child_path[len(f'{parent_path}/'):]

        # Default absolute path
        return child_path

    # Text
    @staticmethod
    def text(text: Optional[str]) -> str:

        # Use text
        if text:
            return text

        # Fallback text
        return '/'
