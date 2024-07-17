from typing import Literal

from pydantic import BaseModel


class CommandConfig(BaseModel):
    app_type: Literal["command"]
    name: str
    command_path: str
    command_args: str = ""
