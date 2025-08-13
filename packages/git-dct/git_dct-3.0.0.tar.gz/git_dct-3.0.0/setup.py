#!/usr/bin/env python3

# Standard libraries
from glob import glob
from os import sep, walk
from os.path import basename, join, splitext
from pathlib import Path
from typing import List, Optional

# Modules libraries
from setuptools import Command, find_packages, setup
from setuptools.command.build import build as BuildCommand
from setuptools.command.sdist import sdist as SourcesCommand

# Requirements
requirements: List[str] = []
with open('requirements/runtime.txt', encoding='utf8', mode='r') as f:
    requirements = [line for line in f.read().splitlines() if not line.startswith('#')]

# Long description
long_description: str = '' # pylint: disable=invalid-name
with open('README.md', encoding='utf8', mode='r') as f:
    long_description = f.read()

# Project configurations
PROJECT_AUTHOR = 'Adrian DC'
PROJECT_DESCRIPTION = 'Git development CLI tools for daily usage'
PROJECT_EMAIL = 'radian.dc@gmail.com'
PROJECT_KEYWORDS = 'git git-dct'
PROJECT_LICENSE = 'Apache License 2.0'
PROJECT_MODULE = 'git_dct'
PROJECT_NAME = 'git-dct'
PROJECT_NAMESPACE = 'RadianDevCore/tools'
PROJECT_PACKAGE = 'git-dct'
PROJECT_SCRIPTS = [
    'git-dct = git_dct.cli.main:main',
    'git-dct-tools-git-cauthor = git_dct.tools.git_cauthor:main',
    'git-dct-tools-git-fcp = git_dct.tools.git_fcp:main',
    'git-dct-tools-git-fe = git_dct.tools.git_fe:main',
    'git-dct-tools-git-pu = git_dct.tools.git_pu:main',
    'git-dct-tools-git-rb = git_dct.tools.git_rb:main',
    'git-dct-tools-git-stat = git_dct.tools.git_stat:main',
]
PROJECT_URL = f'https://gitlab.com/{PROJECT_NAMESPACE}/{PROJECT_NAME}'

