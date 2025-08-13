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
from typing import List, Optional

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

# Update commit authorship, pylint: disable=duplicate-code
def git_cauthor(from_commit: Optional[str] = None, ) -> int:

    # Variables
    git_hooks: List[str]
    name: str
    email: str
    result: int

    # Acquire author from commit
    if from_commit:
        name = Tools.run_output(
            [
                'git',
                'log',
                '--format=%an',
                f'{from_commit}^!',
            ],
            stderr=False,
        ).strip()
        email = Tools.run_output(
            [
                'git',
                'log',
                '--format=%ae',
                f'{from_commit}^!',
            ],
            stderr=False,
        ).strip()

    # Acquire author from user
    else:
        name = Tools.run_output(
            [
                'git',
                'config',
                '--get',
                'user.name',
            ],
            stderr=False,
        ).strip()
        email = Tools.run_output(
            [
                'git',
                'config',
                '--get',
                'user.email',
            ],
            stderr=False,
        ).strip()

    # Validate author
    if not name or not email:
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.RED} Ownership details are incomplete or missing'
              f'{Colors.RESET}')
        print(' ')
        Platform.flush()
        return -1

    # Authorship header
    print(' ')
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.GREEN} Amending commit with author \''
          f'{Colors.CYAN}{name} <{email}>'
          f'{Colors.GREEN}\''
          f'{Colors.RESET}')
    print(' ')
    Platform.flush()

    # Authorship update
    result = Tools.run_command(
        [
            'git',
            'commit',
            '--allow-empty',
            '--amend',
            f'--author=\'{name} <{email}>\'',
            '--no-edit',
            '--quiet',
        ],
        env={
            'GIT_COMMITTER_NAME': name,
            'GIT_COMMITTER_EMAIL': email,
        },
    )
    Platform.flush()

    # Detect hooks
    git_hooks = Tools.git_hooks()
    if any(git_hook in git_hooks for git_hook in [
            'pre-commit',
            'prepare-commit-msg',
            'commit-msg',
    ]):
        print(' ')

    # Authorship display
    Tools.run_command([
        'git',
        'show',
        '--pretty=fuller',
        '--stat',
    ])
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
    Tools.NAME = 'git cauthor'
    Tools.DESCRIPTION = 'Update commit authorship from current user or a commit'

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
        '--validate',
        dest='validate',
        action='store_true',
        help='Validate result by requesting user input',
    )
    group.add_argument(
        'from_commit',
        nargs='?',
        default=None,
        help='Get author from a commit instead of current user',
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
    result = git_cauthor(from_commit=options.from_commit, )

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
