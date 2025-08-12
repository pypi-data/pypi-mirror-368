from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from load_testing_hub.src.api.schema.metrics.base import MetricsSchema
from load_testing_hub.src.api.schema.metrics.content_length import ContentLengthSchema


class MethodResultProtocol(str, Enum):
    HTTP = "http"
    GRPC = "grpc"
    KAFKA = "kafka"


class ShortMethodResult(BaseModel):
    id: int
    method: str


class CreateMethodResult(MetricsSchema, ContentLengthSchema):
    model_config = ConfigDict(populate_by_name=True)

    method: str
    protocol: MethodResultProtocol
    service_id: int = Field(alias="serviceId")
    scenario_id: int = Field(alias="scenarioId")


class CreateMethodResultsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    results: list[CreateMethodResult]
    load_test_result_id: int = Field(alias="loadTestResultId")


class CreateMethodResultsResponse(BaseModel):
    results: list[ShortMethodResult]
