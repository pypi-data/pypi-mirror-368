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
from collections.abc import Callable
from dataclasses import dataclass, field

from envenom.vars import (
    DefaultFactoryVar,
    DefaultVar,
    Namespace,
    OptionalVar,
    Parser,
    RequiredVar,
    Var,
)


@dataclass(frozen=True, eq=True, order=True)
class Entry[T](metaclass=ABCMeta):
    parser: Parser[T]
    file: bool = field(kw_only=True, default=True)

    repr: bool = field(kw_only=True, default=True)
    hash: bool | None = field(kw_only=True, default=None)
    compare: bool = field(kw_only=True, default=True)

    @abstractmethod
    def get_var(self, name: str, namespace: Namespace | None) -> Var[T]: ...


class RequiredEntry[T](Entry[T]):
    def get_var(self, name: str, namespace: Namespace | None) -> RequiredVar[T]:
        return RequiredVar(name, self.parser, namespace=namespace, file=self.file)


class OptionalEntry[T](Entry[T]):
    def get_var(self, name: str, namespace: Namespace | None) -> OptionalVar[T]:
        return OptionalVar(name, self.parser, namespace=namespace, file=self.file)


@dataclass(frozen=True, eq=True, order=True)
class DefaultEntry[T](RequiredEntry[T]):
    default: T = field(kw_only=True)

    def get_var(self, name: str, namespace: Namespace | None) -> DefaultVar[T]:
        return DefaultVar(
            name,
            self.parser,
            default=self.default,
            namespace=namespace,
            file=self.file,
        )


@dataclass(frozen=True, eq=True, order=True)
class DefaultFactoryEntry[T](RequiredEntry[T]):
    default_factory: Callable[[], T] = field(kw_only=True)

    def get_var(self, name: str, namespace: Namespace | None) -> DefaultFactoryVar[T]:
        return DefaultFactoryVar(
            name,
            self.parser,
            default_factory=self.default_factory,
            namespace=namespace,
            file=self.file,
        )
