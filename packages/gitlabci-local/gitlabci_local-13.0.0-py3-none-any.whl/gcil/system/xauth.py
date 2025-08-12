#!/usr/bin/env python3

# Standard libraries
from os import environ
from pathlib import Path
from subprocess import CalledProcessError, check_output, DEVNULL

# Components
from ..system.platform import Platform

# Xauth class
class Xauth:

    # Members
    BINARY: str = 'xauth'

    # Display
    @staticmethod
    def display() -> str:

        # Variables
        result: str = ''

        # Acquire display configuration
        if Platform.ENV_DISPLAY in environ: # pragma: no cover
            result = environ[Platform.ENV_DISPLAY]

        # Result
        return result

    # Magic
    @staticmethod
    def magic() -> str:

        # Variables
        display: str
        result: str = ''
        xauthority_path: str = ''

        # Acquire display configuration
        display = Xauth.display()

        # Specific Xauthority path
        if environ.get(Platform.ENV_XAUTHORITY, '') and Path(
                environ[Platform.ENV_XAUTHORITY]).exists(): # pragma: no cover
            xauthority_path = environ[Platform.ENV_XAUTHORITY]

        # Acquire Xauthority
        if Platform.IS_LINUX:
            try:
                result = check_output(
                    [Xauth.BINARY] + ([
                        '-f',
                        xauthority_path,
                    ] if xauthority_path else []) + [
                        'list',
                        display,
                    ],
                    shell=False,
                    stderr=DEVNULL,
                ).strip().decode().splitlines()[0]
            except (CalledProcessError, FileNotFoundError):
                result = ''

        # Result
        return result
