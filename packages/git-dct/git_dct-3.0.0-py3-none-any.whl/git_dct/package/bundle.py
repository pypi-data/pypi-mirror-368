#!/usr/bin/env python3

# Bundle class, pylint: disable=too-few-public-methods
class Bundle:

    # Modules
    MODULE: str = 'git_dct'

    # Names
    NAME: str = 'git-dct'

    # Packages
    PACKAGE: str = 'git-dct'

    # Details
    DESCRIPTION: str = 'Git development CLI tools for daily usage'

    # Resources
    RESOURCES_ASSETS: str = f'{MODULE}.assets'

    # Sources
    REPOSITORY: str = 'https://gitlab.com/RadianDevCore/tools/git-dct'

    # Releases
    RELEASE_FIRST_TIMESTAMP: int = 1579337311

    # Environment
    ENV_DEBUG_UPDATES_DAILY: str = 'DEBUG_UPDATES_DAILY'
    ENV_DEBUG_UPDATES_DISABLE: str = 'DEBUG_UPDATES_DISABLE'
    ENV_DEBUG_UPDATES_FAKE: str = 'DEBUG_UPDATES_FAKE'
    ENV_DEBUG_UPDATES_OFFLINE: str = 'DEBUG_UPDATES_OFFLINE'
    ENV_DEBUG_VERSION_FAKE: str = 'DEBUG_VERSION_FAKE'
    ENV_FORCE_COLOR: str = 'FORCE_COLOR'
    ENV_NO_COLOR: str = 'NO_COLOR'
