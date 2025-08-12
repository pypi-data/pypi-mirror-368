#!/usr/bin/env python3

# Standard libraries
from os import access, environ, R_OK, sep
from os.path import expanduser
from pathlib import Path, PurePosixPath
from sys import platform, stdin, stdout
from typing import List

# Platform
class Platform:

    # Environment
    ENV_ANDROID: str = 'ANDROID_ROOT'
    ENV_DISPLAY: str = 'DISPLAY'
    ENV_EXPERIMENTAL: str = 'EXPERIMENTAL'
    ENV_SIMULATE_MAC_OS: str = 'SIMULATE_MAC_OS'
    ENV_SSH_AUTH_SOCK: str = 'SSH_AUTH_SOCK'
    ENV_SUDO_USER: str = 'SUDO_USER'
    ENV_XAUTHORITY: str = 'XAUTHORITY'

    # Constants
    IS_ANDROID: bool = 'ANDROID_ROOT' in environ
    IS_EXPERIMENTAL: bool = ENV_EXPERIMENTAL in environ
    IS_LINUX: bool = platform in ['linux', 'linux2']
    IS_MAC_OS: bool = platform in ['darwin'] or ENV_SIMULATE_MAC_OS in environ
    IS_SIMULATED: bool = ENV_SIMULATE_MAC_OS in environ
    IS_WINDOWS: bool = platform in ['win32', 'win64']

    # Paths
    BUILDS_DIR: PurePosixPath = PurePosixPath('/builds')

    # Separators
    PATH_SEPARATOR: str = sep

    # Sockets
    SOCKET_DISPLAY_LINUX: str = '/tmp/.X11-unix'

    # TTYs
    IS_TTY_STDIN: bool = stdin.isatty() and stdin.encoding != 'cp1252'
    IS_TTY_STDOUT: bool = stdout.isatty()
    IS_TTY_UTF8: bool = str(stdout.encoding).lower() == 'utf-8'

    # Outputs
    IS_FLUSH_ENABLED: bool = IS_TTY_STDOUT or IS_WINDOWS

    # Users
    IS_USER_SUDO: bool = ENV_SUDO_USER in environ
    USER_SUDO: str = environ[ENV_SUDO_USER] if IS_USER_SUDO else ''

    # Display
    @staticmethod
    def display() -> List[str]:

        # Variables
        sockets: List[str] = []

        # Linux display
        if Platform.IS_LINUX:
            if Path(Platform.SOCKET_DISPLAY_LINUX).exists(): # pragma: no cover
                sockets += [Platform.SOCKET_DISPLAY_LINUX]
            if environ.get(Platform.ENV_XAUTHORITY, '') and Path(
                    environ[Platform.ENV_XAUTHORITY]).exists(): # pragma: no cover
                sockets += [environ[Platform.ENV_XAUTHORITY]]

        # Result
        return sockets

    # Flush
    @staticmethod
    def flush() -> None:

        # Flush output
        print(
            '',
            end='',
            flush=Platform.IS_FLUSH_ENABLED,
        )

    # Get GID
    @staticmethod
    def getgid() -> int:

        # Result, pylint: disable=import-outside-toplevel
        try:
            from os import getgid
            return getgid()
        except ImportError: # pragma: no cover
            return 0

    # Get UID
    @staticmethod
    def getuid() -> int:

        # Result, pylint: disable=import-outside-toplevel
        try:
            from os import getuid
            return getuid()
        except ImportError: # pragma: no cover
            return 0

    # Get username
    @staticmethod
    def getusername() -> str:

        # Result, pylint: disable=import-outside-toplevel
        try:
            from getpass import getuser
            return getuser()
        except ImportError: # pragma: no cover
            return 'root'

    # Userspace
    @staticmethod
    def userspace(name: str) -> Path:

        # Variables
        home: None | Path = None

        # Elevated home
        if Platform.IS_USER_SUDO: # pragma: linux cover
            home = Path(expanduser(f'~{Platform.USER_SUDO}'))
            if not access(home, R_OK): # pragma: no cover
                home = None

        # Default home
        if not home or not home.is_dir():
            home = Path.home()

        # Windows userspace
        if Platform.IS_WINDOWS: # pragma: windows cover
            return home / 'AppData' / 'Local' / name

        # macOS userspace
        if Platform.IS_MAC_OS: # pragma: macos cover
            return home / 'Library' / 'Preferences' / name

        # Linux userspace
        return home / '.config' / name # pragma: linux cover
