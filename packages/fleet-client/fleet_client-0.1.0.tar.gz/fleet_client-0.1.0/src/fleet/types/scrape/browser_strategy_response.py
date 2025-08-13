# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from ..browser_selection_strategy import BrowserSelectionStrategy

__all__ = ["BrowserStrategyResponse"]


class BrowserStrategyResponse(BaseModel):
    message: str

    strategy: BrowserSelectionStrategy
