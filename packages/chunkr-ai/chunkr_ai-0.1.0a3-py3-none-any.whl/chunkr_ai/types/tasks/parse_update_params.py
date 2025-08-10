# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "ParseUpdateParams",
    "ChunkProcessing",
    "ChunkProcessingTokenizer",
    "ChunkProcessingTokenizerEnum",
    "ChunkProcessingTokenizerString",
    "LlmProcessing",
    "LlmProcessingFallbackStrategy",
    "LlmProcessingFallbackStrategyModel",
    "SegmentProcessing",
    "SegmentProcessingCaption",
    "SegmentProcessingFootnote",
    "SegmentProcessingFormula",
    "SegmentProcessingListItem",
    "SegmentProcessingPage",
    "SegmentProcessingPageFooter",
    "SegmentProcessingPageHeader",
    "SegmentProcessingPicture",
    "SegmentProcessingSectionHeader",
    "SegmentProcessingTable",
    "SegmentProcessingText",
    "SegmentProcessingTitle",
]


class ParseUpdateParams(TypedDict, total=False):
    chunk_processing: Optional[ChunkProcessing]
    """Controls the setting for the chunking and post-processing of each chunk."""

    error_handling: Optional[Literal["Fail", "Continue"]]
    """Controls how errors are handled during processing:

    - `Fail`: Stops processing and fails the task when any error occurs
    - `Continue`: Attempts to continue processing despite non-critical errors (eg.
      LLM refusals etc.)
    """

    expires_in: Optional[int]
    """
    The number of seconds until task is deleted. Expired tasks can **not** be
    updated, polled or accessed via web interface.
    """

    high_resolution: Optional[bool]
    """Whether to use high-resolution images for cropping and post-processing.

    (Latency penalty: ~7 seconds per page)
    """

    llm_processing: Optional[LlmProcessing]
    """Controls the LLM used for the task."""

    ocr_strategy: Optional[Literal["All", "Auto"]]
    """Controls the Optical Character Recognition (OCR) strategy.

    - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
    - `Auto`: Selectively applies OCR only to pages with missing or low-quality
      text. When text layer is present the bounding boxes from the text layer are
      used.
    """

    pipeline: Optional[Literal["Azure", "Chunkr"]]
    """
    Choose the provider whose models will be used for segmentation and OCR. The
    output will be unified to the Chunkr `output` format.
    """

    segment_processing: Optional[SegmentProcessing]
    """Defines how each segment type is handled when generating the final output.

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
    """

    segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]]
    """Controls the segmentation strategy:

    - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
      `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
      segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
    - `Page`: Treats each page as a single segment. Faster processing, but without
      layout element detection and only simple chunking.
    """


class ChunkProcessingTokenizerEnum(TypedDict, total=False):
    enum: Required[
        Annotated[Literal["Word", "Cl100kBase", "XlmRobertaBase", "BertBaseUncased"], PropertyInfo(alias="Enum")]
    ]
    """Use one of the predefined tokenizer types"""


class ChunkProcessingTokenizerString(TypedDict, total=False):
    string: Required[Annotated[str, PropertyInfo(alias="String")]]
    """
    Use any Hugging Face tokenizer by specifying its model ID Examples:
    "Qwen/Qwen-tokenizer", "facebook/bart-large"
    """


ChunkProcessingTokenizer: TypeAlias = Union[ChunkProcessingTokenizerEnum, ChunkProcessingTokenizerString]


class ChunkProcessing(TypedDict, total=False):
    ignore_headers_and_footers: Optional[bool]
    """DEPRECATED: use `segment_processing.ignore` instead"""

    target_length: int
    """The target number of words in each chunk.

    If 0, each chunk will contain a single segment.
    """

    tokenizer: ChunkProcessingTokenizer
    """The tokenizer to use for the chunking process."""


class LlmProcessingFallbackStrategyModel(TypedDict, total=False):
    model: Required[Annotated[str, PropertyInfo(alias="Model")]]
    """Use a specific model as fallback"""


LlmProcessingFallbackStrategy: TypeAlias = Union[Literal["None", "Default"], LlmProcessingFallbackStrategyModel]


class LlmProcessing(TypedDict, total=False):
    fallback_strategy: LlmProcessingFallbackStrategy
    """The fallback strategy to use for the LLMs in the task."""

    llm_model_id: Optional[str]
    """The ID of the model to use for the task.

    If not provided, the default model will be used. Please check the documentation
    for the model you want to use.
    """

    max_completion_tokens: Optional[int]
    """The maximum number of tokens to generate."""

    temperature: float
    """The temperature to use for the LLM."""


class SegmentProcessingCaption(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingFootnote(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingFormula(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingListItem(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingPage(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingPageFooter(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingPageHeader(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingPicture(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingSectionHeader(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingTable(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingText(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessingTitle(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]


class SegmentProcessing(TypedDict, total=False):
    caption: Annotated[Optional[SegmentProcessingCaption], PropertyInfo(alias="Caption")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    footnote: Annotated[Optional[SegmentProcessingFootnote], PropertyInfo(alias="Footnote")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    formula: Annotated[Optional[SegmentProcessingFormula], PropertyInfo(alias="Formula")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    list_item: Annotated[Optional[SegmentProcessingListItem], PropertyInfo(alias="ListItem")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page: Annotated[Optional[SegmentProcessingPage], PropertyInfo(alias="Page")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page_footer: Annotated[Optional[SegmentProcessingPageFooter], PropertyInfo(alias="PageFooter")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page_header: Annotated[Optional[SegmentProcessingPageHeader], PropertyInfo(alias="PageHeader")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    picture: Annotated[Optional[SegmentProcessingPicture], PropertyInfo(alias="Picture")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    section_header: Annotated[Optional[SegmentProcessingSectionHeader], PropertyInfo(alias="SectionHeader")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    table: Annotated[Optional[SegmentProcessingTable], PropertyInfo(alias="Table")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    text: Annotated[Optional[SegmentProcessingText], PropertyInfo(alias="Text")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    title: Annotated[Optional[SegmentProcessingTitle], PropertyInfo(alias="Title")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments. **Note:** This
      uses chunkr's own VLM models and is not configurable via LLM processing
      configuration.
    - `extended_context` uses the full page image as context for LLM generation.

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """
