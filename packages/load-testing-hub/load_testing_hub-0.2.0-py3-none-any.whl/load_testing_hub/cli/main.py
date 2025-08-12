from pathlib import Path

import click

from load_testing_hub.cli.commands.upload_locust_report import upload_locust_report_command


@click.command(
    name="upload-locust-report",
    help="""
    Upload Locust performance test reports to the Load Testing Hub API using 
    configuration provided in either YAML or JSON format.
    """
)
@click.option(
    "--yaml-config",
    type=click.Path(exists=True),
    help="Path to the YAML configuration file."
)
@click.option(
    "--json-config",
    type=click.Path(exists=True),
    help="Path to the JSON configuration file."
)
def upload_locust_report(yaml_config: str, json_config: str):
    if not (yaml_config or json_config):
        raise click.UsageError("You must specify either --yaml-config or --json-config.")
    if yaml_config and json_config:
        raise click.UsageError(
            "Options --yaml-config and --json-config are mutually exclusive; specify only one."
        )

    upload_locust_report_command(
        yaml_config=Path(yaml_config) if yaml_config else None,
        json_config=Path(json_config) if json_config else None
    )


@click.group()
def cli():
    pass


cli.add_command(upload_locust_report)

if __name__ == '__main__':
    cli()
