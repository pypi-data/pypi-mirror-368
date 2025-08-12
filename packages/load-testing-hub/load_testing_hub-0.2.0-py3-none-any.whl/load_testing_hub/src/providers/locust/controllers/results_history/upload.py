from load_testing_hub.src.api.client import build_load_testing_hub_http_client
from load_testing_hub.src.api.schema.load_test_results import LoadTestResultDetails
from load_testing_hub.src.api.schema.upload import UploadReportParams
from load_testing_hub.src.providers.locust.controllers.build import (
    build_locust_report,
    BuildLocustReportParams
)
from load_testing_hub.src.providers.locust.controllers.exception_results import get_exception_results_payload
from load_testing_hub.src.providers.locust.controllers.load_test_results import get_load_test_result_payload
from load_testing_hub.src.providers.locust.controllers.method_results import get_method_results_payload
from load_testing_hub.src.providers.locust.controllers.ratio_results import get_ratio_result_payload
from load_testing_hub.src.providers.locust.controllers.results_history.load_test_results_history import (
    get_load_test_results_history_payload
)
from load_testing_hub.src.providers.locust.controllers.results_history.method_results_history import (
    get_method_results_history_payload
)
from load_testing_hub.src.providers.locust.controllers.scenarios import get_scenario_payload
from load_testing_hub.src.tools.schema import YAMLSchema, JSONSchema


class UploadLocustReportParams(
    YAMLSchema,
    JSONSchema,
    UploadReportParams,
    BuildLocustReportParams
):
    ...


async def upload_locust_report(params: UploadLocustReportParams) -> LoadTestResultDetails:
    client = build_load_testing_hub_http_client(api_url=params.api_url)
    report = build_locust_report(params)

    scenario_payload = get_scenario_payload(report=report, scenario=params.scenario)
    await client.update_scenario(params.scenario.id, scenario_payload)

    load_test_result_payload = get_load_test_result_payload(
        report=report,
        service=params.service,
        scenario=params.scenario,
        trigger_pipeline=params.trigger_pipeline,
        load_tests_pipeline=params.load_tests_pipeline
    )
    load_test_result = await client.create_load_test_result(load_test_result_payload)

    method_results_payload = get_method_results_payload(
        report=report,
        service=params.service,
        scenario=params.scenario,
        load_test_result_id=load_test_result.details.id,
    )
    method_results_response = await client.create_method_results(method_results_payload)

    method_results_history_payload = get_method_results_history_payload(
        report=report,
        method_results=method_results_response.results
    )
    for payload in method_results_history_payload:
        await client.create_method_results_history(payload)

    load_test_results_history_payload = get_load_test_results_history_payload(
        report=report,
        load_test_result_id=load_test_result.details.id,
    )
    await client.create_load_test_results_history(load_test_results_history_payload)

    ratio_result_payload = get_ratio_result_payload(
        report=report,
        load_test_result_id=load_test_result.details.id,
    )
    await client.create_ratio_results(ratio_result_payload)

    exception_results_payload = get_exception_results_payload(
        report=report,
        load_test_result_id=load_test_result.details.id
    )
    await client.create_exception_results(exception_results_payload)

    return load_test_result.details
