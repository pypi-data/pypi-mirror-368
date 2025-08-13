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

# Git statistics, pylint: disable=duplicate-code
def git_stat(
    remote: str,
    reference: str,
    compare: str = 'HEAD',
    stats_only: bool = False,
) -> tuple[int, int]:

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
            return -1, -1

    # Select branch
    if not reference:
        reference = Tools.select_branch(remote)

        # Validate branch
        if not reference:
            print(' ')
            print(f'{Colors.YELLOW} {Tools.NAME}:'
                  f'{Colors.RED} Remote branch selection missing...'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return -2, -2

    # Fetch remote branch
    print(' ')
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.RESET} git fetch {remote} {reference};'
          f'{Colors.RESET} git rev-list --left-right {compare}...FETCH_HEAD'
          f'{Colors.RESET}')
    print(' ')
    Platform.flush()
    if not Tools.git_fetch(remote, reference):
        print(' ')
        print(f'{Colors.YELLOW} {Tools.NAME}:'
              f'{Colors.RED} Remote branch "{reference}" was not found...'
              f'{Colors.RESET}')
        print(' ')
        Platform.flush()
        return -3, -3

    # Show differences
    print(' ')
    if stats_only:
        if Tools.run_command([
                'git',
                '--no-pager',
                'diff',
                '--exit-code',
                '--stat',
                'FETCH_HEAD',
                f'{compare}',
        ]) != 0:
            print(' ')
        Platform.flush()
    else:
        if Tools.run_command([
                'git',
                '--no-pager',
                'diff',
                '--exit-code',
                f'FETCH_HEAD...{compare}',
        ]) != 0:
            print(' ')
        Platform.flush()

    # Show comparison stats
    rev_list = Tools.run_output([
        'git',
        'rev-list',
        '--left-right',
        f'FETCH_HEAD...{compare}',
    ])
    commits_local = sum(1 for line in rev_list.splitlines() if line.startswith('>'))
    commits_remote = sum(1 for line in rev_list.splitlines() if line.startswith('<'))
    print(f'{Colors.YELLOW} {Tools.NAME}:'
          f'{Colors.BOLD} Local commits:'
          f'{Colors.YELLOW} {commits_local} '
          f'{Colors.BOLD}| Upstream commits:'
          f'{Colors.YELLOW} {commits_remote}'
          f'{Colors.RESET}')
    print(' ')
    Platform.flush()

    # Result
    return commits_local, commits_remote

# Main, pylint: disable=duplicate-code
def main() -> None:

    # Variables
    group: _ArgumentGroup
    commits_remote: int

    # Configure tool
    Tools.NAME = 'git stat'
    Tools.DESCRIPTION = 'Git history with remote comparator'

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
        '-r',
        '--ref',
        dest='ref',
        action='store',
        default='HEAD',
        help='Reference to push (default: %(default)s)',
    )
    group.add_argument(
        '--stats-only',
        dest='stats_only',
        action='store_true',
        help='Show only stats of the differences',
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
    _, commits_remote = git_stat(
        remote=options.remote,
        reference=options.branch,
        compare=options.ref,
        stats_only=options.stats_only,
    )

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Validate result
    if options.validate:
        print(
            f'{Colors.YELLOW} {Tools.NAME}:'
            f'{Colors.GREEN if commits_remote >= 0 else Colors.RED} Press any key to continue...'
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
    sys_exit(0 if commits_remote >= 0 else commits_remote)

# Entrypoint
if __name__ == '__main__': # pragma: no cover
    main()
