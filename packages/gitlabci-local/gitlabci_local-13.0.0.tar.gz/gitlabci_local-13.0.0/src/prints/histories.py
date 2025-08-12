#!/usr/bin/env python3

# Standard libraries
from os import environ
from time import time
from typing import List, Optional

# Components
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..system.notify import Notify
from ..system.platform import Platform

# TimedHistory class, pylint: disable=too-few-public-methods
class TimedHistory:

    # Members
    __duration: str
    __start_time: float

    # Constructor
    def __init__(self) -> None:

        # Initialize members
        self.__duration = '0 second'
        self.__start_time = time()

    # Refresh times
    def _refresh_times(self) -> None:

        # Acquire fake duration
        if environ.get(Bundle.ENV_HISTORIES_DURATION_FAKE, ''):
            duration = int(environ[Bundle.ENV_HISTORIES_DURATION_FAKE])

        # Evaluate duration
        else:
            duration = int(time() - self.__start_time)

        # Evaluate seconds
        seconds = f"{duration % 60:.0f} second{'s' if duration % 60 > 1 else ''}"

        # Evaluate minutes
        minutes = ''
        if duration >= 60:
            minutes = f"{duration / 60:.0f} minute{'s' if duration / 60 > 1 else ''} "

        # Store total time
        self.__duration = minutes + seconds

    @property
    def duration(self) -> str:
        return self.__duration

