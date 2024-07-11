from typing import Literal, Optional, Sequence

from pydantic import BaseModel, Field


class EntrypointOptionsConfig(BaseModel):
    apptainer_args: str = ""
    command_args: str = ""
    mounts: Sequence[str] = []


class EntrypointConfig(BaseModel):
    executable_name: str
    command: Optional[str] = None
    options: EntrypointOptionsConfig = Field(default_factory=EntrypointOptionsConfig)


class ContainerImageConfig(BaseModel):
    path: str
    version: str


class ApptainerConfig(BaseModel):
    app_type: Literal["apptainer"]
    name: str
    version: str
    container: ContainerImageConfig
    entrypoints: Sequence[EntrypointConfig]
    global_options: EntrypointOptionsConfig = Field(
        default_factory=EntrypointOptionsConfig
    )
