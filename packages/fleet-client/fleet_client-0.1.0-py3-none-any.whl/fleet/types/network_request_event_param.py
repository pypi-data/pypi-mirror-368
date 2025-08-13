# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Required, TypedDict

from .network_cookie_param import NetworkCookieParam

__all__ = ["NetworkRequestEventParam"]


class NetworkRequestEventParam(TypedDict, total=False):
    event: Required[str]

    headers: Required[Dict[str, object]]

    method: Required[str]

    timestamp: Required[float]

    url: Required[str]

    cookies: Optional[Iterable[NetworkCookieParam]]

    post_data: Optional[str]

    post_data_json: object

    resource_type: Optional[str]
