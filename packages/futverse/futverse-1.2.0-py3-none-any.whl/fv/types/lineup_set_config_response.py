# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["LineupSetConfigResponse"]


class LineupSetConfigResponse(BaseModel):
    formation_id: int

    id: Optional[int] = None
