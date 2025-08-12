from load_testing_hub.src.api.schema.results_history.base import ResultsHistory
from load_testing_hub.src.providers.locust.schema.stats_history import LocustStatsHistory


def get_results_history_payload(history: LocustStatsHistory) -> ResultsHistory:
    return ResultsHistory(
        datetime=history.timestamp,
        number_of_users=history.number_of_users,
        min_response_time=history.min_response_time,
        max_response_time=history.max_response_time,
        number_of_requests=history.number_of_requests,
        number_of_failures=history.number_of_failures,
        requests_per_second=history.requests_per_second,
        failures_per_second=history.failures_per_second,
        median_response_time=history.median_response_time,
        average_response_time=history.average_response_time,
        average_content_length=history.average_content_length,
        response_time_percentile_50=history.response_time_percentile_50,
        response_time_percentile_60=history.response_time_percentile_60,
        response_time_percentile_70=history.response_time_percentile_70,
        response_time_percentile_80=history.response_time_percentile_80,
        response_time_percentile_90=history.response_time_percentile_90,
        response_time_percentile_95=history.response_time_percentile_95,
        response_time_percentile_99=history.response_time_percentile_99,
        response_time_percentile_100=history.response_time_percentile_100
    )
