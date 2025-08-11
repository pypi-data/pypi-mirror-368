# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AuthLoginDiscordParams"]


class AuthLoginDiscordParams(TypedDict, total=False):
    code: Required[str]

    origin: Required[str]

    accept_language: Annotated[str, PropertyInfo(alias="accept-language")]
