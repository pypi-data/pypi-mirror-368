#!/usr/bin/env python3

# Standard libraries
from glob import glob
from os.path import expanduser
from pathlib import Path, PurePosixPath
from typing import List, Union

# Components
from ..system.platform import Platform
from .environment import Environment

# Paths class
class Paths:

    # Basename
    @staticmethod
    def basename(data: str) -> str:

        # POSIX path
        path: PurePosixPath = PurePosixPath(data)

        # Result
        return str(path.name)

    # Expand
    @staticmethod
    def expand(
        path: str,
        env: bool = True,
        home: bool = True,
    ) -> str:

        # Expand environment
        if env:
            path = Environment.expand(path)

        # Expand home
        if home:
            path = expanduser(path)

        # Result
        return path

    # Get
    @staticmethod
    def get(data: Union[Path, PurePosixPath, str]) -> str:

        # POSIX path
        path: PurePosixPath = PurePosixPath(data)

        # Result
        return str(path)

    # Home
    @staticmethod
    def home(user: str) -> str:

        # Expand home
        path: str = expanduser(f'~{user}')
        if path[0:1] != '~':
            return path

        # Default root
        if user == 'root': # pragma: no cover
            return '/root'

        # Default user
        return f'/home/{user}'

    # Resolve
    @staticmethod
    def resolve(data: Union[Path, str]) -> str:

        # Resolve path
        path: str = str(Path(data).resolve())

        # Result
        return path

    # Translate
    @staticmethod
    def translate(data: str) -> str:

        # Double backslash translation
        if data[0:1] == '\\': # pragma: no cover
            data = f'/{data[1:]}'

        # Double slash translation
        if data[0:2] == '//': # pragma: no cover
            data = data[1:]

        # Result
        return data

    # Wildcard
    @staticmethod
    def wildcard(
        path: str,
        strict: bool = False,
    ) -> List[Path]:

        # Variables
        paths: List[Path] = []
        variants: List[str] = []

        # Apply strict wildcards
        if strict:
            path = path.replace('**', '*/**')

        # Generate wildcard variants
        def wildcard_variants(path: str) -> List[str]:
            variants: List[str] = [path]
            if path.startswith('*'): # pragma: no cover
                variants += ['.' + path]
            index = path.find(Platform.PATH_SEPARATOR + '*')
            while index != -1:
                variants_new = []
                for variant in variants:
                    new_variant = variant[:index + 1] + '.' + variant[index + 1:]
                    variants_new.append(new_variant)
                for variant_new in variants_new:
                    if variant_new not in variants:
                        variants += [variant_new]
                index = variants[0].find(Platform.PATH_SEPARATOR + '*', index + 1)
            return variants

        # Evaluate wildcard variants
        variants = wildcard_variants(path)

        # Evaluate wildcards
        for variant in variants:
            for item in [Path(item) for item in glob(
                    variant,
                    recursive=True,
            )]:
                paths += [Path(item)]

        # Fallback to input
        if not paths:
            paths += [Path(path)]

        # Result
        return paths
