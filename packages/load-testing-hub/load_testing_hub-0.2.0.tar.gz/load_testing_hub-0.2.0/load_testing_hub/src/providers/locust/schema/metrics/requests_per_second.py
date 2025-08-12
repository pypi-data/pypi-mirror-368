from pydantic import BaseModel, Field


class LocustStatsRequestsPerSecond(BaseModel):
    requests_per_second: float = Field(alias="Requests/s")
    failures_per_second: float = Field(alias="Failures/s")
