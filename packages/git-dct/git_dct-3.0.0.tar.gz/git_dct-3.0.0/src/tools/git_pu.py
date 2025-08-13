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
from time import sleep
from typing import List, Optional

# Modules libraries
from questionary import (
    confirm as questionary_confirm,
    press_any_key_to_continue as questionary_press_any_key_to_continue,
)

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

# Git push, pylint: disable=duplicate-code,too-many-arguments,too-many-branches,too-many-positional-arguments,too-many-return-statements,too-many-statements
def git_pu(
    remote: str,
    reference: str,
    tags: bool,
    no_verify: bool,
    ref: str,
    force: bool,
    confirmation: Optional[bool] = None,
) -> int:

    # Variables
    commands: List[str]
    result: int
    risky: bool = False

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
    if not tags and not reference:
        reference = Tools.select_branch(remote)

        # Validate branch
        if not reference:
            print(' ')
            print(f'{Colors.YELLOW} {Tools.NAME}:'
                  f'{Colors.RED} Remote branch selection missing...'
                  f'{Colors.RESET}')
            print(' ')
            Platform.flush()
            return -2

    # Push header
    push_target: str
    if tags and reference:
        push_target = f'tag {reference}'
    elif tags:
        push_target = 'tags'
    else:
        push_target = f"branch '{reference}'"
    print(' ')
    print(f'{Colors.GREEN} === {Tools.NAME} - Pushing'
          f' {push_target}'
          f' to remote \'{remote}\' ==='
          f'{Colors.RESET}')
    Platform.flush()

    # Show tags differences
    if tags:
        print(' ')
        commands = [
            'git',
            'push',
            '--dry-run',
        ]
        if no_verify:
            commands += [
                '--no-verify',
            ]
        if not reference:
            commands += [
                '--tags',
            ]
        commands += [
            remote,
        ]
        if reference:
            commands += [
                'tag',
                reference,
            ]
        result = Tools.run_command(commands)
        print(' ')
        Platform.flush()

        # Confirm tags overwrite
        if result != 0:
            risky = True
            print(
                f'{Colors.YELLOW} {Tools.NAME}:'
                f'{Colors.RED} Older tags will be lost on the remote. Continue ?'
                f'{Colors.RESET} [Enter]'
                f'{Colors.RESET}',
                end='',
            )
            Platform.flush()
            if confirmation is True and (not risky or force):
                print(' (Confirmed by argument)')
                Platform.flush()
                sleep(1)
            elif confirmation is False:
                return -3
            elif questionary_press_any_key_to_continue(
                    message='',
                    style=None,
            ).ask() is None:
                print(' ')
                return -3
            print(' ')
            Platform.flush()

    # Show git statistics
    else:
        _, commits_remote = git_stat(
            remote=remote,
            reference=reference,
            compare=ref,
            stats_only=True,
        )
        if commits_remote > 0:
            risky = True
            print(
                f'{Colors.YELLOW} {Tools.NAME}:'
                f'{Colors.RED} {commits_remote} commit{"s" if commits_remote > 1 else ""}'
                ' will be lost on the remote. Continue ?'
                f'{Colors.RESET} [Enter]'
                f'{Colors.RESET}',
                end='',
            )
            Platform.flush()
            if confirmation is True and (not risky or force):
                print(' (Confirmed by argument)')
                Platform.flush()
                sleep(1)
            elif confirmation is False:
                return -4
            elif questionary_press_any_key_to_continue(
                    message='',
                    style=None,
            ).ask() is None:
                print(' ')
                return -4
            print(' ')
            Platform.flush()

    # Prepare push commands
    commands = [
        'git',
        'push',
    ]

    # Configure force option
    if force or risky:
        commands += [
            '--force',
        ]

    # Configure verify option
    if no_verify:
        commands += [
            '--no-verify',
        ]

    # Configure tags option
    if tags and not reference:
        commands += [
            '--tags',
        ]

    # Configure remote argument
    commands += [
        remote,
    ]

    # Configure reference arguments
    if tags and reference:
        commands += [
            'tag',
            reference,
        ]
    elif not tags:
        commands += [
            f'{ref}:refs/heads/{reference}',
        ]

    # Confirm push to remote
    try:
        print(
            f'{Colors.YELLOW} {Tools.NAME}:'
            f'{Colors.RED_THIN if risky else Colors.GREEN_THIN} {" ".join(commands)}'
            f'{Colors.RED if risky else Colors.GREEN} # Update'
            f'{Colors.RESET}',
            end='',
        )
        if confirmation is True and (not risky or force):
            print(' (Confirmed by argument)')
            Platform.flush()
            sleep(1)
        elif confirmation is False:
            print(' (Canceled by argument)')
            print(' ')
            Platform.flush()
            sleep(1)
            return 0
        elif not questionary_confirm(
                message='',
                default=not risky,
                qmark='',
                style=None,
                auto_enter=True,
        ).ask():
            print(' ')
            Platform.flush()
            return 0

    # Selector interruption
    except KeyboardInterrupt:
        print(' ')
        Platform.flush()
        return -5

    # Push to remote
    print(' ')
    result = Tools.run_command(commands)
    print(' ')
    Platform.flush()

    # Result
    return result

# Main, pylint: disable=duplicate-code
def main() -> None:

    # Variables
    confirmation: Optional[bool]
    group: _ArgumentGroup
    result: int

    # Configure tool
    Tools.NAME = 'git pu'
    Tools.DESCRIPTION = 'Git push with interactive selection'

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
        '-f',
        '--force',
        dest='force',
        action='store_true',
        help='Force push changes',
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
        '-t',
        '--tags',
        dest='tags',
        action='store_true',
        help='Push tags instead of branches',
    )
    group.add_argument(
        '--all',
        dest='all',
        action='store_true',
        help='Iterate over available remotes and branches',
    )
    group.add_argument(
        '--no-verify',
        dest='no_verify',
        action='store_true',
        help='Disable pre-commit \'pre-push\' hooks',
    )
    group.add_argument(
        '--validate',
        dest='validate',
        action='store_true',
        help='Validate result by requesting user input',
    )
    group.add_argument(
        '-y',
        '--yes',
        dest='yes',
        action='store_true',
        help='Automatic yes to user inputs',
    )
    group.add_argument(
        '-n',
        '--no',
        dest='no',
        action='store_true',
        help='Automatic no to user inputs',
    )
    group.add_argument(
        'remote',
        nargs='?',
        default=None,
        help='Remote repository name (default: auto)',
    )
    group.add_argument(
        'reference',
        nargs='?',
        default=None,
        help='Branch or tag reference name (default: auto)',
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

    # Prepare confirmation
    if options.no:
        confirmation = False
    elif options.yes:
        confirmation = True
    else:
        confirmation = None

    # Iterate over remotes
    for remote in Tools.git_remotes() if options.all else [
            options.remote,
    ]:

        # Iterate over references
        for reference in Tools.git_branches(remote) if options.all else [
                options.reference,
        ]:

            # Run tool
            result = git_pu(
                remote=remote,
                reference=reference,
                force=options.force,
                no_verify=options.no_verify,
                ref=options.ref,
                tags=options.tags,
                confirmation=confirmation,
            )

            # Validate result
            if result < 0:
                break

    # Check for daily updates
    if updates.enabled and updates.daily:
        updates.check()

    # Validate result
    if options.validate and not options.yes:
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
