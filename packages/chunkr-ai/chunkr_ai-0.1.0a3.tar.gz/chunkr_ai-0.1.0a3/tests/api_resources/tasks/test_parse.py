# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from chunkr_ai import Chunkr, AsyncChunkr
from tests.utils import assert_matches_type
from chunkr_ai.types import Task

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestParse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Chunkr) -> None:
        parse = client.tasks.parse.create(
            file="file",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Chunkr) -> None:
        parse = client.tasks.parse.create(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            llm_processing={
                "fallback_strategy": "None",
                "llm_model_id": "llm_model_id",
                "max_completion_tokens": 0,
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Chunkr) -> None:
        response = client.tasks.parse.with_raw_response.create(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = response.parse()
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Chunkr) -> None:
        with client.tasks.parse.with_streaming_response.create(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = response.parse()
            assert_matches_type(Task, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: Chunkr) -> None:
        parse = client.tasks.parse.update(
            task_id="task_id",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Chunkr) -> None:
        parse = client.tasks.parse.update(
            task_id="task_id",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            high_resolution=True,
            llm_processing={
                "fallback_strategy": "None",
                "llm_model_id": "llm_model_id",
                "max_completion_tokens": 0,
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Chunkr) -> None:
        response = client.tasks.parse.with_raw_response.update(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = response.parse()
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Chunkr) -> None:
        with client.tasks.parse.with_streaming_response.update(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = response.parse()
            assert_matches_type(Task, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.tasks.parse.with_raw_response.update(
                task_id="",
            )


class TestAsyncParse:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.create(
            file="file",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.create(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            llm_processing={
                "fallback_strategy": "None",
                "llm_model_id": "llm_model_id",
                "max_completion_tokens": 0,
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.parse.with_raw_response.create(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = await response.parse()
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.parse.with_streaming_response.create(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = await response.parse()
            assert_matches_type(Task, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.update(
            task_id="task_id",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncChunkr) -> None:
        parse = await async_client.tasks.parse.update(
            task_id="task_id",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            high_resolution=True,
            llm_processing={
                "fallback_strategy": "None",
                "llm_model_id": "llm_model_id",
                "max_completion_tokens": 0,
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncChunkr) -> None:
        response = await async_client.tasks.parse.with_raw_response.update(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        parse = await response.parse()
        assert_matches_type(Task, parse, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncChunkr) -> None:
        async with async_client.tasks.parse.with_streaming_response.update(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            parse = await response.parse()
            assert_matches_type(Task, parse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.tasks.parse.with_raw_response.update(
                task_id="",
            )
