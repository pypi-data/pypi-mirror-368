from pydantic import Field

from load_testing_hub.src.api.schema.results_history.base import CreateResultsHistoryRequest


class CreateMethodResultsHistoryRequest(CreateResultsHistoryRequest):
    method_result_id: int = Field(alias="methodResultId")
