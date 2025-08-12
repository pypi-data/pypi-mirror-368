from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LocustStatsPercentiles(BaseModel):
    response_time_percentile_50: float = Field(alias="50%")
    response_time_percentile_60: float = Field(alias="60%")
    response_time_percentile_70: float = Field(alias="70%")
    response_time_percentile_80: float = Field(alias="80%")
    response_time_percentile_90: float = Field(alias="90%")
    response_time_percentile_95: float = Field(alias="95%")
    response_time_percentile_99: float = Field(alias="99%")
    response_time_percentile_100: float = Field(alias="100%")

    @field_validator(
        'response_time_percentile_50',
        'response_time_percentile_60',
        'response_time_percentile_70',
        'response_time_percentile_80',
        'response_time_percentile_90',
        'response_time_percentile_95',
        'response_time_percentile_99',
        'response_time_percentile_100',
        mode='before'
    )
    def validate_response_time_percentile(cls, value: Literal['N/A'] | float) -> float:
        return float(0 if value == 'N/A' else value)
