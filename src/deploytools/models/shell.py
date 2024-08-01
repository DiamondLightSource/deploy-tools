from typing import Literal

from pydantic import BaseModel


class Shell(BaseModel, extra="forbid"):
    app_type: Literal["shell"]
    name: str
    script: list[str]
