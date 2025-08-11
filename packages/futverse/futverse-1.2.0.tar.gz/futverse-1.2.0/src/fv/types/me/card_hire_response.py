# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel
from ..user.user import User

__all__ = ["CardHireResponse", "Card"]


class Card(BaseModel):
    attack: int

    collection_id: int

    created_at: datetime

    creation: int

    defense: int

    name: str

    nationality_id: int

    overall: int

    position: str

    stats_id: int

    team_id: int

    updated_at: datetime

    id: Optional[str] = None

    background_id: Optional[int] = None

    blocked_contract: Optional[bool] = None

    buy_price: Optional[str] = None

    image: Optional[str] = None

    price: Optional[str] = None

    secundary_positions: Optional[List[object]] = None

    sell_price: Optional[str] = None


class CardHireResponse(BaseModel):
    card: Card

    user: User
