# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .wait_until import WaitUntil

__all__ = ["DownloadCreateJobParams"]


class DownloadCreateJobParams(TypedDict, total=False):
    download_url: Required[str]

    s3_bucket: Required[str]

    aws_access_key_id: Optional[str]

    aws_region: str

    aws_secret_access_key: Optional[str]

    s3_key: Optional[str]

    wait_until: WaitUntil
