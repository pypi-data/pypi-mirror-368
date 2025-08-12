#!/usr/bin/env python3

# Standard libraries
from typing import List, Optional, Union

# Entrypoint type
Entrypoint = Optional[Union[List[str], str]]

# Image type
Image = str

# Images class
class Images:

    # Constants
    DOCKER_DIND_REGEX: str = r'.*docker:.*dind'
    LOCAL_IMAGE: str = 'local'
    LOCAL_QUIET_IMAGE: str = 'local:quiet'
    LOCAL_SILENT_IMAGE: str = 'local:silent'

    # Host
    @staticmethod
    def host(image: str) -> bool:
        return image in [
            Images.LOCAL_IMAGE,
            Images.LOCAL_QUIET_IMAGE,
            Images.LOCAL_SILENT_IMAGE,
        ]

    # Quiet
    @staticmethod
    def quiet(image: str) -> bool:
        return image in [
            Images.LOCAL_QUIET_IMAGE,
            Images.LOCAL_SILENT_IMAGE,
        ]

    # Silent
    @staticmethod
    def silent(image: str) -> bool:
        return image in [
            Images.LOCAL_SILENT_IMAGE,
        ]
