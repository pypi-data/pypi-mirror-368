"""Module for managing records in the Thoughtful system."""
import warnings
from pathlib import Path
from typing import Any, Optional, get_args, get_origin

from pydantic import PrivateAttr, model_validator
from t_bug_catcher import report_error
from t_object import ThoughtfulObject

from .models.models import RecordStatus
from .records_manager import RecordsManager
from .utils.logger import logger

_records_manager: RecordsManager = None


def configure_records_tracing(folder_path: str | Path = "temp/Records") -> None:
    """Configure the RecordsManager for record tracing.
    folder_path: The path to the folder where records will be stored and shared.
    """
    global _records_manager
    try:
        _records_manager = RecordsManager(folder_path)
        logger.info("Records manager initialized successfully.")
    except Exception as e:
        logger.warning(f"Error initializing RecordsManager: {e}")
        report_error(exception=e)
        _records_manager = None
        raise e


class ThoughtfulRecord(ThoughtfulObject):
    """Base class for Thoughtful records."""

    _status_field: Optional[str] = PrivateAttr(default=None)

    @staticmethod
    def __is_record_status_field(annotation: Any) -> bool:
        origin = get_origin(annotation)
        args = get_args(annotation)
        return annotation is RecordStatus or (origin is Optional and args and args[0] is RecordStatus)

    def __detect_status_field(self) -> None:
        status_fields = [
            name for name, field in type(self).model_fields.items() if self.__is_record_status_field(field.annotation)
        ]

        if len(status_fields) > 1:
            raise ValueError(f"Only one 'RecordStatus' field is allowed for 'ThoughtfulRecord', found: {status_fields}")
        elif status_fields:
            self._status_field = status_fields[0]

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute on the ThoughtfulRecord instance."""
        prev_value = getattr(self, name, None)
        super().__setattr__(name, value)

        if name == self._status_field and prev_value != value and _records_manager:
            try:
                record_status = getattr(self, self._status_field)
                _records_manager.update_status(self, record_status)
            except Exception as e:
                logger.warning(f"Error updating status: {e}")
                report_error(exception=e)

    @model_validator(mode="after")
    def validate_and_register(self) -> "ThoughtfulRecord":  # noqa: F821
        """Initialize the ThoughtfulRecord."""
        if not hasattr(self, "id"):
            raise ValueError("ThoughtfulRecord requires an 'id' field")
        if not isinstance(self.id, str):
            raise ValueError("ThoughtfulRecord requires 'id' field to be a string")
        if not self.id.strip():
            raise ValueError("ThoughtfulRecord requires a non-empty 'id' field")

        self.__detect_status_field()
        if _records_manager is not None and not _records_manager.is_record_registered(self.id):
            try:
                _records_manager.register_record(self)
            except Exception as e:
                logger.warning(f"Error registering record: {e}")
                report_error(exception=e)

        return self

    def log_trace(self, action: str = "", reason: str = "", image: Optional[str] = "") -> None:
        """Log a step in the record."""
        if _records_manager is not None:
            try:
                _records_manager.log_trace(self, action, reason, image)
            except Exception as e:
                logger.warning(f"Error logging step: {e}")
                report_error(exception=e)

    def get_traces(self) -> list[dict]:
        """Get all traces for the record."""
        if _records_manager is not None:
            return _records_manager.get_traces(self)
        else:
            return []


def dump_records() -> None:
    """Dump all records to the storage."""
    if _records_manager is not None:
        try:
            _records_manager.dump()
            logger.info("Records dumped successfully.")
        except Exception as e:
            logger.warning(f"Error dumping records: {e}")
            report_error(exception=e)
    else:
        logger.warning("T-Record wasn't configured. Cannot dump records.")


def pack_sharable_zip(file_path: str = "records.zip") -> None:
    """Pack all records to a zip file."""
    if _records_manager is not None:
        try:
            logger.info("Packing records to zip...")
            _records_manager.pack_sharable_zip(file_path)
            logger.info(f"Records data packed to {file_path} successfully.")
        except Exception as e:
            logger.warning(f"Error packing records to zip: {e}")
            report_error(exception=e)
    else:
        logger.warning("T-Record wasn't configured. Cannot pack records to zip.")


def save_records_to_html(file_path: str = "records.html") -> None:
    """Save all records to an HTML file."""
    if _records_manager is not None:
        try:
            logger.info("Generating records HTML...")
            _records_manager.save_records_to_html(file_path)
            logger.info(f"Records HTML saved to {file_path} successfully.")
        except Exception as e:
            logger.warning(f"Error saving records HTML: {e}")
            report_error(exception=e)
    else:
        logger.warning("T-Record wasn't configured. Cannot save records HTML.")


def dump_records_html(file_path: str = "records.html") -> None:
    """[DEPRECATED] Use save_records_to_html instead."""
    warnings.warn(
        "dump_records_html() is deprecated and will be removed in a future version. "
        "Use save_records_to_html() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    save_records_to_html(file_path)
