# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

from .network_cookie_param import NetworkCookieParam

__all__ = ["NetworkRequestFinishedEventParam"]


class NetworkRequestFinishedEventParam(TypedDict, total=False):
    event: Required[str]

    method: Required[str]

    timestamp: Required[float]

    url: Required[str]

    cookies: Optional[Iterable[NetworkCookieParam]]

    post_data: Optional[str]

    post_data_json: object

    resource_type: Optional[str]

    response_body: Optional[str]
