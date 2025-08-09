"""Signal related classes/enums."""

from enum import Enum


class Signal(str, Enum):
    """Available signal prefixes."""

    PROGRESS = "progress"
    OUTPUTS = "outputs"
    TOOL_COMMAND = "tool_command"
    ERROR_MESSAGE = "error_message"
    GET_ALL_TOOLS = "get_all_running_tools"
    EXIT_SIGNAL = "kill_jobs_on_exit"
    CUSTOM_SIGNAL = "custom"


def get_signal_id(id: str, signal: str) -> str:
    return f"{id}_{signal}"


class ToolCommand(str, Enum):
    """Available commands for tools."""

    STOP = "stop"
    START = "start"
    CANCEL = "cancel"
    GET_RESULTS = "get_results"
