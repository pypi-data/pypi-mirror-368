from load_testing_hub.src.api.schema.metrics.number_of_requests import NumberOfRequestsSchema
from load_testing_hub.src.api.schema.metrics.percentiles import PercentilesSchema
from load_testing_hub.src.api.schema.metrics.requests_per_second import RequestsPerSecondSchema
from load_testing_hub.src.api.schema.metrics.response_times import ResponseTimesSchema


class MetricsSchema(
    PercentilesSchema,
    ResponseTimesSchema,
    NumberOfRequestsSchema,
    RequestsPerSecondSchema,
):
    ...
