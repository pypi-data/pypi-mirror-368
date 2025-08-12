# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import Dict, List

import httpx

from ..types import completion_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.stream_options_param import StreamOptionsParam
from ..types.completion_create_response import CompletionCreateResponse

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bennorris123/python-sdk-test#accessing-raw-response-data-eg-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bennorris123/python-sdk-test#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("deprecated")
    def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, int] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        metadata: Dict[str, str] | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: object | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        store: bool | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        stream_options: StreamOptionsParam | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionCreateResponse:
        """
        Creates a completion for the given model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/completions",
            body=maybe_transform(
                {
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "metadata": metadata,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "prompt": prompt,
                    "seed": seed,
                    "stop": stop,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "suffix": suffix,
                    "temperature": temperature,
                    "top_p": top_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionCreateResponse,
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bennorris123/python-sdk-test#accessing-raw-response-data-eg-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bennorris123/python-sdk-test#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("deprecated")
    async def create(
        self,
        *,
        model: str,
        best_of: int | NotGiven = NOT_GIVEN,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, int] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        metadata: Dict[str, str] | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        prompt: object | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        store: bool | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        stream_options: StreamOptionsParam | NotGiven = NOT_GIVEN,
        suffix: str | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CompletionCreateResponse:
        """
        Creates a completion for the given model

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/completions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "best_of": best_of,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "metadata": metadata,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "prompt": prompt,
                    "seed": seed,
                    "stop": stop,
                    "store": store,
                    "stream": stream,
                    "stream_options": stream_options,
                    "suffix": suffix,
                    "temperature": temperature,
                    "top_p": top_p,
                    "user": user,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CompletionCreateResponse,
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                completions.create  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                completions.create  # pyright: ignore[reportDeprecated],
            )
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                completions.create  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                completions.create  # pyright: ignore[reportDeprecated],
            )
        )
