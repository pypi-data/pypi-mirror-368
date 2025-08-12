#!/usr/bin/env python3

# Standard libraries
from typing import Dict

# Components
from .colors import Colors

# Themes class
class Themes:

    # Constants
    POINTER: str = '»'

    # Flags
    __prepared = False

    # Members
    __bold: str = ''
    __cyan: str = ''
    __disabled: str = ''
    __green: str = ''
    __selected: str = ''
    __yellow: str = ''

    # Prepare
    @staticmethod
    def __prepare() -> None:

        # Colors enabled
        if Colors.enabled():
            Themes.__bold = 'bold'
            Themes.__cyan = '#00FFFF bold'
            Themes.__disabled = 'italic'
            Themes.__green = '#00FF00 bold noreverse'
            Themes.__selected = 'bold noreverse'
            Themes.__yellow = '#FFFF00 bold'

        # Colors disabled
        else:
            Themes.__bold = 'noinherit bold'
            Themes.__cyan = 'noinherit bold'
            Themes.__disabled = 'noinherit italic'
            Themes.__green = 'noinherit bold noreverse'
            Themes.__selected = 'noinherit bold noreverse'
            Themes.__yellow = 'noinherit bold'

        # Raise flag
        Themes.__prepared = True

    # Checkbox
    @staticmethod
    def checkbox_style() -> Dict[str, str]:

        # Prepare
        if not Themes.__prepared:
            Themes.__prepare()

        # Result
        return {
            'answer': Themes.__cyan,
            'disabled': Themes.__disabled,
            'instruction': Themes.__cyan,
            'highlighted': Themes.__bold,
            'pointer': Themes.__yellow,
            'qmark': Themes.__yellow,
            'question': Themes.__green,
            'selected': Themes.__selected,
            'separator': Themes.__yellow,
        }

    # Configuration
    @staticmethod
    def configuration_style() -> Dict[str, str]:

        # Prepare
        if not Themes.__prepared:
            Themes.__prepare()

        # Result
        return {
            'answer': Themes.__cyan,
            'instruction': Themes.__cyan,
            'highlighted': Themes.__green,
            'pointer': Themes.__yellow,
            'qmark': Themes.__yellow,
            'question': Themes.__yellow,
            'selected': Themes.__selected,
            'separator': Themes.__yellow,
        }
