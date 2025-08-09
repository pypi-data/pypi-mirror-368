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

from functools import cached_property
from uuid import UUID, uuid4

from envenom import config, defaults, namespace, optional, required, subconfig
from envenom.examples import print_config_tree
from envenom.parsers import bool_parser

myapp = namespace("myapp")
myapp_db = myapp / "db"


@config(myapp_db)
class DbCfg:
    scheme: str = defaults(default="postgresql+psycopg")
    host: str = required()
    port: int = defaults(int, default=5432)
    database: str = required()
    username: str | None = optional()
    password: str | None = optional()
    connection_timeout: int | None = optional(int)
    sslmode_require: bool = defaults(bool_parser, default=False)

    @cached_property
    def auth(self) -> str:
        if not self.username and not self.password:
            return ""

        auth = ""
        if self.username:
            auth += self.username
        if self.password:
            auth += f":{self.password}"
        if auth:
            auth += "@"

        return auth

    @cached_property
    def query_string(self) -> str:
        query: dict[str, str] = {}
        if self.connection_timeout:
            query["timeout"] = str(self.connection_timeout)
        if self.sslmode_require:
            query["sslmode"] = "require"

        if not query:
            return ""

        query_string = "&".join((f"{key}={value}" for key, value in query.items()))
        return f"?{query_string}"

    @cached_property
    def connection_string(self) -> str:
        return (
            f"{self.scheme}://{self.auth}{self.host}:{self.port}"
            f"/{self.database}{self.query_string}"
        )


@config(myapp)
class AppCfg:
    worker_id: UUID = defaults(UUID, default_factory=uuid4)
    secret_key: str = required()
    db: DbCfg = subconfig(DbCfg)


if __name__ == "__main__":
    cfg = AppCfg()

    print_config_tree(cfg)
    print(f"cfg.db.connection_string: {repr(cfg.db.connection_string)}")
