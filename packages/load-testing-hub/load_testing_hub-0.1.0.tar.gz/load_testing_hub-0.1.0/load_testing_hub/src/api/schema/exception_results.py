from pydantic import BaseModel, Field, ConfigDict


class ExceptionResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    details: str
    number_of_exceptions: int = Field(alias="numberOfExceptions")


class CreateExceptionResultsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    results: list[ExceptionResult]
    load_test_result_id: int = Field(alias="loadTestResultId")
