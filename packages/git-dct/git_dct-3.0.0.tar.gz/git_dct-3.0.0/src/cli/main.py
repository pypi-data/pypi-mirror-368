#!/usr/bin/env python3

# Standard libraries
from argparse import (
    _ArgumentGroup,
    _MutuallyExclusiveGroup,
    ArgumentParser,
    Namespace,
    RawTextHelpFormatter,
)
from os import environ
from shutil import get_terminal_size
from sys import exit as sys_exit

# Components
from ..package.bundle import Bundle
from ..package.settings import Settings
from ..package.updates import Updates
from ..package.version import Version
from ..prints.colors import Colors
from ..system.platform import Platform
from .entrypoint import Entrypoint

# Constants
HELP_POSITION: int = 23

# Main, pylint: disable=too-many-branches,too-many-statements
def main() -> None:

    # Variables
    group: _ArgumentGroup
    result: Entrypoint.Result = Entrypoint.Result.ERROR
    subgroup: _MutuallyExclusiveGroup

    # Arguments creation
    parser: ArgumentParser = ArgumentParser(
        prog=Bundle.NAME,
        description=f'{Bundle.NAME}: {Bundle.DESCRIPTION}',
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

    # Arguments modes definitions
    group = parser.add_argument_group('modes arguments')
    subgroup = group.add_mutually_exclusive_group()
    subgroup.add_argument(
        '-e',
        '--enable',
        dest='enable',
        action='store_true',
        help='Enable profiles configurations',
    )
    subgroup.add_argument(
        '-d',
        '--disable',
        dest='disable',
        action='store_true',
        help='Disable profiles configurations',
    )

    # Arguments positional definitions
    group = parser.add_argument_group('positional arguments')
    group.add_argument(
        '--',
        dest='double_dash',
        action='store_true',
        help='Positional arguments separator (recommended)',
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

    # Arguments modes
    if not options.enable and not options.disable:
        result = Entrypoint.Result.CRITICAL

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
        result = Entrypoint.cli(options)

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
