# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from relaxai_test import RelaxaiTest, AsyncRelaxaiTest
from relaxai_test.types import CompletionCreateResponse

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            completion = client.completions.create(
                model="model",
            )

        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            completion = client.completions.create(
                model="model",
                best_of=0,
                echo=True,
                frequency_penalty=0,
                logit_bias={"foo": 0},
                logprobs=0,
                max_tokens=0,
                metadata={"foo": "string"},
                n=0,
                presence_penalty=0,
                prompt={},
                seed=0,
                stop=["string"],
                store=True,
                stream=True,
                stream_options={"include_usage": True},
                suffix="suffix",
                temperature=0,
                top_p=0,
                user="user",
            )

        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.completions.with_raw_response.create(
                model="model",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            with client.completions.with_streaming_response.create(
                model="model",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                completion = response.parse()
                assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            completion = await async_client.completions.create(
                model="model",
            )

        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            completion = await async_client.completions.create(
                model="model",
                best_of=0,
                echo=True,
                frequency_penalty=0,
                logit_bias={"foo": 0},
                logprobs=0,
                max_tokens=0,
                metadata={"foo": "string"},
                n=0,
                presence_penalty=0,
                prompt={},
                seed=0,
                stop=["string"],
                store=True,
                stream=True,
                stream_options={"include_usage": True},
                suffix="suffix",
                temperature=0,
                top_p=0,
                user="user",
            )

        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            response = await async_client.completions.with_raw_response.create(
                model="model",
            )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(CompletionCreateResponse, completion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRelaxaiTest) -> None:
        with pytest.warns(DeprecationWarning):
            async with async_client.completions.with_streaming_response.create(
                model="model",
            ) as response:
                assert not response.is_closed
                assert response.http_request.headers.get("X-Stainless-Lang") == "python"

                completion = await response.parse()
                assert_matches_type(CompletionCreateResponse, completion, path=["response"])

        assert cast(Any, response.is_closed) is True
