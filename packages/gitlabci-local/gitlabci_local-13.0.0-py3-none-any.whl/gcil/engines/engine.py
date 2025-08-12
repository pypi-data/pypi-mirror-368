#!/usr/bin/env python3

# Standard libraries
from enum import Enum
from typing import Dict, List

# Components
from ..models.images import Entrypoint
from ..package.bundle import Bundle
from ..system.platform import Platform
from ..types.volumes import Volumes
from .base import _ExecResult, _LogsResult, BaseEngine, Commands, ContainerName
from .docker import DockerEngine
from .podman import PodmanEngine

# Backend enumeration
class Backend(Enum):
    DOCKER = 1
    PODMAN = 2
    UNKNOWN = 3

# Names enumeration, pylint: disable=too-few-public-methods
class Names:

    # Constants
    AUTO: str = 'auto'
    DOCKER: str = 'docker'
    PODMAN: str = 'podman'

    # Defaults
    DEFAULTS: List[str] = [
        DOCKER,
        PODMAN,
    ]

    # Getter
    @staticmethod
    def get(override: str) -> List[str]:

        # Adapt override
        override = override.lower() if override else ''

        # Handle engine overrides
        if override:
            auto: bool = False
            names: List[str] = []
            overrides: List[str] = override.split(',')
            for item in overrides:
                if item:
                    if Names.AUTO == item:
                        auto = True
                    else:
                        names += [name for name in Names.DEFAULTS if name == item]
            if auto or override[-1] == ',':
                names = names + Names.DEFAULTS
            names = list(dict.fromkeys(names))

        # Use engine defaults
        else:
            names = Names.DEFAULTS

        # Result
        return names

# Privileged default
def privileged_default() -> bool:
    if Platform.IS_WINDOWS:
        return False # pragma: windows cover
    return True

# Supported engines
def supported() -> List[str]:
    return [Names.AUTO] + Names.DEFAULTS

# Engine class
class Engine:

    # Members
    __engine: BaseEngine
    __name: str = ''

    # Constructor
    def __init__(
        self,
        engines_names: str,
    ) -> None:

        # Variables
        engine: BaseEngine | None = None

        # Acquire engine names
        names: List[str] = Names.get(engines_names)

        # Iterate through names
        for name in names:

            # Detect Docker engine
            if name == Names.DOCKER:
                try: # pragma: docker cover
                    engine = DockerEngine()
                    self.__name = Names.DOCKER
                    break
                except (KeyboardInterrupt, ModuleNotFoundError, PermissionError):
                    engine = None

            # Detect Podman engine
            elif name == Names.PODMAN:
                try: # pragma: podman cover
                    engine = PodmanEngine()
                    self.__name = Names.PODMAN
                    break
                except (KeyboardInterrupt, ModuleNotFoundError, PermissionError):
                    engine = None

        # Unknown engine fallback
        if not engine:
            raise NotImplementedError(
                'Unknown or unsupported container engine...'
                f' README: {Bundle.REPOSITORY}#supported-container-engines')

        # Store engine
        self.__engine = engine

    # Command exec
    def cmd_exec(self) -> str:
        return self.__engine.cmd_exec()

    # Container
    @property
    def container(self) -> ContainerName:
        return self.__engine.container

    # Exec
    def exec(self, commands: Commands) -> _ExecResult: # pragma: no cover
        return self.__engine.exec(commands)

    # Get
    def get(self, image: str) -> None:
        self.__engine.get(image)

    # Logs
    def logs(self) -> _LogsResult:
        return self.__engine.logs()

    # Name
    @property
    def name(self) -> str:
        return self.__name

    # Pull
    def pull(
        self,
        image: str,
        force: bool = False,
    ) -> None:
        self.__engine.pull(image, force=force)

    # Remove
    def remove(self) -> None:
        self.__engine.remove()

    # Remove image
    def rmi(self, image: str) -> None:
        self.__engine.rmi(image)

    # Run, pylint: disable=too-many-arguments,too-many-positional-arguments
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
        self.__engine.run(
            image=image,
            commands=commands,
            entrypoint=entrypoint,
            variables=variables,
            network=network,
            option_privileged=option_privileged,
            option_sockets=option_sockets,
            services=services,
            volumes=volumes,
            directory=directory,
            temp_folder=temp_folder,
        )

    # Stop
    def stop(self, timeout: int) -> None:
        self.__engine.stop(timeout)

    # Supports
    def supports(self, binary: str) -> bool:
        return self.__engine.supports(binary)

    # Wait
    def wait(self) -> bool:
        return self.__engine.wait()
