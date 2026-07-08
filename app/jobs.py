import threading
import uuid
from datetime import datetime
from enum import Enum

from app.report_generator import generate_report_file
from app.repository import get_all_orders, get_summary


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


_jobs = {}
_lock = threading.Lock()


def create_job() -> str:
    """Registers a new report job and returns its id, so the
    generation can be tracked and its result retrieved later."""
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = {
            "status": JobStatus.PENDING,
            "created_at": datetime.utcnow().isoformat(),
            "file_path": None,
            "error": None,
        }
    return job_id


def get_job(job_id: str):
    with _lock:
        return _jobs.get(job_id)


def run_report_job(job_id: str):
    """Runs as a background task: queries the data, then renders the
    PDF, then records where the resulting artifact was stored."""
    with _lock:
        _jobs[job_id]["status"] = JobStatus.PROCESSING

    try:
        orders = get_all_orders()
        summary = get_summary()
        file_path = generate_report_file(job_id, orders, summary)

        with _lock:
            _jobs[job_id]["status"] = JobStatus.COMPLETED
            _jobs[job_id]["file_path"] = file_path
    except Exception as exc:
        with _lock:
            _jobs[job_id]["status"] = JobStatus.FAILED
            _jobs[job_id]["error"] = str(exc)
