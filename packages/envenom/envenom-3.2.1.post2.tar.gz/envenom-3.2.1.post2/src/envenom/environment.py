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


import os
import re
from pathlib import Path
from typing import NewType

from encrustable import Err, Nothing, Ok, Option, Result, Some

from envenom.errors import (
    FileAccessDenied,
    FileNotFound,
    FileReadError,
)

Name = NewType("Name", str)
Value = NewType("Value", str)


allowed_characters_pattern = re.compile("[^0-9a-zA-Z_]+")


def construct_normalized_name(*segments: str) -> Name:
    return Name(
        "__".join(
            map(
                lambda s: re.sub(allowed_characters_pattern, "_", s).upper(),
                segments,
            )
        )
    )


def get_file_contents(file: Path) -> Result[Value, FileReadError]:
    try:
        with file.open("r") as f:
            return Ok(Value(f.read()))
    except FileNotFoundError as e:
        return Err(FileNotFound(file, original_error=e))
    except PermissionError as e:
        return Err(FileAccessDenied(file, original_error=e))


def get_env_var_value(name: Name) -> Option[Value]:
    if name in os.environ:
        return Some(Value(os.environ[name]))
    return Nothing()
