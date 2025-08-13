#!/usr/bin/env python3

# Standard libraries
from os.path import join
from typing import List, NamedTuple, Union

# Modules libraries
from gitlab.v4.objects import (
    GroupRunner,
    ProjectRunner,
)

# MigrationEntities class
class MigrationEntities:

    # Members
    cache_entities: List[str] = []
    cache_keys: List[str] = []
    cache_removers: List[str] = []
    cache_templates: List[str] = []

    # Entity
    class Entity(NamedTuple):

        # Variables
        name: str
        group_globs: List[str] = []
        project_directories: List[str] = []
        project_files: List[str] = []

    # Remover
    class Remover(Entity):
        pass

    # Template
    class Template(Entity):
        pass

    # Defaults
    @staticmethod
    def defaults() -> List[str]:

        # Return default exclusions
        return [
            MigrationEntities.MEMBERS.name,
        ]

    # Get
    @staticmethod
    def get(key: str) -> Entity:

        # Get feature object
        feature = getattr(MigrationEntities, key)
        assert isinstance(feature, MigrationEntities.Entity)
        return feature

    # Keys
    @staticmethod
    def keys() -> List[str]:

        # Evaluate keys
        if MigrationEntities.cache_keys:
            return MigrationEntities.cache_keys

        # Evaluate keys
        MigrationEntities.cache_keys = [
            key for key in MigrationEntities.__dict__
            if isinstance(getattr(MigrationEntities, key), MigrationEntities.Entity)
        ]
        return MigrationEntities.cache_keys

    # Entities
    @staticmethod
    def entities() -> List[str]:

        # Evaluate entities
        if MigrationEntities.cache_entities:
            return MigrationEntities.cache_entities

        # Evaluate entities
        MigrationEntities.cache_entities = [
            MigrationEntities.get(key).name for key in MigrationEntities.__dict__
            if isinstance(getattr(MigrationEntities, key), MigrationEntities.Entity) and
            not isinstance(getattr(MigrationEntities, key), MigrationEntities.Remover) and
            not isinstance(getattr(MigrationEntities, key), MigrationEntities.Template)
        ]
        return MigrationEntities.cache_entities

    # Removers
    @staticmethod
    def removers() -> List[str]:

        # Evaluate removers
        if MigrationEntities.cache_removers:
            return MigrationEntities.cache_removers

        # Evaluate removers
        MigrationEntities.cache_removers = [
            MigrationEntities.get(key).name for key in MigrationEntities.__dict__
            if isinstance(getattr(MigrationEntities, key), MigrationEntities.Remover)
        ]
        return MigrationEntities.cache_removers

    # Templates
    @staticmethod
    def templates() -> List[str]:

        # Evaluate templates
        if MigrationEntities.cache_templates:
            return MigrationEntities.cache_templates

        # Evaluate templates
        MigrationEntities.cache_templates = [
            MigrationEntities.get(key).name for key in MigrationEntities.__dict__
            if isinstance(getattr(MigrationEntities, key), MigrationEntities.Template)
        ]
        return MigrationEntities.cache_templates

    # Entity: Members
    MEMBERS = Entity(
        name='Members',
        group_globs=[
            join('tree', 'groups', '*', 'members.ndjson'),
        ],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'project_members.ndjson'),
        ],
    )

    # Entity: Issues
    ISSUES = Entity(
        name='Issues',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'issues.ndjson'),
        ],
    )

    # Entity: Issue boards
    BOARDS = Entity(
        name='Issue boards',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'boards.ndjson'),
        ],
    )

    # Entity: Milestones
    MILESTONES = Entity(
        name='Milestones',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'milestones.ndjson'),
        ],
    )

    # Entity: Labels
    LABELS = Entity(
        name='Labels',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'labels.ndjson'),
        ],
    )

    # Entity: Repository / Merge_requests
    MERGE_REQUESTS = Entity(
        name='Merge requests',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'merge_requests.ndjson'),
        ],
    )

    # Entity: Repository / LFS objects
    LFS_OBJECTS = Entity(
        name='LFS objects',
        group_globs=[],
        project_directories=[
            join('lfs-objects'),
        ],
        project_files=[
            join('lfs-objects.json'),
        ],
    )

    # Entity: Repository / CI/CD Pipelines
    PIPELINES = Entity(
        name='Pipelines',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'ci_pipelines.ndjson'),
            join('tree', 'project', 'pipeline_schedules.ndjson'),
        ],
    )

    # Entity: Wiki
    WIKI = Entity(
        name='Wiki',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('project.wiki.bundle'),
        ],
    )

    # Entity: Snippets
    SNIPPETS = Entity(
        name='Snippets',
        group_globs=[],
        project_directories=[
            join('snippets'),
        ],
        project_files=[
            join('tree', 'project', 'snippets.ndjson'),
        ],
    )

    # Entity: Releases
    RELEASES = Entity(
        name='Releases',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'releases.ndjson'),
        ],
    )

    # Entity: Badges
    BADGES = Entity(
        name='Badges',
        group_globs=[],
        project_directories=[],
        project_files=[
            join('tree', 'project', 'project_badges.ndjson'),
        ],
    )

    # Entity: Uploads (wiki / issues)
    UPLOADS = Entity(
        name='Uploads',
        group_globs=[],
        project_directories=[
            join('uploads'),
        ],
        project_files=[],
    )

    # Remover: Issues
    REMOVER_ISSUES = Remover(
        name='Remove/Issues',
        group_globs=[
            *MEMBERS.group_globs,
            *ISSUES.group_globs,
            *BOARDS.group_globs,
            *MILESTONES.group_globs,
            *LABELS.group_globs,
            *UPLOADS.group_globs,
        ],
        project_directories=[
            *MEMBERS.project_directories,
            *ISSUES.project_directories,
            *BOARDS.project_directories,
            *MILESTONES.project_directories,
            *LABELS.project_directories,
            *UPLOADS.project_directories,
        ],
        project_files=[
            *MEMBERS.project_files,
            *ISSUES.project_files,
            *BOARDS.project_files,
            *MILESTONES.project_files,
            *LABELS.project_files,
            *UPLOADS.project_files,
        ],
    )

    # Remover: Repository
    REMOVER_REPOSITORY = Remover(
        name='Remove/Repository',
        group_globs=[
            *MEMBERS.group_globs,
            *MERGE_REQUESTS.group_globs,
            *LFS_OBJECTS.group_globs,
            *PIPELINES.group_globs,
            *RELEASES.group_globs,
        ],
        project_directories=[
            *MEMBERS.project_directories,
            *MERGE_REQUESTS.project_directories,
            *LFS_OBJECTS.project_directories,
            *PIPELINES.project_directories,
            *RELEASES.project_directories,
        ],
        project_files=[
            *MEMBERS.project_files,
            *MERGE_REQUESTS.project_files,
            *LFS_OBJECTS.project_files,
            *PIPELINES.project_files,
            *RELEASES.project_files,
            join('project.bundle'),
            join('tree', 'project', 'protected_branches.ndjson'),
            join('tree', 'project', 'protected_tags.ndjson'),
        ],
    )

    # Remover: Wiki
    REMOVER_WIKI = Remover(
        name='Remove/Wiki',
        group_globs=[
            *MEMBERS.group_globs,
            *WIKI.group_globs,
        ],
        project_directories=[
            *MEMBERS.project_directories,
            *WIKI.project_directories,
        ],
        project_files=[
            *MEMBERS.project_files,
            *WIKI.project_files,
        ],
    )

    # Template: Issues
    TEMPLATE_ISSUES = Template(
        name='Template/Issues',
        group_globs=[
            *MEMBERS.group_globs,
            *ISSUES.group_globs,
            *MILESTONES.group_globs,
            *UPLOADS.group_globs,
        ],
        project_directories=[
            *MEMBERS.project_directories,
            *ISSUES.project_directories,
            *MILESTONES.project_directories,
            *UPLOADS.project_directories,
        ],
        project_files=[
            *MEMBERS.project_files,
            *ISSUES.project_files,
            *MILESTONES.project_files,
            *UPLOADS.project_files,
        ],
    )

    # Template: Repository
    TEMPLATE_REPOSITORY = Template(
        name='Template/Repository',
        group_globs=[
            *MEMBERS.group_globs,
            *MERGE_REQUESTS.group_globs,
            *PIPELINES.group_globs,
            *RELEASES.group_globs,
        ],
        project_directories=[
            *MEMBERS.project_directories,
            *MERGE_REQUESTS.project_directories,
            *PIPELINES.project_directories,
            *RELEASES.project_directories,
        ],
        project_files=[
            *MEMBERS.project_files,
            *MERGE_REQUESTS.project_files,
            *PIPELINES.project_files,
            *RELEASES.project_files,
            join('tree', 'project', 'protected_tags.ndjson'),
        ],
    )

# RunnerHelpers class, pylint: disable=too-few-public-methods
class RunnerHelpers:

    # Active
    @staticmethod
    def active(runner: Union[GroupRunner, ProjectRunner]) -> bool:

        # Detect inactive runner
        if not runner.active:
            return False

        # Detect paused runner
        if (hasattr(runner, 'paused') and runner.paused) or runner.status == 'paused':
            return False

        # Result
        return True
