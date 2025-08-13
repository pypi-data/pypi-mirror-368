# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

__all__ = ["ProfileCaptureParams"]


class ProfileCaptureParams(TypedDict, total=False):
    url: Required[str]

    resource_types: Optional[List[str]]
