from pydantic import BaseModel, ConfigDict


class ParentModel(BaseModel):
    """Will forbid any extra parameters being provided in any subclass."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)
