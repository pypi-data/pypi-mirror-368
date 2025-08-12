from pydantic import Field, BaseModel, FilePath

from load_testing_hub.src.providers.locust.schema.exceptions import LocustExceptionsList
from load_testing_hub.src.providers.locust.schema.ratios import LocustRatios
from load_testing_hub.src.providers.locust.schema.report import LocustReport
from load_testing_hub.src.providers.locust.schema.stats import LocustStatsList, LocustStatsAggregatedList
from load_testing_hub.src.providers.locust.schema.stats_history import (
    LocustStatsHistoryList,
    LocustStatsHistoryAggregatedList
)


class BuildLocustReportParams(BaseModel):
    csv_locust_stats_file: FilePath = Field(default=FilePath("locust_stats.csv"), validate_default=True)
    json_locust_ratio_file: FilePath = Field(default=FilePath("locust_ratio.json"), validate_default=True)
    csv_locust_exceptions_file: FilePath = Field(default=FilePath("locust_exceptions.csv"), validate_default=True)
    csv_locust_stats_history_file: FilePath = Field(default=FilePath("locust_stats_history.csv"), validate_default=True)


def build_locust_report(params: BuildLocustReportParams) -> LocustReport:
    return LocustReport(
        stats=LocustStatsList.from_csv(params.csv_locust_stats_file),
        stats_aggregated=LocustStatsAggregatedList.from_csv(params.csv_locust_stats_file),

        stats_history=LocustStatsHistoryList.from_csv(params.csv_locust_stats_history_file),
        stats_history_aggregated=LocustStatsHistoryAggregatedList.from_csv(params.csv_locust_stats_history_file),

        ratios=LocustRatios.from_json(params.json_locust_ratio_file),
        exceptions=LocustExceptionsList.from_csv(params.csv_locust_exceptions_file),
    )
