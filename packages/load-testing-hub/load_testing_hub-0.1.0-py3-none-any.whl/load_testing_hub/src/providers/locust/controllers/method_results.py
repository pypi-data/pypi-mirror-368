from load_testing_hub.src.api.schema.method_results import (
    CreateMethodResult,
    MethodResultProtocol,
    CreateMethodResultsRequest
)
from load_testing_hub.src.api.schema.scenarios import Scenario
from load_testing_hub.src.api.schema.services import Service
from load_testing_hub.src.providers.locust.schema.report import LocustReport


def get_method_results_payload(
        report: LocustReport,
        service: Service,
        scenario: Scenario,
        load_test_result_id: int,
) -> CreateMethodResultsRequest:
    return CreateMethodResultsRequest(
        results=[
            CreateMethodResult(
                method=result.method,
                protocol=MethodResultProtocol(result.protocol),
                service_id=service.id,
                scenario_id=scenario.id,
                max_response_time=result.max_response_time,
                min_response_time=result.min_response_time,
                number_of_requests=result.number_of_requests,
                number_of_failures=result.number_of_failures,
                requests_per_second=result.requests_per_second,
                failures_per_second=result.failures_per_second,
                median_response_time=result.median_response_time,
                average_response_time=result.average_response_time,
                average_content_length=result.average_content_length,
                response_time_percentile_50=result.response_time_percentile_50,
                response_time_percentile_60=result.response_time_percentile_60,
                response_time_percentile_70=result.response_time_percentile_70,
                response_time_percentile_80=result.response_time_percentile_80,
                response_time_percentile_90=result.response_time_percentile_90,
                response_time_percentile_95=result.response_time_percentile_95,
                response_time_percentile_99=result.response_time_percentile_99,
                response_time_percentile_100=result.response_time_percentile_100
            )
            for result in report.stats.root
        ],
        load_test_result_id=load_test_result_id
    )
