# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BrowserDownloadFileResponse"]


class BrowserDownloadFileResponse(BaseModel):
    browser_id: str

    download_url: str

    message: str

    success: bool

    aws_region: Optional[str] = None

    error: Optional[str] = None

    file_size: Optional[int] = None

    original_filename: Optional[str] = None

    s3_bucket: Optional[str] = None

    s3_key: Optional[str] = None
