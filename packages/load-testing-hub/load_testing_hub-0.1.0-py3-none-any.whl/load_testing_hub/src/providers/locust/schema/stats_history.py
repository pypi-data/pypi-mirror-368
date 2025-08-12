from datetime import datetime
from typing import Self

from pydantic import Field, FilePath

from load_testing_hub.src.providers.locust.schema.metrics.base import LocustStatsMetrics
from load_testing_hub.src.tools.schema import CSVRootSchema


class LocustStatsHistory(LocustStatsMetrics):
    method: str = Field(alias="Name")
    timestamp: datetime = Field(alias="Timestamp")
    number_of_users: int = Field(alias="User Count")
    min_response_time: float = Field(alias="Total Min Response Time")
    max_response_time: float = Field(alias="Total Max Response Time")
    number_of_requests: int = Field(alias="Total Request Count")
    number_of_failures: int = Field(alias="Total Failure Count")
    median_response_time: float = Field(alias="Total Median Response Time")
    average_response_time: float = Field(alias="Total Average Response Time")
    average_content_length: float = Field(alias="Total Average Content Size")


class LocustStatsHistoryList(CSVRootSchema):
    root: list[LocustStatsHistory]

    @classmethod
    def from_csv(cls, file: FilePath) -> Self:
        result = super().from_csv(file)
        return cls.model_validate(filter(lambda s: s.method != "Aggregated", result.root))


class LocustStatsHistoryAggregatedList(CSVRootSchema):
    root: list[LocustStatsHistory]

    @property
    def timestamps(self) -> list[datetime]:
        return [history.timestamp for history in self.root]

    @classmethod
    def from_csv(cls, file: FilePath) -> Self:
        result = super().from_csv(file)
        return cls.model_validate(filter(lambda s: s.method == "Aggregated", result.root))
