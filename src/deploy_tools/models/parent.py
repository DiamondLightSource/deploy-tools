from pydantic import BaseModel, ConfigDict


class ParentModel(BaseModel):
    """Provide model config for all Pydantic models in this project.

    - ``extra="forbid"``: forbid any extra parameters being provided in any subclass.
    - ``use_enum_values=True``: use the enum value only when serializing the model, so
      the YAML serializer can work with enums.
    """

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )
