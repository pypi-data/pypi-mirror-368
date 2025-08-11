# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["UserinventoryRedeemResponse"]


class UserinventoryRedeemResponse(BaseModel):
    item_id: str

    item_type: str

    id: Optional[int] = None

    display_name_id: Optional[int] = None

    image_url: Optional[str] = None
