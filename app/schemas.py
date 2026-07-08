from typing import Optional

from pydantic import BaseModel


class ReportJobResponse(BaseModel):
    job_id: str
    status: str


class ReportStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    error: Optional[str] = None
