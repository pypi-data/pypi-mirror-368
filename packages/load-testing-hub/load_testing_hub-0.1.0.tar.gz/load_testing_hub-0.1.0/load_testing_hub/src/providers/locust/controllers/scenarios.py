from load_testing_hub.src.api.schema.ratio_results import RatioResult
from load_testing_hub.src.api.schema.scenarios import UpdateScenarioRequest, Scenario
from load_testing_hub.src.providers.locust.schema.report import LocustReport


def get_scenario_payload(report: LocustReport, scenario: Scenario) -> UpdateScenarioRequest:
    return UpdateScenarioRequest(
        name=scenario.name,
        file=scenario.file,
        version=scenario.version,
        ratio_total=RatioResult.from_locust_ratio(report.ratios.total),
        ratio_per_class=RatioResult.from_locust_ratio(report.ratios.per_class),
        number_of_users=scenario.number_of_users,
        runtime_duration=scenario.runtime_duration
    )
