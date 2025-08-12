#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from sys import exc_info
from typing import Dict, List, Optional

# Components
from ..models.pipelines import Pipeline
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..types.yaml import YAML
from .gitlab import GitLab

# Parsers class, pylint: disable=too-few-public-methods
class Parsers:

    # Members
    __options: Namespace

    # Constructor
    def __init__(
        self,
        options: Namespace,
    ) -> None:

        # Prepare options
        self.__options = options

    # Read
    def read(self) -> Optional[Pipeline]:

        # Prepare inputs
        inputs: Dict[str, str] = {}
        if self.__options.input:
            for input_key_value in self.__options.input:
                input_fields: List[str] = input_key_value.split('=')
                if len(input_fields) == 2:
                    input_key: str = input_fields[0]
                    input_value: str = input_fields[1]
                    inputs[input_key] = input_value

        # Read GitLab CI YAML
        try:
            with open(
                    self.__options.configuration,
                    encoding='utf8',
                    mode='r',
            ) as configuration_data:
                data: Optional[YAML.Data] = YAML.load(
                    configuration_data,
                    inputs=inputs,
                    configure=self.__options.configure,
                )
                if not data:
                    raise YAML.Error(
                        f'Empty YAML content found in \'{self.__options.configuration}\'...'
                    )
                return GitLab(self.__options).parse(data)
        except YAML.Error as exc:
            print(' ')
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}{exc}{Colors.RESET}'
            )
            print(' ')
        except (FileNotFoundError, PermissionError):
            print(' ')
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}{str(exc_info()[1])}{Colors.RESET}'
            )
            print(' ')

        # Failure
        return None
