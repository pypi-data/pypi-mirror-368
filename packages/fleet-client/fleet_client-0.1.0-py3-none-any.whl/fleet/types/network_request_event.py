# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel
from .network_cookie import NetworkCookie

__all__ = ["NetworkRequestEvent"]


class NetworkRequestEvent(BaseModel):
    event: str

    headers: Dict[str, object]

    method: str

    timestamp: float

    url: str

    cookies: Optional[List[NetworkCookie]] = None

    post_data: Optional[str] = None

    post_data_json: Optional[object] = None

    resource_type: Optional[str] = None
