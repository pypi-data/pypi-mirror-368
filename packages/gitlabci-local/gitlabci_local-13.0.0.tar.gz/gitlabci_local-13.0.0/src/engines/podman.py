#!/usr/bin/env python3

# Standard libraries
from __future__ import annotations
from os import environ
from subprocess import CompletedProcess, DEVNULL, PIPE, Popen, run
from typing import Dict, Iterator, List, Optional

# Components
from ..models.images import Entrypoint
from ..package.bundle import Bundle
from ..system.platform import Platform
from ..types.volumes import Volumes
from .base import _ExecResult, _LogsResult, BaseEngine, Commands, ContainerName

# Podman engine class
class PodmanEngine(BaseEngine): # pragma: podman cover

    # Members
    __binary: str = 'podman'
    __container: Optional[str]

    # Constructor
    def __init__(self) -> None:

        # Prepare container
        self.__container = None

        # Configure binary
        if environ.get(Bundle.ENV_PODMAN_BINARY_PATH, ''):
            self.__binary = environ[Bundle.ENV_PODMAN_BINARY_PATH]

        # Check engine support
        try:
            result = self.__exec([
                'system',
                'info',
            ], True)
            if result.returncode != 0:
                raise ModuleNotFoundError()
        except FileNotFoundError:
            raise ModuleNotFoundError() from None

    # Internal execution
    def __exec(
        self,
        arguments: List[str],
        quiet: bool = False,
    ) -> 'CompletedProcess[bytes]':

        # Execute quiet command
        if quiet:
            return run(
                [self.__binary] + arguments,
                check=False,
                stdout=DEVNULL,
                stderr=DEVNULL,
            )

        # Execute standard command
        return run(
            [self.__binary] + arguments,
            check=False,
            stdout=PIPE,
            stderr=PIPE,
        )

    # Internal watcher
    def __watch(self, arguments: List[str]) -> Iterator[bytes]:

        # Watch command outputs, pylint: disable=consider-using-with
        stdout = Popen(
            [self.__binary] + arguments,
            stdout=PIPE,
        ).stdout
        if not stdout: # pragma: no cover
            return iter() # type: ignore[call-overload,no-any-return]
        return iter(stdout.readline, b'')

    # Command exec
    def cmd_exec(self) -> str:

        # Result
        if Platform.IS_USER_SUDO:
            return f'sudo {self.__binary} exec -it'
        return f'{self.__binary} exec -it'

    # Container
    @property
    def container(self) -> ContainerName:

        # Result
        assert self.__container is not None
        result = self.__exec([
            'inspect',
            '--type',
            'container',
            '--format',
            '{{.Name}}',
            self.__container,
        ])
        return result.stdout.strip().decode('utf-8') if result.returncode == 0 else ''

    # Exec
    def exec(self, commands: Commands) -> _ExecResult:

        # Execute command in container
        assert self.__container is not None
        result = self.__exec([
            'exec',
            self.__container,
        ] + commands)
        return _ExecResult(
            exit_code=result.returncode,
            output=result.stdout.strip().decode('utf-8'),
        )

    # Get
    def get(self, image: str) -> None:

        # Validate image exists
        result = self.__exec([
            'inspect',
            '--type',
            'image',
            '--format',
            'exists',
            image,
        ], True)

        # Pull missing image
        if result.returncode != 0:
            self.pull(image)

    # Logs
    def logs(self) -> _LogsResult:

        # Return logs stream
        assert self.__container is not None
        return self.__watch([
            'logs',
            '--follow',
            self.__container,
        ])

    # Pull
    def pull(
        self,
        image: str,
        force: bool = False,
    ) -> None:

        # Header
        print(f'Pulling from {image}')
        Platform.flush()

        # Force image removal
        if force:
            self.rmi(image)

        # Pull image with logs stream
        result = self.__exec([
            'pull',
            image,
        ])

        # Layer completion logs
        if result.returncode == 0:
            result = self.__exec([
                'inspect',
                '--type',
                'image',
                '--format',
                '{{.Id}}',
                image,
            ])
            print(f"Digest: {result.stdout.strip().decode('utf-8')}")
            print(f'Status: Image is up to date for {image}')
        else:
            print(f'Status: Image not found for {image}')
            Platform.flush()
            raise FileNotFoundError(result.stderr.decode('utf-8').replace('\\n', '\n'))

        # Footer
        print(' ')
        Platform.flush()

    # Remove
    def remove(self) -> None:

        # Remove container
        if self.__container:
            self.__exec([
                'rm',
                '--force',
                self.__container,
            ])
            self.__container = None

    # Remove image
    def rmi(self, image: str) -> None:

        # Remove image
        result = self.__exec([
            'inspect',
            '--type',
            'image',
            '--format',
            'exists',
            image,
        ], True)
        if result.returncode == 0:
            self.__exec([
                'rmi',
                image,
            ])

    # Run, pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
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

        # Variables
        args_commands: Commands = []
        args_entrypoint: List[str] = []
        args_env: List[str] = []
        args_run: List[str] = []
        args_volumes: List[str] = []

        # Adapt command
        if commands:
            args_commands += commands

        # Adapt entrypoint
        if isinstance(entrypoint, list):
            if len(entrypoint) > 1:
                args_commands = [' '.join(args_commands)]
                args_commands[0:0] = entrypoint[1:]
            entrypoint = entrypoint[0]
        if isinstance(entrypoint, str):
            args_entrypoint = ['--entrypoint', entrypoint]

        # Adapt mounts
        if volumes:
            for volume in volumes.get().values():
                args_volumes += ['--volume', f'{volume.stringify()}']

        # Adapt variables
        for variable in variables:
            args_env.extend(['--env', f'{variable}={variables[variable]}'])

        # Prepare arguments
        args_run += ['create']
        args_run += args_entrypoint
        args_run += args_env
        args_run += ['--tty']
        args_run += args_volumes
        if network:
            args_run += ['--network', network]
        if option_privileged:
            args_run += ['--privileged']
        args_run += ['--security-opt', 'label=disable']
        args_run += ['--workdir', directory]
        args_run += [image]
        args_run += args_commands

        # Create container image
        result = self.__exec(args_run)
        if result.returncode == 0:
            self.__container = result.stdout.strip().decode('utf-8')

        # Handle creation failures
        else:
            raise NotImplementedError(result.stderr.decode('utf-8').replace('\\n', '\n'))

        # Start container
        result = self.__exec([
            'start',
            self.__container,
        ])

        # Handle start failures
        if result.returncode != 0: # pragma: no cover
            raise RuntimeError(result.stderr.decode('utf-8').replace('\\n', '\n'))

    # Stop
    def stop(self, timeout: int) -> None:

        # Stop container
        assert self.__container is not None
        self.__exec([
            'stop',
            '--time',
            str(timeout),
            self.__container,
        ])

    # Supports
    def supports(self, binary: str) -> bool:

        # Validate binary support
        result = self.exec([
            'whereis',
            binary,
        ])

        # Result
        return result.exit_code == 0

    # Wait
    def wait(self) -> bool:

        # Wait container
        assert self.__container is not None
        result = self.__exec([
            'wait',
            self.__container,
        ])

        # Result
        try:
            return int(result.stdout.strip()) == 0 if result.returncode == 0 else False
        except ValueError:
            return False
