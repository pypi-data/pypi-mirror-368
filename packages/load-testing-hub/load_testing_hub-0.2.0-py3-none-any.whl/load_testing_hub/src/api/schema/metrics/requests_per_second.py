from pydantic import Field, BaseModel, ConfigDict


class RequestsPerSecondSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    requests_per_second: float = Field(alias="requestsPerSecond")
    failures_per_second: float = Field(alias="failuresPerSecond")
