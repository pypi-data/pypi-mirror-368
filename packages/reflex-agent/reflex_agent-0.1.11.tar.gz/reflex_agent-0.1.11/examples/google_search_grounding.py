#!/usr/bin/env python3
"""
Google Search Grounding Example

This example demonstrates how to use Google Search grounding with FlexAI's Gemini client.
Google Search grounding allows Gemini to search the web for real-time information and
provide grounded responses with citations.

Features demonstrated:
- Basic Google Search grounding for Gemini 2.0+ models
- Legacy Google Search retrieval for Gemini 1.5 models with dynamic threshold
- Extracting grounding metadata (search queries, sources, citations)
- Backward compatibility when Google Search is disabled
"""

import asyncio
import os
from typing import Any, Mapping, Sequence

from flexai.llm.gemini import GeminiClient
from flexai.message import GroundingBlock, TextBlock, UserMessage


def add_citations_to_text(
    text: str,
    grounding_supports: Sequence[Mapping[str, Any]],
    grounding_chunks: Sequence[Mapping[str, Any]],
) -> str:
    """Add inline citations to text using grounding metadata"""
    # Sort by end_index in descending order to avoid index shifting
    sorted_supports = sorted(
        grounding_supports, key=lambda s: s["segment"]["end_index"], reverse=True
    )

    for support in sorted_supports:
        end_index = support["segment"]["end_index"]
        chunk_indices = support.get("grounding_chunk_indices", [])

        if chunk_indices:
            citation_links = []
            for i in chunk_indices:
                if i < len(grounding_chunks) and "web" in grounding_chunks[i]:
                    uri = grounding_chunks[i]["web"].get("uri", "")
                    title = grounding_chunks[i]["web"].get("title", f"Source {i + 1}")
                    citation_links.append(f"[{title}]({uri})")

            if citation_links:
                citation_string = ", ".join(citation_links)
                text = text[:end_index] + f" ({citation_string})" + text[end_index:]

    return text


async def basic_google_search():
    """Basic Google Search grounding example"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = GeminiClient(api_key=api_key, model="gemini-2.5-flash")

    print("=== Basic Google Search Example ===")

    response = await client.get_chat_response(
        messages=[UserMessage(content="Who won the UEFA Euro 2024 final?")],
        use_google_search=True,
    )

    # Extract text content
    text_content = ""
    grounding_data = None

    for block in response.content:
        if isinstance(block, TextBlock):
            text_content += block.text
        elif isinstance(block, GroundingBlock):
            grounding_data = block

    print(f"Answer: {text_content}")

    if grounding_data:
        print(f"\nSearch queries used: {grounding_data.search_queries}")
        print(f"Sources found: {len(grounding_data.grounding_chunks)}")

        # Show sources
        for i, chunk in enumerate(grounding_data.grounding_chunks):
            if "web" in chunk:
                title = chunk["web"].get("title", "Unknown")
                uri = chunk["web"].get("uri", "")
                print(f"  {i + 1}. {title} - {uri}")


async def legacy_model_with_threshold():
    """Google Search with Gemini 1.5 and dynamic threshold"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = GeminiClient(api_key=api_key, model="gemini-1.5-pro")

    print("\n=== Legacy Model with Dynamic Threshold ===")

    response = await client.get_chat_response(
        messages=[UserMessage(content="Latest developments in renewable energy")],
        use_google_search=True,
        google_search_dynamic_threshold=0.7,  # Only search if confidence < 70%
    )

    # Extract content
    text_content = ""
    grounding_data = None

    for block in response.content:
        if isinstance(block, TextBlock):
            text_content += block.text
        elif isinstance(block, GroundingBlock):
            grounding_data = block

    print(f"Answer: {text_content}")
    print(f"Search used: {grounding_data is not None}")


async def streaming_with_search():
    """Streaming responses with Google Search"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = GeminiClient(api_key=api_key, model="gemini-2.5-flash")

    print("\n=== Streaming with Google Search ===")

    async for chunk in client.stream_chat_response(
        messages=[UserMessage(content="Latest news about renewable energy")],
        use_google_search=True,
    ):
        if isinstance(chunk, TextBlock):
            print(chunk.text, end="", flush=True)
        elif isinstance(chunk, GroundingBlock):
            print(f"\n[Sources: {len(chunk.grounding_chunks)} found]")

    print()  # New line after streaming


async def citation_extraction():
    """Extract and add citations to responses"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = GeminiClient(api_key=api_key, model="gemini-2.5-flash")

    print("\n=== Citation Extraction Example ===")

    response = await client.get_chat_response(
        messages=[
            UserMessage(
                content="What are the main causes of climate change according to recent research?"
            )
        ],
        use_google_search=True,
    )

    # Extract content
    text_content = ""
    grounding_data = None

    for block in response.content:
        if isinstance(block, TextBlock):
            text_content += block.text
        elif isinstance(block, GroundingBlock):
            grounding_data = block

    print("Original response:")
    print(text_content)

    if grounding_data:
        print("\n" + "=" * 50)
        print("Response with citations:")
        cited_text = add_citations_to_text(
            text_content,
            grounding_data.grounding_supports,
            grounding_data.grounding_chunks,
        )
        print(cited_text)


async def backward_compatibility():
    """Demonstrate backward compatibility - search disabled by default"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = GeminiClient(api_key=api_key, model="gemini-2.5-flash")

    print("\n=== Backward Compatibility (Search Disabled) ===")

    # This works exactly as before - no Google Search
    response = await client.get_chat_response(
        messages=[UserMessage(content="What is the capital of France?")]
    )

    # Check if any grounding was used
    has_grounding = any(isinstance(block, GroundingBlock) for block in response.content)

    text_content = ""
    for block in response.content:
        if isinstance(block, TextBlock):
            text_content += block.text

    print(f"Answer: {text_content}")
    print(f"Search used: {has_grounding}")
    print("This demonstrates that existing code works unchanged")


async def main():
    """Run all examples"""
    try:
        await basic_google_search()
        await legacy_model_with_threshold()
        await streaming_with_search()
        await citation_extraction()
        await backward_compatibility()

    except Exception as e:
        print(f"Error: {e}")
        print(
            "Make sure you have set the GEMINI_API_KEY environment variable with a valid API key."
        )


if __name__ == "__main__":
    asyncio.run(main())
