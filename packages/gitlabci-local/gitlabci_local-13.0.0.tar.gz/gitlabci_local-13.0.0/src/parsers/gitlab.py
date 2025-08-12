#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from collections import OrderedDict
from itertools import product
from os import environ
from pathlib import Path
from re import match
from time import sleep
from typing import Any, Dict, List, NamedTuple, Optional, Union

# Modules libraries
from packaging.version import parse as parse_version

# Components
from ..models.flags import Flags
from ..models.images import Image, Images
from ..models.jobs import Job, JobData
from ..models.pipelines import Pipeline
from ..models.services import Service
from ..models.variables import VariablesParser
from ..package.bundle import Bundle
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.environment import Environment
from ..types.paths import Paths
from ..types.volumes import Volumes
from ..types.yaml import YAML

# GitLab class, pylint: disable=too-many-lines
class GitLab:

    # Constants
    LOCAL_NODE: str = '.local'

    # Specifications
    JOB_IMAGE_DEFAULT: str = 'ruby:3.1'
    JOB_STAGE_DEFAULT: str = 'test'
    STAGE_POST: str = '.post'
    STAGE_PRE: str = '.pre'
    STAGES_DEFAULT: Dict[str, int] = {
        STAGE_PRE: 1,
        'build': 2,
        'test': 3,
        'deploy': 4,
        STAGE_POST: 5,
    }

    # Environment
    ENV_BUILDS_DIR: str = 'CI_BUILDS_DIR'
    ENV_GIT_CLONE_PATH: str = 'GIT_CLONE_PATH'
    ENV_JOB_NAME: str = 'CI_JOB_NAME'
    ENV_JOB_NAME_SLUG: str = 'CI_JOB_NAME_SLUG'
    ENV_PROJECT_DIR: str = 'CI_PROJECT_DIR'

    # Variant type
    class Variant(NamedTuple):

        # Properties
        name: str
        variables: Dict[str, str]

    # Members
    __options: Namespace

    # Constructor
    def __init__(
        self,
        options: Namespace,
    ) -> None:

        # Initialize members
        self.__options = options

    # Merges
    @staticmethod
    def __merges(
        data: YAML.Data,
        additions: YAML.Data,
    ) -> None:

        # Validate additions
        if not data or (not isinstance(data, dict)
                        and not isinstance(data, list)): # pragma: no cover
            return

        # Validate additions
        if not additions or not isinstance(additions, dict): # pragma: no cover
            return

        # Agregate data
        base = data.copy()
        data.clear()

        # Merge data additions
        for key in additions:

            # Handle included expanding dict data
            if key in base and isinstance(additions[key], dict) and key in [
                    'variables',
            ]:
                data[key] = base[key]
                data[key].update(additions[key])

            # Handle included expanding list data
            elif key in base and isinstance(additions[key], list) and key in [
                    'volumes',
            ]:
                data[key] = list(set(base[key] + additions[key]))

            # Handle included expanding dict data
            elif key in base and isinstance(additions[key], dict):
                data[key] = base[key]
                GitLab.__merges(data[key], additions[key])

            # Handle included overriding data
            else:
                data[key] = additions[key]

        # Merge data base
        for key in base:

            # Handle unique base data
            if key not in data:
                data[key] = base[key]

    # Scripts
    @staticmethod
    def __scripts(items: Union[str, List[str]]) -> List[str]:

        # Variables
        scripts = []

        # Parse scripts data
        if isinstance(items, str):
            scripts = [items]
        elif isinstance(items, list):
            scripts = []
            for item in items:
                if isinstance(item, str):
                    scripts += [item]
                elif isinstance(item, list):
                    scripts += item[:]

        # Result
        return scripts

    # Pipeline, pylint: disable=too-many-branches
    @staticmethod
    def __pipeline(
        pipeline: Pipeline,
        data: YAML.Data,
        stages: Dict[str, int],
    ) -> None:

        # Parse variables node
        if 'variables' in data:
            GitLab.__pipeline_variables(pipeline, data['variables'])

        # Parse image node
        if 'image' in data:
            GitLab.__pipeline_image(data['image'], pipeline)

        # Parse before_script node
        if 'before_script' in data:
            pipeline.before_script = GitLab.__scripts(data['before_script'])

        # Parse after_script node
        if 'after_script' in data:
            pipeline.after_script = GitLab.__scripts(data['after_script'])

        # Parse services node
        if 'services' in data and isinstance(data['services'], list):
            GitLab.__pipeline_services(data['services'], pipeline)

        # Parse stages node
        if 'stages' in data:
            stages.clear()
            stages[GitLab.STAGE_PRE] = len(stages) + 1
            for _, stage in enumerate(data['stages']):
                if stage is not GitLab.STAGE_PRE and stage is not GitLab.STAGE_POST:
                    stages[stage] = len(stages) + 1
            stages[GitLab.STAGE_POST] = len(stages) + 1

        # Parse default node
        if 'default' in data:

            # Parse default image node
            if 'image' in data['default']:
                if 'image' in data:
                    raise SyntaxError(
                        'image is defined in top-level and `default:` entry')
                GitLab.__pipeline_image(data['default']['image'], pipeline)

            # Parse default before_script node
            if 'before_script' in data['default']:
                if 'before_script' in data:
                    raise SyntaxError(
                        'before_script is defined in top-level and `default:` entry')
                pipeline.before_script = GitLab.__scripts(
                    data['default']['before_script'])

            # Parse default after_script node
            if 'after_script' in data['default']:
                if 'after_script' in data:
                    raise SyntaxError(
                        'after_script is defined in top-level and `default:` entry')
                pipeline.after_script = GitLab.__scripts(data['default']['after_script'])

            # Parse default services node
            if 'services' in data['default'] and isinstance(data['default']['services'],
                                                            list):
                if 'services' in data:
                    raise SyntaxError(
                        'services is defined in top-level and `default:` entry')
                GitLab.__pipeline_services(data['default']['services'], pipeline)

    # Pipeline image
    @staticmethod
    def __pipeline_image(
        image_data: Union[Dict[str, Any], str],
        pipeline: Pipeline,
    ) -> None:

        # Parse image data
        if not pipeline.image:
            if isinstance(image_data, dict):
                pipeline.image = Image(
                    pipeline.variables.expand(
                        image_data['name'], types=[
                            VariablesParser.Types.PARAMETERS,
                            VariablesParser.Types.LOCALS,
                            VariablesParser.Types.GLOBALS,
                            VariablesParser.Types.ENV_FILES,
                        ]))
                if not pipeline.entrypoint:
                    if 'entrypoint' in image_data and len(image_data['entrypoint']) > 0:
                        pipeline.entrypoint = image_data['entrypoint'][:]
                    else:
                        pipeline.entrypoint = None
            else:
                pipeline.image = Image(
                    pipeline.variables.expand(
                        image_data, types=[
                            VariablesParser.Types.PARAMETERS,
                            VariablesParser.Types.LOCALS,
                            VariablesParser.Types.GLOBALS,
                            VariablesParser.Types.ENV_FILES,
                        ]))
                if not pipeline.entrypoint:
                    pipeline.entrypoint = None

    # Pipeline services
    @staticmethod
    def __pipeline_services(
        services_data: List[Any],
        pipeline: Pipeline,
    ) -> None:

        # Parse services data
        pipeline.services = []
        for item in services_data:
            if isinstance(item, dict):
                pipeline.services += [
                    Service(
                        image=Environment.expand(item.get('name', '')),
                        alias=item.get('alias', ''),
                    )
                ]
            elif isinstance(item, str):
                pipeline.services += [
                    Service(
                        image=Environment.expand(item),
                        alias='',
                    )
                ]

    # Pipeline variables
    @staticmethod
    def __pipeline_variables(
        pipeline: Pipeline,
        variables_data: YAML.Data,
    ) -> None:

        # Parse variables data
        for variable in variables_data:
            if variable not in pipeline.variables.globals:
                if variables_data[variable] is None:
                    pipeline.variables.globals[variable] = ''
                else:
                    variable_data = variables_data[variable]
                    if isinstance(variable_data, dict):
                        variable_value = str(variable_data['value'])
                    else:
                        variable_value = str(variable_data)
                    pipeline.variables.globals[variable] = variable_value

    # Include
    @staticmethod
    def __include(
        data: YAML.Data,
        stack: List[str],
        root_directory: Path,
        working_directory: Path,
        parent_path: str,
    ) -> None:

        # Parse nested include
        if data and 'include' in data and data['include']:

            # Prepare includes nodes
            data_include_list = []
            if isinstance(data['include'], dict):
                data_include_list = [data['include']]
            elif isinstance(data['include'], list):
                data_include_list = data['include']
            elif isinstance(data['include'], str):
                data_include_list = [{'local': data['include']}]

            # Iterate through includes nodes
            for include_node in data_include_list:

                # Adapt include nodes
                include_dict: dict = {} # type: ignore[type-arg]
                if isinstance(include_node, dict):
                    include_dict = include_node
                elif isinstance(include_node, str):
                    include_dict = {'local': include_node}

                # Parse local nodes
                if 'local' in include_dict:
                    GitLab.__include_local(
                        data,
                        stack,
                        root_directory,
                        working_directory,
                        include_dict,
                        parent_path,
                    )

                # Parse project node
                elif 'project' in include_dict:
                    GitLab.__include_project(
                        data,
                        stack,
                        working_directory,
                        include_dict,
                        parent_path,
                    )

                # Parse component node
                elif 'component' in include_dict:
                    GitLab.__include_component(
                        data,
                        stack,
                        working_directory,
                        include_dict,
                        parent_path,
                    )

    # Include local, pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
    @staticmethod
    def __include_local(
        data: YAML.Data,
        stack: List[str],
        root_directory: Path,
        working_directory: Path,
        include_dict: dict, # type: ignore[type-arg]
        parent_path: str,
    ) -> None:

        # Variables
        include_path: str = include_dict['local']

        # Handle include relative paths
        if include_path.startswith('/'):
            include_path = include_path.lstrip('/')
            resolved_path = Paths.resolve(root_directory / include_path)

        # Handle include relative paths
        else:
            resolved_path = Paths.resolve(working_directory / include_path)

        # Already included file
        if resolved_path in stack:
            return

        # Parse inputs
        file_inputs: YAML.Data = {}
        if 'inputs' in include_dict and isinstance(include_dict['inputs'], dict):
            file_inputs = include_dict['inputs']

        # Existing file inclusion
        file_paths: Path = Path(working_directory) / resolved_path
        for file_path in Paths.wildcard(str(file_paths), strict=True):
            if file_path.is_file():

                # Register included file
                stack.append(resolved_path)

                # Load included file
                with open(file_path, encoding='utf8', mode='r') as include_data:
                    data_additions: Optional[YAML.Data] = YAML.load(
                        include_data,
                        inputs=file_inputs,
                        configure=False,
                    )
                    if data_additions:

                        # Nested includes (follow working directory)
                        GitLab.__include(
                            data_additions,
                            stack,
                            root_directory,
                            file_path.parent,
                            resolved_path,
                        )

                        # Agregate data
                        GitLab.__merges(data_additions, data)
                        data.clear()
                        data.update(data_additions)

                    # Empty included file
                    else:
                        raise SyntaxError(
                            f'Empty "{file_path}" file included in "{parent_path}"')

            # Missing file failure
            else:
                raise FileNotFoundError(
                    f'Missing "{file_path}" file included in "{parent_path}"')

    # Include project
    @staticmethod
    def __include_project(
        data: YAML.Data,
        stack: List[str],
        working_directory: Path,
        include_dict: dict, # type: ignore[type-arg]
        parent_path: str,
    ) -> None:

        # Variables
        project_path: str = ''
        project_url: str = include_dict['project']

        # Acquire local node
        if GitLab.LOCAL_NODE in data and data[GitLab.LOCAL_NODE]:
            local = data[GitLab.LOCAL_NODE]

            # Acquire local include node
            if 'include' in local and project_url in local['include'] and isinstance(
                    local['include'][project_url], str):
                project_path = Paths.expand(
                    local['include'][project_url],
                    env=True,
                    home=True,
                )

        # Exclude missing include node
        if not project_path:
            return

        # Parse file paths
        file_items: List[str] = []
        if 'file' in include_dict:
            if isinstance(include_dict['file'], list):
                file_items = include_dict['file'][:]
            elif isinstance(include_dict['file'], str):
                file_items = [include_dict['file']]

        # Parse inputs
        file_inputs: YAML.Data = {}
        if 'inputs' in include_dict and isinstance(include_dict['inputs'], dict):
            file_inputs = include_dict['inputs']

        # Iterate through file paths
        for file_item in file_items:

            # Already included file
            resolved_path = Paths.resolve(
                working_directory / project_path / file_item.lstrip('/'))
            if resolved_path in stack:
                continue

            # Existing file inclusion
            file_paths: Path = Path(working_directory) / resolved_path
            for file_path in Paths.wildcard(str(file_paths), strict=True):
                if file_path.is_file():

                    # Register included file
                    stack.append(resolved_path)

                    # Load included file
                    with open(file_path, encoding='utf8', mode='r') as include_data:
                        data_additions: Optional[YAML.Data] = YAML.load(
                            include_data,
                            inputs=file_inputs,
                            configure=False,
                        )
                        if data_additions:

                            # Nested includes (follow working directory)
                            project_working_directory: Path = Path(
                                working_directory) / Paths.resolve(
                                    working_directory / project_path)
                            GitLab.__include(
                                data_additions,
                                stack,
                                project_working_directory,
                                project_working_directory,
                                str(file_path),
                            )

                            # Agregate data
                            GitLab.__merges(data_additions, data)
                            data.clear()
                            data.update(data_additions)

                        # Empty included file
                        else:
                            raise SyntaxError(
                                f'Empty "{file_path}" file included in "{parent_path}"')

                # Missing file failure
                else:
                    raise FileNotFoundError(
                        f'Missing "{file_path}" file included in "{parent_path}"')

    # Include component
    @staticmethod
    def __include_component(
        data: YAML.Data,
        stack: List[str],
        working_directory: Path,
        include_dict: dict, # type: ignore[type-arg]
        parent_path: str,
    ) -> None:

        # Variables
        component_path: str = ''
        component_url: str = include_dict['component']

        # Acquire local node
        if GitLab.LOCAL_NODE in data and data[GitLab.LOCAL_NODE]:
            local = data[GitLab.LOCAL_NODE]

            # Acquire local include node
            if 'include' in local and component_url in local['include'] and isinstance(
                    local['include'][component_url], str):
                component_path = Paths.expand(
                    local['include'][component_url],
                    env=True,
                    home=True,
                )

        # Exclude missing include node
        if not component_path:
            return

        # Parse inputs
        file_inputs: YAML.Data = {}
        if 'inputs' in include_dict and isinstance(include_dict['inputs'], dict):
            file_inputs = include_dict['inputs']

        # Already included file
        resolved_path = Paths.resolve(working_directory / component_path)
        if resolved_path in stack:
            return

        # Existing file inclusion
        file_paths: Path = Path(working_directory) / resolved_path
        for file_path in Paths.wildcard(str(file_paths), strict=True):
            if file_path.is_file():

                # Register included file
                stack.append(resolved_path)

                # Load included file
                with open(file_path, encoding='utf8', mode='r') as include_data:
                    data_additions: Optional[YAML.Data] = YAML.load(
                        include_data,
                        inputs=file_inputs,
                        configure=False,
                    )
                    if data_additions:

                        # Nested includes (follow working directory)
                        component_working_directory: Path = Path(
                            working_directory) / Paths.resolve(
                                working_directory / component_path)
                        GitLab.__include(
                            data_additions,
                            stack,
                            component_working_directory,
                            component_working_directory,
                            str(file_path),
                        )

                        # Agregate data
                        GitLab.__merges(data_additions, data)
                        data.clear()
                        data.update(data_additions)

                    # Empty included file
                    else:
                        raise SyntaxError(
                            f'Empty "{file_path}" file included in "{parent_path}"')

            # Missing file failure
            else:
                raise FileNotFoundError(
                    f'Missing "{file_path}" file included in "{parent_path}"')

    # Local, pylint: disable=too-many-branches,too-many-statements
    @staticmethod
    def __local(
        options: Namespace,
        pipeline: Pipeline,
        data: YAML.Data,
    ) -> None:

        # Variables
        local_unsupported: List[str]
        names_local = False

        # Filter local node, pylint: disable=too-many-nested-blocks
        if GitLab.LOCAL_NODE in data and data[GitLab.LOCAL_NODE]:
            local = data[GitLab.LOCAL_NODE]

            # Parse local all
            if 'all' in local and not options.all:
                options.all = local['all']

            # Parse local env
            if 'env' in local:
                pipeline.variables.local_parse_env(local['env'])

            # Parse local image
            if 'image' in local and not options.image:
                options.image = local['image']

            # Parse local names
            if 'names' in local and not options.names and not options.pipeline:
                names_local = True
                options.names = local['names']

            # Parse local no_regex
            if 'no_regex' in local and not options.no_regex:
                options.no_regex = local['no_regex']

            # Parse local pipeline
            if 'pipeline' in local and not options.pipeline and (not options.names
                                                                 or names_local):
                options.pipeline = local['pipeline']

            # Parse local tags
            if 'tags' in local and options.tags_default:
                options.tags = local['tags'][:]
                options.tags_default = False

            # Parse local variables
            if 'variables' in local:
                pipeline.variables.local_parse_variables(local['variables'])

            # Parse local version
            if 'version' in local:
                version: str = str(local['version'])

                # Newer local recommended version
                package_version: str = Version.get()
                if package_version != '0.0.0' and parse_version(
                        package_version) < parse_version(version):
                    Updates.message(name=Bundle.PACKAGE, recommended=version)
                    sleep(2)

            # Parse local volumes
            if 'volumes' in local:
                if not options.volume:
                    options.volume = []
                for volume in local['volumes']:
                    options.volume += [Volumes.LOCAL_FLAG + volume]

            # Detect unsupported local keys
            local_unsupported = [
                key for key in local if key not in [
                    'all',
                    'env',
                    'image',
                    'include',
                    'names',
                    'no_regex',
                    'pipeline',
                    'tags',
                    'variables',
                    'version',
                    'volumes',
                ]
            ]
            if local_unsupported:
                print(' ')
                print(
                    f'  {Colors.YELLOW}‣ WARNING: '
                    f'{Colors.RED}.local: {", ".join(local_unsupported)}: '
                    f'{Colors.BOLD}YAML configuration '
                    f'{"are" if len(local_unsupported) > 1 else "is"} unsupported, see: '
                    f'{Colors.GREEN}{Bundle.REPOSITORY}/-/issues/292'
                    f'{Colors.RESET}')
                Platform.flush()
                if Platform.IS_TTY_STDIN:
                    sleep(5)

    # Variants, pylint: disable=too-many-nested-blocks
    @staticmethod
    def __variants(
        pipeline: Pipeline,
        data: YAML.Data,
        node: str,
    ) -> List[Variant]:

        # Variables
        variants: List[GitLab.Variant] = []

        # Handle parallel variants integer
        if 'parallel' in data[node] and isinstance(data[node]['parallel'], int):

            # Register all combinations
            for parallel_index in range(1, data[node]['parallel'] + 1):
                variants += [
                    GitLab.Variant(
                        name=f"{node} {parallel_index}/{data[node]['parallel']}",
                        variables={},
                    )
                ]

        # Handle matrix variants list
        elif 'parallel' in data[node] and isinstance(data[node]['parallel'], dict) \
                and 'matrix' in data[node]['parallel']:

            # Iterate through matrix items
            for matrix_item in data[node]['parallel']['matrix']:

                # Prepare matrix map
                matrix_item_map: Dict[str, List[str]] = {}

                # Iterate through matrix item
                for matrix_variable, matrix_values in matrix_item.items():

                    # Already defined environment variable
                    if matrix_variable in pipeline.variables.parameters:
                        matrix_item_map[matrix_variable] = [
                            pipeline.variables.parameters[matrix_variable]
                        ]

                    # Already defined environment variable
                    elif matrix_variable in environ:
                        matrix_item_map[matrix_variable] = [environ[matrix_variable]]

                    # Matrix defined environment variable
                    else:
                        matrix_item_map[matrix_variable] = []
                        if isinstance(matrix_values, str):
                            matrix_item_map[matrix_variable] += [matrix_values]
                        elif isinstance(matrix_values, list):
                            for matrix_value in matrix_values:
                                matrix_item_map[matrix_variable] += [matrix_value]

                # Extract all combinations
                keys, values = zip(*matrix_item_map.items())
                matrix_item_environments: List[Dict[str, str]] = [
                    dict(zip(keys, v)) for v in product(*values)
                ]

                # Register all combinations
                for matrix_item_variables in matrix_item_environments:
                    variants += [
                        GitLab.Variant(
                            name=
                            f"{node}: [{', '.join(list(matrix_item_variables.values()))}]",
                            variables=matrix_item_variables,
                        )
                    ]

        # Prepare default variants list
        else:
            variants = [GitLab.Variant(
                name=node,
                variables={},
            )]

        # Result
        return variants

    # Job, pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-positional-arguments,too-many-statements
    @staticmethod
    def job(
        options: Namespace,
        pipeline: Pipeline,
        job_node: str,
        job_name: str,
        data: YAML.Data,
        extend: bool = False,
    ) -> JobData:

        # Variables
        job: JobData = JobData(name=job_name)
        job_data = data[job_node]

        # Prepare options
        job.options.env_builds_path = GitLab.ENV_BUILDS_DIR
        job.options.env_job_name = GitLab.ENV_JOB_NAME
        job.options.env_job_name_slug = GitLab.ENV_JOB_NAME_SLUG
        job.options.env_job_path = GitLab.ENV_PROJECT_DIR

        # Extract job extends
        if 'extends' in job_data and job_data['extends']:
            if isinstance(job_data['extends'], list):
                job_extends = job_data['extends']
            else:
                job_extends = [job_data['extends']]

            # Iterate through extended jobs
            for job_extend in reversed(job_extends):

                # Validate extended job
                if job_extend not in data:
                    job.options.extends_unknown += [f'{job_extend} unknown']
                    continue

                # Parse extended job
                job_extended: JobData = GitLab.job(
                    options,
                    pipeline,
                    job_extend,
                    job_extend,
                    data,
                    True,
                )

                # List available extended job
                job.options.extends_available += [job_extend]

                # Extract extended job
                if job.stage is None:
                    job.stage = job_extended.stage
                if job.image is None:
                    job.image = job_extended.image
                if job.entrypoint is None:
                    job.entrypoint = job_extended.entrypoint
                if job_extended.variables:
                    for variable, value in job_extended.variables.items():
                        if variable not in job.variables:
                            job.variables[variable] = value
                if job.before_script is None:
                    job.before_script = job_extended.before_script
                if job.script is None:
                    job.script = job_extended.script
                if job.after_script is None:
                    job.after_script = job_extended.after_script
                if job.retry is None:
                    job.retry = job_extended.retry
                if job.when is None:
                    job.when = job_extended.when
                if job.allow_failure is None:
                    job.allow_failure = job_extended.allow_failure
                if job.services is None:
                    job.services = job_extended.services
                if job.tags is None:
                    job.tags = job_extended.tags
                if job.trigger is None:
                    job.trigger = job_extended.trigger

        # Apply pipeline values
        if not extend:
            if job.image is None:
                job.image = pipeline.image
            if job.entrypoint is None:
                job.entrypoint = pipeline.entrypoint[:] if pipeline.entrypoint else None
            if job.before_script is None:
                job.before_script = pipeline.before_script[:]
            if job.script is None:
                job.script = []
            if job.after_script is None:
                job.after_script = pipeline.after_script[:]
            if job.retry is None:
                job.retry = 0
            if job.services is None:
                job.services = pipeline.services[:]
            if job.when is None:
                job.when = 'on_success'
            if job.allow_failure is None:
                job.allow_failure = False

        # Extract job stage
        if 'stage' in job_data and job_data['stage']:
            job.stage = job_data['stage']
        elif job.stage is None and not extend:
            job.stage = GitLab.JOB_STAGE_DEFAULT

        # Extract job image
        if 'image' in job_data and job_data['image']:
            image_data = job_data['image']
            if isinstance(image_data, dict):
                job.image = Environment.expand(image_data['name'])
                if 'entrypoint' in image_data and len(image_data['entrypoint']) > 0:
                    job.entrypoint = image_data['entrypoint'][:]
                else:
                    job.entrypoint = None
            else:
                job.image = Environment.expand(image_data)
                job.entrypoint = None

        # Extract job variables
        if 'variables' in job_data and job_data['variables']:
            job.variables.update(job_data['variables'])

        # Prepare job variables
        job.variables = pipeline.variables.evaluate_job(job.variables)

        # Extract job before_script
        if 'before_script' in job_data:
            job.before_script = GitLab.__scripts(job_data['before_script'])

        # Extract job script
        if 'script' in job_data:
            if options.commands:
                job.script = GitLab.__scripts(options.commands)
            else:
                job.script = GitLab.__scripts(job_data['script'])

        # Extract job after_script
        if 'after_script' in job_data:
            job.after_script = GitLab.__scripts(job_data['after_script'])

        # Extract job retry
        if 'retry' in job_data:
            retry_data = job_data['retry']
            if isinstance(retry_data, dict):
                job.retry = int(retry_data['max'])
            else:
                job.retry = int(retry_data)

        # Extract job when
        if 'when' in job_data and job_data['when'] in [
                'on_success', 'on_failure', 'always', 'manual'
        ]:
            job.when = job_data['when']

        # Extract job allow_failure
        if 'allow_failure' in job_data and job_data['allow_failure'] in [True, False]:
            job.allow_failure = job_data['allow_failure']

        # Extract job services
        if 'services' in job_data and isinstance(job_data['services'], list):
            job.services = []
            for item in job_data['services']:
                if isinstance(item, dict):
                    job.services += [
                        Service(
                            image=Environment.expand(item.get('name', '')),
                            alias=item.get('alias', ''),
                        )
                    ]
                elif isinstance(item, str):
                    job.services += [Service(
                        image=Environment.expand(item),
                        alias='',
                    )]

        # Extract job tags
        if 'tags' in job_data and job_data['tags']:
            job.tags = job_data['tags'][:]
            assert job.tags is not None
            for index, tag in enumerate(job.tags):
                job.tags[index] = Environment.expand(tag)

        # Finalize job extends
        if 'extends' in job_data and job_data['extends']:

            # Allowed incomplete extended job
            if Flags.enabled(Bundle.FLAG_EXTENDS_INCOMPLETE, job.variables):
                pass

            # Detect incomplete extended job
            elif job.options.extends_unknown and \
                    (len(job_extends) == 1 or len(job.options.extends_available) == 0):
                job.options.disabled = ', '.join(job.options.extends_unknown)

        # Extract job trigger
        if 'trigger' in job_data and job_data['trigger']:
            job.options.disabled = 'trigger only'
            if isinstance(job_data['trigger'], (dict, str)):
                job.trigger = job_data['trigger']

        # Finalize pipeline values
        if not extend:

            # Configure job tags
            if job.tags and (set(job.tags) & set(options.tags)):
                job.when = 'manual'

        # Default GitLab image
        if not job.image and not extend:
            if environ.get(Bundle.ENV_IMAGE_DEFAULT, ''):
                job.image = environ[Bundle.ENV_IMAGE_DEFAULT][:]
            else:
                job.image = GitLab.JOB_IMAGE_DEFAULT[:]

        # Detect GIT_CLONE_PATH
        if GitLab.ENV_GIT_CLONE_PATH in job.variables:
            job.options.git_clone_path = job.variables[GitLab.ENV_GIT_CLONE_PATH]

        # Detect host jobs
        if Flags.check_bool(
                option=options.host,
                flag=Bundle.FLAG_HOST,
                variables=job.variables,
                default=False,
        ):
            job.options.host = True
        elif job.image:
            job.options.host = Images.host(job.image)
            if Images.quiet(job.image):
                job.variables[Bundle.FLAG_QUIET] = Flags.string(Images.quiet(job.image))
            job.options.silent = Images.silent(job.image)

        # Apply verbose option
        job.options.verbose = not Flags.check_bool(
            option=options.no_verbose,
            flag=Bundle.FLAG_NO_VERBOSE,
            variables=job.variables,
            default=False,
        ) and not job.options.silent

        # Detect sockets services
        if job.services:
            for service in job.services:
                if match(Images.DOCKER_DIND_REGEX, service.image):
                    job.options.sockets = True

        # Apply sockets option
        if not job.options.sockets:
            job.options.sockets = Flags.check_bool(
                option=options.sockets,
                flag=Bundle.FLAG_SOCKETS,
                variables=job.variables,
                default=False,
            )

        # Apply ssh option
        if not job.options.ssh:
            job.options.ssh = Flags.check_strbool(
                option=options.ssh,
                variables=job.variables,
                flag=Bundle.FLAG_SSH,
                default='',
                const=Bundle.ARGUMENT_SSH_USER_DEFAULT,
            )

        # Result
        return job

    # Parse
    def parse(
        self,
        data: YAML.Data,
    ) -> Pipeline:

        # Variables
        pipeline: Pipeline = Pipeline(self.__options)
        stages: Dict[str, int] = GitLab.STAGES_DEFAULT.copy()

        # Cache environment
        pipeline.variables.environment_cache()

        # Parse nested include
        GitLab.__include(
            data,
            [Paths.resolve(self.__options.path / self.__options.configuration)],
            self.__options.path,
            self.__options.path,
            Paths.resolve(self.__options.path / self.__options.configuration),
        )

        # Resolve YAML nodes
        YAML.resolve(data)

        # Filter local node
        self.__local(self.__options, pipeline, data)

        # Apply variables
        pipeline.variables.apply(types=[
            VariablesParser.Types.PARAMETERS,
            VariablesParser.Types.LOCALS,
            VariablesParser.Types.ENV_FILES,
        ])

        # Prepare pipeline image
        if self.__options.image:
            if isinstance(self.__options.image, dict):
                if 'name' in self.__options.image:
                    pipeline.image = Environment.expand(self.__options.image['name'])
                if 'entrypoint' in self.__options.image and len(
                        self.__options.image['entrypoint']) > 0:
                    pipeline.entrypoint = self.__options.image['entrypoint'][:]
                else:
                    pipeline.entrypoint = None
            else:
                pipeline.image = Environment.expand(self.__options.image)
                pipeline.entrypoint = None

        # Parse pipeline nodes
        GitLab.__pipeline(
            pipeline,
            data,
            stages,
        )

        # Iterate through nodes
        for node in data:

            # Ignore pipeline nodes
            if node in [
                    'after_script',
                    'before_script',
                    'image',
                    'include',
                    'services',
                    'stages',
                    'variables',
            ]:
                continue

            # Validate job node
            if 'script' not in data[node] and 'extends' not in data[node]:
                continue

            # Ignore template stage
            if node[0:1] == '.':
                continue

            # Nodes variants
            variants = GitLab.__variants(
                pipeline,
                data,
                node,
            )

            # Iterate through node
            for variant in variants:

                # Restore environment
                pipeline.variables.environment_restore()

                # Apply variables
                pipeline.variables.apply(types=[
                    VariablesParser.Types.PARAMETERS,
                    VariablesParser.Types.LOCALS,
                    VariablesParser.Types.GLOBALS,
                    VariablesParser.Types.ENV_FILES,
                ])

                # Acquire variant name
                name = variant.name

                # Prepare variant variables
                if variant.variables:
                    VariablesParser.environment_update(variant.variables)

                # Register job
                pipeline.jobs[name] = Job(
                    self.job(
                        self.__options,
                        pipeline,
                        node,
                        name,
                        data,
                    ))

                # Prepare variant variables
                if variant.variables:
                    pipeline.jobs[name].variables.update(variant.variables)

                # Validate job script
                if not pipeline.jobs[name].options.disabled and not pipeline.jobs[
                        name].script:
                    if self.__options.no_script_fail:
                        raise ValueError(
                                f"Missing \"script\" key for \"{pipeline.jobs[name].stage}" \
                                f" / {pipeline.jobs[name].name}\""
                        )
                    pipeline.jobs[name].options.disabled = 'Missing "script" key'

                # Append unknown stage if required
                if pipeline.jobs[name].options.disabled \
                        and pipeline.jobs[name].stage == GitLab.JOB_STAGE_DEFAULT \
                            and GitLab.JOB_STAGE_DEFAULT not in stages:
                    stages[GitLab.JOB_STAGE_DEFAULT] = list(stages.values())[-1] + 1

                # Validate job stage
                if pipeline.jobs[name].stage not in stages:
                    raise ValueError(
                        f"Unknown stage \"{pipeline.jobs[name].stage}\"" \
                            f" for \"{pipeline.jobs[name].name}\""
                    )

            # Restore environment
            pipeline.variables.environment_restore()

        # Sort pipeline jobs based on stages
        pipeline.jobs = OrderedDict(
            sorted(
                pipeline.jobs.items(),
                key=lambda x: stages[x[1].stage],
            ))

        # Result
        return pipeline
