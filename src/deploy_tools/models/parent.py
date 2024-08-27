from pydantic import BaseModel, ConfigDict


class ParentModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
