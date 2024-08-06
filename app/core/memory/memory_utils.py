from datetime import datetime, timedelta
from typing import Any, Dict, List
from app.api.models.memory import MemoryEntry, MemoryContext

# Constants
DEFAULT_MEMORY_TTL = 3600  # Default time-to-live for short-term memories (in seconds)
DEFAULT_CONSOLIDATION_INTERVAL = 3600  # Default interval for memory consolidation (in seconds)
DEFAULT_FORGET_AGE = timedelta(days=30)  # Default age for forgetting long-term memories
MAX_MEMORY_SIZE = 1024 * 1024  # Maximum size of a single memory entry (in bytes)

def serialize_memory_entry(memory_entry: MemoryEntry) -> Dict[str, Any]:
    """
    Serialize a MemoryEntry object to a dictionary.

    Args:
        memory_entry (MemoryEntry): The memory entry to serialize.

    Returns:
        Dict[str, Any]: The serialized memory entry.
    """
    return {
        "content": memory_entry.content,
        "metadata": memory_entry.metadata,
        "context": {
            "context_type": memory_entry.context.context_type,
            "timestamp": memory_entry.context.timestamp.isoformat(),
            "metadata": memory_entry.context.metadata
        }
    }

def deserialize_memory_entry(data: Dict[str, Any]) -> MemoryEntry:
    """
    Deserialize a dictionary to a MemoryEntry object.

    Args:
        data (Dict[str, Any]): The serialized memory entry.

    Returns:
        MemoryEntry: The deserialized memory entry.
    """
    context = MemoryContext(
        context_type=data["context"]["context_type"],
        timestamp=datetime.fromisoformat(data["context"]["timestamp"]),
        metadata=data["context"]["metadata"]
    )
    return MemoryEntry(
        content=data["content"],
        metadata=data["metadata"],
        context=context
    )

def calculate_memory_size(memory_entry: MemoryEntry) -> int:
    """
    Calculate the size of a memory entry in bytes.

    Args:
        memory_entry (MemoryEntry): The memory entry to calculate the size for.

    Returns:
        int: The size of the memory entry in bytes.
    """
    serialized = serialize_memory_entry(memory_entry)
    return len(str(serialized).encode('utf-8'))

def truncate_memory_content(content: str, max_size: int = MAX_MEMORY_SIZE) -> str:
    """
    Truncate memory content to ensure it doesn't exceed the maximum size.

    Args:
        content (str): The memory content to truncate.
        max_size (int): The maximum allowed size in bytes.

    Returns:
        str: The truncated memory content.
    """
    encoded = content.encode('utf-8')
    if len(encoded) <= max_size:
        return content
    return encoded[:max_size].decode('utf-8', errors='ignore')

def merge_memory_entries(entries: List[MemoryEntry]) -> MemoryEntry:
    """
    Merge multiple memory entries into a single entry.

    Args:
        entries (List[MemoryEntry]): The list of memory entries to merge.

    Returns:
        MemoryEntry: The merged memory entry.
    """
    if not entries:
        raise ValueError("Cannot merge an empty list of memory entries")

    merged_content = " ".join(entry.content for entry in entries)
    merged_metadata = {k: v for entry in entries for k, v in entry.metadata.items()}
    latest_timestamp = max(entry.context.timestamp for entry in entries)

    merged_context = MemoryContext(
        context_type="merged",
        timestamp=latest_timestamp,
        metadata={"merged_from": [entry.context.context_type for entry in entries]}
    )

    return MemoryEntry(
        content=truncate_memory_content(merged_content),
        metadata=merged_metadata,
        context=merged_context
    )

def calculate_relevance_score(query: str, memory_entry: MemoryEntry) -> float:
    """
    Calculate the relevance score of a memory entry for a given query.

    Args:
        query (str): The search query.
        memory_entry (MemoryEntry): The memory entry to calculate the relevance for.

    Returns:
        float: The relevance score (0 to 1).
    """
    # This is a simple implementation. You might want to use more sophisticated
    # techniques like TF-IDF or semantic similarity in a real-world scenario.
    query_words = set(query.lower().split())
    content_words = set(memory_entry.content.lower().split())
    common_words = query_words.intersection(content_words)
    return len(common_words) / len(query_words) if query_words else 0

def should_consolidate_memory(memory_entry: MemoryEntry, current_time: datetime) -> bool:
    """
    Determine if a memory entry should be consolidated based on its age.

    Args:
        memory_entry (MemoryEntry): The memory entry to check.
        current_time (datetime): The current time to compare against.

    Returns:
        bool: True if the memory should be consolidated, False otherwise.
    """
    age = current_time - memory_entry.context.timestamp
    return age > timedelta(seconds=DEFAULT_CONSOLIDATION_INTERVAL)

def should_forget_memory(memory_entry: MemoryEntry, current_time: datetime) -> bool:
    """
    Determine if a memory entry should be forgotten based on its age.

    Args:
        memory_entry (MemoryEntry): The memory entry to check.
        current_time (datetime): The current time to compare against.

    Returns:
        bool: True if the memory should be forgotten, False otherwise.
    """
    age = current_time - memory_entry.context.timestamp
    return age > DEFAULT_FORGET_AGE
