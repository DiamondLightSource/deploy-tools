from typing import Literal

from pydantic import BaseModel


class Shell(BaseModel, extra="forbid"):
    """Represents a Shell application.

    This will run the code specified as a shell script. This currently uses Bash for
    improved functionality while retaining high compatibility with various Linux
    operating systems.
    """

    app_type: Literal["shell"]
    name: str
    script: list[str]
