#!/usr/bin/env python3

# Standard libraries
from atexit import register, unregister
from os import getpid, kill
from pathlib import Path
from signal import getsignal, SIGINT, signal, SIGTERM
from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from types import FrameType
from typing import Any, Callable, List, Optional, Union

# Files class
class Files:

    # SignalHandler type
    SignalHandler = Union[Callable[[int, Optional[FrameType]], Any], int, None]

    # TempFile type
    TempFile = Union[_TemporaryFileWrapper] # type: ignore[type-arg]

    # Members
    registered: bool = False
    signal_int: SignalHandler
    signal_term: SignalHandler
    temps: List[TempFile] = []

    # Register
    @staticmethod
    def __register() -> None:

        # Register cleanup
        if not Files.registered:
            register(Files.clean)
            Files.signal_int = getsignal(SIGINT)
            Files.signal_term = getsignal(SIGTERM)
            signal(SIGINT, Files.clean)
            signal(SIGTERM, Files.clean)
            Files.registered = True

    # Unregister
    @staticmethod
    def __unregister() -> None:

        # Unregister cleanup
        if Files.registered:
            unregister(Files.clean)
            signal(SIGINT, Files.signal_int)
            signal(SIGTERM, Files.signal_term)
            Files.registered = False

    # Clean
    @staticmethod
    def clean(
        __signalnum: Optional[int] = None,
        __frame: Optional[FrameType] = None,
    ) -> None:

        # Delete all temps
        for temp in Files.temps:
            temp_file = Path(temp.name)
            if temp_file.exists():
                temp_file.unlink()

        # Reset temps
        Files.temps = []

        # Unregister signals
        Files.__unregister()

        # Raise signal
        if __signalnum:
            kill(getpid(), __signalnum) # pragma: no cover

    # Temp
    @staticmethod
    def temp(
        path: Optional[str] = None,
        mode: str = 'wt',
        newline: str = '\n',
        prefix: str = '.tmp.',
    ) -> TempFile:

        # Create temporary file, pylint: disable=consider-using-with
        temp_file = NamedTemporaryFile(
            delete=False,
            dir=path,
            mode=mode,
            newline=newline,
            prefix=prefix,
        )

        # Register temporary file
        Files.temps += [temp_file]

        # Register signals
        Files.__register()

        # Result
        return temp_file
