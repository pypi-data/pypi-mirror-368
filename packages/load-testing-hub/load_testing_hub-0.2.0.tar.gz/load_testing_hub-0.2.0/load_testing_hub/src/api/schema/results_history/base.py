from datetime import datetime

from pydantic import BaseModel, ConfigDict

from load_testing_hub.src.api.schema.metrics.base import MetricsSchema
from load_testing_hub.src.api.schema.metrics.content_length import ContentLengthSchema
from load_testing_hub.src.api.schema.metrics.number_of_users import NumberOfUsersSchema


class ResultsHistory(MetricsSchema, ContentLengthSchema, NumberOfUsersSchema):
    datetime: datetime


class CreateResultsHistoryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    results: list[ResultsHistory]
