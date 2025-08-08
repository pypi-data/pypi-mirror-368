from t_record.report.html_generator import generate_enhanced_html
from t_record.models.records_logs import RecordLog
from t_record.models.trace import Trace
from t_record.models.status_update import StatusUpdate
from t_record.utils.utils import compare_dicts
from datetime import datetime, timedelta


def test_generate_html_includes_content() -> None:
    # Record 1
    dict1 = {"field1": "value1", "field2": "value2"}
    dict2 = {"field1": "value3", "field2": "value4"}

    trace1 = Trace(
        action="create",
        reason="Initial creation",
        timestamp=datetime.now() - timedelta(days=2),
        dict_updates={},
        image="/path/to/image1.png",
        caller_name="user1",
        traceback="Traceback info 1",
    )
    status_update1 = StatusUpdate(
        timestamp=datetime.now() - timedelta(days=1, hours=2),
        old_status="pending",
        old_status_color="yellow",
        new_status="approved",
        new_status_color="green",
        traceback="Status traceback 1",
    )
    record_log1 = RecordLog(
        record_id="r123",
        record="TypeA",
        status="approved",
        status_color="green",
        status_updates=[status_update1],
        traces=[trace1],
    )

    # Record 2
    trace2 = Trace(
        action="update",
        reason="Field updated",
        timestamp=datetime.now() - timedelta(days=1),
        dict_updates=compare_dicts(dict1, dict2),
        image="/path/to/image2.png",
        caller_name="user2",
        traceback="Traceback info 2",
    )
    status_update2 = StatusUpdate(
        timestamp=datetime.now() - timedelta(hours=5),
        old_status="approved",
        old_status_color="green",
        new_status="completed",
        new_status_color="blue",
        traceback="Status traceback 2",
    )
    record_log2 = RecordLog(
        record_id="r456",
        record="TypeB",
        status="completed",
        status_color="blue",
        status_updates=[status_update2],
        traces=[trace2],
    )

    # Record 3 (no traces, only status updates)
    status_update3 = StatusUpdate(
        timestamp=datetime.now() - timedelta(hours=1),
        old_status="in_progress",
        old_status_color="orange",
        new_status="failed",
        new_status_color="red",
        traceback="Status traceback 3",
    )
    record_log3 = RecordLog(
        record_id="r789",
        record="TypeC",
        status="failed",
        status_color="red",
        status_updates=[status_update3],
        traces=[],
    )

    # Record 4 (empty status)
    record_log4 = RecordLog(record_id="r000", record="TypeD", status="", status_color="", status_updates=[], traces=[])

    logs = {
        "r123": record_log1,
        "r456": record_log2,
        "r789": record_log3,
        "r000": record_log4,
    }

    html = generate_enhanced_html(logs)
    for record_id in logs:
        assert record_id in html
    assert "<html" in html
    assert "Initial creation" in html
    assert "Field updated" in html
    assert "failed" in html
    assert "TypeD" in html
