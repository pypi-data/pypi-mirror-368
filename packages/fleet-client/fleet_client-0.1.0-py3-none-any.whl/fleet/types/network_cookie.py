# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["NetworkCookie"]


class NetworkCookie(BaseModel):
    domain: str

    name: str

    path: str

    value: str

    expires: Optional[float] = None

    http_only: Optional[bool] = FieldInfo(alias="httpOnly", default=None)

    same_site: Optional[str] = FieldInfo(alias="sameSite", default=None)

    secure: Optional[bool] = None
