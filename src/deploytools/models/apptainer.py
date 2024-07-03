from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field


class EntrypointOptionsModel(BaseModel):
    apptainer_args: str = ""
    command_args: str = ""
    mounts: Sequence[str] = []


class EntrypointModel(BaseModel):
    executable_name: str
    command: Optional[str] = None
    options: EntrypointOptionsModel = Field(default_factory=EntrypointOptionsModel)


class ContainerImageModel(BaseModel):
    path: str
    version: str


class ApptainerModel(BaseModel):
    app_type: Literal["apptainer"]
    name: str
    version: str
    container: ContainerImageModel
    entrypoints: Sequence[EntrypointModel]
    global_options: EntrypointOptionsModel = Field(
        default_factory=EntrypointOptionsModel
    )
