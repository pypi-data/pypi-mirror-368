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

from dataclasses import dataclass, field
from functools import cached_property

from envenom import config, namespace, optional, required, subconfig
from envenom.examples import print_config_tree


def derive_public_key(private_key: str) -> str:
    return private_key[:8]


@config(namespace("jwt"))
class JWTCfg:
    issuer: str = field(default="https://example.com")
    private_key: str = required()
    public_key: str | None = optional()

    @cached_property
    def current_public_key(self) -> str:
        return self.public_key or derive_public_key(self.private_key)


@dataclass(frozen=True, eq=True, order=True)
class OAuth2Cfg:
    jwt: JWTCfg = subconfig(JWTCfg)  # subconfig can be used in @dataclass!
    supports_oidc: bool = field(default=True)


@config()
class MainCfg:
    secret_key: str = required()
    oauth2: OAuth2Cfg = subconfig(OAuth2Cfg)


if __name__ == "__main__":
    cfg = MainCfg()

    print_config_tree(cfg)
