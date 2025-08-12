from pydantic import Field, BaseModel, ConfigDict


class NumberOfUsersSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    number_of_users: float = Field(alias="numberOfUsers")
