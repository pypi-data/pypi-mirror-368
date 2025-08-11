# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from ..user.user import User

__all__ = ["CardSellResponse"]


class CardSellResponse(BaseModel):
    amount_claimed: float

    cards_ids: List[str]

    count_cards: int
    """Conta a quantidade de cards."""

    user: User
