#!/usr/bin/env python3

# Standard libraries
from os.path import expandvars
from re import sub as regex_sub

# Environment class, pylint: disable=too-few-public-methods
class Environment:

    # Expand
    @staticmethod
    def expand(
        value: str,
        variable: str = '',
        unknowns: bool = False,
    ) -> str:

        # Variables
        last: str = ''
        result: str = value

        # Avoid nested variable
        if variable:
            result = regex_sub(
                r'(?<!\\)\${' + f'{variable}' + '}',
                '',
                result,
            )
            result = regex_sub(
                r'(?<!\\)\$' + f'{variable}' + r'([^A-Za-z_]+|$)',
                '\\1',
                result,
            )

        # Expand while needed
        while last != result:
            last = result
            result = expandvars(result)

        # Expand unknown variables
        if unknowns:
            result = regex_sub(
                r'(?<!\\)\${?[A-Za-z_][A-Za-z0-9_]*}?',
                '',
                result,
            )

        # Result
        return result
