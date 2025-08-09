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
class FileReadError(Exception, metaclass=ABCMeta):
    """
    Base exception class for any errors relating to reading the contents of a file.
    """

    path: Path
    """Path to the file containing the value."""

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True, eq=True, order=True)
class FileNotFound(FileReadError):
    """
    Specified path does not point to a valid file.
    """

    original_error: FileNotFoundError = field(kw_only=True, repr=False, compare=False)
    """The original `FileNotFoundError` that was the cause of this error."""

    def __str__(self) -> str:
        return f"file '{self.path}' does not exist"


@dataclass(frozen=True, eq=True, order=True)
class FileAccessDenied(FileReadError):
    """
    Specified path points to a file that could not be read.
    """

    original_error: PermissionError = field(kw_only=True, repr=False, compare=False)
    """The original `PermissionError` that was the cause of this error."""

    def __str__(self) -> str:
        return f"access to file '{self.path}' has been denied"


# -------------------------------------------------------------------------------------


@dataclass(frozen=True, eq=True, order=True)
class ConfigurationError(Exception, metaclass=ABCMeta):
    """
    Base exception class for any errors relating to a specific configuration field.
    """

    name: str
    """Name of the environment variable causing the error."""

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
    """Value of the environment variable causing the error."""

    parser: Parser[T] = field(compare=False)
    """Parser used to parse the value for this field."""

    original_error: ValueError = field(kw_only=True, compare=False)
    """The original `ValueError` that was thrown during parsing of the value."""

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
    """Path to the file containing the value."""

    original_error: FileReadError = field(kw_only=True, compare=False)
    """The original `FileReadError` that was the cause of this error."""

    def __str__(self) -> str:
        return (
            f"configuration '{self.name}' " f"could not be read from file '{self.path}'"
        )

    @dataclass(frozen=True, eq=True, order=True)
    class From:
        name: str

        def __call__(self, e: FileReadError) -> ConfigurationError:
            return ConfigurationFileUnreadable(self.name, e.path, original_error=e)