# Setup assets
class SetupAssets(Command):

    # Assets constants
    DOCS_ALIAS: str = 'alias.generated.md'
    DOCS_ALIAS_LINK: str = '../alias.gitconfig/'
    DOCS_PATH: Path = Path('docs')
    DOCS_SEPARATOR: str = '\n'
    GIT_ALIAS: str = 'alias.gitconfig'
    GIT_SEPARATOR: str = '\n'
    PROFILES_PATH: Path = Path('profiles')
    SOURCES_ASSETS_PATH: Path = Path('src') / 'assets'

    # Assets variables
    assets_list: List[str] = []
    assets_keep: bool = False

    # Command configurations
    clean: Optional[int]
    prepare: Optional[int]
    short_options: Optional[str] = None
    user_options = [
        ('clean', short_options, 'Clean assets after setup'),
        ('prepare', short_options, 'Prepare assets after setup'),
    ]

    # Git alias configuration, pylint: disable=too-many-branches,too-many-locals,too-many-statements
    @staticmethod
    def git_configuration_alias(keep: bool = False) -> None:

        # Variables
        comment: str
        command: str
        function_list: List[str]
        function_line: str
        page_position: float = 0.0
        section_current: str
        section_last: str = ''
        section_new: bool
        title: str

        # Prepare documentation sources
        docs: Path = Path.cwd() / SetupAssets.DOCS_PATH
        docs.mkdir(parents=True, exist_ok=True)

        # Prepare profiles sources
        profiles: Path = Path.cwd() / SetupAssets.SOURCES_ASSETS_PATH
        profiles.mkdir(parents=True, exist_ok=True)

        # Write configuration file
        with open(profiles / SetupAssets.GIT_ALIAS, encoding='utf8', mode='w') as asset, \
                open(docs / SetupAssets.DOCS_ALIAS, encoding='utf8', mode='w') as documentation:

            # Keep assets list
            if not keep and asset.name not in SetupAssets.assets_list:
                SetupAssets.assets_list += [asset.name]

            # Configuration file header
            asset.writelines([
                f'{line}{SetupAssets.GIT_SEPARATOR}' for line in [
                    '#####',
                    f'# {PROJECT_NAME}: {PROJECT_DESCRIPTION}',
                    '##',
                    f'# Author: {PROJECT_AUTHOR}',
                    f'# Email: {PROJECT_EMAIL}',
                    f'# License: {PROJECT_LICENSE}',
                    f'# Sources: {PROJECT_URL}',
                    '# Warning: Generated configuration maintained automatically, do not edit',
                    '###',
                    '',
                    '[alias]',
                ]
            ])

            # Documentation file header
            documentation.writelines([
                f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                    '<!-- generated documentation section -->',
                ]
            ])

            # Iterate through profiles files
            for root, _, _ in sorted(walk(SetupAssets.PROFILES_PATH)):

                # Handle profile aliases
                for alias_file in sorted(glob(join(root, '*.alias'))):

                    # Parse profile section
                    section_current = root.split(sep)[-1]
                    section_new = section_last != section_current
                    if section_new:
                        section_last = section_current

                    # Inject page breaks
                    if page_position > 40.0 or (section_new and page_position > 28.0):
                        page_position = 0.0
                        documentation.writelines([
                            f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                                '',
                                '<span class="page-break"></span>',
                            ]
                        ])

                    # Parse profile section
                    section_current = root.split(sep)[-1]
                    if section_new:
                        asset.writelines([
                            f'{line}{SetupAssets.GIT_SEPARATOR}' for line in [
                                '',
                                '\t#####',
                                f'\t## {PROJECT_NAME}: {root}',
                                '\t###',
                            ]
                        ])
                        if page_position > 0.0:
                            documentation.writelines([
                                f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                                    '',
                                    '---',
                                ]
                            ])
                        page_position += 6.0
                        title = ''
                        with open(join(root, '.title'), encoding='utf8',
                                  mode='r') as title_file:
                            title = title_file.read().strip()
                        documentation.writelines([
                            f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                                '',
                                f'## {title}',
                            ]
                        ])

                    # Parse profile file
                    alias_name = splitext(basename(alias_file))[0]
                    with open(alias_file, encoding='utf8', mode='r') as profile_file:
                        lines = profile_file.readlines()
                        page_position += 1.0
                        if len(lines) >= 2:
                            comment = lines[0].strip().lstrip('# ')
                            command = lines[1].strip().replace('"', '\\"')

                            # Inject alias configuration
                            asset.writelines([
                                f'{line}{SetupAssets.GIT_SEPARATOR}' for line in [
                                    '',
                                    f'\t# {comment}',
                                    f'\t{alias_name} = "{command}"',
                                ]
                            ])

                            # Inject alias documentation
                            documentation.writelines([
                                f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                                    '',
                                    f'* **git [{alias_name}]({SetupAssets.DOCS_ALIAS_LINK}) :**'
                                    f' {comment}',
                                ]
                            ])

                # Handle profile functions
                for function_file in sorted(glob(join(root, '*.function'))):

                    # Parse profile section
                    section_current = root.split(sep)[-1]
                    if section_last != section_current:
                        page_position += 6.0
                        section_last = section_current
                        asset.writelines([
                            f'{line}{SetupAssets.GIT_SEPARATOR}' for line in [
                                '',
                                '\t#####',
                                f'\t## {PROJECT_NAME}: {root}',
                                '\t###',
                            ]
                        ])

                    # Parse profile file
                    function_name = splitext(basename(function_file))[0]
                    with open(function_file, encoding='utf8', mode='r') as profile_file:
                        lines = profile_file.readlines()
                        page_position += 1.0
                        if len(lines) >= 2:
                            comment = lines[0].strip().lstrip('# ')
                            function_list = lines[1:]

                            # Prepare function syntax
                            function_list = [
                                line.replace('\\"', '\\\\"').replace('"', '\\"')
                                for line in function_list
                            ]
                            function_line = ''
                            if len(function_list) == 1:
                                function_line = f'{function_list[0].rstrip()} #'
                            else:
                                function_line = '\\'
                                for line in function_list:
                                    function_line += f'\n\t    {line.rstrip()}'
                                    if not function_line.endswith('\\'):
                                        function_line += ' \\'
                                function_line += '\n\t    # \\'
                                function_line += '\n\t'

                            # Inject function configuration
                            asset.writelines([
                                f'{line}{SetupAssets.GIT_SEPARATOR}' for line in [
                                    '',
                                    f'\t# {comment}',
                                    f'\t{function_name} = "! {function_line}"',
                                ]
                            ])

                            # Inject function documentation
                            documentation.writelines([
                                f'{line}{SetupAssets.DOCS_SEPARATOR}' for line in [
                                    '',
                                    f'* **git [{function_name}]({SetupAssets.DOCS_ALIAS_LINK}) :**'
                                    f' {comment}',
                                ]
                            ])

    # Assets initialization
    def initialize_options(self) -> None:
        self.clean = None
        self.prepare = None

    # Assets finalization
    def finalize_options(self) -> None:
        if self.clean:
            self.assets_keep = False
        elif self.prepare:
            self.assets_keep = True
        else:
            self.assets_keep = False

    # Assets entrypoint
    def run(self) -> None:

        # Git alias configuration
        SetupAssets.git_configuration_alias(self.assets_keep)

