from load_testing_hub.src.api.schema.ratio_results import CreateRatioResultRequest, RatioResult
from load_testing_hub.src.providers.locust.schema.report import LocustReport


def get_ratio_result_payload(load_test_result_id: int, report: LocustReport) -> CreateRatioResultRequest:
    return CreateRatioResultRequest(
        ratio_total=RatioResult.from_locust_ratio(report.ratios.total),
        ratio_per_class=RatioResult.from_locust_ratio(report.ratios.per_class),
        load_test_result_id=load_test_result_id
    )
