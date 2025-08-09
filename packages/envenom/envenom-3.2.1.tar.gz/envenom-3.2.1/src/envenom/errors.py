# `envenom` - an elegant application configurator for the more civilized age
# Copyright (C) 2024-2025 Artur Ciesielski <artur.ciesielski@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from envenom.parsers import Parser

# -------------------------------------------------------------------------------------


@dataclass(frozen=True, eq=True, order=True)
class FileNotFound(Exception):
    """
    Specified path does not point to a valid file.
    """

    path: Path
    original_error: FileNotFoundError = field(kw_only=True, repr=False, compare=False)

    def __str__(self) -> str:
        return f"file '{self.path}' does not exist"


@dataclass(frozen=True, eq=True, order=True)
class FileAccessDenied(Exception):
    """
    Specified path points to a file that could not be read.
    """

    path: Path
    original_error: PermissionError = field(kw_only=True, repr=False, compare=False)

    def __str__(self) -> str:
        return f"access to file '{self.path}' has been denied"


type FileReadError = FileNotFound | FileAccessDenied


# -------------------------------------------------------------------------------------


@dataclass(frozen=True, eq=True, order=True)
class ConfigurationError(Exception, metaclass=ABCMeta):
    """
    Base exception class for any errors relating to a specific configuration field.
    """

    name: str

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True, eq=True, order=True)
class ConfigurationMissing(ConfigurationError):
    """
    Required configuration value is missing in the environment.
    """

    def __str__(self) -> str:
        return f"required configuration '{self.name}' is missing in the environment"


@dataclass(frozen=True, eq=True, order=True)
class ConfigurationInvalid[T](ConfigurationError):
    """
    Value for a specific field is invalid for the declared type (conversion failed).
    """

    value: str
    parser: Parser[T] = field(compare=False)
    original_error: ValueError = field(kw_only=True, compare=False)

    def __str__(self) -> str:
        return f"configuration '{self.name}' has invalid value '{self.value}'"

    @dataclass(frozen=True, eq=True, order=True)
    class From[FT]:
        name: str
        value: str
        parser: Parser[FT] = field(compare=False)

        def __call__(self, e: ValueError) -> ConfigurationError:
            return ConfigurationInvalid(
                self.name, self.value, self.parser, original_error=e
            )


@dataclass(frozen=True, eq=True, order=True)
class ConfigurationFileUnreadable(ConfigurationError):
    """
    Environment variable with a `__FILE` suffix is set and
    the configuration value cannot be read from the file.
    """

    path: Path
    original_error: FileReadError = field(kw_only=True, compare=False)

    def __str__(self) -> str:
        return (
            f"configuration '{self.name}' " f"could not be read from file '{self.path}'"
        )

    @dataclass(frozen=True, eq=True, order=True)
    class From:
        name: str

        def __call__(self, e: FileReadError) -> ConfigurationError:
            return ConfigurationFileUnreadable(self.name, e.path, original_error=e)
