from typing import Literal

from pydantic import BaseModel


class ShellConfig(BaseModel):
    app_type: Literal["shell"]
    name: str
    script: list[str]
