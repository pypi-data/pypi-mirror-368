"""StatusUpdate class to represent a status update trace of an action taken on an object."""
from datetime import datetime

from t_object import ThoughtfulObject


class StatusUpdate(ThoughtfulObject):
    """Class to represent a status update trace of an action taken on an object."""

    timestamp: datetime
    old_status: str
    old_status_color: str
    new_status: str
    new_status_color: str
    traceback: str = ""

    def to_html(self) -> str:
        """Convert the trace to an HTML representation."""
        return (
            f"<p><strong>{self.timestamp:%Y-%m-%d %H:%M:%S}</strong> - "
            f"Status update: {self.old_status} -> {self.new_status}</p>"
        )
