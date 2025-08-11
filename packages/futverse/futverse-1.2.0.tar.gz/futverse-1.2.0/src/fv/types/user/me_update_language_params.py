# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MeUpdateLanguageParams"]


class MeUpdateLanguageParams(TypedDict, total=False):
    language: Required[Literal["pt-BR", "en-US", "es-ES"]]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
