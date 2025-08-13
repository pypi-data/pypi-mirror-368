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
from pathlib import Path
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from ..types.environments import Environments
from ..types.gitlab import MigrationEntities
from ..types.paths import Paths
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 29

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    environments: Environments
    group: _ArgumentGroup
    result: Entrypoint.Result = Entrypoint.Result.ERROR
    subgroup: _MutuallyExclusiveGroup

    # Configure environment variables
    environments = Environments()
    environments.group = 'environment variables'
    environments.add(
        'gitlab_input_token',
        Bundle.ENV_GITLAB_INPUT_TOKEN,
        'Input GitLab API token environment variable',
        Bundle.ENV_GITLAB_TOKEN,
    )
    environments.add(
        'gitlab_output_token',
        Bundle.ENV_GITLAB_OUTPUT_TOKEN,
        'Output GitLab API token environment variable',
        Bundle.ENV_GITLAB_TOKEN,
    )
    environments.add(
        'ci_job_token',
        Bundle.ENV_CI_JOB_TOKEN,
        'GitLab CI job token environment variable (CI only)',
    )

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
        epilog=environments.help(HELP_POSITION),
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

    # Arguments credentials definitions
    group = parser.add_argument_group('credentials arguments')
    group.add_argument(
        '-c',
        '--config',
        dest='configs',
        action='append',
        metavar='FILES',
        help=f'Python GitLab configuration files'
        f' (default: {Bundle.ENV_PYTHON_GITLAB_CFG} environment)',
    )

    # Arguments migration definitions
    group = parser.add_argument_group('migration arguments')
    group.add_argument(
        '--archive-exports',
        dest='archive_exports',
        action='store',
        metavar='FOLDER',
        help='Store exported projects and groups to a folder',
    )
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '--archive-sources',
        dest='archive_sources',
        action='store_true',
        help='Archive sources after successful migration',
    )
    subgroup.add_argument(
        '--delete-sources',
        dest='delete_sources',
        action='store_true',
        help='Delete sources after successful migration',
    )
    group.add_argument(
        '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Enable dry run mode to check without saving',
    )
    group.add_argument(
        '--exclude-group',
        dest='exclude_group',
        action='store_true',
        help='Exclude parent group migration',
    )
    group.add_argument(
        '--exclude-subgroups',
        dest='exclude_subgroups',
        action='store_true',
        help='Exclude children subgroups migration',
    )
    group.add_argument(
        '--exclude-projects',
        dest='exclude_projects',
        action='store_true',
        help='Exclude children projects migration',
    )
    group.add_argument(
        '--flatten-group',
        dest='flatten_group',
        action='store_true',
        help='Flatten group projects upon migration',
    )
    group.add_argument(
        '--migrate-packages',
        dest='migrate_packages',
        action='store_true',
        help='Migrate input GitLab Packages to output GitLab projects',
    )
    group.add_argument(
        '--confirm',
        dest='confirm',
        action='store_true',
        help='Automatically confirm all removal and contents warnings',
    )
    group.add_argument(
        '--overwrite',
        dest='overwrite',
        action='store_true',
        help='Overwrite existing projects on output GitLab',
    )
    group.add_argument(
        '--rename-project',
        dest='rename_project',
        action='store',
        metavar='NAME',
        help='Rename GitLab output project (only for single input project)',
    )
    group.add_argument(
        '--normalize-names',
        dest='normalize_names',
        action='store_true',
        help='Normalize GitLab output group and project names',
    )
    group.add_argument(
        '--available-entities',
        dest='available_entities',
        action='store_true',
        help='List the available GitLab export/import entities known by the tool',
    )
    group.add_argument(
        '--reset-entities',
        dest='reset_entities',
        default=','.join(MigrationEntities.defaults()),
        metavar='ENTITIES',
        help='List of GitLab export/import entities to reset separated by ","'
        ' (default: %(default)s)',
    )

    # Arguments general settings definitions
    group = parser.add_argument_group('general settings arguments')
    group.add_argument(
        '--set-avatar',
        dest='set_avatar',
        action='store',
        metavar='FILE',
        help='Set avatar of GitLab output projects and groups',
    )
    group.add_argument(
        '--update-descriptions',
        dest='update_description',
        action='store_true',
        help='Update description of GitLab output projects and groups automatically',
    )

    # Arguments hidden definitions
    group = parser.add_argument_group('hidden arguments')
    group.add_argument(
        '--archive-exports-dir',
        dest='archive_exports_dir',
        action='store',
        default=None,
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
        dest='input_url_path',
        action='store',
        nargs='?',
        help='Input GitLab group or project path URL',
    )
    group.add_argument(
        dest='output_url_namespace',
        action='store',
        nargs='?',
        help='Output GitLab group or user namespace URL',
    )
    group.add_argument(
        dest='rename_project_positional',
        action='store',
        nargs='?',
        metavar='rename_single_project',
        help='Rename GitLab output project (only for single input project)',
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

    # Adapt rename project arguments
    if options.rename_project_positional and not options.rename_project:
        options.rename_project = options.rename_project_positional

    # Arguments validation
    if options.input_url_path and not options.output_url_namespace and (
            options.archive_exports # Export input to archives
            or options.archive_sources # Archive input sources
            or options.delete_sources # Delete input sources
    ):
        pass
    elif not options.input_url_path or not options.output_url_namespace:
        result = Entrypoint.Result.CRITICAL

    # Prepare archive exports
    if options.archive_exports:
        options.archive_exports_dir = Paths.resolve(Path('.') / options.archive_exports)
        Path(options.archive_exports_dir).mkdir(parents=True, exist_ok=True)

    # Header
    print(' ')
    Platform.flush()

    # Tool identifier
    if result != Entrypoint.Result.CRITICAL:
        print(f'{Colors.BOLD} {Bundle.NAME}'
              f'{Colors.YELLOW_LIGHT} ({Version.get()})'
              f'{Colors.RESET}')
        Platform.flush()

    # CLI entrypoint
    if result != Entrypoint.Result.CRITICAL:
        result = Entrypoint.cli(
            options,
            environments,
        )

    # CLI helper
    else:
        parser.print_help()

    # Footer
    print(' ')
    Platform.flush()

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
