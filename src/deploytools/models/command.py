from typing import Literal

from pydantic import BaseModel


class Command(BaseModel, extra="forbid"):
    """Represents a Command application.

    This runs the specified command with the specified arguments, as a bash script. All
    additional arguments and options on the command line are passed through to this
    command.
    """

    app_type: Literal["command"]
    name: str
    command_path: str
    command_args: str = ""
