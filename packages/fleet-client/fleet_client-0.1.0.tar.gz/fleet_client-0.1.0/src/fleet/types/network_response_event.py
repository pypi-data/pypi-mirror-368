# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .network_cookie import NetworkCookie

__all__ = ["NetworkResponseEvent"]


class NetworkResponseEvent(BaseModel):
    event: str

    headers: Dict[str, object]

    ok: bool

    request_method: str

    status: int

    status_text: str

    timestamp: float

    url: str

    cookies: Optional[List[NetworkCookie]] = None

    resource_type: Optional[str] = None
