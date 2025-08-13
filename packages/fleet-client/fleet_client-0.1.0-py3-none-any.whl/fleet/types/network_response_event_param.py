# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Required, TypedDict

from .network_cookie_param import NetworkCookieParam

__all__ = ["NetworkResponseEventParam"]


class NetworkResponseEventParam(TypedDict, total=False):
    event: Required[str]

    headers: Required[Dict[str, object]]

    ok: Required[bool]

    request_method: Required[str]

    status: Required[int]

    status_text: Required[str]

    timestamp: Required[float]

    url: Required[str]

    cookies: Optional[Iterable[NetworkCookieParam]]

    resource_type: Optional[str]
