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

from dataclasses import dataclass

from envenom import config, optional, required
from envenom.examples import print_config_tree
from envenom.parsers import bool_parser, make_bool_parser, make_list_parser


@dataclass(frozen=True, eq=True, order=True)
class Box[T]:
    item: T


def boxed_int_parser(v: str) -> Box[int]:
    return Box(item=int(v))


def boxed_bytes_parser(v: str) -> Box[bytes]:
    return Box(item=v.encode())


@config()
class MainCfg:
    boxed_int: Box[int] = required(boxed_int_parser)
    boxed_bytes: Box[bytes] = required(boxed_bytes_parser)
    optional_boxed_bytes: Box[bytes] | None = optional(boxed_bytes_parser)

    default_boolean: bool = required(bool_parser)
    custom_boolean: bool = required(
        make_bool_parser(true_values={"mhm"}, false_values={"uhhuh"})
    )

    required_list: list[str] = required(make_list_parser(separator=", "))
    required_empty_list: list[str] = required(make_list_parser(separator=", "))
    optional_list: list[str] | None = optional(make_list_parser(separator=", "))
    optional_empty_list: list[str] | None = optional(make_list_parser(separator=", "))
    optional_not_provided_list: list[str] | None = optional(
        make_list_parser(separator=", ")
    )
    custom_list: list[int] = required(make_list_parser(int, separator=";"))


if __name__ == "__main__":
    cfg = MainCfg()

    print_config_tree(cfg)
