from load_testing_hub.src.providers.locust.controllers.results_history.base import get_results_history_payload
from load_testing_hub.src.api.schema.results_history.load_test_results_history import (
    CreateLoadTestResultsHistoryRequest
)
from load_testing_hub.src.providers.locust.schema.report import LocustReport


def get_load_test_results_history_payload(
        load_test_result_id: int,
        report: LocustReport
) -> CreateLoadTestResultsHistoryRequest:
    return CreateLoadTestResultsHistoryRequest(
        results=[
            get_results_history_payload(history)
            for history in report.stats_history_aggregated.root
        ],
        load_test_result_id=load_test_result_id
    )
