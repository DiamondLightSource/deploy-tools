from typing import Literal

from pydantic import BaseModel


class ShellConfig(BaseModel, extra="forbid"):
    app_type: Literal["shell"]
    name: str
    script: list[str]
