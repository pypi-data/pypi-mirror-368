# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ConfigUpdateParams"]


class ConfigUpdateParams(TypedDict, total=False):
    auto_sell_cards_repeated: Optional[bool]

    auto_sell_less_than: Optional[int]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
