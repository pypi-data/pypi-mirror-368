# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CardUpParams"]


class CardUpParams(TypedDict, total=False):
    position: Required[Literal["GOL", "LD", "LE", "ZAG", "VOL", "MA", "MC", "PD", "PE", "CA"]]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
