from enum import StrEnum
from typing import Literal

from pydantic import Field

from .parent import ParentModel


class HashType(StrEnum):
    """
    Type of hash to use for the binary.
    """

    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"
    NONE = "none"


class BinaryApp(ParentModel):
    """
    Represents a standalone Binary application.
    This will fetch a standalone binary, validate its hash and add its
    location to that path.
    """

    app_type: Literal["binary"]
    name: str = Field(
        ...,
        description="Binary filename to use locally",
    )
    url: str = Field(
        ...,
        description="URL to download the binary from.",
    )
    hash_type: HashType = Field(
        ...,
        description="Type of hash used to check the binary.",
    )
    hash: str = Field(
        "",
        description="Hash to verify binary integrity",
    )
