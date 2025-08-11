# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["ConfigRetrieveResponse"]


class ConfigRetrieveResponse(BaseModel):
    user_id: str

    id: Optional[int] = None

    auto_sell_cards_repeated: Optional[bool] = None

    auto_sell_less_than: Optional[int] = None
