from typing import Literal

from .parent import ParentModel


class BinaryApp(ParentModel):
    """
    Represents a standalone Binary application.

    This will fetch a standalone binary, validate its sha256 and add its
    location to that path.
    """

    app_type: Literal["binary"]
    name: str
    url: str
    sha256: str
