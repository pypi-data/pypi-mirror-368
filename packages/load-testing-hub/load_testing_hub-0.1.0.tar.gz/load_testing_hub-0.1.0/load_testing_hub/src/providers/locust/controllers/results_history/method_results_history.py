from load_testing_hub.src.providers.locust.controllers.results_history.base import get_results_history_payload
from load_testing_hub.src.api.schema.method_results import ShortMethodResult
from load_testing_hub.src.api.schema.results_history.method_results_history import CreateMethodResultsHistoryRequest
from load_testing_hub.src.providers.locust.schema.report import LocustReport
from load_testing_hub.src.providers.locust.schema.stats_history import LocustStatsHistory


def get_method_results_history_payload(
        report: LocustReport,
        method_results: list[ShortMethodResult]
) -> list[CreateMethodResultsHistoryRequest]:
    requests: list[CreateMethodResultsHistoryRequest] = []
    for result in method_results:
        stats = list[LocustStatsHistory](filter(lambda s: s.method == result.method, report.stats_history.root))

        requests.append(
            CreateMethodResultsHistoryRequest(
                results=[get_results_history_payload(history) for history in stats],
                method_result_id=result.id
            )
        )

    return requests
