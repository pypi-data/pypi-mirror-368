from pydantic import Field, BaseModel, ConfigDict


class ResponseTimesSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    min_response_time: float = Field(alias="minResponseTime")
    max_response_time: float = Field(alias="maxResponseTime")
    median_response_time: float = Field(alias="medianResponseTime")
    average_response_time: float = Field(alias="averageResponseTime")
