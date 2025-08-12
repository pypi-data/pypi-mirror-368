#!/usr/bin/env python3

# Standard libraries
from pathlib import Path
from sys import exc_info
from typing import Dict, List

# Components
from ..types.files import Files
from ..types.paths import Paths

# ScriptsFile class
class ScriptsFile:

    # Constants
    __SEPARATOR: str = '\n'
    SHEBANG_MARKER_BASH: str = '__GITLAB_CI_LOCAL_SHEBANG_MARKER_BASH__'

    # Members
    __file: Files.TempFile
    __folder: str
    __ready: bool
    __target: str

    # Constructor
    def __init__(
        self,
        paths: Dict[str, str],
        prefix: str = '.tmp.',
    ) -> None:

        # Variables
        error = ''

        # Initialize members
        self.__folder = ''
        self.__ready = False
        self.__target = ''

        # Iterate through paths
        for path in paths:

            # Prepare temporary script
            try:
                self.__file = Files.temp(path=path, prefix=prefix)
                self.__folder = path
                if paths[path]:
                    self.__target = Paths.get(
                        Path(paths[path]) / Path(self.__file.name).name)
                self.__ready = True
                break
            except PermissionError:
                error = str(exc_info()[1])

        # Failed temporary script
        if not self.__ready:
            raise PermissionError(error)

    # Configure
    def configure(
        self,
        errors: bool = True,
        verbose: bool = True,
    ) -> None:

        # Write configuration
        self.writelines([
            '  # Configurations',
            f"  set -{'e' if errors else ''}{'x' if verbose else ''}",
            '',
        ])

    # Close
    def close(self) -> None:

        # Flush file
        self.flush()

        # Close file
        self.__file.close()

    # Flush
    def flush(self) -> None:

        # Flush file
        if not self.__file.closed:
            self.__file.flush()

    # Folder
    @property
    def folder(self) -> str:

        # Result
        return self.__folder

    # Name
    @property
    def name(self) -> str:

        # Result
        return self.__file.name

    # Print
    def print(self) -> None:

        # Flush file
        self.flush()

        # Print content
        with open(self.__file.name, encoding='utf8', mode='r') as file:
            print(file.read())

    # Shebang
    def shebang(self) -> None:

        # Write shebang
        self.write('#!/bin/sh')
        self.write('')

        # Write shebang wrapper
        self.writelines([
            '# Bash shebang wrapper',
            f'if [ -z "${{{self.SHEBANG_MARKER_BASH}}}" ] && type bash >/dev/null 2>&1; then',
            f'  {self.SHEBANG_MARKER_BASH}=true bash "${0}"',
            '  exit "${?}"',
            'fi',
            '',
        ])

    # Subgroup start
    def subgroup_start(self) -> None:

        # Write subgroup start
        self.write('{')

    # Subgroup stop
    def subgroup_stop(self) -> None:

        # Write subgroup stop
        self.write('}')

    # Subshell start
    def subshell_start(
        self,
        section: str,
    ) -> None:

        # Write subshell start
        self.write(f'# Section {section}')
        self.write('(')

    # Subshell stop
    def subshell_stop(
        self,
        section: str,
    ) -> None:

        # Write subshell stop
        self.write(') 2>&1')
        self.write(f'# Section {section}')

    # Target
    def target(self) -> str:

        # Result
        return self.__target

    # Write
    def write(self, line: str = '') -> None:

        # Write line
        self.__file.write(line)
        self.__file.write(self.__SEPARATOR)

    # Write lines
    def writelines(
        self,
        lines: List[str],
    ) -> None:

        # Write line
        self.__file.write(self.__SEPARATOR.join(lines))
        self.__file.write(self.__SEPARATOR)
