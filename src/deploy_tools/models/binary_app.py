from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AnyUrl, Field, StringConstraints

from .app import ENTRYPOINT_NAME_REGEX
from .parent import ParentModel


class HashType(StrEnum):
    """Type of hash to use for the binary."""

    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"
    NONE = "none"


class BinaryApp(ParentModel):
    """Represents a standalone Binary application.

    This will fetch a standalone binary, validate its hash and add its
    location to the path.
    """

    app_type: Annotated[
        Literal["binary"],
        Field(description="A standalone binary to be downloaded and added to the path"),
    ]
    name: Annotated[
        str,
        StringConstraints(pattern=ENTRYPOINT_NAME_REGEX),
        Field(description="Name of executable to use after loading the Module"),
    ]
    url: Annotated[AnyUrl, Field(description="URL to download the binary from")]
    hash: Annotated[str, Field(description="Hash to verify binary integrity")] = ""
    hash_type: Annotated[
        HashType, Field(description="Type of hash used to check the binary")
    ]
