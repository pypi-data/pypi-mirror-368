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

from typing import TypedDict

from flask import Flask

from envenom import config, defaults, namespace, subconfig
from envenom.parsers import bool_parser

app_ns = namespace("app")


@config(app_ns / "flask")
class FlaskCfg:
    static_docs: bool = defaults(bool_parser, default=True)
    interactive_docs: bool = defaults(bool_parser, default=False)


@config(app_ns)
class AppCfg:
    motd: str = defaults(default="This is the default message of the day.")
    flask: FlaskCfg = subconfig(FlaskCfg)


cfg = AppCfg()
app = Flask(__name__)


class IndexResponse(TypedDict):
    motd: str


@app.route("/")
def index() -> IndexResponse:
    return {"motd": cfg.motd}


if cfg.flask.static_docs:

    @app.route("/redoc")
    def static_docs() -> str:
        return "Static docs would be here if Flask had them built-in."


if cfg.flask.interactive_docs:

    @app.route("/docs")
    def interactive_docs() -> str:
        return "Interactive docs would be here if Flask had them built-in."
