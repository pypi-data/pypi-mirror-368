import click
from dbt_yamer.cli.run import run
from dbt_yamer.cli.generate_yaml import generate_yaml
from dbt_yamer.cli.generate_markdown import generate_markdown
from dbt_yamer.cli.generate_yamd import generate_yamd

@click.group()
def cli():
    """
    dbt-yamer CLI

    Use this tool to:
      - Run dbt models
      - Generate YAML configs (with contract enforcement)
      - Generate markdown documentation
      - Generate both YAML and markdown together
    """
    pass

cli.add_command(run)
cli.add_command(generate_yaml)
cli.add_command(generate_markdown)
cli.add_command(generate_yamd)

if __name__ == "__main__":
    cli()
