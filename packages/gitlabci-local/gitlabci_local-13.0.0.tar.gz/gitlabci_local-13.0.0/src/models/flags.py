#!/usr/bin/env python3

# Standard libraries
from typing import Optional, Union

# Components
from .variables import Variables

# Flags class, pylint: disable=too-few-public-methods
class Flags:

    # Boolean
    @staticmethod
    def boolean(value: str) -> bool:
        return value.lower() in [
            'true',
            '1',
        ]

    # String
    @staticmethod
    def string(value: Union[bool, str]) -> str:
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value) # pragma: no cover

    # Exists
    @staticmethod
    def exists(flag: str, variables: Variables) -> bool:
        return flag in variables

    # Enabled
    @staticmethod
    def enabled(flag: str, variables: Variables) -> bool:
        return Flags.exists(flag, variables) and Flags.boolean(str(variables[flag]))

    # Has
    @staticmethod
    def has(
        option: Optional[str],
        flag: str,
        variables: Variables,
    ) -> bool:
        return option is not None or Flags.exists(flag, variables)

    # Check (bool)
    @staticmethod
    def check_bool(
        option: Optional[Union[bool, str]],
        flag: str,
        variables: Variables,
        default: bool,
    ) -> bool:

        # Variables
        result: bool = default

        # Check option (bool)
        if option is not None and isinstance(option, bool) and option != default:
            result = option

        # Check option (str)
        elif option is not None and isinstance(option, str):
            result = Flags.boolean(option)

        # Check variables
        elif Flags.exists(flag, variables):
            result = Flags.boolean(str(variables[flag]))

        # Result
        return result

    # Check (str)
    @staticmethod
    def check_str(
        option: Optional[str],
        flag: str,
        variables: Variables,
        default: str,
    ) -> str:

        # Variables
        result: str = default

        # Check option
        if option is not None and option != '':
            result = option

        # Check variables
        elif Flags.exists(flag, variables):
            result = str(variables[flag])

        # Result
        return result

    # Check (strbool)
    @staticmethod
    def check_strbool(
        option: Optional[str],
        flag: str,
        variables: Variables,
        default: str,
        const: str,
    ) -> str:

        # Variables
        result: str = default

        # Check option
        if option is not None and option != '':
            result = option

        # Check variables
        elif Flags.exists(flag, variables):
            result = str(variables[flag])

        # Evaluate boolean
        if result.lower() in ['true', '1']:
            result = const
        elif result.lower() in ['false', '0']:
            result = ''

        # Result
        return result
