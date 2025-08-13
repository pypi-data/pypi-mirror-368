import click
from pathlib import Path
import subprocess
from dbt_yamer.handlers.markdown_handlers import create_md_file
from dbt_yamer.handlers.file_handlers import find_dbt_project_root

@click.command(name="md")
@click.option(
    "--select",
    "-s",
    is_flag=True,
    help="Use this flag before specifying models"
)
@click.argument('models', nargs=-1)
def generate_markdown(select, models):
    """
    Generate markdown documentation for one or more dbt models and place them next to their .sql sources.

    Example:
      dbt-yamer md -s dim_promotion dim_voucher
      dbt-yamer md --select tag:nightly
      dbt-yamer md -s dim_promotion tag:nightly
    """
    if not select:
        click.echo("Please use --select/-s flag before specifying models.")
        return

    if not models:
        click.echo("No models specified. Please provide at least one model name.")
        return

    # Validate selectors (no '+' allowed)
    for model in models:
        if '+' in model:
            click.echo(f"Error: '+' selector is not supported: {model}")
            return

    # Track successful generations
    md_success = []

    click.echo("\n🔄 Generating markdown documentation...")

    try:
        project_dir = find_dbt_project_root()
    except FileNotFoundError as e:
        click.echo(f"Error: {e}. Please run this command from within a dbt project.")
        return

    # First, if we have a tag selector, get the list of models
    processed_models = []
    for model in models:
        if model.startswith('tag:'):
            click.echo(f"\nExpanding tag selector: {model}")
            ls_cmd = [
                "dbt",
                "--quiet",
                "ls",
                "--select", model
            ]
            try:
                ls_result = subprocess.run(
                    ls_cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                # Split the fully qualified names and take the last part
                tag_models = [
                    path.split('.')[-1] 
                    for path in ls_result.stdout.strip().splitlines()
                ]
                if not tag_models:
                    click.echo(f"Warning: No models found for tag selector '{model}'")
                    continue
                processed_models.extend(tag_models)
                click.echo(f"Found models for {model}: {', '.join(tag_models)}")
            except subprocess.CalledProcessError as e:
                click.echo(f"Error expanding tag selector '{model}':\n{e.stderr}")
                continue
        else:
            processed_models.append(model)

    if not processed_models:
        click.echo("No models found to process after expanding selectors.")
        return

    for model in processed_models:
        click.echo(f"\nProcessing model: {model}")
        
        ls_cmd = [
            "dbt",
            "--quiet",
            "ls",
            "--resource-types", "model",
            "--select", model,
            "--output", "path"
        ]
        
        try:
            ls_result = subprocess.run(
                ls_cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ Unable to locate model '{model}':\n{e.stderr}")
            continue

        paths = ls_result.stdout.strip().splitlines()
        if not paths:
            click.echo(f"⚠️  Warning: Could not find path for '{model}' (dbt ls returned no results).")
            continue

        sql_file_path = Path(paths[0])
        dir_for_sql = sql_file_path.parent
        
        try:
            create_md_file(model, dir_for_sql)
            md_success.append(model)
            click.echo(f"✅ Markdown documentation generated for '{model}'")
        except OSError as e:
            click.echo(f"❌ Could not write markdown file for '{model}': {e}")

    # Summary
    click.echo("\n📊 Generation Summary:")
    if md_success:
        click.echo(f"✅ Markdown generated successfully for: {', '.join(md_success)}")
    else:
        click.echo("❌ No markdown files were generated successfully")

    # Don't report tag selectors as failed models
    failed_models = set(processed_models) - set(md_success)
    if failed_models:
        click.echo(f"\n⚠️  Failed to generate markdown for: {', '.join(failed_models)}") 