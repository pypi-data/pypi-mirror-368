#!/usr/bin/env python3

# Modules libraries
try:
    from prompt_toolkit.styles.style import Style as prompt_toolkit_styles_Style
except ModuleNotFoundError: # pragma: no cover
    from typing import Any as prompt_toolkit_styles_Style # type: ignore[assignment]

# Components
from .colors import Colors

# Themes class, pylint: disable=too-few-public-methods
class Themes:

    # Flags
    __prepared = False

    # Members
    __bold: str = ''
    __red: str = ''
    __selected: str = ''

    # Prepare
    @staticmethod
    def __prepare() -> None:

        # Colors enabled
        if Colors.enabled():
            Themes.__bold = 'bold'
            Themes.__red = '#FF0000 bold'
            Themes.__selected = 'bold noreverse'

        # Colors disabled
        else:
            Themes.__bold = 'noinherit bold'
            Themes.__red = 'noinherit bold'
            Themes.__selected = 'noinherit bold noreverse'

        # Raise flag
        Themes.__prepared = True

    # Confirmation
    @staticmethod
    def confirmation_style() -> prompt_toolkit_styles_Style:

        # Prepare
        if not Themes.__prepared:
            Themes.__prepare()

        # Result
        return prompt_toolkit_styles_Style([
            ('answer', Themes.__red),
            ('instruction', Themes.__red),
            ('highlighted', Themes.__bold),
            ('pointer', Themes.__bold),
            ('qmark', Themes.__bold),
            ('question', Themes.__bold),
            ('selected', Themes.__selected),
            ('separator', Themes.__bold),
        ])
