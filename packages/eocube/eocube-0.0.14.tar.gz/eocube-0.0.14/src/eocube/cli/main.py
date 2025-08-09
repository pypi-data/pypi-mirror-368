# Copyright 2025 West University of Timisoara
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

import importlib
import click

from eocube.utils.geospatialorg.cli import register as register_geospatialorg
from .auth import auth_cli


def is_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


@click.group()
@click.option(
    "--log-level",
    default="WARNING",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"],
        case_sensitive=False,
    ),
    help="Set the logging level.",
)
@click.pass_context
def cli(ctx, log_level):
    logging.getLogger().setLevel(log_level.upper())


@cli.group()
def services():
    """Various Services"""
    pass


cli.add_command(services)
cli.add_command(auth_cli)

register_geospatialorg(services)

if __name__ == "__main__":
    cli()
