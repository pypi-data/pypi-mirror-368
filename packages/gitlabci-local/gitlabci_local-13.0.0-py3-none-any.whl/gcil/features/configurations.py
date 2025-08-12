#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from copy import deepcopy
from typing import Any, Dict

# Components
from ..models.pipelines import Pipeline
from ..system.platform import Platform
from ..types.lists import Lists
from ..types.yaml import YAML

# ConfigurationsFeature class, pylint: disable=too-few-public-methods
class ConfigurationsFeature:

    # Members
    __configuration: Dict[str, Any]

    # Constructor
    def __init__(
        self,
        pipeline: Pipeline,
        options: Namespace,
    ) -> None:

        # Prepare configuration
        self.__configuration = {}
        if options.pipeline and options.names:
            for job in pipeline.jobs:
                if Lists.match(
                        options.names,
                        pipeline.jobs[job].stage,
                        ignore_case=options.ignore_case,
                        no_regex=options.no_regex,
                ):
                    self.__configuration[job] = deepcopy(pipeline.jobs[job].__dict__)
                    self.__cleanup(job)
        elif options.names:
            for job in pipeline.jobs:
                if Lists.match(
                        options.names,
                        job,
                        ignore_case=options.ignore_case,
                        no_regex=options.no_regex,
                ):
                    self.__configuration[job] = deepcopy(pipeline.jobs[job].__dict__)
                    self.__cleanup(job)
        else:
            for job in pipeline.jobs:
                self.__configuration[job] = deepcopy(pipeline.jobs[job].__dict__)
                self.__cleanup(job)

    # Cleanup
    def __cleanup(
        self,
        job: str,
    ) -> None:

        # Cleanup job configurations
        if job in self.__configuration:
            if self.__configuration[job]['entrypoint'] is None:
                del self.__configuration[job]['entrypoint']
            if self.__configuration[job]['retry'] == 0:
                del self.__configuration[job]['retry']
            if not self.__configuration[job]['services']:
                del self.__configuration[job]['services']
            if self.__configuration[job]['tags'] is None:
                del self.__configuration[job]['tags']
            if self.__configuration[job]['trigger'] is None:
                del self.__configuration[job]['trigger']
            if not self.__configuration[job]['variables']:
                del self.__configuration[job]['variables']
            del self.__configuration[job]['options']

    # Dump
    def dump(self) -> bool:

        # Dump configuration results
        print(YAML.dump(self.__configuration))
        print(' ')
        Platform.flush()

        # Result
        return bool(self.__configuration)
