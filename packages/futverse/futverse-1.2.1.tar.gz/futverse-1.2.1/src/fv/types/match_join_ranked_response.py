# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["MatchJoinRankedResponse"]


class MatchJoinRankedResponse(BaseModel):
    home_id: str

    id: Optional[int] = None

    away_id: Optional[str] = None
