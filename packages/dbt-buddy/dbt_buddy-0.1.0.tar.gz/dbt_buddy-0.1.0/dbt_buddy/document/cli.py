from pathlib import Path
from typing import Optional

import click

from dbt_buddy.document.doc_generator.generator import DBTDocGenerator


@click.command()
@click.option(
    "-m",
    "--model",
    type=str,
    required=True,
    help="The name of existing dbt-model.",
)
@click.option(
    "--project-dir",
    type=click.Path(),
    default=None,
    help="Path to directory with dbt_project.yml. Default is the current working directory.",
)
@click.option(
    "--profiles-dir",
    type=click.Path(),
    default=None,
    help="Path to directory with profiles.yml. Default is the current working directory.",
)
@click.option(
    "-e",
    "--examples",
    is_flag=True,
    help="Whether to include AI-generated possible values for the field.",
)
@click.option(
    "-s",
    "--save",
    is_flag=True,
    help="Whether to save generated documentation to YAML-file.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Whether to print a raw answer from YandexGPT to the console.",
)
def document(
    model: str,
    examples: bool,
    save: bool,
    verbose: bool,
    project_dir: Optional[Path],
    profiles_dir: Optional[Path],
):
    """
    The function for generating documentation and filling YAML.
    """
    dbt_doc = DBTDocGenerator(
        model=model,
        examples=examples,
        save=save,
        verbose=verbose,
        project_dir=project_dir,
        profiles_dir=profiles_dir,
    )
    dbt_doc.run()
