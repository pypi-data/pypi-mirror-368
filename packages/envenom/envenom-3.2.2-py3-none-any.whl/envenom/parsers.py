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

from collections.abc import Callable, Collection

type Parser[T] = Callable[[str], T]


def make_bool_parser(
    true_values: Collection[str] = {"t", "true", "y", "yes", "1", "+", "✓"},
    false_values: Collection[str] = {"f", "false", "n", "no", "0", "-", "✗"},
) -> Parser[bool]:
    """
    This handles one of the most basic conversions: `str` -> `bool` in a sane way.

    `bool`, unlike basic type converters like `int`, will not just do the right thing,
    so we need a specialized parser.

    This parser is case-insensitive.

    Parameters:
        true_values:    Collection of values which will evaluate to `True`.
        false_values:   Collection of values which will evaluate to `False`.

    Returns:
        A parser callable which will parse the `str` semantically into a `bool`.

    Example:
        ```python
        from envenom import config, defaults
        from envenom.parsers import make_bool_parser


        @config()
        class AppCfg:
            feature_flag: bool = defaults(make_bool_parser(), default=False)
        ```

    """

    ts = set(map(lambda s: s.lower(), true_values))
    fs = set(map(lambda s: s.lower(), false_values))

    def __parser(v: str) -> bool:
        normalized = v.lower()

        if normalized in ts:
            return True
        if normalized in fs:
            return False

        raise ValueError(v)

    return __parser


bool_parser = make_bool_parser()
"""
A default instantiation of the `make_bool_parser` factory.
"""


def make_list_parser[T](
    parser: Parser[T] = str, *, separator: str = ","
) -> Parser[list[T]]:
    """
    This handles one of the most basic conversions: lists of items.

    Parameters:
        parser:     Parser applied to each list element.
        separator:  Separator for splitting the list.

    Returns:
        A parser callable which will parse the `str` into a list of objects of
            type `T` resulting from splitting the value using the delimiter
            and applying the parser function on each element.

    Example:
        ```python
        from uuid import UUID

        from envenom import config, required
        from envenom.parsers import make_list_parser


        @config()
        class AppCfg:
            admin_uuids: list[UUID] = required(make_list_parser(UUID, separator=";"))
        ```

    """

    def __parser(v: str) -> list[T]:
        if not v:
            return []
        return [parser(s) for s in v.split(separator)]

    return __parser
