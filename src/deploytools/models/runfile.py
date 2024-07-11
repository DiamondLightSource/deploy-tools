from typing import Literal

from pydantic import BaseModel


class RunFileConfig(BaseModel):
    app_type: Literal["runfile"]
    name: str
    command_path: str
    command_args: str = ""
