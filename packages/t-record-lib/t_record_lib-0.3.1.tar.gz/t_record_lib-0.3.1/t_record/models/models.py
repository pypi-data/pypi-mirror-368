"""Module for defining various models used in the system."""
from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class RecordStatus(str):
    """Class to represent the status of a record."""

    def __new__(cls, value: str, color: str = "transparent"):
        """Create a new RecordStatus instance."""
        obj = str.__new__(cls, value)
        obj.color = color
        return obj

    def __repr__(self):
        """Return a string representation of the RecordStatus instance."""
        return f"RecordStatus({super().__repr__()}, color={self.color!r})"

    @classmethod
    def __get_pydantic_core_schema__(
        cls: "RecordStatus", _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Get the core schema for the RecordStatus class."""
        return core_schema.no_info_plain_validator_function(cls._validate)

    @classmethod
    def _validate(cls: "RecordStatus", value: Any) -> "RecordStatus":
        """Validate the value to ensure it's a valid RecordStatus."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            return cls(value)
        raise TypeError("RecordStatus must be created from str or RecordStatus")

    @classmethod
    def __get_pydantic_json_schema__(
        cls: "RecordStatus", core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Tell Pydantic how to represent this type in JSON Schema"""
        return {"type": "string", "title": "RecordStatus", "description": "A string with optional color attribute"}


class Status:
    """Model for representing various statuses in the system."""

    EMPTY = RecordStatus("Empty", color="white")
    SUCCESS = RecordStatus("Success", color="limegreen")  # Fresh green
    EXCEPTION = RecordStatus("Exception", color="crimson")  # Rich red
    WARNING = RecordStatus("Warning", color="gold")  # Golden yellow
    PENDING = RecordStatus("Pending", color="deepskyblue")  # Bright blue
    RUNNING = RecordStatus("Running", color="dodgerblue")  # Slightly deeper blue
    SKIPPED = RecordStatus("Skipped", color="lightgrey")  # Soft grey
    FAILED = RecordStatus("Failed", color="firebrick")  # Darker red
    COMPLETED = RecordStatus("Completed", color="seagreen")  # Distinct from SUCCESS
    IN_PROGRESS = RecordStatus("In Progress", color="cornflowerblue")  # Mid blue
    CANCELLED = RecordStatus("Cancelled", color="darkorange")  # Strong orange

    RETRYING = RecordStatus("Retrying", color="violet")  # Purple shade
    TIMEOUT = RecordStatus("Timeout", color="orangered")  # Alarm red/orange
    STALE = RecordStatus("Stale", color="darkgray")  # Neutral dull
    AWAITING_REVIEW = RecordStatus("Awaiting Review", color="mediumslateblue")  # Calm bluish tone
    APPROVED = RecordStatus("Approved", color="mediumseagreen")  # Light green
    REJECTED = RecordStatus("Rejected", color="indianred")  # Soft red tone
    ON_HOLD = RecordStatus("On Hold", color="khaki")  # Warm yellow
    RESTARTED = RecordStatus("Restarted", color="mediumvioletred")  # Punchy pink/purple
