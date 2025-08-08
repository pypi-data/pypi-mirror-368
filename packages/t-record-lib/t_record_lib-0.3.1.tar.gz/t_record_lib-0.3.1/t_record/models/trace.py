"""Module to handle traces of actions taken on objects."""
import os.path
from datetime import datetime

from t_object import ThoughtfulObject


class Trace(ThoughtfulObject):
    """Class to represent a trace of an action taken on an object."""

    action: str = ""
    reason: str = ""
    timestamp: datetime
    dict_updates: dict[str, dict[str, any]] = {}
    image: str = ""
    caller_name: str = ""
    traceback: str = ""
    image_src_uri: str = ""

    @property
    def html_image_path(self) -> str:
        """Return the path to the image."""
        if self.image:
            return os.path.join("images", os.path.basename(self.image))
        return ""
