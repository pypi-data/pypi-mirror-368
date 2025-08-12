#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from os import chmod, environ, stat, system
from pathlib import Path, PurePosixPath
from re import sub as regex_sub
from signal import getsignal, SIGINT, signal, SIGTERM
from stat import S_IRGRP, S_IROTH, S_IXGRP, S_IXOTH, S_IXUSR
from subprocess import run
from sys import stdout
from time import sleep
from types import FrameType
from typing import Dict, List, Optional

# Components
from ..engines.engine import Engine, privileged_default
from ..models.flags import Flags
from ..models.images import Entrypoint
from ..models.jobs import Job
from ..package.bundle import Bundle
from ..prints.histories import PipelineHistory
from ..system.git import Git
from ..system.platform import Platform
from ..system.xauth import Xauth
from ..types.environment import Environment
from ..types.paths import Paths
from ..types.strings import Strings
from ..types.volumes import Volumes
from .outputs import Outputs
from .scripts import ScriptsFile

# Runner class, pylint: disable=too-few-public-methods
class Runner:

    # Constants
    __MARKER_DEBUG: str = '__GITLAB_CI_LOCAL_DEBUG__'
    __MARKER_ENDING: str = '__GITLAB_CI_LOCAL_ENDING__'
    __MARKER_RESULT: str = '__GITLAB_CI_LOCAL_RESULT__'

    # Members
    __engines: Dict[str, Optional[Engine]] = {}
    __interrupted: bool
    __options: Namespace

    # Constructor
    def __init__(
        self,
        options: Namespace,
    ) -> None:

        # Prepare flags
        self.__interrupted = False

        # Prepare options
        self.__options = options

    # Run container, pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-positional-arguments,too-many-statements
    def __run_container(
        self,
        engine: Optional[Engine],
        variables: Dict[str, str],
        path_parent: str,
        target_parent: str,
        image: str,
        job: Job,
        script_file: ScriptsFile,
        entrypoint: Entrypoint,
        network: str,
        privileged: bool,
        target_workdir: str,
        last_result: bool,
        result: bool,
    ) -> bool:

        # Validate engine
        assert engine is not None

        # Configure engine variables
        variables[Bundle.ENV_ENGINE_NAME] = engine.name

        # Prepare volumes mounts
        volumes = Volumes()

        # Mount repository folder
        volumes.add(
            path_parent,
            target_parent,
            'rw',
            True,
        )

        # Extend mounts
        if self.__options.volume:
            for volume in self.__options.volume:

                # Handle .local volumes
                cwd = Path('.')
                volume_local = False
                if volume.startswith(Volumes.LOCAL_FLAG):
                    cwd = self.__options.path
                    volume_local = True
                    volume = volume[len(Volumes.LOCAL_FLAG):]

                # Parse volume fields
                volume_nodes = Volumes.parse(volume)

                # Parse HOST:TARGET:MODE, pylint: disable=line-too-long
                if len(volume_nodes) == 3:
                    volume_host = Paths.resolve(cwd / Paths.expand(volume_nodes[0]))
                    volume_target = Paths.expand(volume_nodes[1], home=False)
                    volume_mode = volume_nodes[2]

                # Parse HOST:TARGET, pylint: disable=line-too-long
                elif len(volume_nodes) == 2:
                    volume_host = Paths.resolve(cwd / Paths.expand(volume_nodes[0]))
                    volume_target = Paths.expand(volume_nodes[1], home=False)
                    volume_mode = 'rw'

                # Parse VOLUME, pylint: disable=line-too-long
                else:
                    volume_host = Paths.resolve(cwd / Paths.expand(volume_nodes[0]))
                    volume_target = Paths.resolve(cwd / Paths.expand(volume_nodes[0]))
                    volume_mode = 'rw'

                # Append volume mounts
                volumes.add(
                    volume_host,
                    volume_target,
                    volume_mode,
                    not volume_local,
                )

        # Image validation
        if not image: # pragma: no cover
            raise ValueError(f"Missing image for \"{job.stage} / {job.name}\"")
        engine.get(image)

        # Display option
        if Flags.check_bool(
                option=self.__options.display,
                flag=Bundle.FLAG_DISPLAY,
                variables=job.variables,
                default=False,
        ):

            # Bind display environment
            if Platform.ENV_DISPLAY in environ: # pragma: no cover
                variables[Platform.ENV_DISPLAY] = environ[Platform.ENV_DISPLAY]
            if Platform.ENV_XAUTHORITY in environ: # pragma: no cover
                variables[Platform.ENV_XAUTHORITY] = environ[Platform.ENV_XAUTHORITY]

            # Bind display socket
            for display_socket in Platform.display(): # pragma: no cover
                volumes.add(
                    display_socket,
                    display_socket,
                    'rw',
                    False,
                )

            # Bind display Xauthority
            display_xauth_magic: str = Xauth.magic()
            if display_xauth_magic: # pragma: no cover
                variables[Bundle.ENV_DISPLAY_XAUTH_MAGIC_ADD] = display_xauth_magic

        # SSH option
        ssh: str = Flags.check_strbool(
            option=self.__options.ssh,
            flag=Bundle.FLAG_SSH,
            variables=job.variables,
            default='',
            const=Bundle.ARGUMENT_SSH_USER_DEFAULT,
        )
        if ssh:

            # Bind SSH credentials
            volumes.add(
                Paths.expand('~/.ssh'),
                Paths.home(ssh) + '/.ssh',
                'ro',
                False,
            )

            # Bind SSH agent
            if Platform.ENV_SSH_AUTH_SOCK in environ:
                if environ[Platform.ENV_SSH_AUTH_SOCK]:
                    volumes.add(
                        Paths.expand(environ[Platform.ENV_SSH_AUTH_SOCK]),
                        Paths.expand(environ[Platform.ENV_SSH_AUTH_SOCK]),
                        'ro',
                        True,
                    )
                variables[Platform.ENV_SSH_AUTH_SOCK] = environ[
                    Platform.ENV_SSH_AUTH_SOCK]

        # Launch container
        engine.run(
            image=image,
            commands=[script_file.target()],
            entrypoint=entrypoint,
            variables=variables,
            network=network,
            option_privileged=privileged,
            option_sockets=job.options.sockets,
            services=bool(job.services),
            volumes=volumes,
            directory=target_workdir,
            temp_folder=script_file.folder,
        )

        # Create interruption handler
        def interrupt_handler(
            __signalnum: Optional[int] = None,
            __frame: Optional[FrameType] = None,
        ) -> None:
            self.__interrupted = True
            Outputs.interruption()
            assert engine is not None
            engine.stop(0)

        # Register interruption handler
        handler_int_original = getsignal(SIGINT)
        handler_term_original = getsignal(SIGTERM)
        signal(SIGINT, interrupt_handler)
        signal(SIGTERM, interrupt_handler)

        # Execution wrapper
        marker_result: Optional[bool] = None
        success = False

        # Show container logs
        for line in engine.logs():
            if isinstance(line, bytes):
                line_decoded = line.decode()
                if self.__MARKER_DEBUG in line_decoded:
                    break # pragma: no cover
                if self.__MARKER_RESULT in line_decoded:
                    marker_result = int(
                        line_decoded.split(f'{self.__MARKER_RESULT}:', 1)[1]) == 0
                    continue
                if self.__MARKER_ENDING in line_decoded:
                    break
                stdout.buffer.write(line)
                Platform.flush()

        # Runner bash or debug mode
        if not self.__interrupted and (Flags.check_bool(
                option=self.__options.bash,
                flag=Bundle.FLAG_BASH,
                variables=job.variables,
                default=False,
        ) or Flags.check_bool(
                option=self.__options.debug,
                flag=Bundle.FLAG_DEBUG,
                variables=job.variables,
                default=False,
        )):

            # Select shell
            shell: str = ''
            if Flags.has(
                    option=self.__options.shell,
                    flag=Bundle.FLAG_SHELL,
                    variables=job.variables,
            ):
                shell = Flags.check_str(
                    option=self.__options.shell,
                    flag=Bundle.FLAG_SHELL,
                    variables=job.variables,
                    default='sh',
                )
            elif engine.supports('bash'):
                shell = 'bash'
            else:
                shell = 'sh'

            # Select console
            console: bool = Platform.IS_TTY_STDIN and not Flags.check_bool(
                option=self.__options.no_console,
                flag=Bundle.FLAG_NO_CONSOLE,
                variables=job.variables,
                default=False,
            )

            # Acquire container informations
            container_exec = engine.cmd_exec()
            container_name = engine.container

            # Debugging informations
            Outputs.debugging(
                container_exec,
                container_name,
                shell,
                console=console,
            )

            # Launch container console
            if console:
                run(
                    f'{container_exec} {container_name} {shell}',
                    check=False,
                    shell=True,
                )
                self.__interrupted = True
                engine.stop(0)

        # Check container status
        success = engine.wait()

        # Stop container
        engine.stop(0)
        sleep(0.1)

        # Remove container
        engine.remove()

        # Unregister interruption handler
        signal(SIGINT, handler_int_original)
        signal(SIGTERM, handler_term_original)

        # Result evaluation
        if job.when in [
                'on_failure',
                'always',
        ]:
            result = last_result
        elif success:
            result = True
        elif self.__interrupted and marker_result is not None:
            result = marker_result
        return result

    # Run native, pylint: disable=too-many-arguments,too-many-positional-arguments
    @staticmethod
    def __run_native(
        variables: Dict[str, str],
        entrypoint: Entrypoint,
        script_file: ScriptsFile,
        job: Job,
        last_result: bool,
        result: bool,
    ) -> bool:

        # Configure host variables
        variables[Bundle.ENV_HOST] = 'true'

        # Prepare environment
        _environ = dict(environ)
        environ.update(variables)

        # Detect nested execution
        if ScriptsFile.SHEBANG_MARKER_BASH in environ:
            del environ[ScriptsFile.SHEBANG_MARKER_BASH]

        # Native execution
        scripts: List[str] = []
        if entrypoint:
            scripts += entrypoint
        if not scripts:
            scripts = ['sh']
        scripts += [f'"{script_file.name}"']
        success = system(' '.join(scripts)) == 0

        # Result evaluation
        if job.when in [
                'on_failure',
                'always',
        ]:
            result = last_result
        elif success:
            result = True

        # Restore environment
        environ.clear()
        environ.update(_environ)

        # Result
        return result

    # Run, pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-statements
    def run(
        self,
        job: Job,
        last_result: bool,
        pipeline_history: PipelineHistory,
    ) -> bool:

        # Variables
        engine: Optional[Engine] = None
        engines_names: str
        engine_type: str = ''
        host: bool = False
        network: str
        privileged: bool
        quiet: bool
        random_paths: bool = False
        real_paths: bool = False
        result: bool = False
        script_file: ScriptsFile

        # Prepare history
        job_history = pipeline_history.add(
            job.stage,
            job.name,
        )

        # Validate paths
        if Flags.check_bool(
                option=self.__options.random_paths,
                flag=Bundle.FLAG_RANDOM_PATHS,
                variables=job.variables,
                default=False,
        ) and Flags.check_bool(
                option=self.__options.real_paths,
                flag=Bundle.FLAG_REAL_PATHS,
                variables=job.variables,
                default=False,
        ):
            Outputs.warning(
                'The real paths feature is in conflict with the random paths feature...')
            random_paths = True

        # Prepare random paths
        elif Flags.check_bool(
                option=self.__options.random_paths,
                flag=Bundle.FLAG_RANDOM_PATHS,
                variables=job.variables,
                default=False,
        ):
            random_paths = True

        # Prepare real paths
        elif Flags.check_bool(
                option=self.__options.real_paths,
                flag=Bundle.FLAG_REAL_PATHS,
                variables=job.variables,
                default=False,
        ):
            if Platform.IS_LINUX or Platform.IS_MAC_OS:
                real_paths = True

            # Unavailable feature
            else: # pragma: no cover
                Outputs.warning('The real paths feature is not available...')

        # Initial job details
        job_details_list: List[str] = []
        job_details_string: str = ''

        # Prepare when details
        if job.when not in ['on_success']:
            job_details_list += [f"when: {job.when}"]

        # Prepare allow_failure details
        if job.allow_failure:
            job_details_list += ['failure allowed']
            job_history.failure_allowed = True

        # Prepare job details
        if job_details_list:
            job_details_string = f" ({', '.join(job_details_list)})"

        # Update job details
        job_history.details = job_details_string

        # Filter when
        if last_result and job.when not in [
                'on_success',
                'manual',
                'always',
        ]:
            return last_result
        if not last_result and job.when not in [
                'on_failure',
                'always',
        ]:
            return last_result

        # Prepare image
        image: str = job.image

        # Prepare local runner
        if self.__options.host or job.options.host:
            image = 'local'
            host = True

        # Prepare quiet flag
        quiet = Flags.check_bool(
            option=self.__options.quiet,
            flag=Bundle.FLAG_QUIET,
            variables=job.variables,
            default=False,
        )

        # Drop quiet flag
        if not quiet and pipeline_history.jobs_quiet:
            pipeline_history.jobs_quiet = False

        # Prepare engine execution
        if not host:
            engines_names = Flags.check_str(
                option=None,
                flag=Bundle.FLAG_ENGINE,
                variables=job.variables,
                default=self.__options.engine,
            )
            if engines_names not in self.__engines or self.__engines[
                    engines_names] is None:
                self.__engines[engines_names] = Engine(engines_names)
            engine = self.__engines[engines_names]
            assert engine is not None
            engine_type = engine.name

        # Prepare native execution
        else:
            engine_type = 'native'

        # Header
        if not quiet:
            job_history.header(
                pipeline_history.jobs_count,
                image,
                engine_type,
            )

        # Acquire project paths
        path_project = Paths.resolve(self.__options.path)
        path_parent = Paths.resolve(Path(self.__options.path).parent)

        # Acquire project targets
        if host or real_paths:
            target_project = path_project
            target_parent = path_parent
        elif job.options.git_clone_path:
            git_clone_path = PurePosixPath(job.options.git_clone_path)
            target_project = Paths.get(git_clone_path / Path(path_project).name)
            target_parent = Paths.get(git_clone_path)
        elif random_paths:
            random_path: str = Strings.random(8)
            target_project = Paths.get(
                Platform.BUILDS_DIR / random_path / Path(path_project).name)
            target_parent = Paths.get(Platform.BUILDS_DIR / random_path)
        else:
            target_project = Paths.get(Platform.BUILDS_DIR / Path(path_project).name)
            target_parent = Paths.get(Platform.BUILDS_DIR)

        # Prepare specific working directory
        if Flags.has(
                option=self.__options.workdir,
                flag=Bundle.FLAG_WORKDIR,
                variables=job.variables,
        ):
            relativedir: Path = Path('.')
            workdir: str = Flags.check_str(
                option=self.__options.workdir,
                flag=Bundle.FLAG_WORKDIR,
                variables=job.variables,
                default='.',
            )

            # Expand real working directory
            if Platform.IS_LINUX or Platform.IS_MAC_OS:
                workdir = Paths.expand(workdir)
                if host or real_paths:
                    target_workdir = Paths.get((relativedir / workdir).resolve())
                else:
                    target_workdir = Paths.get(PurePosixPath(target_project) / workdir)

            # Expand remote working directory
            else: # pragma: no cover
                if workdir[0:1] == '~':
                    target_workdir = Paths.get(workdir)
                else:
                    workdir = Paths.expand(workdir, home=False)
                    if host or real_paths:
                        target_workdir = Paths.get((relativedir / workdir).resolve())
                    else:
                        target_workdir = Paths.get(
                            PurePosixPath(target_project) / workdir)

        # Prepare real working directory
        elif host or real_paths:
            target_workdir = Paths.get(self.__options.path)

        # Prepare target working directory
        else:
            target_workdir = target_project

        # Prepare entrypoint and scripts
        scripts_after: List[str] = []
        scripts_before: List[str] = []
        scripts_commands: List[str] = []
        scripts_debug: List[str] = []

        # Prepare before_scripts
        if Flags.check_bool(
                option=self.__options.before,
                flag=Bundle.FLAG_BEFORE,
                variables=job.variables,
                default=True,
        ):
            scripts_before += job.before_script

        # Prepare scripts
        scripts_commands += job.script
        if not host:
            if Flags.check_bool(
                    option=self.__options.bash,
                    flag=Bundle.FLAG_BASH,
                    variables=job.variables,
                    default=False,
            ):
                scripts_commands = []
            if Flags.check_bool(
                    option=self.__options.bash,
                    flag=Bundle.FLAG_BASH,
                    variables=job.variables,
                    default=False,
            ) or Flags.check_bool(
                    option=self.__options.debug,
                    flag=Bundle.FLAG_DEBUG,
                    variables=job.variables,
                    default=False,
            ):
                scripts_debug += [
                    f"echo \"{self.__MARKER_DEBUG}\"", 'tail -f /dev/null || true'
                ]

        # Prepare after_scripts
        if Flags.check_bool(
                option=self.__options.after,
                flag=Bundle.FLAG_AFTER,
                variables=job.variables,
                default=True,
        ):
            scripts_after += job.after_script

        # Prepare script file
        script_file = ScriptsFile(
            paths={
                path_parent: target_parent,
                path_project: target_project
            },
            prefix='.tmp.entrypoint.',
        )

        # Prepare execution context
        script_file.shebang()
        script_file.writelines([
            '# Variables',
            'result=1',
            '',
        ])

        # Prepare host working directory
        if host:
            script_file.writelines([
                '# Work directory',
                f'cd "{target_workdir}"',
                '',
            ])

        # Configure Git
        if not host and not self.__options.no_git_safeties:
            script_file.writelines([
                '# Configure Git safeties',
                'if type git >/dev/null 2>&1; then',
                f'  git config --global --add safe.directory "{target_workdir}"',
                'else',
                '  echo "[safe]" >>~/.gitconfig',
                f'  echo -e "\tdirectory = {target_workdir}" >>~/.gitconfig',
                'fi',
                '',
            ])

        # Configure Xauth, pylint: disable=line-too-long
        if not host:
            script_file.writelines([
                '# Configure Xauthority',
                f'if [ ! -z "${{{Bundle.ENV_DISPLAY_XAUTH_MAGIC_ADD}}}" ] && type xauth >/dev/null 2>&1; then',
                f'  if [ ! -z "${{{Platform.ENV_XAUTHORITY}}}" ] && [ ! -w "${{{Platform.ENV_XAUTHORITY}}}" ]; then',
                '    true',
                '  else',
                f'    xauth -q add ${{{Bundle.ENV_DISPLAY_XAUTH_MAGIC_ADD}}} 2>/dev/null',
                '  fi',
                'fi',
                '',
            ])

        # Prepare before_script/script context
        script_file.subshell_start('before_script/script')
        script_file.configure(
            errors=True,
            verbose=job.options.verbose,
        )

        # Prepare before_script commands
        if len(scripts_before) > 0:
            script_file.write('# Run before_script')
            script_file.subgroup_start()
            script_file.writelines(scripts_before)
            script_file.subgroup_stop()
            script_file.write('')

        # Prepare script commands
        if len(scripts_commands) > 0:
            script_file.write('# Run script')
            script_file.subgroup_start()
            script_file.writelines(scripts_commands)
            script_file.subgroup_stop()
            script_file.write('')
        else:
            script_file.write('# Missing script')
            script_file.write('false')
            script_file.write('')

        # Finish before_script/script context
        script_file.subshell_stop('before_script/script')
        script_file.write('')

        # Get before_script/script result
        script_file.write('# Result')
        script_file.write('result=${?}')
        script_file.write('')

        # Prepare container result
        if not host:
            script_file.writelines([
                '# Result marker',
                f'echo "{self.__MARKER_RESULT}:${{result}}"',
                '',
            ])

        # Prepare debug script commands
        if len(scripts_debug) > 0:
            script_file.subshell_start('debug')
            if job.options.verbose:
                script_file.configure(
                    errors=False,
                    verbose=True,
                )
            script_file.writelines(scripts_debug)
            script_file.subshell_stop('debug')
            script_file.write('')

        # Prepare after_script commands
        if len(scripts_after) > 0:
            script_file.subshell_start('after_script')
            script_file.configure(
                errors=True,
                verbose=job.options.verbose,
            )
            script_file.write('# Run after_script')
            script_file.subgroup_start()
            script_file.writelines(scripts_after)
            script_file.subgroup_stop()
            script_file.subshell_stop('after_script')
            script_file.write('')

        # Prepare container ending
        if not host:
            script_file.writelines([
                '# Ending marker',
                f'echo "{self.__MARKER_ENDING}"',
                '',
            ])

        # Prepare execution result
        script_file.writelines([
            '# Exit',
            'exit "${result}"',
            '',
        ])

        # Prepare script execution
        script_stat = stat(script_file.name)
        chmod(script_file.name, script_stat.st_mode | S_IXUSR | S_IXGRP
              | S_IRGRP | S_IROTH | S_IXOTH)
        script_file.close()

        # Print script contents
        if self.__options.scripts:
            script_file.print()
            return True

        # Store environment
        _environ = dict(environ)

        # Acquire job data
        env_builds_path: str = job.options.env_builds_path
        env_job_name: str = job.options.env_job_name
        env_job_name_slug: str = job.options.env_job_name_slug
        env_job_path: str = job.options.env_job_path
        variables = job.variables.copy()

        # Configure job settings
        environ[env_builds_path] = target_parent
        environ[env_job_name] = job.name
        environ[env_job_name_slug] = regex_sub(
            r'[^a-z0-9]',
            '-',
            job.name.lower()[0:63],
        ).strip('-')
        environ[env_job_path] = target_project
        environ[Bundle.ENV_LOCAL] = 'true'
        environ[Bundle.ENV_PROJECT_NAME] = Paths.basename(target_project)
        environ[Bundle.ENV_PROJECT_NAMESPACE] = Paths.basename(target_parent)

        # Prepare Git environment
        git: Git = Git()

        # Configure Git variables
        if Bundle.ENV_COMMIT_REF_NAME in variables:
            environ[Bundle.ENV_COMMIT_REF_NAME] = variables[Bundle.ENV_COMMIT_REF_NAME]
        else:
            environ[Bundle.ENV_COMMIT_REF_NAME] = git.head_reference_name(path_project)
        if Bundle.ENV_COMMIT_REF_SLUG in variables:
            environ[Bundle.ENV_COMMIT_REF_SLUG] = variables[Bundle.ENV_COMMIT_REF_SLUG]
        else:
            environ[Bundle.ENV_COMMIT_REF_SLUG] = git.head_reference_slug(
                path_project, name=environ[Bundle.ENV_COMMIT_REF_NAME])
        if Bundle.ENV_COMMIT_SHA in variables:
            environ[Bundle.ENV_COMMIT_SHA] = variables[Bundle.ENV_COMMIT_SHA]
        else:
            environ[Bundle.ENV_COMMIT_SHA] = git.head_revision_hash(path_project)
        if Bundle.ENV_COMMIT_SHORT_SHA1 in variables:
            environ[Bundle.ENV_COMMIT_SHORT_SHA1] = variables[
                Bundle.ENV_COMMIT_SHORT_SHA1]
        else:
            environ[Bundle.ENV_COMMIT_SHORT_SHA1] = git.head_revision_short_hash(
                path_project)
        if Bundle.ENV_DEFAULT_BRANCH in variables:
            environ[Bundle.ENV_DEFAULT_BRANCH] = variables[Bundle.ENV_DEFAULT_BRANCH]
        else:
            environ[Bundle.ENV_DEFAULT_BRANCH] = git.branch_default(path_project)

        # Prepare network
        network = ''
        if self.__options.network:
            network = self.__options.network
            variables[Bundle.FLAG_NETWORK] = network
        elif Bundle.FLAG_NETWORK in variables:
            network = variables[Bundle.FLAG_NETWORK]
            variables[Bundle.FLAG_NETWORK] = network

        # Prepare privileged
        privileged = Flags.check_bool(
            option=self.__options.privileged,
            flag=Bundle.FLAG_PRIVILEGED,
            variables=variables,
            default=privileged_default(),
        )
        variables[Bundle.FLAG_PRIVILEGED] = Flags.string(privileged)

        # Prepare user variables
        environ[Bundle.ENV_USER_HOST_GID] = str(Platform.getgid())
        environ[Bundle.ENV_USER_HOST_UID] = str(Platform.getuid())
        environ[Bundle.ENV_USER_HOST_USERNAME] = Platform.getusername()

        # Prepare CI variables
        for variable in [
                env_builds_path,
                env_job_name,
                env_job_name_slug,
                env_job_path,
                Bundle.ENV_COMMIT_REF_NAME,
                Bundle.ENV_COMMIT_REF_SLUG,
                Bundle.ENV_COMMIT_SHA,
                Bundle.ENV_COMMIT_SHORT_SHA1,
                Bundle.ENV_DEFAULT_BRANCH,
                Bundle.ENV_LOCAL,
                Bundle.ENV_PROJECT_NAME,
                Bundle.ENV_PROJECT_NAMESPACE,
                Bundle.ENV_USER_HOST_GID,
                Bundle.ENV_USER_HOST_UID,
                Bundle.ENV_USER_HOST_USERNAME,
        ]:
            if variable not in variables:
                variables[variable] = environ[variable]

        # Prepare job variables
        for variable in variables:
            variables[variable] = Environment.expand(variables[variable])

        # Prepare environment
        environ.update(variables)

        # Prepare job variables
        for variable in variables:
            variables[variable] = Environment.expand(
                variables[variable],
                variable=variable,
                unknowns=True,
            )

        # Restore environment
        environ.clear()
        environ.update(_environ)

        # Container execution
        if not host:
            result = self.__run_container(
                engine=engine,
                variables=variables,
                path_parent=path_parent,
                target_parent=target_parent,
                image=image,
                job=job,
                script_file=script_file,
                entrypoint=job.entrypoint,
                network=network,
                privileged=privileged,
                target_workdir=target_workdir,
                last_result=last_result,
                result=result,
            )

        # Native execution
        else:
            result = self.__run_native(
                variables=variables,
                entrypoint=job.entrypoint,
                script_file=script_file,
                job=job,
                last_result=last_result,
                result=result,
            )

        # Update job history
        job_history.result = result

        # Update interacted flag
        if not pipeline_history.interacted and self.__interrupted:
            pipeline_history.interacted = True

        # Update interrupted flag
        job_history.interrupted = self.__interrupted

        # Separator
        print(' ')
        Platform.flush()

        # Footer
        if not quiet:
            job_history.footer()

        # Allowed failure result
        if job.when not in [
                'on_failure',
                'always',
        ] and not result and job.allow_failure:
            result = True

        # Result
        return result
