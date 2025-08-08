import warnings
import zipfile
import json
from pathlib import Path
from typing import Any

from t_record import Status
from t_record.record import (
    configure_records_tracing,
    dump_records,
    pack_sharable_zip,
    dump_records_html,
    save_records_to_html,
)
from tests.conftest import SimpleRecord


def test_record_lifecycle(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    simple_record.status = simple_record.status
    simple_record.log_trace(action="start", reason="testing")
    dump_records()

    process_folder = next(tmp_storage_dir.glob("*/*"))
    assert (process_folder / "records_logs.json").exists()

    html_file = process_folder / "records_report.html"
    save_records_to_html(str(html_file))
    html_content = html_file.read_text()
    assert "test123" in html_content

    zip_file = tmp_storage_dir / "out.zip"
    pack_sharable_zip(str(zip_file))
    assert zip_file.exists()
    with zipfile.ZipFile(zip_file) as zf:
        assert any("records.html" in n for n in zf.namelist())


def test_persistence_across_runs(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    # First run
    configure_records_tracing(tmp_storage_dir)
    rec = simple_record
    rec.status = Status.RUNNING
    rec.log_trace("first")
    dump_records()

    # Second run, continuing history
    configure_records_tracing(tmp_storage_dir)
    rec2 = simple_record
    rec2.status = Status.COMPLETED
    rec2.log_trace("second")
    dump_records()

    process_folder = next(tmp_storage_dir.glob("*/*"))
    json_file = process_folder / "records_logs.json"
    data = json.loads(json_file.read_text())
    assert len(data["data"][rec2.id]["traces"]) >= 3
    assert any(trace["action"] == "first" for trace in data["data"][rec2.id]["traces"])


def test_status_updates_logged(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    record = simple_record
    record.status = Status.RUNNING
    record.log_trace("doing")
    dump_records()

    process_folder = next(tmp_storage_dir.glob("*/*"))
    data = json.loads((process_folder / "records_logs.json").read_text())
    assert record.id in data["data"]


def test_log_trace_with_images(tmp_storage_dir: Path, simple_record: SimpleRecord) -> None:
    record = simple_record

    # Create dummy images and log traces with them
    dummy_images = []
    for i in range(3):
        img_path = tmp_storage_dir / f"test_image_{i}.png"
        img_path.parent.mkdir(parents=True, exist_ok=True)
        img_path.write_text("fake content")  # Simulating an image file
        dummy_images.append(str(img_path))
        record.log_trace(action=f"test_action_{i}", reason=f"test_reason_{i}", image=str(img_path))

    dump_records()
    traces = record.get_traces()

    # Verify each trace contains the correct image name format
    image_traces = [t for t in traces if t["action"].startswith("test_action_")]
    assert len(image_traces) == 3


def test_log_trace_with_complex_id(tmp_storage_dir: Path) -> None:
    configure_records_tracing(tmp_storage_dir)

    complex_id = "  my<>inv:alid/ID\\with*?|chars🙂.and...spaces  "
    record = SimpleRecord(id=complex_id, status=Status.EMPTY)

    # Create a dummy image
    img_path = tmp_storage_dir / "very_real_image.png"
    img_path.parent.mkdir(parents=True, exist_ok=True)
    img_path.write_text("image content")

    record.log_trace("complex id test", "to check sanitize", image=str(img_path))
    dump_records()

    traces = record.get_traces()
    assert traces[-1]["action"] == "complex id test"


def test_dump_records_html_deprecated(monkeypatch: Any) -> None:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        dump_records_html("test.html")
        assert any("deprecated" in str(warn.message).lower() for warn in w)
