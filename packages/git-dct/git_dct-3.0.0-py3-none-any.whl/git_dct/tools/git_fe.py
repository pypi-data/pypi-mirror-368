#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from shutil import get_terminal_size
from sys import exit as sys_exit
from typing import List

# Modules libraries
from questionary import press_any_key_to_continue as questionary_press_any_key_to_continue

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..prints.colors import Colors
from ..system.platform import Platform
from .tools import Tools

# Constants
HELP_POSITION: int = 23

# Git fetch, pylint: disable=duplicate-code
def git_fe(
    remote: str,
    branch: str,
    tags: bool = False,
    reset: bool = False,
) -> int:

    # Variables
    commands: List[str]
    result: int

    # Select remote
    if not remote:
        remote = Tools.select_remote()

        # Validate remote
        if not remote:
            print(' ')
            print(f'{Colors.YELLOW} {Tools.NAME}:'
                  f'{Colors.RED} Remote selection missing...'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return -1

    # Select branch
    if not branch:
        branch = Tools.select_branch(remote)

        # Validate branch
        if not branch:
            print(' ')
            print(f'{Colors.YELLOW} {Tools.NAME}:'
                  f'{Colors.RED} Remote branch selection missing...'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return -3

    # Cleanup local tags
    if tags:

        # Get existing tags
        tags_list = Tools.run_output([
            'git',
            'tag',
        ]).strip().splitlines()

        # Delete existing tags
        for tag_name in tags_list:
            Tools.run_command(
                [
                    'git',
                    'tag',
                    '-d',
                    tag_name,
                ],
                stdout=False,
            )

    # Rebase header
    print(' ')
    print(f'{Colors.GREEN} === {Tools.NAME} - Fetching branch \''
          f'{Colors.CYAN}{branch}'
          f'{Colors.GREEN}\' from remote \''
          f'{Colors.CYAN}{remote}'
          f'{Colors.GREEN}\' ==='
          f'{Colors.RESET}')
    Platform.flush()

    # Prepare fetch commands
    commands = [
        'git',
        'fetch',
    ]
    if tags:
        commands += [
            '--tags',
        ]
    commands += [
        remote,
        branch,
    ]

    # Fetch from remote branch
    print(' ')
    result = Tools.run_command(commands)
    Platform.flush()

    # Reset mode
    if reset:

        # Prepare reset commands
        commands = [
            'git',
            'reset',
            '--hard',
            'FETCH_HEAD',
        ]

        # Reset to fetched remote
        print(' ')
        result = Tools.run_command(commands)
        Platform.flush()

    # Get commit description
    tag_describe = Tools.run_output([
        'git',
        'describe',
        '--always',
    ])

    # Commit informations
    if reset:
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.BOLD} Current HEAD is'
              f'{Colors.CYAN} {tag_describe}'
              f'{Colors.RESET}')
        Platform.flush()

    # Footer
    print(' ')
    Platform.flush()

    # Result
    return result

# Main, pylint: disable=duplicate-code
def main() -> None:

    # Variables
    group: _ArgumentGroup
    result: int

    # Configure tool
    Tools.NAME = 'git fe'
    Tools.DESCRIPTION = 'Git fetch and reset sources with interactive selection'

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Tools.NAME,
        description=f'{Tools.NAME}: {Tools.DESCRIPTION} ({Bundle.NAME})',
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

    # Arguments tool definitions
    group = parser.add_argument_group('tool arguments')
    group.add_argument(
        '-h',
        '--help',
        dest='help',
        action='store_true',
        help='Show this help message',
    )
    group.add_argument(
        '--reset',
        dest='reset',
        action='store_true',
        help='Reset sources to fetched remote branch',
    )
    group.add_argument(
        '--tags',
        dest='tags',
        action='store_true',
        help='Fetch and refresh all tags',
    )
    group.add_argument(
        '--validate',
        dest='validate',
        action='store_true',
        help='Validate result by requesting user input',
    )
    group.add_argument(
        'remote',
        nargs='?',
        default=None,
        help='Remote repository name (default: auto)',
    )
    group.add_argument(
        'branch',
        nargs='?',
        default=None,
        help='Branch name (default: auto)',
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

    # Prepare colors
    Colors.prepare()

    # Instantiate updates
    updates: Updates = Updates(
        name=Bundle.PACKAGE,
        settings=settings,
    )

    # Run tool
    result = git_fe(
        remote=options.remote,
        branch=options.branch,
        tags=options.tags,
        reset=options.reset,
    )

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Validate result
    if options.validate:
        print(
            f'{Colors.YELLOW} {Tools.NAME}:'
            f'{Colors.GREEN if result >= 0 else Colors.RED} Press any key to continue...'
            f'{Colors.RESET} [Enter]'
            f'{Colors.RESET}',
            end='',
        )
        questionary_press_any_key_to_continue(
            message='',
            style=None,
        ).ask()
        print(' ')

    # Result
    sys_exit(0 if result >= 0 else result)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
