# Load Testing Hub

Load Testing Hub is a Python library and CLI tool designed to upload performance testing results into the
[load-testing-hub-api](https://github.com/Nikita-Filonov/load-testing-hub-api). It provides a convenient connector for
reading and transforming [Locust](https://locust.io/) reports and sending them to the Load Testing Hub API over HTTP.

## Key Features

- Easy integration with Locust reports (CSV/JSON).
- Raw Python API for programmatic usage.
- CLI support for quick uploads from configuration files (YAML or JSON).
- Pydantic-powered configuration for strict validation and clear error messages.

## Installation

```bash
pip install load-testing-hub
```

For development:

```bash
git clone https://github.com/Nikita-Filonov/load-testing-hub.git
cd load-testing-hub
pip install -e .
```

## Usage

### 1. Python API

You can upload Locust results directly from your Python code by using the raw API:

```python
import asyncio
from pathlib import Path

from load_testing_hub import (
    Service,
    Scenario,
    upload_locust_report,
    UploadLocustReportParams
)


# Main async function to upload Locust test results
async def main():
    await upload_locust_report(
        UploadLocustReportParams(
            # Base URL of the Load Testing Hub API
            api_url="http://localhost:8000",

            # Information about the service for which results are uploaded
            service=Service(id=1),

            # Scenario metadata (name, configuration file, version, and load parameters)
            scenario=Scenario(
                id=1,
                name="get accounts",  # Scenario name
                file="./scenarios/get_accounts/v1.0.conf",  # Path to scenario config file
                version="v1.0",  # Scenario version
                number_of_users=500,  # Number of virtual users in the test
                runtime_duration="3m"  # Test duration (3 minutes)
            ),

            # Paths to Locust report files
            csv_locust_stats_file=Path("locust_stats.csv"),  # Aggregated statistics
            json_locust_ratio_file=Path("locust_ratio.json"),  # Response time percentiles
            csv_locust_exceptions_file=Path("locust_exceptions.csv"),  # Exceptions during test
            csv_locust_stats_history_file=Path("locust_stats_history.csv"),  # Time-series stats
        )
    )


# Run the async main function
asyncio.run(main())
```

### 2. CLI Usage

The package provides a built-in CLI command for uploading reports.

#### Example with YAML configuration

Configuration file ([./examples/locust.yaml](./examples/locust.yaml)):

```yaml
# Base URL of the Load Testing Hub API
api_url: http://localhost:8000

# Information about the service for which results are uploaded
service:
  id: 1  # Unique service identifier

# Scenario metadata
scenario:
  id: 1  # Unique scenario identifier
  name: "get account"  # Scenario name (for reference in the UI or reports)
  file: "./scenarios/get_accounts/v1.0.conf"  # Path to the scenario configuration file
  version: "v1.0"  # Version of the scenario
  number_of_users: 500  # Number of virtual users executed in the test
  runtime_duration: "3m"  # Test runtime duration (3 minutes)

# Paths to Locust output files generated after test execution
csv_locust_stats_file: "locust_stats.csv"  # Aggregated test statistics
json_locust_ratio_file: "locust_ratio.json"  # Percentile and ratio statistics
csv_locust_exceptions_file: "locust_exceptions.csv"  # Exceptions captured during the test
csv_locust_stats_history_file: "locust_stats_history.csv"  # Time-series performance stats
```

Command:

```bash
load-testing-hub upload-locust-report --yaml-config=./examples/locust.yaml
```

#### Example with JSON configuration

Configuration file ([./examples/locust.json](./examples/locust.json)):

```json
{
  "api_url": "http://localhost:8000",
  "service": {
    "id": 1
  },
  "scenario": {
    "id": 1,
    "name": "get account",
    "file": "./scenarios/get_accounts/v1.0.conf",
    "version": "v1.0",
    "number_of_users": 500,
    "runtime_duration": "3m"
  },
  "csv_locust_stats_file": "locust_stats.csv",
  "json_locust_ratio_file": "locust_ratio.json",
  "csv_locust_exceptions_file": "locust_exceptions.csv",
  "csv_locust_stats_history_file": "locust_stats_history.csv"
}
```

Command:

```bash
load-testing-hub upload-locust-report --json-config=./examples/locust.json
```