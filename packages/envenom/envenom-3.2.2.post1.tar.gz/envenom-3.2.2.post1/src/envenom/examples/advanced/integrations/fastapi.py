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

from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.routing import APIRoute

from envenom import config, defaults, namespace, subconfig
from envenom.parsers import bool_parser

app_ns = namespace("app")


@config(app_ns / "fastapi")
class FastAPICfg:
    static_docs: bool = defaults(bool_parser, default=True)
    interactive_docs: bool = defaults(bool_parser, default=False)


@config(app_ns)
class AppCfg:
    motd: str = defaults(default="This is the default message of the day.")
    fastapi: FastAPICfg = subconfig(FastAPICfg)


cfg = AppCfg()


@dataclass(frozen=True, eq=True, order=True)
class IndexResponse:
    motd: str


async def get_index() -> IndexResponse:
    return IndexResponse(motd=cfg.motd)


app = FastAPI(
    title="envenom.examples.advanced.integrations.fastapi:app",
    redoc_url="/redoc" if cfg.fastapi.static_docs else None,
    docs_url="/docs" if cfg.fastapi.interactive_docs else None,
    routes=[
        APIRoute("/", get_index, methods={"GET"}),
    ],
)
