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

from envenom import config, namespace, required, subconfig
from envenom.examples import print_config_tree

ns1 = namespace("ns1")
ns_2 = namespace("ns-2")


@config(ns_2)
class AnotherNamespaceCfg:
    some_value: str = required()


@config(ns1 / "sub")
class NestedNamespaceCfg:
    some_value: str = required()


@config(ns1)
class OuterNamespaceCfg:
    some_value: str = required()
    nested_namespace: NestedNamespaceCfg = subconfig(NestedNamespaceCfg)


@config()
class MainCfg:
    some_value: str = required()
    outer_namespace: OuterNamespaceCfg = subconfig(OuterNamespaceCfg)
    another_namespace: AnotherNamespaceCfg = subconfig(AnotherNamespaceCfg)


if __name__ == "__main__":
    cfg = MainCfg()

    print_config_tree(cfg)
