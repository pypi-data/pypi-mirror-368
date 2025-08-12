import asyncio
from pathlib import Path

from load_testing_hub.src.providers.locust.controllers.results_history.upload import (
    upload_locust_report,
    UploadLocustReportParams
)


def upload_locust_report_command(yaml_config: Path | None, json_config: Path | None):
    params: UploadLocustReportParams | None = None
    if yaml_config:
        params = UploadLocustReportParams.from_yaml(yaml_config)
    if json_config:
        params = UploadLocustReportParams.from_json(json_config)

    if not params:
        raise ValueError(
            "Failed to load configuration parameters from the provided YAML or JSON file."
        )

    asyncio.run(upload_locust_report(params))
