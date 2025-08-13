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

# Git fetch path and cherry-pick commits, pylint: disable=duplicate-code
def git_fcp(
    path: str,
    commits: int = 1,
) -> int:

    # Variables
    fetch_range: str
    result: int

    # Fetch header
    print(' ')
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.GREEN} Fetching from path '
          f'{Colors.CYAN}\'{path}\''
          f'{Colors.RESET}')
    Platform.flush()

    # Fetch path
    print(' ')
    result = Tools.run_command([
        'git',
        'fetch',
        path,
    ])
    Platform.flush()
    if result != 0:
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.RED} Failed to fetch from path'
              f'{Colors.RESET}')
        print(' ')
        Platform.flush()
        return result

    # Cherry-pick preparation
    fetch_range = f'FETCH_HEAD~{commits}..FETCH_HEAD' if commits > 1 else 'FETCH_HEAD'
    Tools.run_command(
        [
            'git',
            'cherry-pick',
            '--abort',
        ],
        stdout=False,
        stderr=False,
    )

    # Cherry-pick header
    print(' ')
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.GREEN} Cherry-picking'
          f'{Colors.CYAN} \'{fetch_range}\''
          f'{Colors.RESET}')
    print(' ')
    Platform.flush()

    # Cherry-pick fetched commits
    result = Tools.run_command([
        'git',
        'cherry-pick',
        fetch_range,
    ])
    Platform.flush()
    if result != 0:
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.RED} Cherry-pick failed'
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
    Tools.NAME = 'git fcp'
    Tools.DESCRIPTION = 'Git fetch path and cherry-pick commits'

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
        'path',
        nargs='?',
        default=None,
        help='Sources folder to fetch from',
    )
    group.add_argument(
        'commits',
        nargs='?',
        type=int,
        default=1,
        help='Number of commits to cherry-pick (default: %(default)s)',
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

    # Validate arguments
    if options.path is None:
        print(' ')
        parser.print_help()
        print(' ')
        Platform.flush()
        sys_exit(2)

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
    result = git_fcp(
        path=options.path,
        commits=options.commits,
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
