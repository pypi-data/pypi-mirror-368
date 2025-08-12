#!/usr/bin/env python3

# Standard libraries
from os import linesep
from pathlib import Path
from typing import List, Optional

# Modules libraries
from packaging.version import Version as PackageVersion

# Components
from ..system.platform import Platform
from ..system.commands import Commands

# Commitizen class
class Commitizen:

    # Constants
    BINARY: str = 'cz'
    CONFIGURATION_EXTENSION: str = '.yaml'
    CONFIGURATION_FILE: str = '.cz.yaml'
    MARKER: str = '# register-python-argcomplete cz'
    PACKAGE: str = 'commitizen'
    SOURCES: str = 'git+https://github.com/AdrianDC/commitizen.git'
    VERSION_COMPATIBLE: str = '4.8.2+adriandc.20250608'

    # Internals
    __flags_configuration: List[str] = []

    # Check
    @staticmethod
    def check(rev_range: str) -> bool:

        # Check commitizen range
        return Commands.run(
            Commitizen.BINARY, Commitizen.__flags_configuration + [
                '--no-raise',
                '23',
                'check',
                '--rev-range',
                rev_range,
            ])

    # Compatible
    @staticmethod
    def compatible() -> bool:

        # Missing commitizen
        if not Commitizen.exists():
            return False

        # Get commitizen version
        version: str = Commands.output(Commitizen.BINARY, [
            'version',
        ])

        # Result
        return PackageVersion(version) >= PackageVersion(Commitizen.VERSION_COMPATIBLE)

    # Configure
    @staticmethod
    def configure() -> str:

        # Variables
        bashrc: Optional[Path] = Platform.bashrc()

        # Configure commitizen in bashrc
        if bashrc:
            with open(bashrc, encoding='utf8', mode='a') as f:
                f.write(f'{linesep}')
                f.write(f'# register-python-argcomplete cz{linesep}')
                f.write(f'eval "$(register-python-argcomplete cz)"{linesep}')
                return str(bashrc)

        # Fallback
        return ''

    # Configured
    @staticmethod
    def configured() -> bool:

        # Variables
        bashrc: Optional[Path] = Platform.bashrc()

        # Missing bashrc
        if not bashrc:
            return False

        # Result
        return Commands.grep(
            bashrc,
            Commitizen.MARKER,
        )

    # Dependencies
    @staticmethod
    def dependencies() -> bool:

        # Uninstall existing commitizen
        if Commands.exists(Commitizen.BINARY):
            Commands.pip([
                'uninstall',
                Commitizen.PACKAGE,
            ])

        # Install commitizen
        return Commands.pip([
            'install',
            f'{Commitizen.SOURCES}@{Commitizen.VERSION_COMPATIBLE}',
        ])

    # Exists
    @staticmethod
    def exists() -> bool:

        # Check if binary exists
        return Commands.exists(Commitizen.BINARY)

    # Set configuration
    @staticmethod
    def set_configuration(file: str) -> None:

        # Set configuration flags
        if file:
            Commitizen.__flags_configuration = [
                '--config',
                file,
            ]
        else:
            Commitizen.__flags_configuration = []
