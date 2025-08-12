#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from os import environ
from pathlib import Path
from typing import Dict, List

# Components
from ..types.environment import Environment

# VariableName type
VariableName = str

# VariableValue type
VariableValue = str

# Variables type
Variables = Dict[VariableName, VariableValue]

# VariablesParser class
class VariablesParser:

    # Enumerations
    Types = Enum('Types', [
        'PARAMETERS',
        'LOCALS',
        'GLOBALS',
        'ENV_FILES',
    ])

    # Members
    __cache: Variables
    __env_files: Variables
    __globals: Variables
    __locals: Variables
    __options: Namespace
    __parameters: Variables

    # Constructor
    def __init__(
        self,
        options: Namespace,
    ) -> None:

        # Prepare options
        self.__options = options

        # Prepare members
        self.__env_files = {}
        self.__globals = {}
        self.__locals = {}
        self.__parameters = {}

        # Cache environment
        self.environment_cache()

        # Parse env options
        self.options_parse_env()

    # Cache environment
    def environment_cache(self) -> None:
        self.__cache = environ.copy()

    # Restore environment
    def environment_restore(self) -> None:
        environ.clear()
        environ.update(self.__cache)

    # Update environment
    @staticmethod
    def environment_update(values: Dict[str, str]) -> None:

        # Apply environment values
        environ.update(values)

    # Apply variables
    def apply(
        self,
        types: List[Types],
    ) -> None:

        # Prepare parameters variables
        if VariablesParser.Types.PARAMETERS in types:
            for variable, value in self.__parameters.items():
                environ[variable] = value

        # Prepare locals variables
        if VariablesParser.Types.LOCALS in types:
            for variable, value in self.__locals.items():
                if variable not in environ:
                    environ[variable] = value

        # Prepare globals variables
        if VariablesParser.Types.GLOBALS in types:
            for variable, value in self.__globals.items():
                if variable not in environ:
                    environ[variable] = value

        # Prepare env_files variables
        if VariablesParser.Types.ENV_FILES in types:
            for variable, value in self.__env_files.items():
                if variable not in environ:
                    environ[variable] = value

    # Evaluate job variables
    def evaluate_job(
        self,
        job_variables: Dict[str, str],
    ) -> Dict[str, str]:

        # Variables
        variables: Variables = {}

        # Register parameters variables
        for variable, value in self.__parameters.items():
            variables[variable] = value

        # Register locals variables
        for variable, value in self.__locals.items():
            if variable not in variables:
                variables[variable] = value

        # Register job variables
        for variable, value in job_variables.items():
            if variable not in variables:
                variables[variable] = str(value)

        # Register globals variables
        for variable, value in self.__globals.items():
            if variable not in variables:
                variables[variable] = value

        # Register env_files variables
        for variable, value in self.__env_files.items():
            if variable not in variables:
                variables[variable] = value

        # Result
        return variables

    # Expand value
    def expand(
        self,
        value: str,
        types: List[Types],
    ) -> str:

        # Cache environment
        cache = environ.copy()

        # Apply variables
        self.apply(types)

        # Expand environment
        result = Environment.expand(value)

        # Restore environment
        environ.clear()
        environ.update(cache)

        # Result
        return result

    # Parse options
    def options_parse_env(self) -> None:

        # Variables
        files: List[Path] = []

        # Register .env file
        files += [
            Path(self.__options.path) / '.env',
        ]

        # Parse env options
        if self.__options.env:
            for env in self.__options.env:
                env_parsed = env.split('=', 1)

                # Parse VARIABLE=value
                if len(env_parsed) == 2:
                    variable = env_parsed[0]
                    value = env_parsed[1]
                    self.__parameters[variable] = value

                # Parse ENVIRONMENT_FILE
                elif (Path(self.__options.path) / env).is_file():
                    files += [Path(self.__options.path) / env]

                # Parse VARIABLE
                else:
                    variable = env
                    if variable in environ:
                        self.__parameters[variable] = environ[variable]

        # Parse environment files
        if files:

            # Modules libraries, pylint: disable=import-outside-toplevel
            from dotenv import dotenv_values

            # Iterate through environment files
            for env_file in files:
                try:
                    if not env_file.is_file():
                        continue
                except PermissionError: # pragma: no cover
                    continue

                # Parse environment files
                env_values = dotenv_values(dotenv_path=env_file)
                for variable in env_values:

                    # Define default environment variable
                    if isinstance(env_values[variable], str):
                        self.__env_files[variable] = str(env_values[variable])

    # Parse local_env
    def local_parse_env(
        self,
        data_node: List[str],
    ) -> None:

        # Parse data node
        for env in data_node:
            env_parsed = env.split('=', 1)

            # Parse VARIABLE=value
            if len(env_parsed) == 2:
                variable = env_parsed[0]
                value = env_parsed[1]
                if variable not in self.__locals:
                    self.__locals[variable] = value

            # Parse ENVIRONMENT_FILE
            elif (Path(self.__options.path) / env).is_file():

                # Modules libraries, pylint: disable=import-outside-toplevel
                from dotenv import dotenv_values

                # Parse environment file
                env_file = Path(self.__options.path) / env
                env_values = dotenv_values(dotenv_path=env_file)
                for variable in env_values:

                    # Define default environment variable
                    if variable not in self.__locals and isinstance(
                            env_values[variable], str):
                        self.__locals[variable] = str(env_values[variable])

            # Parse VARIABLE
            else:
                variable = env
                if variable not in self.__locals and variable in environ:
                    self.__locals[variable] = environ[variable]

    # Parse local_variables
    def local_parse_variables(
        self,
        data_node: Dict[str, str],
    ) -> None:

        # Parse data node
        for variable in data_node:
            value = data_node[variable]
            if variable not in self.__locals:
                self.__locals[variable] = str(value)

    # Globals
    @property
    def globals(self) -> Dict[str, str]:
        return self.__globals

    # Parameters
    @property
    def parameters(self) -> Dict[str, str]:
        return self.__parameters
