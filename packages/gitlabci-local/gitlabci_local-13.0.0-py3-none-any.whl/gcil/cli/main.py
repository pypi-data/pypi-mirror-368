#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    _MutuallyExclusiveGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
    SUPPRESS,
)
from os import environ
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..engines.engine import supported as engine_supported, privileged_default
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 23

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    group: _ArgumentGroup
    result: Entrypoint.Result
    subgroup: _MutuallyExclusiveGroup

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
        add_help=False,
        formatter_class=lambda prog: RawTextHelpFormatter(
            prog,
            max_help_position=HELP_POSITION,
            width=min(
                120,
                get_terminal_size().columns - 2,
            ),
        ),
    )

    # Arguments internal definitions
    group = parser.add_argument_group('internal arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '--version',
        dest='version',
        action='store_true',
        help='Show the current version',
    )
    group.add_argument(
        '--no-color',
        dest='no_color',
        action='store_true',
        help=f'Disable colors outputs with \'{Bundle.ENV_NO_COLOR}=1\'\n'
        '(or default settings: [themes] > no_color)',
    )
    group.add_argument(
        '--update-check',
        dest='update_check',
        action='store_true',
        help='Check for newer package updates',
    )
    group.add_argument(
        '--settings',
        dest='settings',
        action='store_true',
        help='Show the current settings path and contents',
    )
    group.add_argument(
        '--set',
        dest='set',
        action='store',
        metavar=('GROUP', 'KEY', 'VAL'),
        nargs=3,
        help='Set settings specific \'VAL\' value to [GROUP] > KEY\n' \
             'or unset by using \'UNSET\' as \'VAL\'',
    )

    # Arguments pipeline definitions
    group = parser.add_argument_group('pipeline arguments')
    group.add_argument(
        '-p',
        '--pipeline',
        dest='pipeline',
        action='store_true',
        help='Automatically run pipeline stages rather than jobs',
    )
    group.add_argument(
        '-q',
        '--quiet',
        dest='quiet',
        action='store_true',
        help='Hide jobs execution context',
    )
    group.add_argument(
        '-c',
        dest='configuration',
        action='store',
        default=Bundle.CONFIGURATION,
        help=f'Path to the {Bundle.CONFIGURATION} configuration file or folder',
    )
    group.add_argument(
        '-B',
        '--no-before',
        dest='before',
        action='store_false',
        help='Disable before_script executions',
    )
    group.add_argument(
        '-A',
        '--no-after',
        dest='after',
        action='store_false',
        help='Disable after_script executions',
    )
    group.add_argument(
        '-C',
        dest='commands',
        action='store',
        help='Run specific commands instead of "scripts" commands',
    )
    group.add_argument(
        '-n', dest='network', action='store', help=
        f'Configure the network mode used (or define {Bundle.FLAG_NETWORK})\n' \
            f"Choices: {', '.join(Bundle.ARGUMENT_NETWORKS_ENUM)}. " \
            f'Default: {Bundle.ARGUMENT_NETWORKS_ENUM[0]}'
    )
    group.add_argument(
        '-e',
        dest='env',
        action='append',
        help='Define VARIABLE=value, pass VARIABLE or ENV file',
    )
    group.add_argument(
        '-E', dest='engine', action='store', help=
        f'Force a specific engine (or define {Bundle.FLAG_ENGINE})\n' \
            f"Default list: {','.join(engine_supported())}"
    )
    group.add_argument(
        '-H',
        '--host',
        dest='host',
        action='store_true',
        help=f'Run jobs on the host rather than containers (or define {Bundle.FLAG_HOST})',
    )
    group.add_argument(
        '--notify',
        dest='notify',
        action='store_true',
        help='Enable host notifications of pipeline and jobs results',
    )
    group.add_argument(
        '--privileged',
        dest='privileged',
        action='store',
        metavar='BOOL',
        nargs='?',
        const='true' if privileged_default() else 'false',
        help='Give extended privileges to the containers\n'
        f'(Defaults to \'%(const)s\', or define {Bundle.FLAG_PRIVILEGED})',
    )
    group.add_argument(
        '--random-paths',
        dest='random_paths',
        action='store_true',
        help='Mount random folder paths in the container',
    )
    group.add_argument(
        '-r',
        '--real-paths',
        dest='real_paths',
        action='store_true',
        help='Mount real folder paths in the container (Linux / macOS only)',
    )
    group.add_argument(
        '-S',
        '--sockets',
        dest='sockets',
        action='store_true',
        help='Mount engine sockets for nested containers\n'
        '(Enabled by default with services: docker:*dind)',
    )
    group.add_argument(
        '--ssh',
        dest='ssh',
        action='store',
        metavar='SSH_USER',
        nargs='?',
        const=Bundle.ARGUMENT_SSH_USER_DEFAULT,
        help='Bind SSH credentials to a container\'s user',
    )
    group.add_argument(
        '-v',
        dest='volume',
        action='append',
        help='Mount VOLUME or HOST:TARGET in containers',
    )
    group.add_argument(
        '-w',
        dest='workdir',
        action='store',
        help='Override the container\'s working path',
    )

    # Arguments debugging definitions
    group = parser.add_argument_group('debugging arguments')
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--bash',
        dest='bash',
        action='store_true',
        help='Prepare runners for manual bash purposes',
    )
    subgroup.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='Keep runners active for debugging purposes',
    )
    group.add_argument(
        '--display',
        dest='display',
        action='store_true',
        help='Enable host DISPLAY forwarding features',
    )
    group.add_argument(
        '--shell',
        dest='shell',
        action='store',
        help='Configure the default bash/debug shell entrypoint',
    )

    # Arguments jobs definitions
    group = parser.add_argument_group('jobs arguments')
    group.add_argument(
        '--all',
        dest='all',
        action='store_true',
        help='Enable all jobs by default in selections',
    )
    group.add_argument(
        '--configure',
        dest='configure',
        action='store_true',
        help='Show interactive configurations for CI/CD inputs',
    )
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--input',
        dest='input',
        action='append',
        metavar='KEY=VAL',
        help='Define KEY=value for CI/CD inputs',
    )
    group.add_argument(
        '-f',
        '--force',
        dest='force',
        action='store_true',
        help='Force the action (use with --pull)',
    )
    group.add_argument(
        '-i',
        '--ignore-case',
        dest='ignore_case',
        action='store_true',
        help='Ignore case when searching for names',
    )
    group.add_argument(
        '-m',
        '--manual',
        dest='manual',
        action='store_true',
        help='Allow manual jobs to be used',
    )
    group.add_argument(
        '--no-console',
        dest='no_console',
        action='store_true',
        help='Disable console launch in bash/debug modes\n'
        '(or default settings: [runner] > no_console)',
    )
    group.add_argument(
        '--no-git-safeties',
        dest='no_git_safeties',
        action='store_true',
        help='Disable automated Git safeties configuration\n'
        '(or default settings: [runner] > no_git_safeties)',
    )
    group.add_argument(
        '--no-script-fail',
        dest='no_script_fail',
        action='store_true',
        help='Fail on missing \'script\' nodes of jobs\n'
        '(or default settings: [runner] > no_script_fail)',
    )
    group.add_argument(
        '-R',
        '--no-regex',
        dest='no_regex',
        action='store_true',
        help='Disable regex search of names',
    )
    group.add_argument(
        '--no-verbose',
        dest='no_verbose',
        action='store_true',
        help='Hide jobs verbose outputs',
    )
    group.add_argument(
        '--scripts',
        dest='scripts',
        action='store_true',
        help='Dump parsed jobs entrypoint scripts',
    )
    group.add_argument(
        '-t', dest='tags', action='store', help=
        f"Handle listed tags as manual jobs\nDefault list: {','.join(Bundle.ARGUMENT_TAGS_DEFAULT)}"
    )

    # Arguments features definitions
    group = parser.add_argument_group('features arguments')
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '-d',
        '--dump',
        dest='dump',
        action='store_true',
        help=f'Dump parsed {Bundle.CONFIGURATION} configuration',
    )
    subgroup.add_argument(
        '-s',
        '--select',
        dest='select',
        action='store_true',
        help='Force jobs selection from enumerated names',
    )
    subgroup.add_argument(
        '-l',
        '--list',
        dest='list',
        action='store_true',
        help='Select one job to run (implies --manual)',
    )
    subgroup.add_argument(
        '--pull',
        dest='pull',
        action='store_true',
        help='Pull container images from all jobs',
    )
    subgroup.add_argument(
        '--rmi',
        dest='rmi',
        action='store_true',
        help='Delete container images from all jobs',
    )

    # Arguments hidden definitions
    group = parser.add_argument_group('hidden arguments')
    group.add_argument(
        '--engine-default',
        dest='engine_default',
        action='store_true',
        help=SUPPRESS,
    )
    group.add_argument(
        '--image',
        dest='image',
        action='store',
        help=SUPPRESS,
    )
    group.add_argument(
        '--tags-default',
        dest='tags_default',
        action='store_true',
        help=SUPPRESS,
    )

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument(
        '--',
        dest='double_dash',
        action='store_true',
        help='Positional arguments separator (recommended)',
    )
    group.add_argument(
        'names',
        nargs='*',
        help='Names of specific jobs (or stages with --pipeline)\n'
        'Regex names is supported unless --no-regex is used',
    )

    # Arguments parser
    options: Namespace = parser.parse_args()

    # Help informations
    if options.help:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(0)

    # Instantiate settings
    settings: Settings = Settings(name=Bundle.NAME)

    # Prepare no_color
    if not options.no_color:
        if settings.has('themes', 'no_color'):
            options.no_color = settings.get_bool('themes', 'no_color')
        else:
            options.no_color = False
            settings.set_bool('themes', 'no_color', options.no_color)

    # Configure no_color
    if options.no_color:
        environ[Bundle.ENV_FORCE_COLOR] = '0'
        environ[Bundle.ENV_NO_COLOR] = '1'

    # Prepare colors
    Colors.prepare()

    # Settings setter
    if options.set:
        settings.set(options.set[0], options.set[1], options.set[2])
        settings.show()
        sys_exit(0)

    # Settings informations
    if options.settings:
        settings.show()
        sys_exit(0)

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.PACKAGE,
        settings=settings,
    )

    # Version informations
    if options.version:
        print(
            f'{Bundle.NAME} {Version.get()} from {Version.path()} (python {Version.python()})'
        )
        Platform.flush()
        sys_exit(0)

    # Check for current updates
    if options.update_check:
        if not updates.check():
            updates.check(older=True)
        sys_exit(0)

    # CLI entrypoint
    result = Entrypoint.cli(
        options,
        settings,
    )

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Result
    if result in [
            Entrypoint.Result.SUCCESS,
            Entrypoint.Result.FINALIZE,
    ]:
        sys_exit(0)
    else:
        sys_exit(1)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
