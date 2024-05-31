from typing import Literal

from pydantic import BaseModel


class RunfileModel(BaseModel):
    app_type: Literal["runfile"]
    path: str
    global_args: str
