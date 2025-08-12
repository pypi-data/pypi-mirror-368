from load_testing_hub.src.providers.locust.schema.metrics.percentiles import LocustStatsPercentiles
from load_testing_hub.src.providers.locust.schema.metrics.protocol import LocustStatsProtocol
from load_testing_hub.src.providers.locust.schema.metrics.requests_per_second import LocustStatsRequestsPerSecond


class LocustStatsMetrics(
    LocustStatsProtocol,
    LocustStatsPercentiles,
    LocustStatsRequestsPerSecond
):
    ...
