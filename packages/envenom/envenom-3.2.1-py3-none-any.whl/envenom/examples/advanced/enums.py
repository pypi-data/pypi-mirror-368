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

import enum

from envenom import config, defaults, optional, required
from envenom.examples import print_config_tree


class ExitCode(enum.IntEnum):
    OK = 0
    MISSING_CONFIG = 1
    INVALID_CONFIG = 2
    CONFIG_FILE_UNREADABLE = 3


class LaunchCode(enum.StrEnum):
    OK = enum.auto()
    LAUNCHPAD_OBSTRUCTED = enum.auto()
    NOT_ENOUGH_FUEL = enum.auto()
    OVERRIDDEN = enum.auto()


class DaVinciCode(enum.Enum):
    UNSOLVED = enum.auto()
    SOLVED = enum.auto()


@config()
class MainCfg:
    exit_code: ExitCode = required(lambda c: ExitCode(int(c)))
    launch_code: LaunchCode | None = optional(LaunchCode)
    davinci_code: DaVinciCode = defaults(
        lambda c: DaVinciCode(int(c)), default=DaVinciCode.UNSOLVED
    )


if __name__ == "__main__":
    cfg = MainCfg()

    print_config_tree(cfg)
