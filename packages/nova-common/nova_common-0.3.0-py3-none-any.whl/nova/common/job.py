"""Job related classes."""

from enum import Enum

from pydantic import BaseModel


class WorkState(Enum):
    """The state of a job."""

    NOT_STARTED = "not_started"
    UPLOADING_DATA = "uploading"
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    DELETED = "deleted"
    CANCELED = "canceled"
    STOPPING = "stopping"
    CANCELING = "canceling"


class ToolOutputs(BaseModel):
    """Class that for tool outputs."""

    stdout: str = ""
    stderr: str = ""
