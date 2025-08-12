#!/usr/bin/env python3

# Standard libraries
from os import environ
from re import sub as regex_sub
from subprocess import CalledProcessError, check_output, DEVNULL
from typing import Optional

# Components
from ..package.bundle import Bundle

# Git class
class Git:

    # Members
    __binary: str = 'git'

    # Constructor
    def __init__(self) -> None:

        # Configure binary
        if environ.get(Bundle.ENV_GIT_BINARY_PATH, ''):
            self.__binary = environ[Bundle.ENV_GIT_BINARY_PATH]

    # Default branch
    def branch_default(
        self,
        workdir: Optional[str] = None,
    ) -> str:

        # Result
        try:
            remote_name: str = check_output(
                [self.__binary, 'remote'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode().splitlines()[0]
            return check_output(
                [
                    self.__binary,
                    'symbolic-ref',
                    '--short',
                    f'refs/remotes/{remote_name}/HEAD',
                ],
                shell=False,
                stderr=DEVNULL,
            ).strip().decode().rsplit('/', maxsplit=1)[-1]
        except (CalledProcessError, FileNotFoundError):
            return 'main'

    # HEAD reference name
    def head_reference_name(
        self,
        workdir: Optional[str] = None,
    ) -> str:

        # Result
        try:
            return check_output(
                [self.__binary, 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode()
        except (CalledProcessError, FileNotFoundError):
            return ''

    # HEAD reference slug
    def head_reference_slug(
        self,
        workdir: Optional[str] = None,
        name: Optional[str] = None,
    ) -> str:

        # Get name
        if name is None: # pragma: no cover
            name = self.head_reference_name(workdir)

        # Adapt slug
        slug = name.lower()[0:63]
        slug = regex_sub(r'[^a-z0-9]', '-', slug).strip('-')

        # Result
        return slug

    # HEAD revision hash
    def head_revision_hash(
        self,
        workdir: Optional[str] = None,
    ) -> str:

        # Result
        try:
            return check_output(
                [self.__binary, 'rev-parse', 'HEAD'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode()
        except (CalledProcessError, FileNotFoundError):
            return ''

    # HEAD revision short hash
    def head_revision_short_hash(
        self,
        workdir: Optional[str] = None,
    ) -> str:

        # Result
        try:
            return check_output(
                [self.__binary, 'rev-parse', '--short', 'HEAD'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode()
        except (CalledProcessError, FileNotFoundError):
            return ''
