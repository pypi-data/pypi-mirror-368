#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
import re
from tempfile import NamedTemporaryFile
from typing import List, NamedTuple, Optional, Union
import urllib.parse

# Modules libraries
from gitlab.config import ConfigError, GitlabConfigParser
from gitlab.exceptions import (
    GitlabGetError,
    GitlabListError,
)
from gitlab.v4.objects import (
    Group as GitLabGroup,
    GroupProject as GitLabGroupProject,
    Namespace as GitLabNamespace,
    Project as GitLabProject,
    ProjectImport as GitLabProjectImport,
    User as GitLabUser,
    UserProject as GitLabUserProject,
)
import questionary

# Components
from ..features.gitlab import GitLabFeature
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..prints.themes import Themes
from ..system.platform import Platform
from ..types.environments import Environments
from ..types.humanize import Humanize
from ..types.gitlab import MigrationEntities
from ..types.namespaces import Namespaces
from ..types.paths import Paths

# Entrypoint class, pylint: disable=too-many-lines,too-few-public-methods,too-many-nested-blocks,too-many-statements
class Entrypoint:

    # Constants
    EXPORTS_PREFIX: str = f'{Bundle.NAME}-exports-'
    PACKAGES_PREFIX: str = f'{Bundle.NAME}-packages-'

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
        environments: Environments,
    ) -> Result:

        # Variables
        changed: bool = False
        input_gitlab: GitLabFeature
        input_group: Optional[GitLabGroup] = None
        input_project: Optional[GitLabProject] = None
        input_user: Optional[GitLabUser] = None
        output_enabled: bool = bool(options.output_url_namespace)
        output_exists: bool = False
        output_gitlab: Optional[GitLabFeature] = None
        output_gitlab_id: str
        output_gitlab_namespace: str = ''
        output_gitlab_url: str
        output_namespace: Optional[GitLabNamespace] = None
        progress_count: int
        progress_index: int
        project: Union[GitLabGroupProject, GitLabUserProject]
        projects: Union[List[GitLabGroupProject], List[GitLabUserProject]]
        result: Entrypoint.Result

        # Header
        print(' ')

        # Parse input URL variables
        input_gitlab_splits: urllib.parse.SplitResult = urllib.parse.urlsplit(
            options.input_url_path)
        input_gitlab_id: str = f'{input_gitlab_splits.netloc}'
        input_gitlab_url: str = f'{input_gitlab_splits.scheme}://{input_gitlab_splits.netloc}'
        input_gitlab_path: str = input_gitlab_splits.path.lstrip('/')

        # Parse output URL variables
        if output_enabled:
            output_gitlab_splits: urllib.parse.SplitResult = urllib.parse.urlsplit(
                options.output_url_namespace)
            output_gitlab_id = f'{output_gitlab_splits.netloc}'
            output_gitlab_url = f'{output_gitlab_splits.scheme}://{output_gitlab_splits.netloc}'
            output_gitlab_namespace = output_gitlab_splits.path.lstrip('/')

        # Prepare credentials
        input_private_token: str = environments.value('gitlab_input_token')
        output_private_token: str = environments.value('gitlab_output_token')
        job_token: str = environments.value('ci_job_token')
        input_ssl_verify: Union[bool, str] = True
        output_ssl_verify: Union[bool, str] = True

        # Parse configuration files
        try:
            input_config: GitlabConfigParser
            if not input_private_token:
                input_config = GitlabConfigParser(input_gitlab_id, options.configs)
                input_private_token = str(input_config.private_token)
                if input_ssl_verify and (not input_config.ssl_verify
                                         or isinstance(input_config.ssl_verify, str)):
                    input_ssl_verify = input_config.ssl_verify
            output_config: GitlabConfigParser
            if not output_private_token and output_enabled:
                output_config = GitlabConfigParser(output_gitlab_id, options.configs)
                output_private_token = str(output_config.private_token)
                if output_ssl_verify and (not output_config.ssl_verify
                                          or isinstance(output_config.ssl_verify, str)):
                    output_ssl_verify = output_config.ssl_verify
        except ConfigError as e:
            print(str(e))

        # Input client
        input_gitlab = GitLabFeature(
            url=input_gitlab_url,
            private_token=input_private_token,
            job_token=job_token,
            ssl_verify=input_ssl_verify,
            dry_run=options.dry_run,
        )
        print(f'{Colors.BOLD} - GitLab input: '
              f'{Colors.GREEN}{input_gitlab.url}'
              f'{Colors.CYAN} ({input_gitlab.username})'
              f'{Colors.RESET}')
        Platform.flush()

        # Output client
        if output_enabled:
            output_gitlab = GitLabFeature(
                url=output_gitlab_url,
                private_token=output_private_token,
                job_token=job_token,
                ssl_verify=output_ssl_verify,
                dry_run=options.dry_run,
            )
            print(f'{Colors.BOLD} - GitLab output: '
                  f'{Colors.GREEN}{output_gitlab.url}'
                  f'{Colors.CYAN} ({output_gitlab.username})'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()

        # Input path
        try:
            input_group = input_gitlab.group(input_gitlab_path)
            print(f'{Colors.BOLD} - GitLab input group: '
                  f'{Colors.GREEN}{input_group.full_path}'
                  f'{Colors.CYAN} # {Namespaces.text(input_group.description)}'
                  f'{Colors.RESET}')
            Platform.flush()
        except GitlabGetError as exception:
            try:
                if '/' in input_gitlab_path:
                    raise TypeError from exception
                input_user = input_gitlab.user(input_gitlab_path)
                input_namespace = input_gitlab.namespace(input_gitlab_path)
                print(f'{Colors.BOLD} - GitLab input user namespace: '
                      f'{Colors.GREEN}{input_namespace.full_path}'
                      f'{Colors.CYAN} # {input_namespace.name}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
            except (GitlabGetError, TypeError):
                input_project = input_gitlab.project(input_gitlab_path)
                print(f'{Colors.BOLD} - GitLab input project: '
                      f'{Colors.GREEN}{input_project.path_with_namespace}'
                      f'{Colors.CYAN} # {Namespaces.text(input_project.description)}'
                      f'{Colors.RESET}')
                Platform.flush()

        # Output group
        if output_enabled:
            assert output_gitlab
            try:
                output_exists = False
                output_group = output_gitlab.group(output_gitlab_namespace)
                output_namespace = output_gitlab.namespace(output_gitlab_namespace)
                output_exists = True
                print(f'{Colors.BOLD} - GitLab output group: '
                      f'{Colors.GREEN}{output_group.full_path}'
                      f'{Colors.CYAN} # {Namespaces.text(output_group.description)}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()

            # Output namespace
            except GitlabGetError as exception:
                try:
                    if '/' in output_gitlab_namespace:
                        raise TypeError from exception
                    _output_user = output_gitlab.user(output_gitlab_namespace)
                    output_namespace = output_gitlab.namespace(output_gitlab_namespace)
                    output_exists = True
                    print(f'{Colors.BOLD} - GitLab output user namespace: '
                          f'{Colors.GREEN}{output_namespace.full_path}'
                          f'{Colors.CYAN} # {output_namespace.name}'
                          f'{Colors.RESET}')
                    print(' ')
                    Platform.flush()

                # Output parent group
                except (GitlabGetError, TypeError): # pylint: disable=raise-missing-from

                    # Validate options
                    if (not input_group and not input_user) or options.exclude_group:
                        raise exception

                    # Missing output group
                    print(f'{Colors.BOLD} - GitLab output group: '
                          f'{Colors.GREEN}{output_gitlab_namespace}'
                          f'{Colors.RED} (Non-existent output group)'
                          f'{Colors.RESET}')
                    print(' ')
                    Platform.flush()

        # Validate options
        if options.rename_project and not input_project:
            raise RuntimeError(
                'Renaming project is only allowed with a single input project')

        # Handle available features
        if options.available_entities:
            print(f'{Colors.BOLD} - GitLab project:'
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}   - Available entities: '
                  f'{Colors.CYAN}\'{", ".join(MigrationEntities.entities())}\''
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}   - Available removers: '
                  f'{Colors.CYAN}\'{", ".join(MigrationEntities.removers())}\''
                  f'{Colors.RESET}')
            print(f'{Colors.BOLD}   - Available templates: '
                  f'{Colors.CYAN}\'{", ".join(MigrationEntities.templates())}\''
                  f'{Colors.RESET}')
            Platform.flush()
            return Entrypoint.Result.FINALIZE

        # Handle single project
        if input_project:

            # Validate types
            if output_enabled:
                assert output_gitlab
                assert output_namespace

            # Handle project
            Entrypoint.project(
                options,
                input_gitlab,
                output_gitlab,
                input_project.path_with_namespace,
                input_project.namespace['id'],
                output_namespace.full_path if output_namespace else '',
                output_gitlab_namespace,
                options.rename_project,
                1,
                1,
            )

            # Handle sources
            if options.archive_sources or options.delete_sources:
                print(f'{Colors.BOLD} - GitLab input project: '
                      f'{Colors.GREEN}{input_project.path_with_namespace}'
                      f'{Colors.CYAN} # {Namespaces.text(input_project.description)}'
                      f'{Colors.RESET}')
                Platform.flush()

                # Archive input project
                if options.archive_sources:
                    changed = input_gitlab.project_set_archive(
                        input_project.path_with_namespace,
                        enabled=True,
                    )
                    print(f'{Colors.BOLD}   - Archive sources project: '
                          f'{Colors.CYAN if changed else Colors.GREEN}'
                          f'{"Success" if changed else "Already done"}'
                          f'{Colors.RESET}')
                    print(' ')
                    Platform.flush()

                # Delete input project
                elif options.delete_sources:

                    # Confirm project deletion
                    if not Entrypoint.confirm(
                            'Delete project',
                            input_project.path_with_namespace,
                            not options.confirm,
                            'deletion',
                    ):
                        raise PermissionError()

                    # Delete input project
                    input_gitlab.project_delete(input_project.path_with_namespace)
                    print(f'{Colors.BOLD}   - Delete sources project: '
                          f'{Colors.GREEN}Success'
                          f'{Colors.RESET}')
                    print(' ')
                    Platform.flush()

        # Handle group recursively
        elif input_group:

            # Handle group if missing
            if not options.exclude_group:
                result = Entrypoint.group(
                    options,
                    input_gitlab,
                    output_gitlab,
                    input_group.full_path,
                    output_gitlab_namespace,
                    migration=not output_exists,
                )
                if result in [
                        Entrypoint.Result.FINALIZE,
                        Entrypoint.Result.ERROR,
                ]:
                    return result

                # Acquire output namespace
                if output_gitlab:
                    output_namespace = output_gitlab.namespace(
                        output_gitlab_namespace,
                        optional=True,
                    )

            # Validate types
            if output_enabled:
                assert output_gitlab
                assert output_namespace

            # Iterate through subgroups
            if output_gitlab and not options.exclude_subgroups and not options.flatten_group \
                    or not output_exists:
                input_subgroups = sorted(
                    input_group.descendant_groups.list(
                        get_all=True,
                        # include_subgroups=True,
                        order_by='path',
                        sort='asc',
                    ),
                    key=lambda item: item.full_path,
                )
                progress_count = len(input_subgroups)
                progress_index = 0
                for input_subgroup in input_subgroups:
                    progress_index += 1
                    result = Entrypoint.subgroup(
                        options,
                        input_gitlab,
                        output_gitlab,
                        input_group.full_path,
                        input_subgroup.full_path,
                        output_namespace.full_path if output_namespace else '',
                        migration=output_exists,
                        progress_index=progress_index,
                        progress_count=progress_count,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

            # Iterate through projects
            if not options.exclude_projects:
                projects = sorted(
                    input_group.projects.list(
                        get_all=True,
                        with_shared=False,
                        include_subgroups=not options.exclude_subgroups,
                        order_by='path',
                        sort='asc',
                    ),
                    key=lambda item: item.path_with_namespace,
                )
                progress_count = len(projects)
                progress_index = 0
                for project in projects:
                    progress_index += 1
                    result = Entrypoint.project(
                        options,
                        input_gitlab,
                        output_gitlab,
                        project.path_with_namespace,
                        input_group.full_path,
                        output_namespace.full_path if output_namespace else '',
                        output_gitlab_namespace,
                        progress_index=progress_index,
                        progress_count=progress_count,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

                    # Archive input project
                    if options.archive_sources:
                        changed = input_gitlab.project_set_archive(
                            project.path_with_namespace,
                            enabled=True,
                        )
                        print(f'{Colors.BOLD} - GitLab input project: '
                              f'{Colors.YELLOW_LIGHT}{project.path_with_namespace}'
                              f'{Colors.CYAN} # {Namespaces.text(project.description)}'
                              f'{Colors.RESET}')
                        print(f'{Colors.BOLD}   - Archive sources project: '
                              f'{Colors.CYAN if changed else Colors.GREEN}'
                              f'{"Success" if changed else "Already done"}'
                              f'{Colors.RESET}')
                        print(' ')
                        Platform.flush()

            # Delete input group after validation
            if options.delete_sources:
                print(f'{Colors.BOLD} - GitLab input group: '
                      f'{Colors.GREEN}{input_group.full_path}'
                      f'{Colors.CYAN} # {Namespaces.text(input_group.description)}'
                      f'{Colors.RESET}')
                Platform.flush()
                if not Entrypoint.confirm(
                        'Delete group',
                        input_group.full_path,
                        not options.confirm,
                        'deletion',
                ):
                    raise PermissionError()

                # Delete input group
                input_gitlab.group_delete(input_group.full_path)
                print(f'{Colors.BOLD}   - Delete sources group: '
                      f'{Colors.GREEN}Success'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()

        # Handle user
        elif input_user:

            # Validate types
            if output_enabled:
                assert output_gitlab
                assert output_namespace

            # Iterate through projects
            if not options.exclude_projects:
                projects = sorted(
                    input_user.projects.list(
                        get_all=True,
                        order_by='path',
                        sort='asc',
                    ),
                    key=lambda item: item.path_with_namespace,
                )
                progress_count = len(projects)
                progress_index = 0
                for project in projects:
                    progress_index += 1
                    result = Entrypoint.project(
                        options,
                        input_gitlab,
                        output_gitlab,
                        project.path_with_namespace,
                        input_namespace.full_path,
                        output_namespace.full_path if output_namespace else '',
                        output_gitlab_namespace,
                        progress_index=progress_index,
                        progress_count=progress_count,
                    )
                    if result in [
                            Entrypoint.Result.FINALIZE,
                            Entrypoint.Result.ERROR,
                    ]:
                        return result

                    # Handle sources
                    if options.archive_sources or options.delete_sources:
                        print(f'{Colors.BOLD} - GitLab input project: '
                              f'{Colors.GREEN}{project.path_with_namespace}'
                              f'{Colors.CYAN} # {Namespaces.text(project.description)}'
                              f'{Colors.RESET}')
                        Platform.flush()

                        # Archive input project
                        if options.archive_sources:
                            changed = input_gitlab.project_set_archive(
                                project.path_with_namespace,
                                enabled=True,
                            )
                            print(f'{Colors.BOLD}   - Archive sources project: '
                                  f'{Colors.CYAN if changed else Colors.GREEN}'
                                  f'{"Success" if changed else "Already done"}'
                                  f'{Colors.RESET}')
                            print(' ')
                            Platform.flush()

                        # Delete input project
                        elif options.delete_sources:

                            # Confirm project deletion
                            if not Entrypoint.confirm(
                                    'Delete project',
                                    project.path_with_namespace,
                                    not options.confirm,
                                    'deletion',
                            ):
                                print(' ')
                                Platform.flush()
                                return Entrypoint.Result.SUCCESS

                            # Delete input project
                            input_gitlab.project_delete(project.path_with_namespace)
                            print(f'{Colors.BOLD}   - Delete sources project: '
                                  f'{Colors.GREEN}Success'
                                  f'{Colors.RESET}')
                            print(' ')
                            Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS

    # Confirm
    @staticmethod
    def confirm(
        description: str,
        text: str = '',
        interactive: bool = True,
        action: str = '',
        indent: str = '   ',
    ) -> bool:

        # Header
        print(
            f'{Colors.BOLD}{indent}- {description}{": " if description else ""}Confirm \''
            f'{Colors.RED}{text}'
            f'{Colors.BOLD}\' {action}:'
            f'{Colors.RESET}', end='')
        Platform.flush()

        # Confirm without user interaction
        if not interactive:
            print(f'{Colors.RED} Confirmed by parameters'
                  f'{Colors.RESET}')
            Platform.flush()
            return True

        # Confirm without user input
        if not Platform.IS_TTY_STDIN:
            print(f'{Colors.RED} Confirmed without user input'
                  f'{Colors.RESET}')
            Platform.flush()
            return True

        # Get user configuration
        answer: bool = questionary.confirm(
            message='',
            default=False,
            qmark='',
            style=Themes.confirmation_style(),
            auto_enter=True,
        ).ask()

        # Result
        return answer

    # Group, pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
    @staticmethod
    def group(
        options: Namespace,
        input_gitlab: GitLabFeature,
        output_gitlab: Optional[GitLabFeature],
        criteria_input_group: str,
        criteria_output_group: str,
        migration: bool = True,
    ) -> Result:

        # Variables
        changed: bool
        input_subgroup_allowed: str
        input_subgroup_parent: str
        output_group: Optional[GitLabGroup] = None
        output_namespace: Optional[GitLabNamespace] = None

        # Acquire input group
        input_group = input_gitlab.group(criteria_input_group)
        input_group_namespace, _ = Namespaces.split_namespace(
            criteria_input_group,
            relative=False,
        )

        # Detect group or subgroup
        output_group_namespace, output_group_path = Namespaces.split_namespace(
            criteria_output_group,
            relative=False,
        )

        # Detect identical input and output
        same_namespace: bool = False
        if output_gitlab and input_gitlab.url == output_gitlab.url \
                and input_group_namespace == output_group_namespace:
            same_namespace = True

        # Prepare output group name
        output_group_name = input_group.name \
            if input_group.name != input_group.path and not same_namespace \
            else output_group_path

        # Show group details
        print(f'{Colors.BOLD} - GitLab group: '
              f'{Colors.YELLOW_LIGHT}{input_group.full_path} '
              f'{Colors.CYAN}({Namespaces.text(input_group.description)})'
              f'{Colors.RESET}')
        Platform.flush()

        # Validate subgroup paths
        for input_subgroup in input_group.descendant_groups.list(
                get_all=True,
                order_by='path',
                sort='asc',
                # include_subgroups=True,
        ):
            input_subgroup_allowed = input_subgroup.path.lstrip('-_').rstrip('._')
            input_subgroup_parent = input_subgroup.full_path[:-len(input_subgroup.path)]
            if input_subgroup.path != input_subgroup_allowed:
                print(f'{Colors.RED}   - Incompatible GitLab subgroup path detected: '
                      f'{Colors.CYAN}{input_subgroup.full_path}'
                      f'{Colors.RED} != '
                      f'{Colors.GREEN}{input_subgroup_parent}{input_subgroup_allowed}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                return Entrypoint.Result.ERROR

        # Migration mode
        if output_gitlab and not migration:

            # Existing user
            try:
                if '/' in criteria_output_group:
                    raise TypeError
                _output_user = output_gitlab.user(criteria_output_group)
                output_namespace = output_gitlab.namespace(criteria_output_group)
                print(
                    f'{Colors.BOLD}   - Already existing user namespace in GitLab output: '
                    f'{Colors.GREEN}{output_namespace.full_path}'
                    f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

            # Existing group
            except (GitlabGetError, RuntimeError, TypeError):
                output_group = output_gitlab.group(criteria_output_group)
                print(f'{Colors.BOLD}   - Already existing group in GitLab output: '
                      f'{Colors.GREEN}{output_group.full_path}'
                      f'{Colors.CYAN} # {Namespaces.text(output_group.description)}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

        # Ignore existing names
        if output_gitlab:
            output_group_parent = output_gitlab.group(output_group_namespace)
            if output_group_name in [
                    output_group.name
                    for output_group in output_group_parent.subgroups.list(get_all=True)
            ]:
                print(f'{Colors.RED}   - Already existing group name in GitLab output: '
                      f'{Colors.CYAN}{output_group_name}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                raise RuntimeError()

        # Confirm group is exportable
        export_limitations = input_gitlab.group_export_limitations(input_group.full_path)
        if export_limitations:
            print(f'{Colors.BOLD}   - Limited group export detected: '
                  f'{Colors.RESET}')
            for limitation, items in export_limitations.items():
                (level, values) = items
                if level == GitLabFeature.LIMITATIONS_ERROR:
                    print(f'{Colors.BOLD}     - With data loss: '
                          f'{Colors.RED}{limitation}'
                          + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                          f'{Colors.RESET}')
                else:
                    print(f'{Colors.BOLD}     - With optional custom migration: '
                          f'{Colors.YELLOW_LIGHT}{limitation}'
                          + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                          f'{Colors.RESET}')
            if not options.dry_run and not Entrypoint.confirm(
                    '',
                    input_group.full_path,
                    not options.confirm,
                    'limited group export',
                    indent='     ',
            ):
                raise PermissionError()

        # Export group
        if output_gitlab or options.archive_exports:
            print(f'{Colors.BOLD}   - Exporting from: '
                  f'{Colors.GREEN}{input_group.full_path}'
                  f'{Colors.RESET}')
            Platform.flush()
            with NamedTemporaryFile(
                    prefix=Paths.slugify(f'{Entrypoint.EXPORTS_PREFIX}'
                                         f'-{input_group.full_path}-'),
                    suffix='.tar.gz',
                    dir=options.archive_exports_dir,
                    delete=not options.archive_exports_dir,
            ) as file_export:
                input_gitlab.group_export(
                    file_export.name,
                    input_group.full_path,
                    options.reset_entities,
                )

                # Import group
                if output_gitlab:
                    print(f'{Colors.BOLD}   - Importing to: '
                          f'{Colors.GREEN}{criteria_output_group}'
                          f'{Colors.RESET}')
                    Platform.flush()
                    output_gitlab.group_import(
                        file_export.name,
                        output_group_namespace,
                        output_group_path,
                        output_group_name,
                    )

            # Abort group migration
            if not output_gitlab:
                print(f'{Colors.BOLD}   - Exported group: '
                      f'{Colors.GREEN}Success'
                      f'{Colors.RESET}')
                Platform.flush()

        # Abort output group
        if not output_gitlab:
            print(' ')
            Platform.flush()
            return Entrypoint.Result.SUCCESS

        # Acquire output group
        output_group_criteria: str = ''
        if not options.dry_run:
            output_group = output_gitlab.group(criteria_output_group)
            output_group_criteria = output_group.full_path

        # Set group description
        description = Namespaces.describe(
            name=output_group_name,
            description=input_group.description,
        )
        changed = output_gitlab.group_set_description(
            output_group_criteria,
            description,
        )
        print(f'{Colors.BOLD}     - Set description: '
              f'{Colors.CYAN if changed else Colors.GREEN}{description}'
              f'{Colors.RESET}')
        Platform.flush()

        # Set group avatar
        if options.set_avatar:
            output_gitlab.group_set_avatar(
                output_group_criteria,
                options.set_avatar,
            )
            print(f'{Colors.BOLD}     - Set avatar: '
                  f'{Colors.CYAN}{options.set_avatar}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Show group result
        print(f'{Colors.BOLD}   - Migrated group: '
              f'{Colors.GREEN}Success'
              f'{Colors.RESET}')
        Platform.flush()

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS

    # Project, pylint: disable=too-many-arguments,too-many-branches,too-many-locals,too-many-positional-arguments
    @staticmethod
    def project(
        options: Namespace,
        input_gitlab: GitLabFeature,
        output_gitlab: Optional[GitLabFeature],
        criteria_project: str,
        criteria_input_namespace: str,
        criteria_output_namespace: str,
        output_gitlab_namespace: str,
        rename_project: str = '',
        progress_index: int = 1,
        progress_count: int = 1,
    ) -> Result:

        # Variables
        archived: bool
        branch_default: str
        changed: bool = False
        input_namespace: GitLabNamespace
        input_project: GitLabProject
        output_exists: bool = False
        output_path: str
        output_project: GitLabProjectImport
        output_subnamespace: str
        output_subpath: str
        project: GitLabProject

        # Acquire input project
        input_project = input_gitlab.project(
            criteria_project,
            statistics=True,
        )

        # Acquire input namespace
        input_namespace = input_gitlab.namespace(criteria_input_namespace)

        # Parse input subpath
        input_subpath = Namespaces.subpath(
            input_namespace.full_path,
            input_project.path_with_namespace,
        )

        # Acquire output namespace
        if output_gitlab:
            output_namespace = output_gitlab.namespace(
                criteria_output_namespace,
                optional=True,
            )

        # Prepare project path
        output_project_path: str = rename_project if rename_project else input_project.path
        output_project_path = re.sub(r'\.+', '.', output_project_path)
        output_project_path = re.sub(r'-+', '-', output_project_path)
        output_project_path = re.sub(r'_+', '_', output_project_path)

        # Normalize project path
        output_project_path = output_project_path.lstrip('-_. ')
        output_project_path = output_project_path.rstrip('-_. ')
        output_project_path = re.sub(r'\.git$', '', output_project_path)
        output_project_path = re.sub(r'\.atom$', '', output_project_path)
        if options.normalize_names:
            output_project_path = output_project_path.replace(' ', '-')
            output_project_path = output_project_path.replace('_', '-')
            output_project_path = output_project_path.lower()

        # Parse output path
        if output_gitlab:
            output_subnamespace, output_path = Namespaces.split_namespace(
                input_subpath,
                relative=True,
            )
            if output_path:
                output_path = re.sub(
                    f'{input_project.path}$',
                    output_project_path,
                    output_path,
                )

        # Flatten output group
        if output_gitlab and options.flatten_group:
            output_subnamespace = ''

        # Parse output subpath
        if output_gitlab:
            output_subpath = Namespaces.subpath(
                output_namespace.full_path,
                f'{output_gitlab_namespace}{output_subnamespace}/{output_path}',
            )

        # Show project details
        print(f'{Colors.BOLD} - GitLab input project ('
              f'{Colors.GREEN}{progress_index}'
              f'{Colors.RESET}/'
              f'{Colors.CYAN}{progress_count}'
              f'{Colors.BOLD}) : '
              f'{Colors.YELLOW_LIGHT}{input_project.path_with_namespace} '
              f'{Colors.CYAN}({Namespaces.text(input_project.description)})'
              f'{Colors.RESET}')
        Platform.flush()

        # Ignore existing projects
        if output_gitlab and output_subpath in [
                Namespaces.subpath(
                    output_namespace.full_path,
                    output_project.path_with_namespace,
                ) for output_project in output_gitlab.namespace_projects(
                    criteria_output_namespace,
                    include_subgroups=True,
                )
        ]:
            output_exists = True
            project = output_gitlab.project(
                f'{output_namespace.full_path}/{output_subpath}')
            print(f'{Colors.BOLD}   - Already existing project in GitLab output: '
                  f'{Colors.GREEN}{project.path_with_namespace}'
                  f'{Colors.CYAN} # {Namespaces.text(project.description)}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Ignore existing names
        if not output_exists and output_gitlab and output_project_path in [
                output_project.name
                for output_project in output_gitlab.namespace_projects(
                    f'{output_gitlab_namespace}{output_subnamespace}',
                    include_subgroups=False,
                )
        ]:
            print(f'{Colors.RED}   - Already existing project name in GitLab output: '
                  f'{Colors.CYAN}{output_project_path}'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            raise RuntimeError()

        # Migrate missing projects
        if not output_exists or options.overwrite:

            # Detect project export limitions
            export_limitations = input_gitlab.project_export_limitations(
                input_project.path_with_namespace)

            # Accept project packages migration
            if output_gitlab and options.migrate_packages and \
                    'Packages registry' in export_limitations:
                del export_limitations['Packages registry']

            # Confirm project is exportable
            if export_limitations:
                print(f'{Colors.BOLD}   - Limited project export detected: '
                      f'{Colors.RESET}')
                for limitation, items in export_limitations.items():
                    (level, values) = items
                    if level == GitLabFeature.LIMITATIONS_ERROR:
                        print(f'{Colors.BOLD}     - With data loss: '
                              f'{Colors.RED}{limitation}'
                              + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                              f'{Colors.RESET}')
                    else:
                        print(f'{Colors.BOLD}     - With optional custom migration: '
                              f'{Colors.YELLOW_LIGHT}{limitation}'
                              + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                              f'{Colors.RESET}')
                if not options.dry_run and not Entrypoint.confirm(
                        '',
                        input_project.path_with_namespace,
                        not options.confirm,
                        'limited project export',
                        indent='     ',
                ):
                    raise PermissionError()

            # Acquire project settings
            archived = input_project.archived
            branch_default = input_gitlab.project_get_branch_default(
                input_project.path_with_namespace)

            # Export project
            if output_gitlab or options.archive_exports:
                print(f'{Colors.BOLD}   - Exporting from: '
                      f'{Colors.GREEN}{input_namespace.full_path}'
                      f'{Colors.CYAN} / {input_subpath}'
                      f'{Colors.RESET}')
                Platform.flush()

                # Show project sizes
                print(
                    f'{Colors.BOLD}     - Project sizes: '
                    f'{Colors.CYAN}{Humanize.size(input_project.statistics["storage_size"])} '
                    f'{Colors.YELLOW_LIGHT}(storage), '
                    f'{Colors.CYAN}{Humanize.size(input_project.statistics["repository_size"])} '
                    f'{Colors.YELLOW_LIGHT}(repository)'
                    f'{Colors.RESET}')
                Platform.flush()

                # Archive project during export
                changed = input_gitlab.project_set_archive(
                    input_project.path_with_namespace,
                    True,
                )
                print(f'{Colors.BOLD}     - Archiving during export: '
                      f'{Colors.CYAN if changed else Colors.GREEN}Success'
                      f'{Colors.RESET}')
                Platform.flush()

                # Export project to file
                with NamedTemporaryFile(
                        prefix=Paths.slugify(f'{Entrypoint.EXPORTS_PREFIX}'
                                             f'-{input_project.path_with_namespace}-'),
                        suffix='.tar.gz',
                        dir=options.archive_exports_dir,
                        delete=not options.archive_exports_dir,
                ) as file_export:
                    input_gitlab.project_export(
                        file_export.name,
                        input_project.path_with_namespace,
                        options.reset_entities,
                    )

                    # Restore project archive
                    if not archived:
                        changed = input_gitlab.project_set_archive(
                            input_project.path_with_namespace,
                            False,
                        )
                        print(f'{Colors.BOLD}     - Unarchived after export: '
                              f'{Colors.CYAN if changed else Colors.GREEN}Success'
                              f'{Colors.RESET}')
                        Platform.flush()

                    # Existing project removal
                    if output_gitlab and options.overwrite:
                        if not Entrypoint.confirm(
                                'Delete project',
                                f'{output_namespace.full_path}/{output_subpath}',
                                not options.confirm,
                                'deletion',
                        ):
                            raise PermissionError()
                        output_gitlab.project_delete(
                            f'{output_namespace.full_path}/{output_subpath}')

                    # Import project
                    if output_gitlab:
                        print(f'{Colors.BOLD}   - Importing to: '
                              f'{Colors.GREEN}{output_gitlab_namespace}'
                              f'{Colors.CYAN} / {output_subpath}'
                              f'{Colors.RESET}')
                        Platform.flush()
                        output_project = output_gitlab.project_import(
                            file_export.name,
                            f'{output_gitlab_namespace}{output_subnamespace}',
                            output_path,
                            output_project_path,
                            options.overwrite,
                            sudo=output_namespace.full_path
                            if output_namespace.kind == 'user'
                            and output_namespace != output_gitlab.username else None,
                        )

                # Successful project migration
                if not output_gitlab:
                    print(f'{Colors.BOLD}   - Exported project: '
                          f'{Colors.GREEN}Success'
                          f'{Colors.RESET}')
                    Platform.flush()

            # Abort output project
            if not output_gitlab:
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

            # Acquire subgroup description
            output_subgroup_description: str
            if options.dry_run:
                output_subgroup_description = input_project.description
            elif output_namespace.kind == 'user':
                output_subgroup_description = output_namespace.name
            else:
                output_subgroup = output_gitlab.group(
                    f'{output_gitlab_namespace}{output_subnamespace}')
                output_subgroup_description = output_subgroup.description

            # Update project description
            if options.update_description:
                group_description = Namespaces.describe(
                    name=output_project_path,
                    description=output_subgroup_description,
                )
                if not output_project.description or \
                        not output_project.description.endswith(f' - {group_description}'):
                    description = f'{Namespaces.describe(name=output_project.name)}' \
                                    f' - {group_description}'
                    changed = output_gitlab.project_set_description(
                        output_project.path_with_namespace,
                        description,
                    )
                    print(f'{Colors.BOLD}     - Updated description: '
                          f'{Colors.CYAN if changed else Colors.GREEN}{description}'
                          f'{Colors.RESET}')
                    Platform.flush()
                else:
                    print(f'{Colors.BOLD}     - Kept description: '
                          f'{Colors.GREEN}{Namespaces.text(output_project.description)}'
                          f'{Colors.RESET}')
                    Platform.flush()

            # Reset project members
            if MigrationEntities.MEMBERS.name in options.reset_entities:
                output_gitlab.project_reset_members(output_project.path_with_namespace)
                print(f'{Colors.BOLD}     - Reset members: '
                      f'{Colors.GREEN}Success'
                      f'{Colors.RESET}')
                Platform.flush()

            # Set project avatar
            if options.set_avatar:
                output_gitlab.project_set_avatar(
                    output_project.path_with_namespace,
                    options.set_avatar,
                )
                print(f'{Colors.BOLD}     - Set avatar: '
                      f'{Colors.CYAN}{options.set_avatar}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Configure project repository
            if branch_default:
                changed = output_gitlab.project_set_branch_default(
                    output_project.path_with_namespace,
                    branch_default,
                )
                print(f'{Colors.BOLD}     - Set default branch: '
                      f'{Colors.CYAN if changed else Colors.GREEN}{branch_default}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Configure project archive
            changed = output_gitlab.project_set_archive(
                output_project.path_with_namespace,
                archived,
            )
            print(f'{Colors.BOLD}     - '
                  f'{"Archived" if archived else "Unarchived"}'
                  ' migrated project: '
                  f'{Colors.CYAN if changed else Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

            # Show project result
            print(f'{Colors.BOLD}     - Migrated project: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Migrate project packages
        if output_gitlab and options.migrate_packages and not options.dry_run:

            # Prepare packages migration
            project = output_gitlab.project(
                f'{output_namespace.full_path}/{output_subpath}')
            print(f'{Colors.BOLD}   - Migrating packages from: '
                  f'{Colors.GREEN}{input_namespace.full_path}'
                  f'{Colors.CYAN} / {input_subpath}'
                  f'{Colors.RESET}')
            Platform.flush()

            # Detect migrated packages
            GitLabPackageFile = NamedTuple('GitLabPackageFile', (
                ('name', str),
                ('version', str),
                ('package_type', str),
                ('file_name', str),
                ('size', int),
                ('file_md5', str),
                ('file_sha1', str),
                ('file_sha256', str),
            ))
            input_project_packages: List[GitLabPackageFile] = []
            output_project_packages: List[GitLabPackageFile] = []
            try:
                for package in project.packages.list(
                        get_all=True,
                        include_versionless=True,
                ):
                    for package_file in package.package_files.list(get_all=True):
                        output_project_packages += [
                            GitLabPackageFile(
                                name=package.name,
                                version=package.version,
                                package_type=package.package_type,
                                file_name=package_file.file_name,
                                size=package_file.size,
                                file_md5=package_file.file_md5,
                                file_sha1=package_file.file_sha1,
                                file_sha256=package_file.file_sha256,
                            )
                        ]
            except GitlabListError:
                pass

            # Detect existing packages
            try:
                for package in input_project.packages.list(
                        get_all=True,
                        include_versionless=True,
                ):

                    # Iterate through packages files
                    print(f'{Colors.BOLD}     - Importing project package:'
                          f'{Colors.YELLOW_LIGHT} {package.name}'
                          f'{Colors.CYAN} / {package.version}'
                          f'{Colors.RESET}')
                    Platform.flush()
                    for package_file in package.package_files.list(get_all=True):
                        with NamedTemporaryFile(
                                prefix=Paths.slugify(f'{Entrypoint.PACKAGES_PREFIX}'
                                                     f'-{package.id}-{package_file.id}-'),
                                suffix='.tmp',
                                delete=True,
                        ) as package_tempfile:

                            # Detect already migrated package file
                            if GitLabPackageFile(
                                    name=package.name,
                                    version=package.version,
                                    package_type=package.package_type,
                                    file_name=package_file.file_name,
                                    size=package_file.size,
                                    file_md5=package_file.file_md5,
                                    file_sha1=package_file.file_sha1,
                                    file_sha256=package_file.file_sha256,
                            ) in output_project_packages:
                                print(
                                    f'{Colors.BOLD}       - Kept already migrated package file:'
                                    f'{Colors.GREEN} {package_file.file_name}'
                                    f'{Colors.GREY} / {package_file.size} bytes'
                                    f'{Colors.RESET}')
                                Platform.flush()

                            # Handle input package file
                            else:
                                input_project_package = GitLabPackageFile(
                                    name=package.name,
                                    version=package.version,
                                    package_type=package.package_type,
                                    file_name=package_file.file_name,
                                    size=0,
                                    file_md5='',
                                    file_sha1='',
                                    file_sha256='',
                                )
                                if input_project_package in input_project_packages and \
                                    not Entrypoint.confirm(
                                        'Duplicated package file name detected',
                                        package_file.file_name,
                                        not options.confirm,
                                        'unsafe migration',
                                        '       ',
                                ):
                                    continue
                                input_project_packages += [input_project_package]

                                # Upload generic package file
                                if package.package_type == 'generic':
                                    package_tempfile.write(
                                        input_project.generic_packages.download(
                                            package_name=package.name,
                                            package_version=package.version,
                                            file_name=package_file.file_name,
                                        ))
                                    package_tempfile.flush()
                                    project.generic_packages.upload(
                                        package_name=package.name,
                                        package_version=package.version,
                                        file_name=package_file.file_name,
                                        path=package_tempfile.name,
                                    )
                                    print(f'{Colors.BOLD}       - Uploaded package file:'
                                          f'{Colors.GREEN} {package_file.file_name}'
                                          f'{Colors.GREY} / {package_file.size} bytes'
                                          f'{Colors.RESET}')
                                    Platform.flush()

                                # Unsupported package file
                                else:
                                    raise RuntimeError(
                                        f'Unknown GitLab Packages type "{package.package_type}"'
                                        f' for package {package.name}')

                # Successful packages migration
                print(f'{Colors.BOLD}     - Migrated project packages: '
                      f'{Colors.GREEN}Success'
                      f'{Colors.RESET}')
                Platform.flush()

            # Ignore missing packages
            except GitlabListError:
                print(f'{Colors.BOLD}     - Ignored project packages: '
                      f'{Colors.CYAN}No packages found'
                      f'{Colors.RESET}')
                Platform.flush()

        # Validate project migration
        if output_gitlab and not options.dry_run:
            print(f'{Colors.BOLD}     - Validating project migration:'
                  f'{Colors.RESET}')
            Platform.flush()

            # Confirm project migration
            project = output_gitlab.project(
                f'{output_namespace.full_path}/{output_subpath}')
            migration_differences = GitLabFeature.migration_projects_compare(
                input_project,
                project,
                options.reset_entities,
            )
            if migration_differences:
                print(f'{Colors.BOLD}     - '
                      f'{Colors.RED}Differences detected after migration:'
                      f'{Colors.RESET}')
                for migration_difference in migration_differences:
                    difference, details = migration_difference
                    print(f'{Colors.BOLD}       - '
                          f'{Colors.RED}{difference}:'
                          f'{Colors.CYAN} {details}'
                          f'{Colors.RESET}')
                if not Entrypoint.confirm(
                        '',
                        project.path_with_namespace,
                        not options.confirm,
                        'incomplete project migration',
                        indent='       ',
                ):
                    raise PermissionError()

            # Show project validation
            print(f'{Colors.BOLD}     - Validated project migration: '
                  f'{Colors.GREEN}Success'
                  f'{Colors.RESET}')
            Platform.flush()

        # Separator
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS

    # Subgroup, pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-statements
    @staticmethod
    def subgroup(
        options: Namespace,
        input_gitlab: GitLabFeature,
        output_gitlab: Optional[GitLabFeature],
        criteria_input_group: str,
        criteria_input_subgroup: str,
        criteria_output_group: str,
        migration: bool = True,
        progress_index: int = 1,
        progress_count: int = 1,
    ) -> Result:

        # Variables
        changed: bool
        input_subpath: str
        output_subgroup_fullpath: str
        output_subgroup_namespace: str
        output_subgroup_path: str

        # Acquire input group
        input_group = input_gitlab.group(criteria_input_group)

        # Acquire input subgroup
        input_subgroup = input_gitlab.group(criteria_input_subgroup)

        # Acquire output group
        if output_gitlab:
            output_group = output_gitlab.group(criteria_output_group, optional=True)

        # Show subgroup details
        print(f'{Colors.BOLD} - GitLab subgroup ('
              f'{Colors.GREEN}{progress_index}'
              f'{Colors.RESET}/'
              f'{Colors.CYAN}{progress_count}'
              f'{Colors.BOLD}) : '
              f'{Colors.YELLOW_LIGHT}{input_subgroup.full_path} '
              f'{Colors.CYAN}({Namespaces.text(input_subgroup.description)})'
              f'{Colors.RESET}')
        Platform.flush()

        # Parse subgroup paths
        input_subpath = Namespaces.subpath(
            input_group.full_path,
            input_subgroup.full_path,
        )
        output_subgroup_namespace, output_subgroup_path = Namespaces.split_namespace(
            input_subpath,
            relative=True,
        )
        output_subgroup_fullpath = f'{output_subgroup_namespace}/{output_subgroup_path}'

        # Migration mode
        if migration:

            # Ignore existing subgroup
            if output_gitlab and f'{output_subgroup_fullpath.lstrip("/")}' in [
                    Namespaces.subpath(
                        output_group.full_path,
                        output_subgroup.full_path,
                    ) for output_subgroup in output_group.descendant_groups.list(
                        get_all=True,
                        # include_subgroups=True,
                    )
            ]:
                output_subgroup = output_gitlab.group(
                    f'{output_group.full_path}{output_subgroup_fullpath}')
                print(f'{Colors.BOLD}   - Already existing subgroup in GitLab output: '
                      f'{Colors.GREEN}{output_subgroup.full_path}'
                      f'{Colors.CYAN} # {Namespaces.text(output_subgroup.description)}'
                      f'{Colors.RESET}')
                print(' ')
                Platform.flush()
                return Entrypoint.Result.SUCCESS

            # Confirm subgroup is exportable
            export_limitations = input_gitlab.group_export_limitations(
                input_subgroup.full_path)
            if export_limitations:
                print(f'{Colors.BOLD}   - Limited subgroup export detected: '
                      f'{Colors.RESET}')
                for limitation, items in export_limitations.items():
                    (level, values) = items
                    if level == GitLabFeature.LIMITATIONS_ERROR:
                        print(f'{Colors.BOLD}     - With data loss: '
                              f'{Colors.RED}{limitation}'
                              + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                              f'{Colors.RESET}')
                    else:
                        print(f'{Colors.BOLD}     - With optional custom migration: '
                              f'{Colors.YELLOW_LIGHT}{limitation}'
                              + (f'{Colors.CYAN} ({", ".join(values)})' if values else '') + \
                              f'{Colors.RESET}')
                if not options.dry_run and not Entrypoint.confirm(
                        '',
                        input_subgroup.full_path,
                        not options.confirm,
                        'limited subgroup export',
                        indent='     ',
                ):
                    raise PermissionError()

            # Export subgroup
            if output_gitlab or options.archive_exports:
                print(f'{Colors.BOLD}   - Exporting from: '
                      f'{Colors.GREEN}{input_subgroup.full_path}'
                      f'{Colors.RESET}')
                Platform.flush()
                with NamedTemporaryFile(
                        prefix=Paths.slugify(f'{Entrypoint.EXPORTS_PREFIX}'
                                             f'-{input_subgroup.full_path}-'),
                        suffix='.tar.gz',
                        dir=options.archive_exports_dir,
                        delete=not options.archive_exports_dir,
                ) as file_export:
                    input_gitlab.group_export(
                        file_export.name,
                        input_subgroup.full_path,
                        options.reset_entities,
                    )

                    # Import subgroup
                    if output_gitlab:
                        print(f'{Colors.BOLD}   - Importing to: '
                              f'{Colors.GREEN}'
                              f'{output_group.full_path}{output_subgroup_fullpath}'
                              f'{Colors.RESET}')
                        Platform.flush()
                        output_gitlab.group_import(
                            file_export.name,
                            f'{output_group.full_path}{output_subgroup_namespace}',
                            output_subgroup_path,
                            input_subgroup.name,
                        )

            # Abort subgroup migration
            if not output_gitlab:
                print(f'{Colors.BOLD}   - Exported subgroup: '
                      f'{Colors.GREEN}Success'
                      f'{Colors.RESET}')
                Platform.flush()

        # Abort output subgroup
        if not output_gitlab:
            print(' ')
            Platform.flush()
            return Entrypoint.Result.SUCCESS

        # Acquire subgroups
        output_subgroup_child_description: str
        output_subgroup_child_name: str
        output_subgroup_parent_description: str
        if not options.dry_run:
            output_subgroup_parent = output_gitlab.group(
                f'{output_group.full_path}{output_subgroup_namespace}')
            output_subgroup_parent_description = output_subgroup_parent.description
            output_subgroup_child = output_gitlab.group(
                f'{output_group.full_path}{output_subgroup_fullpath}')
            output_subgroup_child_description = output_subgroup_child.description
            output_subgroup_child_name = output_subgroup_child.name
        else:
            output_subgroup_parent_description = input_subgroup.description
            output_subgroup_child_description = input_subgroup.description
            output_subgroup_child_name = input_subgroup.name

        # Update subgroup header
        print(f'{Colors.BOLD}   - Updating subgroup: '
              f'{Colors.GREEN}{output_group.full_path}{output_subgroup_fullpath}'
              f'{Colors.RESET}')
        Platform.flush()

        # Update subgroup description
        if options.update_description:
            parent_description = Namespaces.describe(
                name=output_subgroup_child_name,
                description=output_subgroup_parent_description,
            )
            if not output_subgroup_child_description.endswith(f' - {parent_description}'):
                description = f'{Namespaces.describe(name=output_subgroup_child_name)}' \
                              f' - {parent_description}'
                changed = output_gitlab.group_set_description(
                    f'{output_group.full_path}{output_subgroup_fullpath}',
                    description,
                )
                print(f'{Colors.BOLD}     - Updated description: '
                      f'{Colors.CYAN if changed else Colors.GREEN}{description}'
                      f'{Colors.RESET}')
                Platform.flush()
            else:
                print(f'{Colors.BOLD}     - Kept description: '
                      f'{Colors.GREEN}{output_subgroup_child_description}'
                      f'{Colors.RESET}')
                Platform.flush()

        # Set subgroup avatar
        if options.set_avatar:
            output_gitlab.group_set_avatar(
                f'{output_group.full_path}{output_subgroup_fullpath}',
                options.set_avatar,
            )
            print(f'{Colors.BOLD}     - Set avatar: '
                  f'{Colors.CYAN}{options.set_avatar}'
                  f'{Colors.RESET}')
            Platform.flush()

        # Show subgroup result
        print(f'{Colors.BOLD}   - Migrated subgroup: '
              f'{Colors.GREEN}Success'
              f'{Colors.RESET}')
        Platform.flush()

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return Entrypoint.Result.SUCCESS
