#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace

# Components
from ..jobs.runner import Runner
from ..models.flags import Flags
from ..models.pipelines import Pipeline
from ..package.bundle import Bundle
from ..prints.histories import PipelineHistory
from ..system.platform import Platform
from ..types.lists import Lists

# PipelinesFeature class, pylint: disable=too-few-public-methods
class PipelinesFeature:

    # Members
    __pipeline: Pipeline
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

    # Filter
    def __filter(
        self,
        job: str,
    ) -> bool:

        # Filter pipeline jobs list, pylint: disable=duplicate-code
        if not self.__options.pipeline and not Lists.match(
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

        # Filter manual pipeline jobs
        job_manual = self.__pipeline.jobs[job].when == 'manual'
        if job_manual and not Flags.check_bool(
                option=self.__options.manual,
                flag=Bundle.FLAG_MANUAL,
                variables=self.__pipeline.jobs[job].variables,
                default=False,
        ) and not Lists.match(
                self.__options.names,
                job,
                ignore_case=self.__options.ignore_case,
                no_regex=self.__options.no_regex,
        ):
            return False

        # Filter disabled pipeline jobs
        if self.__pipeline.jobs[job].options.disabled:
            return False

        # Result
        return True

    # Launch
    def launch(self) -> bool:

        # Variables
        notify: bool = False
        pipeline_history = PipelineHistory()
        result = None

        # Prepare interacted flag
        pipeline_history.interacted = False

        # Run selected pipeline jobs
        for job in self.__pipeline.jobs:

            # Filter pipeline jobs
            if not self.__filter(job):
                continue

            # Raise initial result
            if result is None:
                result = True

            # Raise interacted flag
            if Flags.check_bool(
                    option=self.__options.bash,
                    flag=Bundle.FLAG_BASH,
                    variables=self.__pipeline.jobs[job].variables,
                    default=False,
            ) or Flags.check_bool(
                    option=self.__options.debug,
                    flag=Bundle.FLAG_DEBUG,
                    variables=self.__pipeline.jobs[job].variables,
                    default=False,
            ):
                pipeline_history.interacted = True

            # Raise notify flag
            if not notify and Flags.check_bool(
                    option=self.__options.notify,
                    flag=Bundle.FLAG_NOTIFY,
                    variables=self.__pipeline.jobs[job].variables,
                    default=False,
            ):
                notify = True

            # Run job
            expected = result
            result = Runner(options=self.__options).run(
                self.__pipeline.jobs[job],
                result,
                pipeline_history,
            )

            # Retry job if allowed
            attempt: int = 0
            if expected and not result and self.__pipeline.jobs[job].retry > 0:
                while not result and attempt < self.__pipeline.jobs[job].retry:
                    attempt += 1
                    result = Runner(options=self.__options).run(
                        self.__pipeline.jobs[job],
                        expected,
                        pipeline_history,
                    )

        # Update pipeline history
        pipeline_history.result = bool(result)

        # Non quiet jobs
        if not pipeline_history.jobs_quiet and not self.__options.scripts:

            # Pipeline jobs footer
            if pipeline_history.jobs_count > 1:

                # Output pipeline history
                pipeline_history.print()

            # Notify pipeline history
            if not pipeline_history.interacted and notify:
                pipeline_history.notify()

            # Footer
            print(' ')
            Platform.flush()

        # Result
        return bool(result)
