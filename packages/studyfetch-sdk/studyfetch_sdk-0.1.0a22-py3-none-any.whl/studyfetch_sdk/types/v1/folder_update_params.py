# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["FolderUpdateParams"]


class FolderUpdateParams(TypedDict, total=False):
    name: str
    """New folder name"""

    parent_id: Annotated[str, PropertyInfo(alias="parentId")]
    """New parent folder ID"""
