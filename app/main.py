from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.database import init_db
from app.jobs import JobStatus, create_job, get_job, run_report_job
from app.schemas import ReportJobResponse, ReportStatusResponse

app = FastAPI(title="PDF Report Generator")


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/reports", response_model=ReportJobResponse, status_code=202)
def request_report(background_tasks: BackgroundTasks):
    """Triggers on-demand report generation. The data is queried and
    the PDF is rendered in a background job; this endpoint returns
    immediately with a job id instead of the file itself."""
    job_id = create_job()
    background_tasks.add_task(run_report_job, job_id)
    return ReportJobResponse(job_id=job_id, status=JobStatus.PENDING)


@app.get("/reports/{job_id}/status", response_model=ReportStatusResponse)
def get_report_status(job_id: str):
    """Lets the caller poll the background job until it completes."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return ReportStatusResponse(
        job_id=job_id,
        status=job["status"],
        created_at=job["created_at"],
        error=job["error"],
    )


@app.get("/reports/{job_id}/download")
def download_report(job_id: str):
    """Serves the stored PDF artifact for download once the job has
    completed, rather than returning the file inline anywhere else."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Report is not ready yet (status: {job['status']})",
        )
    return FileResponse(
        path=job["file_path"],
        media_type="application/pdf",
        filename=f"report_{job_id}.pdf",
    )
