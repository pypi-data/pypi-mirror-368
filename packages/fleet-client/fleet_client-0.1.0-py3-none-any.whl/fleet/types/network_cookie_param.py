# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["NetworkCookieParam"]


class NetworkCookieParam(TypedDict, total=False):
    domain: Required[str]

    name: Required[str]

    path: Required[str]

    value: Required[str]

    expires: Optional[float]

    http_only: Annotated[Optional[bool], PropertyInfo(alias="httpOnly")]

    same_site: Annotated[Optional[str], PropertyInfo(alias="sameSite")]

    secure: Optional[bool]
