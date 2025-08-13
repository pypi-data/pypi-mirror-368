# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .job_status import JobStatus

__all__ = ["AsyncCreateResponse"]


class AsyncCreateResponse(BaseModel):
    job_id: str

    message: str

    status: JobStatus
