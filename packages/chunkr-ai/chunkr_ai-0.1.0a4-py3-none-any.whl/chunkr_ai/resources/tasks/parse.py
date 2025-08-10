# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.task import Task
from ...types.tasks import parse_create_params, parse_update_params
from ..._base_client import make_request_options

__all__ = ["ParseResource", "AsyncParseResource"]


class ParseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ParseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return ParseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ParseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return ParseResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        file: str,
        chunk_processing: Optional[parse_create_params.ChunkProcessing] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[parse_create_params.LlmProcessing] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[parse_create_params.SegmentProcessing] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Queues a document for processing and returns a TaskResponse containing:

        - Task ID for status polling
        - Initial configuration
        - File metadata
        - Processing status
        - Creation timestamp
        - Presigned URLs for file access

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /tasks/{task_id}` endpoint to poll for completion.

        Args:
          file:
              The file to be uploaded. Supported inputs:

              - `ch://files/{file_id}`: References a previously uploaded file you own
                (authorization enforced)
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be uploaded. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and
              **descriptions** further refine behaviour.

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown, description off) • `Table` → **LLM**
              (HTML, description on) • `Picture` → **LLM** (Markdown, description off,
              cropping _All_) • `Formula`, `Page` → **LLM** (Markdown, description off) •
              `PageHeader`, `PageFooter` → **Ignore** (removed from output)

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/tasks/parse",
            body=maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_create_params.ParseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def update(
        self,
        task_id: str,
        *,
        chunk_processing: Optional[parse_update_params.ChunkProcessing] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        high_resolution: Optional[bool] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[parse_update_params.LlmProcessing] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[parse_update_params.SegmentProcessing] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """Updates an existing task's configuration and reprocesses the document.

        The
        original configuration will be used for all values that are not provided in the
        update.

        Requirements:

        - Task must have status `Succeeded` or `Failed`
        - New configuration must be different from the current one

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /tasks/{task_id}` endpoint to poll for completion.

        Args:
          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          high_resolution: Whether to use high-resolution images for cropping and post-processing. (Latency
              penalty: ~7 seconds per page)

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and
              **descriptions** further refine behaviour.

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown, description off) • `Table` → **LLM**
              (HTML, description on) • `Picture` → **LLM** (Markdown, description off,
              cropping _All_) • `Formula`, `Page` → **LLM** (Markdown, description off) •
              `PageHeader`, `PageFooter` → **Ignore** (removed from output)

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._patch(
            f"/tasks/parse/{task_id}",
            body=maybe_transform(
                {
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "high_resolution": high_resolution,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_update_params.ParseUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )


class AsyncParseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncParseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncParseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncParseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncParseResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: str,
        chunk_processing: Optional[parse_create_params.ChunkProcessing] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[parse_create_params.LlmProcessing] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[parse_create_params.SegmentProcessing] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Queues a document for processing and returns a TaskResponse containing:

        - Task ID for status polling
        - Initial configuration
        - File metadata
        - Processing status
        - Creation timestamp
        - Presigned URLs for file access

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /tasks/{task_id}` endpoint to poll for completion.

        Args:
          file:
              The file to be uploaded. Supported inputs:

              - `ch://files/{file_id}`: References a previously uploaded file you own
                (authorization enforced)
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be uploaded. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and
              **descriptions** further refine behaviour.

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown, description off) • `Table` → **LLM**
              (HTML, description on) • `Picture` → **LLM** (Markdown, description off,
              cropping _All_) • `Formula`, `Page` → **LLM** (Markdown, description off) •
              `PageHeader`, `PageFooter` → **Ignore** (removed from output)

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/tasks/parse",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_create_params.ParseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    async def update(
        self,
        task_id: str,
        *,
        chunk_processing: Optional[parse_update_params.ChunkProcessing] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        high_resolution: Optional[bool] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[parse_update_params.LlmProcessing] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[parse_update_params.SegmentProcessing] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """Updates an existing task's configuration and reprocesses the document.

        The
        original configuration will be used for all values that are not provided in the
        update.

        Requirements:

        - Task must have status `Succeeded` or `Failed`
        - New configuration must be different from the current one

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /tasks/{task_id}` endpoint to poll for completion.

        Args:
          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          high_resolution: Whether to use high-resolution images for cropping and post-processing. (Latency
              penalty: ~7 seconds per page)

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and
              **descriptions** further refine behaviour.

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown, description off) • `Table` → **LLM**
              (HTML, description on) • `Picture` → **LLM** (Markdown, description off,
              cropping _All_) • `Formula`, `Page` → **LLM** (Markdown, description off) •
              `PageHeader`, `PageFooter` → **Ignore** (removed from output)

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._patch(
            f"/tasks/parse/{task_id}",
            body=await async_maybe_transform(
                {
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "high_resolution": high_resolution,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_update_params.ParseUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )


class ParseResourceWithRawResponse:
    def __init__(self, parse: ParseResource) -> None:
        self._parse = parse

        self.create = to_raw_response_wrapper(
            parse.create,
        )
        self.update = to_raw_response_wrapper(
            parse.update,
        )


class AsyncParseResourceWithRawResponse:
    def __init__(self, parse: AsyncParseResource) -> None:
        self._parse = parse

        self.create = async_to_raw_response_wrapper(
            parse.create,
        )
        self.update = async_to_raw_response_wrapper(
            parse.update,
        )


class ParseResourceWithStreamingResponse:
    def __init__(self, parse: ParseResource) -> None:
        self._parse = parse

        self.create = to_streamed_response_wrapper(
            parse.create,
        )
        self.update = to_streamed_response_wrapper(
            parse.update,
        )


class AsyncParseResourceWithStreamingResponse:
    def __init__(self, parse: AsyncParseResource) -> None:
        self._parse = parse

        self.create = async_to_streamed_response_wrapper(
            parse.create,
        )
        self.update = async_to_streamed_response_wrapper(
            parse.update,
        )
