"""Module for remote storage operations."""
import os.path
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from t_utils.const_utils import EMPOWER_RUN_ID
from t_utils.robocloud_utils import RC_PROCESS_NAME

from .models.records_logs import RecordsLogs
from .utils.utils import SimpleFileLock
from .utils.logger import logger

HTML_FILE_NAME = "records_report.html"


class RemoteStorage:
    """Class to manage remote storage for records logs."""

    def __init__(self, root_folder_path: str | Path):
        """Initialize the RemoteStorage."""
        process_name = RC_PROCESS_NAME or "process_name"
        run_id = EMPOWER_RUN_ID or "run_id"

        process_path = Path(root_folder_path) / process_name
        self.root_path: Path = process_path / run_id
        self._cleanup_old_runs(process_path)

    def _cleanup_old_runs(self, process_path: Path, days: int = 7) -> None:
        """Delete folders older than a given number of days."""
        if not process_path.exists():
            return

        now = datetime.now()
        threshold = timedelta(days=days)
        items_to_delete = []

        for item in process_path.iterdir():
            if item.is_dir() and item != self.root_path:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if now - mtime > threshold:
                    items_to_delete.append(item)

        if not items_to_delete:
            return

        logger.info(f"Cleaning up old runs in {process_path}. Found {len(items_to_delete)} items to delete.")

        deleted_count = 0
        for item in items_to_delete:
            try:
                shutil.rmtree(item)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to remove folder {item}: {e}")

        logger.info(f"Cleanup finished. {deleted_count} old run folder(s) removed.")

    def get_records_logs(self) -> RecordsLogs:
        """Get all records for a given run_id."""
        json_file = self.root_path / "records_logs.json"
        if json_file.exists():
            return RecordsLogs.load_from_json_file(json_file)
        else:
            return RecordsLogs()

    def get_global_records_logs(self) -> RecordsLogs:
        json_file = self.root_path / "records_logs.json"
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as file:
                return RecordsLogs.model_validate_json(file.read())
        else:
            return RecordsLogs()

    def update_records_logs(self, new_records: RecordsLogs) -> None:
        """Safely merge local logs with global logs (parallel-safe)."""
        self.root_path.mkdir(parents=True, exist_ok=True)
        json_file = self.root_path / "records_logs.json"
        lock_file = self.root_path / "records_logs.json.lock"

        with SimpleFileLock(lock_file):
            existing_records = self.get_global_records_logs()

            for record_id, new_log in new_records.data.items():
                if record_id in existing_records.data:
                    existing_log = existing_records.data[record_id]
                    existing_log.traces.extend(new_log.traces)
                    existing_log.status_updates.extend(new_log.status_updates)

                    if existing_log.record != new_log.record:
                        existing_log.record = new_log.record
                    existing_log.status = new_log.status
                    existing_log.status_color = new_log.status_color
                else:
                    existing_records.data[record_id] = new_log

                for trace in new_log.traces:
                    if trace.image and os.path.exists(trace.image):
                        new_image_path = self.root_path / trace.html_image_path
                        new_image_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(trace.image, new_image_path)

            with open(json_file, "w", encoding="utf-8") as file:
                file.write(existing_records.to_json_str())

    def get_image(self, image_name: str, output_folder: str | Path = None) -> Path:
        """Get an image from the remote storage and copy it to the specified output folder.

        Args:
            image_name: Name of the image file to retrieve.
            output_folder: Optional; folder to copy the image to. If None, uses current directory.
        Returns:
            The path to the copied image file.
        """
        image_file_path = self.root_path / "images" / image_name
        if output_folder is None:
            dst_image_path = Path(image_name)
        else:
            dst_image_path = Path(output_folder) / image_name

        shutil.copyfile(image_file_path, dst_image_path)
        return dst_image_path
