from pydantic import Field, BaseModel, ConfigDict


class NumberOfRequestsSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    number_of_requests: float = Field(alias="numberOfRequests")
    number_of_failures: float = Field(alias="numberOfFailures")
