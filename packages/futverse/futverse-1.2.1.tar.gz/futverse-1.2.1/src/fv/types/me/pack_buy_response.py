# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["PackBuyResponse"]


class PackBuyResponse(BaseModel):
    pack_id: str

    user_id: str

    id: Optional[int] = None

    quant: Optional[int] = None