# JobHistory class
class JobHistory(TimedHistory):

    # Constants
    __SYMBOL_FAILED = '✘' if Platform.IS_TTY_UTF8 else 'x'
    __SYMBOL_FOOTER = '‣' if Platform.IS_TTY_UTF8 else '>'
    __SYMBOL_SKIPPED = '»' if Platform.IS_TTY_UTF8 else '~'
    __SYMBOL_SUCCESS = '✔' if Platform.IS_TTY_UTF8 else 'v'
    __SYMBOL_WARNING = '!'

    # Members
    __details: str = ''
    __failure_allowed: bool
    __interrupted: bool
    __name: str
    __result: Optional[bool]
    __stage: str

    # Constructor
    def __init__(self, name: str, stage: str) -> None:

        # Initialize members
        super().__init__()
        self.__details = ''
        self.__failure_allowed = False
        self.__interrupted = False
        self.__name = name
        self.__result = None
        self.__stage = stage

    @property
    def failure_allowed(self) -> bool:
        return self.__failure_allowed

    @failure_allowed.setter
    def failure_allowed(self, value: bool) -> None:
        self.__failure_allowed = value

    @property
    def details(self) -> str:
        return self.__details

    @details.setter
    def details(self, value: str) -> None:
        self.__details = value

    @property
    def interrupted(self) -> Optional[bool]:
        return self.__interrupted

    @interrupted.setter
    def interrupted(self, value: bool) -> None:
        self.__interrupted = value

    @property
    def name(self) -> str:
        return self.__name

    @property
    def result(self) -> Optional[bool]:
        return self.__result

    @result.setter
    def result(self, value: bool) -> None:
        self.__result = value
        self._refresh_times()

    # Header
    def header(
        self,
        jobs_count: int,
        image: str,
        engine_type: str,
    ) -> None:

        # Header output
        if jobs_count > 1:
            print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}{self.__stage}:' \
                f' {Colors.YELLOW}{self.__name} {Colors.CYAN}' \
                    f'({image}, {engine_type}) {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Footer
    def footer(self) -> None:

        # Result
        result: str
        if self.interrupted:
            result = 'Interrupted after'
        elif self.result:
            result = 'Success in'
        else:
            result = 'Failure in'

        # Footer output
        print(
            f'  {Colors.YELLOW}{self.__SYMBOL_FOOTER} {self.__name}:' \
                f' {Colors.GREEN if self.result else Colors.RED}' \
                f'{result} {self.duration}{Colors.CYAN}{self.details}{Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Print
    def print(self) -> None:

        # Variables
        icon = ''
        summary = ''

        # Prepare job result
        if self.result:
            icon = f'{Colors.GREEN}{self.__SYMBOL_SUCCESS}'
            summary = f'{Colors.GREEN}Success in {self.duration}'
        elif self.failure_allowed:
            icon = f'{Colors.YELLOW}{self.__SYMBOL_WARNING}'
            summary = f'{Colors.YELLOW}Failure in {self.duration}'
        elif self.result is None:
            icon = f'{Colors.GREY}{self.__SYMBOL_SKIPPED}'
            summary = f'{Colors.GREY}Skipped'
        else:
            icon = f'{Colors.RED}{self.__SYMBOL_FAILED}'
            summary = f'{Colors.RED}Failure in {self.duration}'

        # Prepare interrupted result
        if self.interrupted:
            summary += f' {Colors.YELLOW}(Interrupted)'

        # Print result
        print(
            f'    {icon} {Colors.BOLD}{self.name}:' \
                f' {summary}{Colors.CYAN}{self.details}{Colors.RESET}'
        )

# StageHistory class
class StageHistory:

    # Constants
    __SYMBOL_STAGE = '•' if Platform.IS_TTY_UTF8 else '-'

    # Members
    __jobs: List[JobHistory] = []
    __name: str

    # Constructor
    def __init__(self, name: str) -> None:

        # Initialize members
        self.__jobs = []
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    # Add
    def add(self, job_name: str) -> JobHistory:

        # Add job
        job = JobHistory(job_name, self.name)
        self.__jobs += [job]

        # Result
        return job

    # Print
    def print(self) -> None:

        # Stage header
        print(f'  {Colors.YELLOW}{self.__SYMBOL_STAGE} Stage {self.name}:{Colors.RESET}')

        # Iterate through jobs
        for job in self.__jobs:
            job.print()

# PipelineHistory class
class PipelineHistory(TimedHistory):

    # Constants
    __SYMBOL_PIPELINE = '‣' if Platform.IS_TTY_UTF8 else '>'

    # Members
    __interacted: bool
    __jobs_count: int
    __jobs_quiet: bool
    __pipeline: List[StageHistory]
    __result: Optional[bool]

    # Constructor
    def __init__(self) -> None:

        # Initialize members
        super().__init__()
        self.__interacted = False
        self.__jobs_count = 0
        self.__jobs_quiet = True
        self.__pipeline = []
        self.__result = None

    @property
    def interacted(self) -> bool:
        return self.__interacted

    @interacted.setter
    def interacted(self, value: bool) -> None:
        self.__interacted = value

    @property
    def jobs_count(self) -> int:
        return self.__jobs_count

    @property
    def jobs_quiet(self) -> bool:
        return self.__jobs_quiet

    @jobs_quiet.setter
    def jobs_quiet(self, value: bool) -> None:
        self.__jobs_quiet = value

    @property
    def result(self) -> Optional[bool]:
        return self.__result

    @result.setter
    def result(self, value: bool) -> None:
        self.__result = value
        self._refresh_times()

    # Add
    def add(
        self,
        stage_name: str,
        job_name: str,
    ) -> JobHistory:

        # Increment jobs count
        self.__jobs_count += 1

        # Find stage
        stage = self.get(stage_name)

        # Prepare stage
        if not stage:
            stage = StageHistory(stage_name)
            self.__pipeline += [stage]

        # Add job
        job = stage.add(job_name)

        # Result
        return job

    # Get
    def get(self, stage_name: str) -> Optional[StageHistory]:

        # Find stage
        for stage in self.__pipeline:
            if stage.name == stage_name:
                return stage

        # Fallback
        return None

    # Print
    def print(self) -> None:

        # Header
        print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}Pipeline:' \
                f' {Colors.BOLD}{self.jobs_count} jobs {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')

        # Iterate through stages
        for stage in self.__pipeline:
            stage.print()
            print(' ')

        # Footer
        print(
            f'  {Colors.YELLOW}{self.__SYMBOL_PIPELINE} Pipeline:' \
                f' {Colors.BOLD if self.result else Colors.RED}' \
                    f"{'Success' if self.result else 'Failure'}" \
                        f' in {self.duration} total{Colors.RESET}'
        )
        print(' ')

    # Notify
    def notify(self) -> None:

        # Notify pipeline result
        Notify().notify('Pipeline: ' \
            f"{'Success' if self.result else 'Failure'}" \
                f' in {self.duration} total')
