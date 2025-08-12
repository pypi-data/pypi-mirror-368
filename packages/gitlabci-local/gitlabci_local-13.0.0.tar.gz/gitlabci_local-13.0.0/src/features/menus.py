#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from typing import Any, Dict, List, Optional, Union

# Components
from ..models.flags import Flags
from ..models.pipelines import Pipeline
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..prints.themes import Themes
from ..system.platform import Platform
from ..types.lists import Lists
from .pipelines import PipelinesFeature

# MenusFeature class
class MenusFeature:

    # Members
    __pipeline: Optional[Pipeline]
    __options: Namespace

    # Constructor
    def __init__(
        self,
        pipeline: Optional[Pipeline],
        options: Namespace,
    ) -> None:

        # Prepare jobs
        self.__pipeline = pipeline

        # Prepare options
        self.__options = options

    # Configure, pylint: disable=too-many-branches,too-many-locals,too-many-statements
    @staticmethod
    def configure(configurations: Dict[str, Any]) -> Dict[str, str]:

        # Variables
        result = {}

        # Header
        print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}Configurations menu' \
                f' {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')
        Platform.flush()

        # Walk through configurations
        for variable in configurations:

            # Variables
            variable_choices: List[Dict[str, str]] = []
            variable_default: str = ''
            variable_index: int = 0
            variable_set: bool = False
            variable_values: List[str] = []

            # Extract configuration fields
            variable_node = configurations[variable]
            variable_help = variable_node['help']
            variable_type = variable_node['type']

            # Prepare configuration selection
            configuration_message: str = f'[{variable}] {variable_help}:'
            configuration_type = None

            # Extract configuration set
            if 'set' in variable_node and isinstance(variable_node['set'], bool):
                variable_set = variable_node['set']
                if 'default' in variable_node:
                    variable_default = variable_node['default']

            # Parse configuration types: boolean
            if variable_type == 'boolean':
                if 'default' in variable_node and variable_node['default'] in [
                        False, 'false'
                ]:
                    variable_values = ['false', 'true']
                else:
                    variable_values = ['true', 'false']
                if not variable_set:
                    variable_default = variable_values[0]
                for choice in variable_values:
                    variable_index += 1
                    variable_choices += [{
                        # 'key': str(variable_index),
                        'name': f'{choice}',
                        'value': choice
                    }]
                configuration_type = 'select'

            # Parse configuration types: choice
            elif variable_type == 'choice':
                variable_values = variable_node['values']
                if not variable_set:
                    variable_default = variable_values[0]
                for choice in variable_values:
                    variable_index += 1
                    variable_choices += [{
                        'key': str(variable_index),
                        'name': f'{choice}',
                        'value': choice
                    }]
                configuration_type = 'select'

            # Parse configuration types: input
            elif variable_type == 'input':
                configuration_type = 'text'
                if 'default' in variable_node and variable_node[
                        'default'] and not variable_set:
                    variable_default = variable_node['default']

            # Use configuration defaults
            if not Platform.IS_TTY_STDIN or variable_set:
                result[variable] = variable_default
                print(
                    f' {Colors.YELLOW}{configuration_message}' \
                        f' {Colors.CYAN}{result[variable]}{Colors.RESET}'
                )

            # Request configuration selection
            else:

                # Modules libraries
                from prompt_toolkit.styles.style import Style # pylint: disable=import-outside-toplevel
                from questionary import ( # pylint: disable=import-outside-toplevel
                    select as questionary_select, text as questionary_text,
                )

                # User interactive request
                if configuration_type == 'select':
                    answers = questionary_select(
                        message=configuration_message,
                        choices=variable_choices,
                        qmark='',
                        pointer=Themes.POINTER,
                        style=Style.from_dict(Themes.configuration_style()),
                        use_indicator=False,
                        use_shortcuts=False,
                        use_arrow_keys=True,
                        use_jk_keys=True,
                        show_selected=False,
                    ).ask()
                elif configuration_type == 'text':
                    answers = questionary_text(
                        message=configuration_message,
                        default=variable_default,
                        qmark='',
                        style=Style.from_dict(Themes.configuration_style()),
                        multiline=False,
                    ).ask()
                else: # pragma: no cover
                    answers = None
                if answers is None: # pragma: no cover
                    raise KeyboardInterrupt
                result[variable] = str(answers)

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return result

    # Select, pylint: disable=too-many-branches,too-many-statements
    def select(self) -> bool:

        # Modules libraries
        from prompt_toolkit.styles.style import Style # pylint: disable=import-outside-toplevel
        from questionary import ( # pylint: disable=import-outside-toplevel
            checkbox as questionary_checkbox, select as questionary_select, Choice as
            questionary_Choice, Separator as questionary_Separator,
        )

        # Variables
        default_check: bool = self.__options.all
        jobs_available: bool = False
        jobs_choices: List[Union[questionary_Choice, questionary_Separator]] = []
        result: bool = True
        stage: str = ''

        # Stages groups
        assert self.__pipeline is not None
        for job in self.__pipeline.jobs:

            # Filter names
            if self.__options.names:

                # Filter jobs list, pylint: disable=duplicate-code
                if not self.__options.pipeline and not Lists.match(
                        self.__options.names,
                        job,
                        ignore_case=self.__options.ignore_case,
                        no_regex=self.__options.no_regex,
                ):
                    continue

                # Filter stages list
                if self.__options.pipeline and not Lists.match(
                        self.__options.names,
                        self.__pipeline.jobs[job].stage,
                        ignore_case=self.__options.ignore_case,
                        no_regex=self.__options.no_regex,
                ):
                    continue

            # Stages separator
            if stage != self.__pipeline.jobs[job].stage:
                stage = self.__pipeline.jobs[job].stage
                jobs_choices += [questionary_Separator(f'\n Stage {stage}:')]

            # Initial job details
            job_details_list: List[str] = []
            job_details_string: str = ''
            tags: str = ''

            # Disabled jobs
            disabled: Optional[str] = None
            if self.__pipeline.jobs[job].when in ['manual'] and not Flags.check_bool(
                    option=self.__options.manual,
                    flag=Bundle.FLAG_MANUAL,
                    variables=self.__pipeline.jobs[job].variables,
                    default=False,
            ):
                disabled = 'Manual'
            elif self.__pipeline.jobs[job].script:
                if self.__pipeline.jobs[job].when == 'manual':
                    job_details_list += ['Manual']
                elif self.__pipeline.jobs[job].when == 'on_failure':
                    job_details_list += ['On failure']
                jobs_available = True

            # Parser disabled jobs
            if self.__pipeline.jobs[job].options.disabled:
                disabled = self.__pipeline.jobs[job].options.disabled

            # Failure allowed jobs
            if self.__pipeline.jobs[job].allow_failure:
                job_details_list += ['Failure allowed']

            # Register job tags
            job_tags: Optional[List[str]] = self.__pipeline.jobs[job].tags
            if job_tags:
                tags = f" [{','.join(job_tags)}]"

            # Prepare job details
            if job_details_list:
                job_details_string = f" ({', '.join(job_details_list)})"

            # Job choices
            jobs_choices += [
                questionary_Choice(
                    title=f'{self.__pipeline.jobs[job].name}{tags}{job_details_string}',
                    value=job,
                    disabled=disabled,
                    checked=default_check,
                    shortcut_key=True,
                )
            ]

        # Request jobs selection
        if jobs_choices and jobs_available:
            try:
                if self.__options.list:
                    answers = questionary_select(
                        message='===[ Jobs selector ]===',
                        choices=jobs_choices,
                        qmark='',
                        pointer=Themes.POINTER,
                        style=Style.from_dict(Themes.configuration_style()),
                        use_indicator=False,
                        use_shortcuts=False,
                        use_arrow_keys=True,
                        use_jk_keys=True,
                        show_selected=False,
                    ).ask()
                else:
                    answers = questionary_checkbox(
                        message='===[ Jobs selector ]===',
                        choices=jobs_choices,
                        qmark='',
                        pointer=Themes.POINTER,
                        style=Style.from_dict(Themes.checkbox_style()),
                        use_arrow_keys=True,
                        use_jk_keys=True,
                    ).ask()
            except KeyboardInterrupt: # pragma: no cover
                answers = None

        # No jobs found
        else:
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}No jobs found for selection{Colors.RESET}'
            )
            answers = None

        # Parse jobs selection
        if answers:
            if self.__options.list:
                self.__options.names = [answers]
            else:
                self.__options.names = answers
        else:
            self.__options.names = []

        # Drop pipeline mode for jobs
        self.__options.pipeline = False

        # Footer
        print(' ')
        print(' ')
        Platform.flush()

        # Launch jobs
        if self.__options.names:
            result = PipelinesFeature(
                self.__pipeline,
                self.__options,
            ).launch()

        # Result
        return result
