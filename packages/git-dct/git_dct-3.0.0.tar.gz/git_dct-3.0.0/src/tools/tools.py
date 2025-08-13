# Standard libraries
from os import environ
from pathlib import Path
from subprocess import run, CalledProcessError, DEVNULL, PIPE
from typing import Dict, List, Optional

# Modules libraries
from questionary import text as questionary_text

# Components
from ..prints.colors import Colors

# Tools class
class Tools:

    # Members
    DESCRIPTION: str = ''
    NAME: str = ''

    # Run command
    @staticmethod
    def run_command(
        command: list[str],
        stdout: bool = True,
        stderr: bool = True,
        env: Optional[Dict[str, str]] = None,
    ) -> int:
        return run(
            command,
            stdout=None if stdout else DEVNULL,
            stderr=None if stderr else DEVNULL,
            text=True,
            check=False,
            env={
                **environ,
                **env
            } if env else None,
        ).returncode

    # Run with output
    @staticmethod
    def run_output(
        command: list[str],
        stderr: bool = True,
    ) -> str:
        try:
            result = run(
                command,
                text=True,
                check=True,
                stdout=PIPE,
                stderr=PIPE if stderr else DEVNULL,
            )
            return str(result.stdout.strip())
        except CalledProcessError as error:
            if stderr and error.stderr:
                return str(error.stderr.strip())
            return ''

    # Get git branches
    @staticmethod
    def git_branches(remote: str) -> List[str]:

        # Variables
        branches: List[str]

        # Acquire branches
        branches = sorted({
            line.split(f'{remote}/')[-1]
            for line in Tools.run_output(
                [
                    'git',
                    'branch',
                    '-ar',
                ],
                stderr=False,
            ).splitlines() if line.lstrip().startswith(remote) and '->' not in line
        })

        # Result
        return branches if branches else []

    # Get .git directory
    @staticmethod
    def git_dir() -> str:
        return Tools.run_output(
            [
                'git',
                'rev-parse',
                '--git-dir',
            ],
            stderr=False,
        )

    # Fetch remote branch
    @staticmethod
    def git_fetch(remote: str, branch: str) -> bool:
        return Tools.run_command([
            'git',
            'fetch',
            remote,
            branch,
        ]) == 0

    # Get git hooks
    @staticmethod
    def git_hooks() -> List[str]:

        # Variables
        git_dir: str
        hooks: List[str] = []

        # Access .git
        git_dir = Tools.git_dir()
        if not git_dir:
            return []

        # Detect hooks
        hooks_dir = Path(git_dir) / 'hooks'
        for hooks_item in hooks_dir.iterdir():
            if hooks_item.is_file() and not hooks_item.name.endswith('.sample'):
                hooks.append(hooks_item.name)

        # Result
        return hooks

    # Get git remotes
    @staticmethod
    def git_remotes() -> List[str]:

        # Variables
        remotes: List[str]

        # Acquire remotes
        remotes = Tools.run_output(
            [
                'git',
                'remote',
            ],
            stderr=False,
        ).splitlines()

        # Result
        return remotes if remotes else []

    # Select remote
    @staticmethod
    def select_remote() -> str:

        # Acquire remotes
        remotes = Tools.git_remotes()
        if not remotes:
            return ''

        # Detect single remote
        if len(remotes) == 1:
            return remotes[0]

        # Selector header
        print(' ')
        print(f'{Colors.GREEN} === {Tools.NAME} - Remote selection ==='
              f'{Colors.RESET}')
        print(' ')

        # Selector items
        for idx, remote in enumerate(remotes, start=1):
            remote_url = Tools.run_output([
                'git',
                'config',
                '--get',
                f'remote.{remote}.url',
            ])
            print(
                f'{Colors.YELLOW} [{idx}] {Colors.BOLD}{remote} - {Colors.YELLOW_THIN}{remote_url}'
                f'{Colors.RESET}')

        # Selector input
        print(' ')
        try:
            print(
                f'{Colors.YELLOW} {Tools.NAME}:'
                f'{Colors.BOLD} Choose a remote'
                f'{Colors.GREEN} [1-{len(remotes)}]'
                f' {Colors.YELLOW}:'
                f'{Colors.RESET}',
                end='',
            )
            choice: Optional[str] = questionary_text(
                message='',
                default='',
                validate=None,
                qmark='',
                style=None,
                multiline=False,
                instruction=None,
                lexer=None,
            ).ask()
            if choice and 1 <= int(choice) <= len(remotes):
                return remotes[int(choice) - 1]
            raise ValueError

        # Selector interruption
        except KeyboardInterrupt:
            print(' ')
            return ''

        # Selector fallback
        except (IndexError, ValueError):
            return ''

    # Select branch
    @staticmethod
    def select_branch(remote: str) -> str:

        # Validate input
        if not remote:
            return ''

        # Acquire branches
        branches = Tools.git_branches(remote)

        # Selector header
        print(' ')
        print(f'{Colors.GREEN} === {Tools.NAME} - Branch selection ==='
              f'{Colors.RESET}')
        print(' ')

        # Selector items
        print(f'{Colors.YELLOW} [0] {Colors.BOLD}Manual branch input'
              f'{Colors.RESET}')
        if branches:
            print(' ')
            for idx, branch in enumerate(branches, start=1):
                print(
                    f'{Colors.YELLOW} [{idx}] {Colors.BOLD}{branch} - {Colors.YELLOW_THIN}{remote}'
                    f'{Colors.RESET}')

        # Selector input
        print(' ')
        try:
            print(
                f'{Colors.YELLOW} {Tools.NAME}:'
                f'{Colors.BOLD} Select branch'
                f'{Colors.GREEN} [0-{len(branches)}]'
                f' {Colors.RESET}:',
                end='',
            )
            choice: Optional[str] = questionary_text(
                message='',
                default='',
                validate=None,
                qmark='',
                style=None,
                multiline=False,
                instruction=None,
                lexer=None,
            ).ask()

            # Manual branch input
            if choice and int(choice) == 0:
                print(
                    f'{Colors.YELLOW} {Tools.NAME}:'
                    f'{Colors.BOLD} Remote branch input'
                    f' {Colors.RESET}:',
                    end='',
                )
                branch = questionary_text(
                    message='',
                    default='',
                    validate=None,
                    qmark='',
                    style=None,
                    multiline=False,
                    instruction=None,
                    lexer=None,
                ).ask()
                return branch.strip() if branch else ''

            # Branch selection
            if choice and 1 <= int(choice) <= len(branches):
                return branches[int(choice) - 1]

            # Unknown selection
            raise ValueError

        # Selector interruption
        except KeyboardInterrupt:
            print(' ')
            return ''

        # Selector fallback
        except (IndexError, ValueError):
            return ''
