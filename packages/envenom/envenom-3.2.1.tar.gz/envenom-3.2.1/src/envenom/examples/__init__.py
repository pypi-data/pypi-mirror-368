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

from dataclasses import fields, is_dataclass


def print_config_tree(cfg: object) -> None:
    print("-----")
    print("cfg:")
    print_config_nested(cfg, indent=2)
    print("-----")


def print_config_nested(cfg: object, indent: int) -> None:
    for field in fields(cfg):  # type: ignore
        value = getattr(cfg, field.name)
        print(f"{" " * indent}{field.name}: ", end="")
        if not is_dataclass(value):
            print(repr(value))
        else:
            print()
            print_config_nested(value, indent=indent + 2)
