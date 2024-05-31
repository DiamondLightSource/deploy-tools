import json
from typing import Self

import yaml
from pydantic import BaseModel


class YamlSchemaModel(BaseModel):
    @classmethod
    def from_yaml(cls, file_path: str) -> Self:
        with open(file_path) as f:
            config = yaml.safe_load(f)
            return cls(**config)

    @classmethod
    def generate_schema(cls) -> str:
        schema = cls.model_json_schema()
        return json.dumps(schema, indent=2)
