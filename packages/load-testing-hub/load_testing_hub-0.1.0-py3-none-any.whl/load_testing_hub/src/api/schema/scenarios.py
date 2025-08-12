from pydantic import BaseModel, ConfigDict, Field

from load_testing_hub.src.api.schema.ratio_results import RatioResult


class ShortScenario(BaseModel):
    id: int
    name: str
    version: str


class Scenario(ShortScenario):
    model_config = ConfigDict(populate_by_name=True)

    file: str
    number_of_users: int = Field(alias="numberOfUsers")
    runtime_duration: str = Field(alias="runtimeDuration")


class UpdateScenarioRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    file: str
    version: str
    ratio_total: list[RatioResult] = Field(alias="ratioTotal")
    ratio_per_class: list[RatioResult] = Field(alias="ratioPerClass")
    number_of_users: int = Field(alias="numberOfUsers")
    runtime_duration: str = Field(alias="runtimeDuration")
