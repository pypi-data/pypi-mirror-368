from pydantic import BaseModel, ConfigDict, Field

from load_testing_hub.src.providers.locust.schema.ratios import TaskSet


class RatioResult(BaseModel):
    name: str
    ratio: float
    tasks: list['RatioResult']

    @classmethod
    def from_locust_ratio(cls, ratio: dict[str, TaskSet] | None) -> list['RatioResult']:
        if not ratio:
            return []

        return [
            RatioResult(
                name=key,
                ratio=task_set.ratio,
                tasks=cls.from_locust_ratio(task_set.tasks)
            )
            for key, task_set in ratio.items()
        ]


class CreateRatioResultRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ratio_total: list[RatioResult] = Field(alias="ratioTotal")
    ratio_per_class: list[RatioResult] = Field(alias="ratioPerClass")
    load_test_result_id: int = Field(alias="loadTestResultId")
