# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = ["PackOpenResponse", "PackOpenResponseItem"]


class PackOpenResponseItem(BaseModel):
    card_id: str

    rule: Optional[Literal["auto_sell_less_than", "auto_sell_cards_repeated"]] = None

    sold: bool

    usercard_id: int

    sold_value: Optional[float] = None


PackOpenResponse: TypeAlias = List[PackOpenResponseItem]
