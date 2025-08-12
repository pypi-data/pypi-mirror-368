# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import Required, TypedDict

from .stream_options_param import StreamOptionsParam

__all__ = ["CompletionCreateParams"]


class CompletionCreateParams(TypedDict, total=False):
    model: Required[str]

    best_of: int

    echo: bool

    frequency_penalty: float

    logit_bias: Dict[str, int]

    logprobs: int

    max_tokens: int

    metadata: Dict[str, str]

    n: int

    presence_penalty: float

    prompt: object

    seed: int

    stop: List[str]

    store: bool

    stream: bool

    stream_options: StreamOptionsParam

    suffix: str

    temperature: float

    top_p: float

    user: str
