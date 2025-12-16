from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from .app import ENTRYPOINT_NAME_REGEX
from .parent import ParentModel


class ShellApp(ParentModel):
    """Represents a Shell application.

    This will run the code specified as a shell script. This currently uses Bash for
    improved functionality while retaining high compatibility with various Linux
    distributions.
    """

    app_type: Annotated[
        Literal["shell"],
        Field(description="A shell application with the given script"),
    ]
    name: Annotated[
        str,
        StringConstraints(pattern=ENTRYPOINT_NAME_REGEX),
        Field(description="Name of executable to use after loading the Module"),
    ]
    script: Annotated[list[str], Field(description="Script to be run")] = []
