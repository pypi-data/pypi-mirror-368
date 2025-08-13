import click
from dbt_yamer.utils.subprocess_utils import run_subprocess, validate_dbt_available
from dbt_yamer.utils.security_utils import validate_model_name, validate_tag_selector, validate_target, build_safe_command, SecurityError
from dbt_yamer.exceptions import SubprocessError


@click.command()
@click.option(
    "--select",
    "-s",
    multiple=True,
    help="Specify models to run using dbt's node selection syntax (supports tag selectors, e.g., tag:nightly)"
)
@click.option(
    "--exclude",
    "-e",
    multiple=True,
    help="Specify models to exclude using dbt's node selection syntax"
)
@click.option(
    "--target",
    "-t",
    default=None,
    help="Specify the target profile to run against"
)
def run(select, exclude, target):
    """
    Run one or more dbt models using dbt-style selection syntax.

    Example:
      dbt-yamer run -s model_a model_b
      dbt-yamer run --select tag:nightly
      dbt-yamer run -s model_a -e model_b
      dbt-yamer run -s model_a -t prod
    """
    if not select:
        click.echo("No selection criteria provided. Please specify models using --select/-s.")
        return
    
    # Check if dbt is available
    if not validate_dbt_available():
        click.echo("Error: dbt command not found. Please ensure dbt is installed and available in PATH.")
        raise click.Abort()

    try:
        # Validate inputs
        validated_selectors = []
        for selector in select:
            if '+' in selector:
                click.echo(f"Error: '+' selector is not supported: {selector}")
                return
            validated_selectors.append(validate_tag_selector(selector))

        validated_exclusions = []
        for exclusion in exclude:
            if '+' in exclusion:
                click.echo(f"Error: '+' selector is not supported in exclusions: {exclusion}")
                return
            validated_exclusions.append(validate_tag_selector(exclusion))

        validated_target = None
        if target:
            validated_target = validate_target(target)

        # Build command safely
        cmd_args = []
        for selector in validated_selectors:
            cmd_args.extend(["--select", selector])
        
        for exclusion in validated_exclusions:
            cmd_args.extend(["--exclude", exclusion])
        
        if validated_target:
            cmd_args.extend(["--target", validated_target])

        cmd_list = build_safe_command(["dbt", "run"], cmd_args)
        
        # Execute command
        run_subprocess(cmd_list)
        click.echo("✅ dbt run completed successfully")

    except SecurityError as e:
        click.echo(f"❌ Security validation error: {e}")
        raise click.Abort()
    except SubprocessError as e:
        click.echo(f"❌ Error running dbt models: {e}")
        raise click.Abort()
