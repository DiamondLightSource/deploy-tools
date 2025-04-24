from pydantic import BaseModel, ConfigDict


class ParentModel(BaseModel):
    """
    Provides Model Config for all Pydantic models in this project:

      forbid:          forbid any extra parameters being provided in any subclass.
      use_enum_values: use the enum value only when serializing the model,
                       this means the yaml serializer can work with enums
    """

    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
    )
