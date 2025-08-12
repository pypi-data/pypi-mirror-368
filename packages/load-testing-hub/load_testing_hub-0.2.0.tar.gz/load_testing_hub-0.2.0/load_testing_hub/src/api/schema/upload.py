from pydantic import BaseModel

from load_testing_hub.src.api.schema.pipeline import Pipeline
from load_testing_hub.src.api.schema.scenarios import Scenario
from load_testing_hub.src.api.schema.services import Service


class UploadReportParams(BaseModel):
    api_url: str
    service: Service
    scenario: Scenario
    trigger_pipeline: Pipeline = Pipeline()
    load_tests_pipeline: Pipeline = Pipeline()
