#!/usr/bin/env python3

# Standard libraries
from typing import Dict, List, NamedTuple

# Components
from ..system.platform import Platform
from ..types.paths import Paths

# Volume type
class Volume(NamedTuple):

    # Properties
    bind: str
    mode: str
    source: str

    # Stringify
    def stringify(self) -> str: # pragma: podman cover

        # Variables
        options = ''

        # Extract options
        if self.mode == 'ro':
            options += ':ro'
        elif self.mode == 'rw':
            options += ':rw'

        # Result
        return f'{self.source}:{self.bind}{options}'

# Volumes class
class Volumes:

    # Constants
    LOCAL_FLAG: str = '.local:'

    # Members
    __volumes: Dict[str, Volume]

    # Constructor
    def __init__(self) -> None:

        # Initialize members
        self.__volumes = {}

    # Add
    def add(
        self,
        source: str,
        target: str,
        mode: str,
        override: bool,
    ) -> None:

        # Handle overrides
        if target in [volume.bind for _, volume in self.__volumes.items()]:
            if not override:
                return

            # Detect duplicated volumes
            duplicates = [
                key for key, volume in self.__volumes.items()
                if volume.source == source and volume.bind == target
            ]
            if duplicates:
                self.__volumes.pop(duplicates[0])

        # Adapt source to allow duplicates
        while source in self.__volumes:
            if Platform.IS_WINDOWS: # pragma: no cover
                source = f'{source}{Platform.PATH_SEPARATOR}.'
            else:
                source = f'{Platform.PATH_SEPARATOR}.{source}'

        # Add volume binding
        self.__volumes[source] = Volume(
            bind=target,
            mode=mode,
            source=source,
        )

    # Get
    def get(self) -> Dict[str, Volume]: # pragma: podman cover

        # Result
        return self.__volumes

    # Flatten
    def flatten(self) -> Dict[str, Dict[str, str]]: # pragma: docker cover

        # Variables
        volumes: Dict[str, Dict[str, str]] = {}

        # Flatten volumes
        for source, volume in self.__volumes.items():
            volumes[source] = dict(volume._asdict().items())

        # Result
        return volumes

    # Parse
    @staticmethod
    def parse(volume: str) -> List[str]:

        # Invalid volume
        if not volume:
            raise ValueError('Empty volume parameter cannot be parsed')

        # Relative volume
        if 1 <= len(volume) <= 2:
            return [volume]

        # Variables
        volume_node: str = ''
        volume_nodes: List[str] = []

        # Iterate through volume
        for char in f'{volume}\x00':

            # Detect Windows drive
            if char == ':' and len(volume_node) == 1 and volume_node[0].isalpha():
                volume_node += char # pragma: no cover

            # Detect separator or end
            elif char in (':', ';', '\0'):
                volume_nodes += [Paths.translate(volume_node)]
                volume_node = ''

            # Append to volume node
            else:
                volume_node += char

        # Result
        return volume_nodes
