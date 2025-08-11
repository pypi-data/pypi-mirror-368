# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CardHireParams"]


class CardHireParams(TypedDict, total=False):
    card_id: Required[str]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
