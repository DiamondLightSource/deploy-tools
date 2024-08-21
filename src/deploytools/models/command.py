from typing import Literal

from .parent import ParentModel


class Command(ParentModel):
    """Represents a Command application.

    This runs the specified command with the specified arguments, as a bash script. All
    additional arguments and options on the command line are passed through to this
    command.
    """

    app_type: Literal["command"]
    name: str
    command_path: str
    command_args: str = ""
