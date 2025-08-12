from pydantic import Field, BaseModel, ConfigDict


class ContentLengthSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    average_content_length: float = Field(alias="averageContentLength")
