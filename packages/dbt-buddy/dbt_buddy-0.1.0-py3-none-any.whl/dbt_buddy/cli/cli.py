import logging
from typing import List, Optional

import click
from pyfiglet import Figlet

from dbt_buddy.document.cli import document

f: Figlet = Figlet(font="larry3d")
click.echo(f.renderText("dbt-buddy"))

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class BuddyCLI(click.MultiCommand):
    """Custom class for BuddyCLI inherited from Click.MultiCommand."""

    _CMD_MAP: dict = {
        "document": document,
    }

    def list_commands(self, ctx: click.Context) -> List[str]:
        return self._CMD_MAP.keys()

    def get_command(self, ctx: click.Context, name: str) -> Optional[click.Command]:
        ctx.auto_envvar_prefix = "BUDDY"
        return self._CMD_MAP.get(name)


@click.command(
    cls=BuddyCLI,
    help="""
    LLM-based documentation for dbt-models. Read more about YandexGPT: https://cloud.yandex.com/en/services/yandexgpt
    """,
)
def cli():
    """Main CLI function for BuddyCLI."""
    pass


if __name__ == "__main__":
    cli()
