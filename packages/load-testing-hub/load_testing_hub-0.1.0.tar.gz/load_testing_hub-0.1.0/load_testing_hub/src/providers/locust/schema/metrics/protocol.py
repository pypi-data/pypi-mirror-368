from enum import Enum

from pydantic import BaseModel, Field, field_validator


class LocustProtocol(str, Enum):
    HTTP = "http"
    GRPC = "grpc"
    KAFKA = "kafka"


class LocustStatsProtocol(BaseModel):
    protocol: LocustProtocol | None = Field(alias="Type", default=None)

    @field_validator("protocol", mode="before")
    def validate_protocol(cls, value: str) -> str | None:
        return value or None
