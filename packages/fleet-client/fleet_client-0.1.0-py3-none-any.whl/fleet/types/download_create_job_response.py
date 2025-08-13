# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .scrape.job_status import JobStatus

__all__ = ["DownloadCreateJobResponse"]


class DownloadCreateJobResponse(BaseModel):
    job_id: str

    message: str

    status: JobStatus
