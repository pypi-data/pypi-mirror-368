# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .._models import BaseModel
from .network_request_event import NetworkRequestEvent
from .network_response_event import NetworkResponseEvent
from .network_request_failed_event import NetworkRequestFailedEvent
from .network_request_finished_event import NetworkRequestFinishedEvent

__all__ = ["ProfileCaptureResponse", "Event"]

Event: TypeAlias = Union[
    NetworkRequestEvent, NetworkResponseEvent, NetworkRequestFinishedEvent, NetworkRequestFailedEvent
]


class ProfileCaptureResponse(BaseModel):
    events: List[Event]
