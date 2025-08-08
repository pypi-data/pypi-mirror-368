"""Top-level package for T-Record."""

__author__ = """Thoughtful"""
__email__ = "support@thoughtful.ai"
__version__ = "__version__ = '0.3.1'"

from .models.models import RecordStatus, Status
from .record import (
    ThoughtfulRecord,
    dump_records,
    pack_sharable_zip,
    configure_records_tracing,
    dump_records_html,
    save_records_to_html,
)

__all__ = [
    "ThoughtfulRecord",
    "dump_records",
    "pack_sharable_zip",
    "RecordStatus",
    "Status",
    "configure_records_tracing",
    "dump_records_html",
    "save_records_to_html",
]
