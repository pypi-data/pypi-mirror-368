#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from typing import List

# Components
from ..engines.engine import Engine
from ..models.pipelines import Pipeline
from ..types.lists import Lists

# ImagesFeature class
class ImagesFeature:

    # Members
    __engine: Engine
    __images: List[str]
    __options: Namespace

    # Constructor
    def __init__(
        self,
        pipeline: Pipeline,
        options: Namespace,
    ) -> None:

        # Prepare pipeline
        self.__pipeline = pipeline

        # Prepare options
        self.__options = options

        # Prepare engine
        self.__engine = Engine(self.__options.engine)

        # Prepare images
        self.__images = []
        self.__prepare_images()

    # Filter
    def __filter(
        self,
        job: str,
    ) -> bool:

        # Filter pipeline jobs list, pylint: disable=duplicate-code
        if not self.__options.pipeline and self.__options.names and not Lists.match(
                self.__options.names,
                job,
                ignore_case=self.__options.ignore_case,
                no_regex=self.__options.no_regex,
        ):
            return False

        # Filter pipeline stages list
        if self.__options.pipeline and self.__options.names and not Lists.match(
                self.__options.names,
                self.__pipeline.jobs[job].stage,
                ignore_case=self.__options.ignore_case,
                no_regex=self.__options.no_regex,
        ):
            return False

        # Result
        return True

    # Prepare images
    def __prepare_images(self) -> None:

        # Iterate through images
        for job in self.__pipeline.jobs:

            # Filter jobs
            if not self.__filter(job):
                continue

            # Extract job image
            image = self.__pipeline.jobs[job].image
            if image and not self.__pipeline.jobs[
                    job].options.host and image not in self.__images:
                self.__images += [image]

            # Extract job services
            for service in self.__pipeline.jobs[job].services:
                if service.image not in self.__images:
                    self.__images += [service.image]

        # Sort images
        self.__images.sort()

    # Pull
    def pull(self) -> bool:

        # Pull images
        for image in self.__images:
            self.__engine.pull(
                image,
                self.__options.force,
            )

        # Result
        return bool(self.__images)

    # Remove images
    def rmi(self) -> bool:

        # Remove images
        for image in self.__images:
            self.__engine.rmi(image)

        # Result
        return bool(self.__images)
