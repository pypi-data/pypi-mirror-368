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

from typing import Any, ClassVar

from envenom import config


class Singleton(type):
    __instances: ClassVar[dict[type[Any], Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls.__instances:  # type: ignore
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]


@config()
class DefaultMainCfg:
    pass


@config()
class SingletonMainCfg(metaclass=Singleton):
    pass


if __name__ == "__main__":
    default_cfg1 = DefaultMainCfg()
    default_cfg2 = DefaultMainCfg()

    singleton_cfg1 = SingletonMainCfg()
    singleton_cfg2 = SingletonMainCfg()

    assert id(default_cfg1) != id(default_cfg2), "DefaultMainCfg IDs are the same!"
    assert id(singleton_cfg1) == id(singleton_cfg2), "SingletonMainCfg IDs differ!"
