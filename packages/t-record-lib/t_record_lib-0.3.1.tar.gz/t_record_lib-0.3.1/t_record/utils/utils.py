"""Utility functions for t_record."""
import base64
import json
import os
import re
import time
import traceback
from pathlib import Path
from typing import Any


def __format_value(val: Any) -> str:
    if val is True:
        return "true"
    elif val is False:
        return "false"
    elif val is None:
        return "null"
    else:
        return json.dumps(val)


def compare_dicts(d1: dict, d2: dict, path: str = "") -> dict:
    """Compare two dictionaries and return a dict of differences with 'from' and 'to' values,
    skipping values where both sides are None."""
    updates = {}

    for key in d1.keys() | d2.keys():
        new_path = f"{path}.{key}" if path else key
        has_old = key in d1
        has_new = key in d2
        v1 = d1.get(key)
        v2 = d2.get(key)

        if isinstance(v1, dict) and isinstance(v2, dict):
            nested_updates = compare_dicts(v1, v2, new_path)
            updates.update(nested_updates)
        elif isinstance(v2, dict) and v1 is None:
            nested_updates = compare_dicts({}, v2, new_path)
            updates.update(nested_updates)
        elif isinstance(v1, dict) and v2 is None:
            nested_updates = compare_dicts(v1, {}, new_path)
            updates.update(nested_updates)

        elif has_old and not has_new:
            if v1 is not None:  # Don't add if both are None
                updates[new_path] = {"from": v1, "to": None}
        elif not has_old and has_new:
            if v2 is not None:  # Don't add if both are None
                updates[new_path] = {"from": None, "to": v2}
        elif v1 != v2:
            if v1 is None and v2 is None:
                continue
            updates[new_path] = {"from": v1, "to": v2}

    return updates


def format_traceback_short(stack: list[traceback.FrameSummary] = None, work_dir: str = None) -> str:
    """Format the traceback for better readability."""
    if stack is None:
        stack = traceback.extract_stack()[:-2]

    work_dir = work_dir or os.getcwd()
    formatted = []

    for frame in stack:
        if "site-packages" in frame.filename or "<frozen" in frame.filename:
            continue

        try:
            rel_path = os.path.relpath(frame.filename, work_dir)
        except ValueError:
            rel_path = frame.filename

        if frame.name != "<module>":
            formatted.append(f"{rel_path}:{frame.lineno} ({frame.name})")
        else:
            formatted.append(f"{rel_path}:{frame.lineno}")

    return "\n".join(formatted)


class SimpleFileLock:
    """A very simple cross-platform file lock."""

    def __init__(self, lock_file_path: Path, retry_delay: float = 0.1, max_retries: int = 300):
        """Initialize the SimpleFileLock."""
        self.lock_file_path = lock_file_path
        self.retry_delay = retry_delay
        self.max_retries = max_retries

    def acquire(self) -> None:
        """Acquire the file lock, retrying if necessary."""
        retries = 0
        while retries < self.max_retries:
            try:
                fd = os.open(str(self.lock_file_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                return
            except FileExistsError:
                time.sleep(self.retry_delay)
                retries += 1
        raise TimeoutError(f"Could not acquire lock after {self.max_retries} retries: {self.lock_file_path}")

    def release(self) -> None:
        """Release the file lock by deleting the lock file."""
        try:
            os.unlink(self.lock_file_path)
        except FileNotFoundError:
            pass

    def __enter__(self) -> None:
        """Context manager entry method to acquire the lock."""
        self.acquire()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit method to release the lock."""
        self.release()


def get_image_src_uri(image_path: str) -> str:
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

    mime_type = mime_types.get(ext)
    if not mime_type:
        raise ValueError(f"Unsupported image format: {ext}")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def sanitize_path_filename(filename: str, replacement: str = "_") -> str:
    # Replace spaces with underscore
    filename = filename.replace(" ", replacement)

    # Split the filename and extension
    name, ext = os.path.splitext(filename)

    # Remove invalid characters (keep letters, digits, _, -, .)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', replacement, name)

    # Replace multiple consecutive replacements with single
    name = re.sub(re.escape(replacement) + r"{2,}", replacement, name)

    # Remove leading/trailing replacements
    name = name.strip(replacement)

    # Truncate if too long
    max_length = 255 - len(ext)
    name = name[:max_length]

    return f"{name}{ext}"
