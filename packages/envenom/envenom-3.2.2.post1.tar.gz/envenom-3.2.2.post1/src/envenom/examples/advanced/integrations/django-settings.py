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

from typing import Any

from django.core.exceptions import ImproperlyConfigured

from envenom import config, defaults, optional, required
from envenom.errors import ConfigurationError, ConfigurationInvalid
from envenom.parsers import bool_parser


@config()
class DjangoCfg:
    secret_key: str = required()
    service_port: int | None = optional(int)
    feature_flag: bool = defaults(bool_parser, default=False)


try:
    cfg = DjangoCfg()
except ConfigurationInvalid as ci:
    ci: ConfigurationInvalid[Any]
    raise ImproperlyConfigured(ci.name, ci.value)
except ConfigurationError as ce:
    raise ImproperlyConfigured(ce.name)


SECRET_KEY = cfg.secret_key
SERVICE_PORT = cfg.service_port
FEATURE_FLAG = cfg.feature_flag
