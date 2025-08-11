# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CardUpdateParams"]


class CardUpdateParams(TypedDict, total=False):
    favorite: Optional[bool]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
