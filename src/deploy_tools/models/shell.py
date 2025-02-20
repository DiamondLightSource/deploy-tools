from typing import Literal

from .parent import ParentModel


class Shell(ParentModel):
    """Represents a Shell application.

    This will run the code specified as a shell script. This currently uses Bash for
    improved functionality while retaining high compatibility with various Linux
    distributions.
    """

    app_type: Literal["shell"]
    name: str
    script: list[str]
