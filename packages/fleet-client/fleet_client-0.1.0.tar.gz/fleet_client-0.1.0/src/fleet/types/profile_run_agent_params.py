# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypeAlias, TypedDict

from .network_request_event_param import NetworkRequestEventParam
from .network_response_event_param import NetworkResponseEventParam
from .network_request_failed_event_param import NetworkRequestFailedEventParam
from .network_request_finished_event_param import NetworkRequestFinishedEventParam

__all__ = ["ProfileRunAgentParams", "NetworkEvent"]


class ProfileRunAgentParams(TypedDict, total=False):
    network_events: Required[Iterable[NetworkEvent]]

    user_prompt: Required[str]


NetworkEvent: TypeAlias = Union[
    NetworkRequestEventParam,
    NetworkResponseEventParam,
    NetworkRequestFinishedEventParam,
    NetworkRequestFailedEventParam,
]
