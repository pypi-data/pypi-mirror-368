# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CardSellParams"]


class CardSellParams(TypedDict, total=False):
    cards_ids: Required[Iterable[int]]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
