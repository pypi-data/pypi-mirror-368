# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["PackListResponse", "PackListResponseItem"]


class PackListResponseItem(BaseModel):
    created_at: datetime

    emoji: str

    image: str

    name: str

    updated_at: datetime

    id: Optional[str] = None

    can_buy: Optional[bool] = None

    cards_amount: Optional[int] = None

    color: Optional[str] = None

    limit_per_user: Optional[int] = None

    price: Optional[str] = None


PackListResponse: TypeAlias = List[PackListResponseItem]
