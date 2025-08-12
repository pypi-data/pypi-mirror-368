from httpx import AsyncClient, AsyncHTTPTransport

from load_testing_hub.src.api.schema.exception_results import CreateExceptionResultsRequest
from load_testing_hub.src.api.schema.load_test_results import (
    CreateLoadTestResultRequest,
    CreateLoadTestResultResponse
)
from load_testing_hub.src.api.schema.method_results import (
    CreateMethodResultsRequest,
    CreateMethodResultsResponse
)
from load_testing_hub.src.api.schema.ratio_results import CreateRatioResultRequest
from load_testing_hub.src.api.schema.results_history.load_test_results_history import (
    CreateLoadTestResultsHistoryRequest
)
from load_testing_hub.src.api.schema.results_history.method_results_history import CreateMethodResultsHistoryRequest
from load_testing_hub.src.api.schema.scenarios import UpdateScenarioRequest
from load_testing_hub.src.tools.clients.http.client import HTTPClient
from load_testing_hub.src.tools.clients.http.event_hooks.logger import LoggerEventHook
from load_testing_hub.src.tools.clients.http.transports.retry import RetryTransport
from load_testing_hub.src.tools.logger import get_logger


class LoadTestingHubHTTPClient(HTTPClient):
    async def create_load_test_result(self, request: CreateLoadTestResultRequest) -> CreateLoadTestResultResponse:
        response = await self.post(
            '/api/v1/load-test-results',
            json=request.model_dump(by_alias=True, mode='json')
        )
        return CreateLoadTestResultResponse(**response.json())

    async def create_method_results(self, request: CreateMethodResultsRequest) -> CreateMethodResultsResponse:
        response = await self.post(
            '/api/v1/method-results',
            json=request.model_dump(by_alias=True, mode='json')
        )
        return CreateMethodResultsResponse(**response.json())

    async def create_method_results_history(self, request: CreateMethodResultsHistoryRequest):
        await self.post(
            '/api/v1/method-results-history',
            json=request.model_dump(by_alias=True, mode='json')
        )

    async def create_load_test_results_history(self, request: CreateLoadTestResultsHistoryRequest):
        await self.post(
            '/api/v1/load-test-results-history',
            json=request.model_dump(by_alias=True, mode='json')
        )

    async def create_ratio_results(self, request: CreateRatioResultRequest):
        await self.post(
            '/api/v1/ratio-results',
            json=request.model_dump(by_alias=True, mode='json')
        )

    async def create_exception_results(self, request: CreateExceptionResultsRequest):
        await self.post(
            '/api/v1/exception-results',
            json=request.model_dump(by_alias=True, mode='json')
        )

    async def update_scenario(self, scenario_id: int, request: UpdateScenarioRequest):
        await self.patch(
            f'/api/v1/scenarios/{scenario_id}',
            json=request.model_dump(by_alias=True, mode='json')
        )


def build_load_testing_hub_http_client(api_url: str) -> LoadTestingHubHTTPClient:
    logger = get_logger('LOAD_TESTING_HUB_HTTP_CLIENT')
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(transport=AsyncHTTPTransport())

    client = AsyncClient(
        base_url=api_url,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return LoadTestingHubHTTPClient(client=client)
