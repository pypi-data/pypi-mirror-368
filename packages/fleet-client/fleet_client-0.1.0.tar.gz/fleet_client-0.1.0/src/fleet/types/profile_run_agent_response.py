# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["ProfileRunAgentResponse", "Request", "RequestRequest"]


class RequestRequest(BaseModel):
    url: str
    """The target URL for the HTTP request"""

    allow_redirects: Optional[bool] = None
    """Whether to automatically follow HTTP redirects"""

    auth: Optional[List[object]] = None
    """Basic authentication credentials as (username, password) tuple"""

    cookies: Optional[List[Dict[str, object]]] = None
    """List of cookie dictionaries with name/value pairs"""

    data: Optional[str] = None
    """Raw POST data as string"""

    headers: Optional[Dict[str, object]] = None
    """HTTP headers to include in the request"""

    json_data: Optional[object] = None
    """JSON data for POST requests"""

    method: Optional[str] = None
    """HTTP method to use (GET, POST, etc.)"""

    params: Optional[Dict[str, object]] = None
    """URL query parameters to append to the request"""

    proxies: Optional[Dict[str, str]] = None
    """
    Proxy configuration (e.g., {'http': 'http://proxy:port', 'https':
    'https://proxy:port'})
    """

    resource_type: Optional[str] = None
    """Type of resource being requested (document, script, stylesheet, etc.)"""

    timeout: Optional[float] = None
    """Request timeout in seconds"""

    verify: Optional[bool] = None
    """Whether to verify SSL certificates"""


class Request(BaseModel):
    reasoning: str

    request: RequestRequest
    """Base model representing input for building HTTP requests from network events."""


class ProfileRunAgentResponse(BaseModel):
    pagination: bool

    pagination_explanation: str

    requests: List[Request]

    total_requests_to_make: int

    url: str
