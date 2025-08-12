from _typeshed import Incomplete
from gllm_core.schema import Chunk
from typing import Any

logger: Incomplete

def validate_references(references: list[Any]) -> list[Chunk]:
    """Deduplicate reference data from agent state.

    Since the reducer function (add_references_chunks) already filters for valid Chunk objects,
    this function focuses on deduplication by content.

    Args:
        references: List of reference data from agent state (expected to be Chunk objects).

    Returns:
        List of deduplicated Chunk objects by content.
    """
def serialize_references_for_a2a(references: list[Any]) -> str | None:
    """Serialize references into a JSON string for A2A protocol.

    Args:
        references: List of reference objects to serialize

    Returns:
        JSON string with serialized references, or None if no valid references
    """
def embed_references_in_content(content: str, references: list[Any]) -> str:
    """Embed references into content for A2A protocol.

    Args:
        content: The original content string
        references: List of reference objects to embed

    Returns:
        JSON string with content and references embedded, or original content if references fail
    """
def add_references_chunks(left: list[Chunk], right: list[Chunk]) -> list[Chunk]:
    """Reducer function to accumulate reference data from multiple tool calls.

    This is a LangGraph reducer function that should be forgiving and handle
    edge cases gracefully. Non-Chunk items are filtered out.

    Args:
        left: Existing list of reference chunks (or None/non-list)
        right: New list of reference chunks to add (or None/non-list)

    Returns:
        Combined list of valid Chunk objects
    """
