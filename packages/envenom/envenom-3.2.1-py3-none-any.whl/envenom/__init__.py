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

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, overload

from envenom.entries import (
    DefaultEntry,
    DefaultFactoryEntry,
    Entry,
    OptionalEntry,
    RequiredEntry,
)
from envenom.vars import Namespace

# Why so much 'type: ignore' around here?
#
# It's a hard truth to accept, but dataclasses are lying to us.
#
# When the `field` function is called it creates a `Field[T]` object, but it tells
# us that it really returns a `T` (or sometimes `None`), I swear, pretty please.
#
# Because we're exposing a similar interface and hooking into this exact layer,
# we therefore need to lie to our consumers on the API side just like `field` would,
# except of course we supply three versions of the `field` function, so we need
# to lie on all three fronts.


def config[T](
    namespace: Namespace | None = None,
    *,
    repr: bool = True,
    eq: bool = True,
    order: bool = True,
    frozen: bool = True,
) -> Callable[[type[T]], type[T]]:
    """
    Defines a new config class.

    Parameters:
        namespace:  A `Namespace` object representing the environment variable
                    namespaces to pull config values from. This allows different
                    configuration items with the same base name to exist in
                    different contexts.
        repr:       Same as for `dataclasses.dataclass`.
        eq:         Same as for `dataclasses.dataclass`.
        order:      Same as for `dataclasses.dataclass`.
        frozen:     Same as for `dataclasses.dataclass`.

    Returns:
        A callable which transforms a class into a new config class.

    Example:
        Use this as a class decorator:

        ```python
        from envenom import config, required


        @config()
        class AppCfg:
            secret_key: str = required()
        ```

    """

    def __wrapper(cls: type[T]) -> type[T]:
        annotations = cls.__annotations__
        new_fields: dict[str, Any] = {
            name: field(
                init=False,
                repr=entry.repr,
                hash=entry.hash,
                compare=entry.compare,
                default_factory=entry.get_var(name, namespace).get,
                metadata={
                    "config": cls,
                    "type": annotations[name],
                },
            )
            for name, entry in cls.__dict__.items()
            if isinstance(entry, Entry) and name in annotations
        }

        for name, f in new_fields.items():
            setattr(cls, name, f)

        return dataclass(repr=repr, eq=eq, order=order, frozen=frozen)(cls)

    return __wrapper


def required[T](
    parser: Callable[[str], T] = str,
    *,
    file: bool = True,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T:
    """
    Creates a required config field.

    Fields created with this function will have a type of `T`.

    Parameters:
        parser: Callable which will convert a single `str` into the
                desired object type.
        file:   Whether to try and retrieve the configuration value from a file
                using the environment variable with the `__FILE` suffix.
        repr:               Same as for `dataclasses.field`.
        hash:               Same as for `dataclasses.field`.
        compare:            Same as for `dataclasses.field`.

    Returns:
        An object of type `T` instantiated from the environment.

    Example:
        ```python
        from envenom import config, required


        @config()
        class AppCfg:
            secret_key: str = required()
        ```

    """

    return RequiredEntry(
        parser,
        file=file,
        repr=repr,
        hash=hash,
        compare=compare,
    )  # type: ignore


def optional[T](
    parser: Callable[[str], T] = str,
    *,
    file: bool = True,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T | None:
    """
    Creates an optional config field.

    Fields created with this function will have a type of `T | None`.

    Parameters:
        parser: Callable which will convert a single `str` into the
                desired object type.
        file:   Whether to try and retrieve the configuration value from a file
                using the environment variable with the `__FILE` suffix.
        repr:               Same as for `dataclasses.field`.
        hash:               Same as for `dataclasses.field`.
        compare:            Same as for `dataclasses.field`.

    Returns:
        An object of type `T` instantiated from the environment if available,
            otherwise `None`.

    Example:
        ```python
        from envenom import config, optional


        @config()
        class AppCfg:
            signature: str | None = optional()
        ```

    """

    return OptionalEntry(
        parser,
        file=file,
        repr=repr,
        hash=hash,
        compare=compare,
    )  # type: ignore


@overload
def defaults[T](
    parser: Callable[[str], T] = str,
    *,
    default: T,
    file: bool = True,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T: ...


@overload
def defaults[T](
    parser: Callable[[str], T] = str,
    *,
    default_factory: Callable[[], T],
    file: bool = True,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T: ...


def defaults[T](
    parser: Callable[[str], T] = str,
    *,
    default: T | None = None,
    default_factory: Callable[[], T] | None = None,
    file: bool = True,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T:
    """
    Creates an optional config field with a default value. The default value
    can be static, or can be created on instantiation by a factory function.

    One of `default` and `default_factory` parameters is required.

    Fields created with this function will have a type of `T`.

    Parameters:
        parser:             Callable which will convert a single `str` into the
                            desired object type.
        default:            The default to return if value is not set in the
                            environment.
        default_factory:    The default factory to call if value is not set in the
                            environment.
        file:               Whether to try and retrieve the configuration value
                            from a file using the environment variable with the
                            `__FILE` suffix.
        repr:               Same as for `dataclasses.field`.
        hash:               Same as for `dataclasses.field`.
        compare:            Same as for `dataclasses.field`.

    Returns:
        An object of type `T` instantiated from the environment if available,
            otherwise the default value.

    Example:
        ```python
        from envenom import config, defaults
        from envenom.parsers import make_bool_parser


        @config()
        class AppCfg:
            feature_flag: bool = defaults(make_bool_parser(), default=False)
        ```

    """

    if default is not None:
        return DefaultEntry(
            parser,
            default=default,
            file=file,
            repr=repr,
            hash=hash,
            compare=compare,
        )  # type: ignore

    if default_factory is not None:
        return DefaultFactoryEntry(
            parser,
            default_factory=default_factory,
            file=file,
            repr=repr,
            hash=hash,
            compare=compare,
        )  # type: ignore

    raise RuntimeError("neither `default` nor `default_factory` provided")


def subconfig[T](
    cls: Callable[[], T],
    /,
    *,
    repr: bool = True,
    hash: bool | None = True,
    compare: bool = True,
) -> T:
    """
    Includes another config class as a field of the current config class.

    This is really a convenvience function for expressing a dataclass
    field with a default factory, but it expresses the intention better too.

    `subconfig(cls)` is equivalent to `field(default_factory=cls)`.

    This function, unlike others in this module, is compatible with the
    standard `@dataclass` decorator.

    Parameters:
        cls:            Subconfig class to include as a field in this config class.
        repr:           Same as for `dataclasses.field`.
        hash:           Same as for `dataclasses.field`.
        compare:        Same as for `dataclasses.field`.

    Returns:
        An instantiated object of the subconfig class.

    Example:
        ```python
        from envenom import config, required, subconfig


        @config()
        class SubCfg:
            secret_key: str = required()


        @config()
        class AppCfg:
            subcfg: SubCfg = subconfig(SubCfg)
        ```
    """

    return field(default_factory=cls, repr=repr, hash=hash, compare=compare)


def namespace(segment: str, *segments: str) -> Namespace:
    """
    Defines a new config class namespace.

    Parameters:
        *segments:  Segments (a sequence of `str`s) that will form the
                    nested levels of the namespace.

    Returns:
        A new `Namespace` object.

    Example:
        ```python
        from envenom import config, namespace, required


        @config(namespace("app"))
        class AppCfg:
            secret_key: str = required()
        ```

    """

    return Namespace(segment, *segments)
