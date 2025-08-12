#!/usr/bin/env python3

# Standard libraries
from os import environ
from typing import Any, cast, Dict, Optional, TYPE_CHECKING

# Modules libraries
if TYPE_CHECKING: # pragma: no cover, pylint: disable=wrong-import-position
    from docker import DockerClient
    from docker.models.containers import Container
else:
    DockerClient = Any
    Container = Any

# Components
from ..jobs.outputs import Outputs
from ..models.images import Entrypoint
from ..system.platform import Platform
from ..types.volumes import Volumes
from .base import _ExecResult, _LogsResult, BaseEngine, Commands, ContainerName

# Docker engine class
class DockerEngine(BaseEngine): # pragma: docker cover

    # Constants
    ENV_DOCKER_CERT_PATH: str = 'DOCKER_CERT_PATH'
    ENV_DOCKER_HOST: str = 'DOCKER_HOST'
    ENV_DOCKER_TLS_VERIFY: str = 'DOCKER_TLS_VERIFY'

    # Members
    __client: DockerClient
    __container: Optional[Container]

    # Constructor
    def __init__(self) -> None:

        # Modules libraries, pylint: disable=import-outside-toplevel
        from docker import from_env
        from docker.errors import DockerException

        # Prepare container
        self.__container = None

        # Engine client
        try:
            self.__client = from_env()
            self.__client.ping()
        except DockerException:
            raise ModuleNotFoundError() from None

    # Sockets, pylint: disable=no-self-use
    def __sockets(
        self,
        variables: Dict[str, str],
        volumes: Volumes,
    ) -> None:

        # Variables
        docker_host = ''

        # Detect TLS configurations
        if DockerEngine.ENV_DOCKER_TLS_VERIFY in environ:
            variables[DockerEngine.ENV_DOCKER_TLS_VERIFY] = environ[
                DockerEngine.ENV_DOCKER_TLS_VERIFY]

        # Detect certificates configurations
        if environ.get(DockerEngine.ENV_DOCKER_CERT_PATH, ''): # pragma: no local cover
            variables[DockerEngine.ENV_DOCKER_CERT_PATH] = '/certs'
            volumes.add(
                environ[DockerEngine.ENV_DOCKER_CERT_PATH],
                '/certs',
                'ro',
                True,
            )

        # Detect host configurations
        if environ.get(DockerEngine.ENV_DOCKER_HOST, ''):
            docker_host = environ[DockerEngine.ENV_DOCKER_HOST]

        # Network Docker socket
        if docker_host[0:7] == 'http://' or docker_host[0:6] == 'tcp://':
            variables[DockerEngine.ENV_DOCKER_HOST] = docker_host # pragma: no local cover

        # Local Docker socket
        elif docker_host[0:7] == 'unix://': # pragma: no cover
            volumes.add(
                docker_host[7:],
                docker_host[7:],
                'rw',
                True,
            )

        # Default Docker socket
        elif not docker_host: # pragma: no cover

            # Add socket volume
            if Platform.IS_LINUX or Platform.IS_WINDOWS or Platform.IS_EXPERIMENTAL:
                volumes.add(
                    '/var/run/docker.sock',
                    '/var/run/docker.sock',
                    'rw',
                    True,
                )

            # Unavailable feature
            else:
                Outputs.warning('The Docker sockets feature is not available...')

        # Unknown feature
        else: # pragma: no cover
            Outputs.warning(
                f'The {DockerEngine.ENV_DOCKER_HOST} = {docker_host}' \
                    ' configuration is not supported yet...'
            )

    # Command exec, pylint: disable=no-self-use
    def cmd_exec(self) -> str:

        # Result
        return 'docker exec -it'

    # Container
    @property
    def container(self) -> ContainerName:

        # Result
        assert self.__container is not None
        return cast(str, self.__container.name)

    # Exec
    def exec(self, commands: Commands) -> _ExecResult:

        # Execute command in container
        assert self.__container is not None
        result = self.__container.exec_run(' '.join(commands))
        return _ExecResult(
            exit_code=result.exit_code,
            output=result.output.strip().decode('utf-8'),
        )

    # Get
    def get(self, image: str) -> None:

        # Modules libraries, pylint: disable=import-outside-toplevel
        from docker.errors import ImageNotFound

        # Validate image exists
        try:
            self.__client.images.get(image)

        # Pull missing image
        except ImageNotFound:
            self.pull(image)

    # Logs
    def logs(self) -> _LogsResult:

        # Return logs stream
        assert self.__container is not None
        return self.__container.logs(stream=True) # type: ignore[no-any-return]

    # Pull
    def pull(
        self,
        image: str,
        force: bool = False,
    ) -> None:

        # Force image removal
        if force:
            self.rmi(image)

        # Pull image with logs stream
        for data in self.__client.api.pull(image, stream=True, decode=True):

            # Layer progress logs
            if 'progress' in data:
                if Platform.IS_TTY_STDOUT:
                    print(f"\r\x1b[K{data['id']}: {data['status']} {data['progress']}",
                          end='')
                    Platform.flush()

            # Layer event logs
            elif 'progressDetail' in data:
                if Platform.IS_TTY_STDOUT:
                    print(f"\r\x1b[K{data['id']}: {data['status']}", end='')
                    Platform.flush()

            # Layer completion logs
            elif 'id' in data:
                print(f"\r\x1b[K{data['id']}: {data['status']}")
                Platform.flush()

            # Layer error logs
            elif 'error' in data: # pragma: no cover
                print(f"\r\x1b[K{data['error']}")
                Platform.flush()

            # Layer status logs
            elif 'status' in data:
                print(f"\r\x1b[K{data['status']}")
                Platform.flush()

            # Unsupported data logs
            else: # pragma: no cover
                print(f"\r\x1b[K{data}")
                Platform.flush()

        # Footer
        print(' ')
        Platform.flush()

    # Remove
    def remove(self) -> None:

        # Remove container
        if self.__container:
            self.__container.remove(force=True)
            self.__container = None

    # Remove image
    def rmi(self, image: str) -> None:

        # Modules libraries, pylint: disable=import-outside-toplevel
        from docker.errors import ImageNotFound

        # Remove image
        try:
            self.__client.api.remove_image(image)
        except ImageNotFound:
            pass

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

        # Append sockets mounts
        if option_sockets:
            self.__sockets(variables, volumes)

        # Run container image
        self.__container = self.__client.containers.run(
            image=image,
            command=commands,
            detach=True,
            entrypoint=entrypoint,
            environment=variables,
            network_mode=network if network else 'bridge',
            privileged=option_privileged,
            remove=False,
            stdout=True,
            stderr=True,
            stream=True,
            volumes=volumes.flatten(),
            working_dir=directory,
        )

    # Stop
    def stop(self, timeout: int) -> None:

        # Stop container
        assert self.__container is not None
        self.__container.stop(timeout=timeout)

    # Supports
    def supports(self, binary: str) -> bool:

        # Modules libraries, pylint: disable=import-outside-toplevel
        from docker.errors import APIError

        # Variables
        exit_code: int = 1

        # Validate binary support
        try:
            exit_code = self.exec([
                'whereis',
                f'{binary}',
            ]).exit_code
        except APIError: # pragma: no cover
            pass

        # Result
        return exit_code == 0

    # Wait
    def wait(self) -> bool:

        # Wait container
        assert self.__container is not None
        result = self.__container.wait()

        # Result
        return cast(int, result['StatusCode']) == 0
