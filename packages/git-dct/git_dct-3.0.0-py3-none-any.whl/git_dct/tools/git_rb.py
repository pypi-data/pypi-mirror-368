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
from .git_stat import git_stat
from .tools import Tools

# Constants
HELP_POSITION: int = 23

# Git rebase, pylint: disable=duplicate-code
def git_rb(
    remote: str,
    branch: str,
    local: bool = False,
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

    # Rebase header
    print(' ')
    if local:
        print(f'{Colors.GREEN} === {Tools.NAME} - Rebasing'
              f' local commits'
              f' against branch \'{branch}\''
              f' from remote \'{remote}\' ==='
              f'{Colors.RESET}')
    else:
        print(f'{Colors.GREEN} === {Tools.NAME} - Rebasing'
              f' over branch \'{branch}\''
              f' from remote \'{remote}\' ==='
              f'{Colors.RESET}')
    Platform.flush()

    # Show git statistics
    commits_local, _ = git_stat(
        remote=remote,
        reference=branch,
        compare='HEAD',
        stats_only=False,
    )

    # Prepare rebase commands
    if local:
        commands = [
            'git',
            'rebase',
            '-i',
            f'HEAD~{commits_local}',
        ]
    else:
        commands = [
            'git',
            'rebase',
            'FETCH_HEAD',
        ]

    # Rebase over remote branch
    result = Tools.run_command(commands)
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
    Tools.NAME = 'git rb'
    Tools.DESCRIPTION = 'Git rebase with interactive selection'

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
        '--local',
        dest='local',
        action='store_true',
        help='Rebase only local commits against remote branch',
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
    result = git_rb(
        remote=options.remote,
        branch=options.branch,
        local=options.local,
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
