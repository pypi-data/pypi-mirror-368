# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Usage", "CompletionTokensDetails", "PromptTokensDetails"]


class CompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: int

    audio_tokens: int

    reasoning_tokens: int

    rejected_prediction_tokens: int


class PromptTokensDetails(BaseModel):
    audio_tokens: int

    cached_tokens: int


class Usage(BaseModel):
    completion_tokens: int

    completion_tokens_details: CompletionTokensDetails

    prompt_tokens: int

    prompt_tokens_details: PromptTokensDetails

    total_tokens: int
