"""Module to manage records logs."""
from t_object import ThoughtfulObject

from .trace import Trace
from ..models.status_update import StatusUpdate


class RecordLog(ThoughtfulObject):
    """Class to represent a record log."""

    record_id: str
    record: str
    status: str = ""
    status_color: str = ""
    status_updates: list[StatusUpdate] = []
    traces: list[Trace] = []


class RecordsLogs(ThoughtfulObject):
    """Class to manage records logs."""

    data: dict[str, RecordLog] = {}
