#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from os import environ
from pathlib import Path
from subprocess import check_output, DEVNULL, Popen
from sys import argv
from typing import Optional

# Components
from ..engines.engine import supported as engine_supported
from ..features.configurations import ConfigurationsFeature
from ..features.images import ImagesFeature
from ..features.menus import MenusFeature
from ..features.pipelines import PipelinesFeature
from ..models.pipelines import Pipeline
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..parsers.parsers import Parsers
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.files import Files

# Entrypoint class, pylint: disable=too-few-public-methods,too-many-statements
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # CLI, pylint: disable=too-many-branches,too-many-locals,too-many-return-statements
    @staticmethod
    def cli(
        options: Namespace,
        settings: Settings,
    ) -> Result:

        # Variables
        hint: str = ''
        interactive: bool = Platform.IS_TTY_STDIN and Platform.IS_TTY_STDOUT
        result: bool = False

        # Prepare configuration
        if Path(options.configuration).is_dir():
            options.configuration = Path(options.configuration) / Bundle.CONFIGURATION

        # Prepare engine
        if options.engine is None and environ.get(Bundle.FLAG_ENGINE, ''):
            options.engine = environ[Bundle.FLAG_ENGINE]
            options.engine_default = True
        elif options.engine is not None:
            environ[Bundle.FLAG_ENGINE] = options.engine
            options.engine_default = False
        elif settings.has(group='engines', key='engine'):
            options.engine = settings.get(group='engines', key='engine')
            options.engine_default = True
        else:
            options.engine = ','.join(engine_supported())
            options.engine_default = True
            settings.set(group='engines', key='engine', value=options.engine)

        # Prepare no_console
        if not options.no_console:
            if settings.has('runner', 'no_console'):
                options.no_console = settings.get_bool('runner', 'no_console')
            else:
                options.no_console = False
                settings.set_bool('runner', 'no_console', options.no_console)

        # Prepare no_git_safeties
        if not options.no_git_safeties:
            if settings.has('runner', 'no_git_safeties'):
                options.no_git_safeties = settings.get_bool('runner', 'no_git_safeties')
            else:
                options.no_git_safeties = False
                settings.set_bool('runner', 'no_git_safeties', options.no_git_safeties)

        # Prepare no_script_fail
        if not options.no_script_fail:
            if settings.has('parsers', 'no_script_fail'):
                options.no_script_fail = settings.get_bool('parsers', 'no_script_fail')
            else:
                options.no_script_fail = False
                settings.set_bool('parsers', 'no_script_fail', options.no_script_fail)

        # Prepare paths
        options.configuration = Path(options.configuration).resolve()
        options.path = options.configuration.parent

        # Prepare tags
        if options.tags:
            options.tags = options.tags.split(',')
        else:
            options.tags = Bundle.ARGUMENT_TAGS_DEFAULT
            options.tags_default = True

        # Read configuration
        pipeline: Optional[Pipeline] = Parsers(options).read()
        if not pipeline:
            return Entrypoint.Result.CRITICAL

        # Header
        print(' ')
        Platform.flush()

        # Dump configuration
        if options.dump:
            result = ConfigurationsFeature(
                pipeline=pipeline,
                options=options,
            ).dump()

        # Pull jobs images
        elif options.pull:
            result = ImagesFeature(
                pipeline=pipeline,
                options=options,
            ).pull()

        # Remove jobs images
        elif options.rmi:
            result = ImagesFeature(
                pipeline=pipeline,
                options=options,
            ).rmi()

        # Select job
        elif options.list and interactive:
            options.manual = True
            options.no_regex = True
            result = MenusFeature(
                pipeline=pipeline,
                options=options,
            ).select()

        # Select jobs
        elif options.select and interactive:
            options.no_regex = True
            result = MenusFeature(
                pipeline=pipeline,
                options=options,
            ).select()

        # Launch pipeline or jobs
        elif options.pipeline or options.names:
            result = PipelinesFeature(
                pipeline=pipeline,
                options=options,
            ).launch()

        # Select jobs
        elif interactive:
            options.no_regex = True
            result = MenusFeature(
                pipeline=pipeline,
                options=options,
            ).select()

        # Launch all jobs
        elif options.all:
            options.pipeline = True
            result = PipelinesFeature(
                pipeline=pipeline,
                options=options,
            ).launch()

        # Unsupported case
        else:

            # Windows WinPTY compatibility
            if Platform.IS_WINDOWS and Bundle.ENV_WINPTY not in environ: # pragma: windows cover

                # Prepare WinPTY variables
                hint = ' (on Windows, winpty is required)'
                winpty: Optional[str] = None
                if environ.get(Bundle.ENV_WINPTY_PATH, ''):
                    winpty = environ[Bundle.ENV_WINPTY_PATH]

                # Acquire WinPTY path
                try:
                    if not winpty:
                        winpty = str(
                            check_output(
                                args=['where', 'winpty.exe'],
                                stderr=DEVNULL,
                            ).strip())
                except FileNotFoundError: # pragma: no cover
                    pass
                else:

                    # Nested WinPTY launch
                    _environ = environ.copy()
                    _environ[Bundle.ENV_WINPTY] = 'true'
                    try:
                        with Popen(
                                args=[winpty] + argv if winpty else argv,
                                env=_environ,
                        ) as process:
                            process.wait()
                            return Entrypoint.Result.CRITICAL
                    except OSError: # pragma: no cover
                        pass

            # Unsupported interactive terminal
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR: ' \
                    f'{Colors.BOLD}Unsupported non-interactive context{hint}...{Colors.RESET}'
            )
            print(' ')
            Platform.flush()

        # Cleanup at exit
        Files.clean()

        # Result
        return Entrypoint.Result.SUCCESS if result else Entrypoint.Result.ERROR
