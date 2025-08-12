from pydantic import BaseModel, HttpUrl


class Pipeline(BaseModel):
    ci_job_url: HttpUrl | None = None
    ci_project_url: HttpUrl | None = None
    ci_pipeline_url: HttpUrl | None = None
    ci_project_version: str | None = None
