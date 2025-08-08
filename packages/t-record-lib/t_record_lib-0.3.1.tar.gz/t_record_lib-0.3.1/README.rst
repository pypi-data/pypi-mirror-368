T-Record
========

A lightweight Python library for robust record tracing, status tracking, and detailed logging —
built for automation pipelines and data integrity.

Features
--------

* **ThoughtfulRecord model**
  Track each record's status, lifecycle, and traces with robust JSON-serializable objects.

* **Automatic history**
  Dumps detailed logs, merges previous runs seamlessly, preserving full audit history.

* **Enhanced HTML reports**
  Auto-generates beautiful HTML reports with status summary, traces, diffs, and screenshots.

* **Portable archive**
  Packs all data (logs + images + HTML) into a shareable ZIP file.

* **Fail-safe logging**
  Internally uses ``try/except`` to ensure tracing never crashes your main process.

Installation
------------

Install via pip::

    pip install t-record-lib

Or for local development::

    git clone https://github.com/YOUR_ORG/t_record.git
    cd t_record
    pip install -e .

Quickstart
----------

.. code-block:: python

    from t_record.record import configure_records_tracing, ThoughtfulRecord, dump_records, pack_sharable_zip, RecordStatus

    # 1. Configure
    configure_records_tracing("records_folder")

    # 2. Create your record
    class MyRecord(ThoughtfulRecord):
        id: str
        status: RecordStatus = ""

    record = MyRecord(id="rec_001")

    # 3. Change status or add traces
    record.status = Status.RUNNING
    record.log_trace("Started processing", reason="Data loaded")

    # 4. Save everything
    dump_records()

    # 5. Create shareable ZIP
    pack_sharable_zip("records.zip")

Output files
------------

By default, each run will produce::

    /records_folder/{process_name}/{run_id}/
        records_logs.json     # full structured logs (merged from previous runs)
        records_report.html   # human-readable dashboard
        /images/              # attached screenshots

Plus a zip archive on demand.

Advanced usage
--------------

* Continue an existing run (merges history automatically)::

    configure_record_tracing("records_folder")
    record = MyRecord(id="rec_001")  # picks up previous traces
    record.status = Status.COMPLETED
    dump_records()

* Add an image trace::

    record.log_trace("Reviewed", reason="Visual QC", image="path/to/image.png")




