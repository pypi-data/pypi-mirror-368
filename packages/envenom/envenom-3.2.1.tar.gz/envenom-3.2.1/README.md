<!-- `envenom` - an elegant application configurator for the more civilized age
Copyright (C) 2024-2025 Artur Ciesielski <artur.ciesielski@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>. -->

# envenom

[![pipeline status](https://gitlab.com/arcanery/python/envenom/badges/main/pipeline.svg)](https://gitlab.com/arcanery/python/envenom/-/commits/main)
[![coverage report](https://gitlab.com/arcanery/python/envenom/badges/main/coverage.svg)](https://gitlab.com/arcanery/python/envenom/-/commits/main)
[![latest release](https://gitlab.com/arcanery/python/envenom/-/badges/release.svg)](https://gitlab.com/arcanery/python/envenom/-/releases)

## Introduction

`envenom` is an elegant application configurator for the more civilized age.

`envenom` is written with simplicity and type safety in mind. It allows
you to express your application configuration declaratively in a dataclass-like
format while providing your application with type information about each entry,
its nullability and default values.

`envenom` is designed for modern usecases, allowing for pulling configuration from
environment variables or files for more sophisticated deployments on platforms
like Kubernetes - all in the spirit of [12factor](https://12factor.net/).

### How it works

An `envenom` config class looks like a regular Python dataclass - because it is one.

The `@envenom.config` decorator creates a new dataclass by converting the config fields
into their `dataclass` equivalents providing the relevant default field parameters.

This also means it's 100% compatible with dataclasses. You can:

- use a config class as a property of a regular dataclass
- use a regular dataclass as a property of a config class
- declare static or dynamic fields using standard dataclass syntax
- use the `InitVar`/`__post_init__` method for delayed initialization of fields
- use methods, `classmethod`s, `staticmethod`s, and properties

`envenom` will automatically fetch the environment variable values to populate
dataclass fields (optionally running parsers so that fields are automatically
converted to desired types). This works out of the box with all built-in types trivially
convertible from `str` (like `StrEnum` and `UUID`) and with any object type that can be
instantiated easily from a single string (any function `(str,) -> T` will work as a
parser).

If using a static type checker the type deduction system will correctly identify most
mistakes if you declare fields, parsers or default values with mismatched types. There
are certain exceptions, for example `T` will always satisfy type bounds `T | None`.

`envenom` also offers reading variable contents from file by specifying an environment
variable with the suffix `__FILE` which contains the path to a file with the respective
secret. This aims to facilitate a common deploy pattern where secrets are mounted as
files (especially prevalent with Kubernetes).

### What `envenom` isn't

`envenom` has a clearly defined scope limited to configuration management from the
application's point of view.

This means `envenom` is only interested in converting the environment into application
configuration and does not care about how the environment gets populated in the first place.

Things that are out of scope for `envenom` include, but are not limited to:

- injecting the environment into the runtime or orchestrator
- retrieving configuration or secrets from the cloud or another storage
(AWS Parameter/Secret Store, Azure Key Vault, HashiCorp Vault, etc.)
- retrieving and parsing configuration from structured config files (`YAML`/`JSON`/`INI` etc.)

## Getting started

### Installation

```bash
python -m pip install envenom
```

### Config classes

Config classes are created with the `envenom.config` class decorator. It behaves exactly
like `dataclasses.dataclass` but allows to replace standard `dataclasses.field`
definitions with one of `envenom`-specific configuration field types.

To append a prefix to all your environment variable names within a config class, a namespace
needs to be created.

```python
from uuid import UUID, uuid4

from envenom import config, defaults, namespace, optional, required


@config(namespace("myapp"))
class AppCfg:
    required_str = required()
    optional_int = optional(int)
    defaults_uuid = defaults(UUID, default_factory=uuid4)
```

### Field types

`envenom` offers three supported field types:

- `required` for configuration variables that have to be provided. If the value cannot
be found, `ConfigurationMissing` will be raised.
- `optional` for configuration variables that don't have to be provided. If the value cannot
be found, it will be set to `None`.
- `defaults` for configuration variables where a default value can be provided. If the
value cannot be found, it will be set to the default, which can be either a static value
or created at instantiation by a factory function.

### Supplying values

To generate the environment variable name:

- join all namespace segments and the variable name together with `__`
- replace strings of nonsensical characters (`[^0-9a-zA-Z_]+`) with `_`
- transform to uppercase

As an example, a field named `dsn` in a config class with `Namespace("myapp", "db")`
will be mapped to `MYAPP__DB__DSN`.

## Basic usage - complete example

This example shows how to build a basic config structure for an application using a
database service with injectable configuration as an example. It is available in the
`envenom.examples.quickstart` runnable module.

```python
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
```

Run the example:

```bash
python -m envenom.examples.quickstart
```

```
Traceback (most recent call last):
    ...
    raise ConfigurationMissing(self.env_name)
envenom.errors.ConfigurationMissing: 'MYAPP__SECRET_KEY'
```

As soon as it encounters a required field, the config class returns
an error because there's no environment set.

Run the example again with the environment set:

```bash
MYAPP__SECRET_KEY='}uZ?uvJdKDM+$2[$dR)).n4q1SX!A$0u{(+D$PVB' \
MYAPP__DB__HOST='postgres' \
MYAPP__DB__DATABASE='database-name' \
MYAPP__DB__USERNAME='user' \
MYAPP__DB__SSLMODE_REQUIRE='t' \
MYAPP__DB__CONNECTION_TIMEOUT='15' \
python -m envenom.examples.quickstart
```

```
-----
cfg:
  worker_id: UUID('2fd334a5-5f08-4815-8107-928c291264c3')
  secret_key: '}uZ?uvJdKDM+$2[$dR)).n4q1SX!A$0u{(+D$PVB'
  db:
    scheme: 'postgresql+psycopg'
    host: 'postgres'
    port: 5432
    database: 'database-name'
    username: 'user'
    password: None
    connection_timeout: 15
    sslmode_require: True
-----
cfg.db.connection_string: 'postgresql+psycopg://user@postgres:5432/database-name?timeout=15&sslmode=require'
```
