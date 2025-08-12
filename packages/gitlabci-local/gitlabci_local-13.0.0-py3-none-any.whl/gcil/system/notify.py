#!/usr/bin/env python3

# Standard libraries
from os import environ
from subprocess import CalledProcessError, check_output, DEVNULL

# Components
from ..package.bundle import Bundle

# Notify class, pylint: disable=too-few-public-methods
class Notify:

    # Members
    __binary: str = 'notify-send'

    # Constructor
    def __init__(self) -> None:

        # Configure binary
        if environ.get(Bundle.ENV_NOTIFY_BINARY_PATH, ''):
            self.__binary = environ[Bundle.ENV_NOTIFY_BINARY_PATH]

    # Notify
    def notify(self, message: str) -> None:

        # Result
        try:
            check_output(
                [self.__binary, message],
                shell=False,
                stderr=DEVNULL,
            )
        except (CalledProcessError, FileNotFoundError):
            pass