# Setup sources, pylint: disable=too-few-public-methods
class SetupSources(SourcesCommand):

    # Sources entrypoint
    def run(self) -> None:

        # Git alias configuration
        SetupAssets.git_configuration_alias()

        # Inherited entrypoint
        SourcesCommand.run(self)

# Setup build, pylint: disable=too-few-public-methods
class SetupBuild(BuildCommand):

    # Build entrypoint
    def run(self) -> None:

        # Git alias configuration
        SetupAssets.git_configuration_alias()

        # Inherited entrypoint
        BuildCommand.run(self)

# Setup configurations
setup(
    name=PROJECT_PACKAGE,
    use_scm_version=True,
    author=PROJECT_AUTHOR,
    author_email=PROJECT_EMAIL,
    license=PROJECT_LICENSE,
    description=PROJECT_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=PROJECT_URL,
    project_urls={
        'Bug Reports': f'{PROJECT_URL}/-/issues',
        'Changelog': f'{PROJECT_URL}/blob/main/CHANGELOG.md',
        'Documentation': f'{PROJECT_URL}#{PROJECT_NAME}',
        'Source': f'{PROJECT_URL}',
        'Statistics': f'https://pypistats.org/packages/{PROJECT_PACKAGE}'
    },
    packages=[
        PROJECT_MODULE,
    ] + [
        f'{PROJECT_MODULE}.{module}' for module in find_packages(
            where='src',
            exclude=['tests'],
        )
    ],
    package_data={
        f'{PROJECT_MODULE}.assets': [
            '.*',
            '*',
        ],
    },
    package_dir={
        PROJECT_MODULE: 'src',
    },
    setup_requires=['setuptools_scm'],
    install_requires=requirements,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    keywords=PROJECT_KEYWORDS,
    python_requires=','.join([
        '>=3',
        '!=3.0.*',
        '!=3.1.*',
        '!=3.2.*',
        '!=3.3.*',
        '!=3.4.*',
        '!=3.5.*',
        '!=3.6.*',
        '!=3.7.*',
    ]),
    cmdclass={
        'assets': SetupAssets,
        'sdist': SetupSources,
        'build': SetupBuild,
    },
    entry_points={
        'console_scripts': PROJECT_SCRIPTS,
    },
)

# Assets cleanup
for asset_file in SetupAssets.assets_list:
    if Path(asset_file).is_file():
        Path(asset_file).unlink()
