from pydantic import Field

from load_testing_hub.src.api.schema.results_history.base import CreateResultsHistoryRequest


class CreateLoadTestResultsHistoryRequest(CreateResultsHistoryRequest):
    load_test_result_id: int = Field(alias="loadTestResultId")
