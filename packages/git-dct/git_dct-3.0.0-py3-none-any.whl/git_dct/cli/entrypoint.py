#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace
from enum import Enum
from importlib.resources import as_file as resource_as_file, files as resources_files
from pathlib import Path
from subprocess import CalledProcessError, check_output, DEVNULL
from time import sleep

# Components
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..system.platform import Platform

# Entrypoint class, pylint: disable=too-few-public-methods
class Entrypoint:

    # Enumerations
    Result = Enum('Result', [
        'SUCCESS',
        'FINALIZE',
        'ERROR',
        'CRITICAL',
    ])

    # Assets
    ASSET_GIT_CONFIGURATION_ALIAS: str = 'alias.gitconfig'

    # CLI
    @staticmethod
    def cli(options: Namespace) -> Result:

        # Variable
        asset_path: Path

        # Enable or disable profiles configurations
        if options.enable or options.disable:

            # Acquire asset configuration
            try:
                with resource_as_file(
                        resources_files(Bundle.RESOURCES_ASSETS) \
                            .joinpath(Entrypoint.ASSET_GIT_CONFIGURATION_ALIAS)
                        ) as file_path:
                    asset_path = file_path # pragma: no cover
            except ModuleNotFoundError:
                asset_path = Path(__file__).resolve().parent.parent.joinpath(
                    'assets').joinpath(Entrypoint.ASSET_GIT_CONFIGURATION_ALIAS)

            # Disable asset configuration
            if options.disable:
                print(' ')
                print(f'{Colors.BOLD} - Disable Git alias configurations: '
                      f'{Colors.GREEN}{asset_path}'
                      f'{Colors.RESET}')
                Platform.flush()

            # Reset asset configuration
            if options.enable or options.disable:
                try:
                    check_output(
                        [
                            'git',
                            'config',
                            '--global',
                            '--unset',
                            'include.path',
                            str(asset_path),
                        ],
                        stderr=DEVNULL,
                    )
                except CalledProcessError:
                    pass

            # Enable asset configuration
            if options.enable:
                print(' ')
                print(f'{Colors.BOLD} - Enable Git alias configurations: '
                      f'{Colors.GREEN}{asset_path}'
                      f'{Colors.RESET}')
                Platform.flush()
                check_output([
                    'git',
                    'config',
                    '--global',
                    '--add',
                    'include.path',
                    str(asset_path),
                ])

            # Delay execution
            sleep(1)

        # Result
        return Entrypoint.Result.SUCCESS
