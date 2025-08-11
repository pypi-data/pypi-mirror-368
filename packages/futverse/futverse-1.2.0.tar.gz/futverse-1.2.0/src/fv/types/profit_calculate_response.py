# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ProfitCalculateResponse", "Description"]


class Description(BaseModel):
    en: str

    es: str

    name: str

    pt: str

    id: Optional[int] = None


class ProfitCalculateResponse(BaseModel):
    amount: float

    description: Description

    probability: int

    id: Optional[int] = None
