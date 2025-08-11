# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["RedeemRedeemCodeResponse"]


class RedeemRedeemCodeResponse(BaseModel):
    code: str

    item_id: int

    id: Optional[int] = None

    banner: Optional[str] = None

    expire_at: Optional[datetime] = None

    limit_uses: Optional[int] = None
