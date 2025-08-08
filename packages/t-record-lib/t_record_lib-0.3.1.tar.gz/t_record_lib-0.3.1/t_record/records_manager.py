"""Module to manage records and their logs for the StepTracer library."""
import json
import os
import shutil
import tempfile
import traceback
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models.models import RecordStatus
from .models.records_logs import RecordLog, RecordsLogs
from .models.status_update import StatusUpdate
from .models.trace import Trace
from .remote_storage import RemoteStorage
from .report.html_generator import generate_enhanced_html
from .utils.utils import compare_dicts, format_traceback_short, sanitize_path_filename, get_image_src_uri


class RecordsManager:
    """Singleton class to manage records and their logs."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one instance of RecordsManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, root_folder: str | Path):
        """Initialize the RecordsManager with a root folder."""
        self.storage: RemoteStorage = RemoteStorage(root_folder)
        self.global_records_logs: RecordsLogs = self.storage.get_records_logs()
        self.local_records_logs: RecordsLogs = RecordsLogs()
        self.temp_dir = tempfile.TemporaryDirectory()

    def dump(self) -> None:
        """Dump the local records logs to the remote storage."""
        self.storage.update_records_logs(self.local_records_logs)

        # Clear local records logs after dumping
        for record_log in self.local_records_logs.data.values():
            record_log.traces.clear()
            record_log.status_updates.clear()

        self.temp_dir.cleanup()

    def pack_sharable_zip(self, file_path: str) -> None:
        """Pack all records logs and HTML report into a zip file."""
        merged_logs = self.storage.get_records_logs()
        html_content = generate_enhanced_html(merged_logs.data)

        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Add HTML file
            zipf.writestr("records.html", html_content)

            with tempfile.TemporaryDirectory() as temp_dir:
                for records_log in merged_logs.data.values():
                    for trace in records_log.traces:
                        if trace.image:
                            trace_image_name = os.path.basename(trace.image)
                            image_path = self.storage.get_image(trace_image_name, output_folder=temp_dir)
                            arcname = Path("images") / image_path.name
                            zipf.write(image_path, arcname=arcname)

    def save_records_to_html(self, file_path: str) -> None:
        """Dump all records logs to an HTML file."""
        merged_logs = self.storage.get_records_logs()

        for log in merged_logs.data.values():
            for trace in log.traces:
                if trace.image:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        trace_image_name = os.path.basename(trace.image)
                        img_path = self.storage.get_image(trace_image_name, output_folder=temp_dir)
                        trace.image_src_uri = get_image_src_uri(str(img_path))

        # Generate HTML content from merged logs
        html_content = generate_enhanced_html(merged_logs.data, add_images_as_uri=True)
        Path(file_path).write_text(html_content, encoding="utf-8")

    def is_record_registered(self, record_id: str) -> bool:
        """Check if a record is already registered."""
        return record_id in self.global_records_logs.data or record_id in self.local_records_logs.data

    def register_record(self, record: "ThoughtfulRecord") -> None:  # noqa: F821
        """Register a new record and initialize its log."""
        current_dict = json.loads(record.to_json_str())
        dict_updates = compare_dicts({}, current_dict)

        trace = Trace(
            action="Initialize record",
            timestamp=datetime.now(),
            dict_updates=dict_updates,
            traceback=format_traceback_short(traceback.extract_stack()[:-2]),
        )

        new_log = RecordLog(record_id=record.id, record=record.to_json_str(), traces=[trace])

        if record._status_field:
            record_status: RecordStatus = getattr(record, record._status_field)
            if isinstance(record_status, str):
                record_status = RecordStatus(record_status)
            new_log.status = record_status
            new_log.status_color = record_status.color

        self.local_records_logs.data[record.id] = new_log

    def get_or_prepare_local_record_log(self, record: "ThoughtfulRecord") -> RecordLog:  # noqa: F821
        """Get record_log for record, ensure it is present in local_records_logs."""
        if record.id in self.local_records_logs.data:
            return self.local_records_logs.data[record.id]

        if record.id in self.global_records_logs.data:
            global_log = self.global_records_logs.data[record.id]

            # Create local log copy — only essential fields
            local_log = RecordLog(
                record_id=global_log.record_id,
                record=global_log.record,
                status=global_log.status,
                status_color=global_log.status_color,
                status_updates=[],
                traces=[],
            )

            self.local_records_logs.data[record.id] = local_log
            return local_log

        raise RuntimeError(f"Record {record.id} is not registered — this should not happen!")

    def update_status(self, record: "ThoughtfulRecord", new_status: RecordStatus) -> None:  # noqa: F821
        """Update the status of a record and log the change."""
        record_log = self.get_or_prepare_local_record_log(record)

        status_update = StatusUpdate(
            timestamp=datetime.now(),
            old_status=record_log.status,
            old_status_color=record_log.status_color,
            new_status=new_status,
            new_status_color=new_status.color,
            traceback=format_traceback_short(traceback.extract_stack()[:-2]),
        )

        record_log.status_updates.append(status_update)
        record_log.status = new_status
        record_log.status_color = new_status.color

    def get_traces(self, record: "ThoughtfulRecord") -> list[dict]:  # noqa: F821
        """Get all traces for a record."""
        traces = []
        global_records_logs = self.storage.get_global_records_logs()
        if record.id in global_records_logs.data:
            traces.extend(global_records_logs.data[record.id].traces)

        local_record_log = self.get_or_prepare_local_record_log(record)
        traces.extend(local_record_log.traces)

        traces_data = []
        for trace in traces:
            traces_data.append(
                {"action": trace.action, "reason": trace.reason, "timestamp": trace.timestamp.isoformat()}
            )
        return traces_data

    def log_trace(
        self, record: "ThoughtfulRecord", action: str, reason: str, image: Optional[str] = ""  # noqa: F821
    ) -> None:
        """Log a trace for a record with the specified action, reason, and optional image."""
        record_log = self.get_or_prepare_local_record_log(record)

        previous_dict = json.loads(record_log.record)
        current_dict = json.loads(record.to_json_str())
        record_log.record = record.to_json_str()

        dict_updates = compare_dicts(previous_dict, current_dict)

        if image:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S_%f")[:-3]
            unique_image_name = f"{timestamp}{Path(image).suffix}"

            file_name = sanitize_path_filename(unique_image_name)
            dest = Path(self.temp_dir.name) / file_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            image = shutil.copy(image, dest)

        trace = Trace(
            action=action,
            reason=reason,
            timestamp=datetime.now(),
            dict_updates=dict_updates,
            image=str(image),
            traceback=format_traceback_short(traceback.extract_stack()[:-2]),
        )

        record_log.traces.append(trace)
