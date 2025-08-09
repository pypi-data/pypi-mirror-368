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


from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from encrustable import Err, Nothing, Ok, Option, Result, Some

from envenom.environment import (
    Name,
    Value,
    construct_normalized_name,
    get_env_var_value,
    get_file_contents,
)
from envenom.errors import (
    ConfigurationError,
    ConfigurationFileUnreadable,
    ConfigurationInvalid,
    ConfigurationMissing,
)
from envenom.parsers import Parser


@dataclass(frozen=True, eq=True, order=True, init=False)
class Namespace:
    segments: Iterable[str]

    def __init__(self, segment: str, *segments: str) -> None:
        object.__setattr__(self, "segments", (segment, *segments))

    def __truediv__(self, rhs: str) -> Namespace:
        return self.nested(rhs)

    def nested(self, rhs: str) -> Namespace:
        return Namespace(*self.segments, rhs)


type VarResult[T] = Result[T, ConfigurationError]


@dataclass(frozen=True, eq=True, order=True)
class Var[T](metaclass=ABCMeta):
    name: str = field(repr=True)
    parser: Parser[T] = field(repr=False)

    namespace: Namespace | None = field(default=None, repr=True, kw_only=True)
    file: bool = field(default=True, repr=False, kw_only=True)

    @cached_property
    def name_segments(self) -> Iterable[str]:
        if self.namespace is not None:
            return (*self.namespace.segments, self.name)
        return (self.name,)

    @cached_property
    def var_name(self) -> Name:
        return construct_normalized_name(*self.name_segments)

    @cached_property
    def file_var_name(self) -> Name:
        return construct_normalized_name(*self.name_segments, "FILE")

    @abstractmethod
    def get(self) -> T | None: ...

    def get_value(self) -> Option[VarResult[T]]:
        return (
            self.get_raw_value_from_env()
            .or_else(self.get_raw_value_from_file)
            .map(self.parse_result)
        )

    def get_raw_value_from_env(self) -> Option[VarResult[Value]]:
        return get_env_var_value(self.var_name).map(Ok)

    def get_raw_value_from_file(self) -> Option[VarResult[Value]]:
        if not self.file:
            return Nothing()

        return (
            get_env_var_value(self.file_var_name)
            .map(Path)
            .map(get_file_contents)
            .map(lambda r: r.map_err(ConfigurationFileUnreadable.From(self.var_name)))
        )

    def parse_result(self, r: VarResult[Value]) -> VarResult[T]:
        return r.map(self.parse).flatten()

    def parse(self, v: Value) -> VarResult[T]:
        try:
            return Ok(self.parser(v))
        except ValueError as e:
            return Err(ConfigurationInvalid.From[T](self.var_name, v, self.parser)(e))


class OptionalVar[T](Var[T]):
    def get(self) -> T | None:
        match self.result():
            case Some(r):
                match r:
                    case Ok(v):
                        return v
                    case Err(e):  # pragma: nobranch
                        raise e
            case Nothing():  # pragma: nobranch
                return None

    def result(self) -> Option[VarResult[T]]:
        return self.get_value()


class RequiredVar[T](Var[T]):
    def get(self) -> T:
        match self.result():
            case Ok(v):
                return v
            case Err(e):  # pragma: nobranch
                raise e

    def result(self) -> VarResult[T]:
        return self.get_value().unwrap_or(Err(ConfigurationMissing(self.var_name)))


@dataclass(frozen=True, eq=True, order=True)
class DefaultVar[T](RequiredVar[T]):
    default: T = field(repr=True, kw_only=True)

    def result(self) -> VarResult[T]:
        return self.get_value().unwrap_or(Ok(self.default))


@dataclass(frozen=True, eq=True, order=True)
class DefaultFactoryVar[T](RequiredVar[T]):
    default_factory: Callable[[], T] = field(repr=True, kw_only=True, compare=False)

    def result(self) -> VarResult[T]:
        return self.get_value().unwrap_or_else(lambda: Ok(self.default_factory()))
