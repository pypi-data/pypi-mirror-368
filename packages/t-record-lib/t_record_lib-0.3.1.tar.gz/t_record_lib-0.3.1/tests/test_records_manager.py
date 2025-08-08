from pathlib import Path

from t_record import Status
from t_record.records_manager import RecordsManager
from t_record.remote_storage import RemoteStorage
from tests.conftest import SimpleRecord


def test_storage_writes(tmp_storage_dir: Path) -> None:
    storage = RemoteStorage(tmp_storage_dir)
    logs = storage.get_records_logs()
    assert isinstance(logs.data, dict)


def test_register_and_update(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    mgr = RecordsManager(tmp_storage_dir)
    rec = simple_record
    rec._status_field = None
    mgr.register_record(rec)
    assert simple_record.id in mgr.local_records_logs.data

    mgr.update_status(rec, Status.COMPLETED)
    log = mgr.local_records_logs.data[simple_record.id]
    assert log.status == Status.COMPLETED


def test_merge_logs(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    mgr1 = RecordsManager(tmp_storage_dir)
    rec = simple_record
    mgr1.register_record(rec)
    mgr1.dump()

    # new manager simulating new run
    mgr2 = RecordsManager(tmp_storage_dir)
    assert rec.id in mgr2.global_records_logs.data


def test_get_traces_only_local(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    mgr = RecordsManager(tmp_storage_dir)
    rec = simple_record
    mgr.register_record(rec)
    mgr.log_trace(rec, action="Local action", reason="testing local only")

    traces = mgr.get_traces(rec)
    assert len(traces) == 2
    assert traces[1]["action"] == "Local action"


def test_get_traces_only_global(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    # First manager to register + dump to global
    mgr1 = RecordsManager(tmp_storage_dir)
    rec = simple_record
    mgr1.register_record(rec)
    mgr1.log_trace(rec, action="Global action", reason="testing global only")
    mgr1.dump()

    # New manager simulating new run, local logs empty, but global logs loaded
    mgr2 = RecordsManager(tmp_storage_dir)
    traces = mgr2.get_traces(rec)
    assert len(traces) == 2
    assert traces[1]["action"] == "Global action"


def test_get_traces_combined(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    # First run: register + dump global
    mgr1 = RecordsManager(tmp_storage_dir)
    rec = simple_record
    mgr1.register_record(rec)
    mgr1.log_trace(rec, action="Global action", reason="testing global")
    mgr1.dump()

    # Second run: simulate local logs
    mgr2 = RecordsManager(tmp_storage_dir)
    mgr2.get_or_prepare_local_record_log(rec)  # ensures local log exists
    mgr2.log_trace(rec, action="Local action", reason="testing local")

    traces = mgr2.get_traces(rec)
    assert len(traces) == 3
    assert traces[1]["action"] == "Global action"
    assert traces[2]["action"] == "Local action"


def test_dump_clears_local_traces_and_status_updates(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    mgr = RecordsManager(tmp_storage_dir)
    rec = simple_record

    # Register and add data
    mgr.register_record(rec)
    mgr.update_status(rec, Status.COMPLETED)
    mgr.log_trace(rec, action="Testing dump", reason="should clear traces after dump")

    # Check local data populated before dump
    log = mgr.local_records_logs.data[rec.id]
    assert len(log.traces) == 2
    assert len(log.status_updates) == 1

    # Perform dump
    mgr.dump()

    # Should still have record logs entry
    assert rec.id in mgr.local_records_logs.data

    # But traces and status_updates must be cleared
    log_after = mgr.local_records_logs.data[rec.id]
    assert log_after.traces == []
    assert log_after.status_updates == []
