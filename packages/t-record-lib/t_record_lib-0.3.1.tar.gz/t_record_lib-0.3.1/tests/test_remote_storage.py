from pathlib import Path

from t_record.models.records_logs import RecordLog
from t_record.remote_storage import RemoteStorage


def test_remote_storage_lifecycle(tmp_storage_dir: Path) -> None:
    storage = RemoteStorage(tmp_storage_dir)
    logs = storage.get_records_logs()
    assert isinstance(logs.data, dict)

    logs.data["sample"] = RecordLog(record_id="sample", record="Sample Record")
    storage.update_records_logs(logs)
    assert (storage.root_path / "records_logs.json").exists()
