from typing import Literal, Optional, Sequence

from pydantic import BaseModel


class Entrypoint(BaseModel):
    name: str
    path: Optional[str] = None
    args: Optional[str] = None
    mounts: Optional[Sequence[str]] = None


class ContainerImage(BaseModel):
    path: str
    version: str


class Apptainer(BaseModel):
    app_type: Literal["apptainer"]
    container: ContainerImage
    global_args: Optional[str] = None
    entrypoints: Sequence[Entrypoint]
    mounts: Optional[Sequence[str]] = None
