# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["User"]


class User(BaseModel):
    avatar_url: str

    created_at: datetime

    updated_at: datetime

    username: str

    id: Optional[str] = None

    balance: Optional[str] = None

    banned: Optional[bool] = None

    booster: Optional[bool] = None

    language: Optional[str] = None

    level: Optional[int] = None

    next_level_xp: Optional[int] = None

    xp: Optional[int] = None
