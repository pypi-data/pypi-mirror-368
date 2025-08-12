#!/usr/bin/env python3

# Standard libraries
from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, NamedTuple

# Components
from ..models.images import Entrypoint
from ..types.volumes import Volumes

# Commands type
Commands = List[str]

# ContainerName type
ContainerName = str

# _ExecResult type
class _ExecResult(NamedTuple):

    # Properties
    exit_code: int
    output: str

# _LogsResult type
_LogsResult = Iterator[bytes]

# Base engine class, pylint: disable=unused-argument
class BaseEngine(ABC): # pragma: no cover

    # Command exec
    @abstractmethod
    def cmd_exec(self) -> str:
        return ''

    # Container
    @property
    @abstractmethod
    def container(self) -> ContainerName:
        return ''

    # Exec
    @abstractmethod
    def exec(self, commands: Commands) -> _ExecResult:
        return _ExecResult(
            0,
            '',
        )

    # Get
    @abstractmethod
    def get(self, image: str) -> None:
        pass

    # Logs
    @abstractmethod
    def logs(self) -> _LogsResult:
        return iter() # type: ignore[call-overload,no-any-return]

    # Pull
    @abstractmethod
    def pull(
        self,
        image: str,
        force: bool = False,
    ) -> None:
        pass

    # Remove
    @abstractmethod
    def remove(self) -> None:
        pass

    # Remove image
    @abstractmethod
    def rmi(self, image: str) -> None:
        pass

    # Run, pylint: disable=too-many-arguments,too-many-positional-arguments
    @abstractmethod
    def run(
        self,
        image: str,
        commands: Commands,
        entrypoint: Entrypoint,
        variables: Dict[str, str],
        network: str,
        option_privileged: bool,
        option_sockets: bool,
        services: bool,
        volumes: Volumes,
        directory: str,
        temp_folder: str,
    ) -> None:
        pass

    # Stop
    @abstractmethod
    def stop(self, timeout: int) -> None:
        pass

    # Supports
    @abstractmethod
    def supports(self, binary: str) -> bool:
        return False

    # Wait
    @abstractmethod
    def wait(self) -> bool:
        return False
