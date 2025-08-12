# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from pydantic import Field as FieldInfo

from .usage import Usage
from .._models import BaseModel

__all__ = ["CompletionCreateResponse", "Choice", "ChoiceLogprobs"]


class ChoiceLogprobs(BaseModel):
    text_offset: List[int]

    token_logprobs: List[float]

    tokens: List[str]

    top_logprobs: List[Dict[str, float]]


class Choice(BaseModel):
    finish_reason: str

    index: int

    logprobs: ChoiceLogprobs

    text: str


class CompletionCreateResponse(BaseModel):
    id: str

    choices: List[Choice]

    created: int

    http_header: Dict[str, List[str]] = FieldInfo(alias="httpHeader")

    model: str

    object: str

    usage: Usage
