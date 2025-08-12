# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .usage import Usage
from .._models import BaseModel

__all__ = ["EmbeddingCreateResponse", "Data"]


class Data(BaseModel):
    embedding: List[float]

    index: int

    object: str


class EmbeddingCreateResponse(BaseModel):
    data: List[Data]

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    model: str

    object: str

    usage: Usage
