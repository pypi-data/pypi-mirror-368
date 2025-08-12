"""Search utilities for fuzzy matching and ranking."""

import re
from typing import Any, Callable, List, Tuple


def fuzzy_match(pattern: str, text: str) -> Tuple[bool, float]:
    """
    Perform fuzzy matching between pattern and text.
    
    Returns:
        Tuple of (match_found, relevance_score)
        - match_found: True if pattern matches text
        - relevance_score: Float between 0.0 and 1.0, higher is better
    """
    if not pattern or not text:
        return False, 0.0

    pattern_lower = pattern.lower()
    text_lower = text.lower()

    # Exact match gets highest score
    if pattern_lower == text_lower:
        return True, 1.0

    # Exact substring match gets high score
    if pattern_lower in text_lower:
        # Score based on position and length ratio
        position = text_lower.index(pattern_lower)
        position_score = 1.0 - (position / len(text_lower))
        length_ratio = len(pattern_lower) / len(text_lower)
        return True, 0.8 + (0.2 * position_score * length_ratio)

    # Word boundary matches - only match complete words or word prefixes
    words = text_lower.split()
    word_matches = 0
    pattern_words = pattern_lower.split()

    for pattern_word in pattern_words:
        for word in words:
            # Match complete words or words that start with the pattern
            if word == pattern_word or word.startswith(pattern_word):
                word_matches += 1
                break

    if word_matches > 0:
        word_score = word_matches / len(pattern_words)
        return True, 0.3 + (0.4 * word_score)

    # Character sequence matching disabled to prevent false positives
    # The scattered character matching was too aggressive for this use case
    return False, 0.0


def _character_sequence_score(pattern: str, text: str) -> float:
    """Calculate score based on character sequence matching."""
    if not pattern or not text:
        return 0.0

    matches = 0
    text_idx = 0

    for char in pattern:
        while text_idx < len(text) and text[text_idx] != char:
            text_idx += 1
        if text_idx < len(text):
            matches += 1
            text_idx += 1
        else:
            break

    return matches / len(pattern) if len(pattern) > 0 else 0.0


def search_and_rank(
    items: List[Any],
    query: str,
    search_fields: List[Callable[[Any], str]],
    min_score: float = 0.1
) -> List[Tuple[Any, float]]:
    """
    Search and rank items based on fuzzy matching.
    
    Args:
        items: List of items to search
        query: Search query string
        search_fields: List of functions that extract searchable text from items
        min_score: Minimum relevance score to include in results
    
    Returns:
        List of (item, score) tuples, sorted by relevance score (highest first)
    """
    # Validate query input
    if not query or not query.strip():
        return []

    # Clean the query
    query = query.strip()

    results = []

    for item in items:
        max_score = 0.0

        # Check all search fields and take the best score
        for field_func in search_fields:
            try:
                field_text = field_func(item)
                if field_text:
                    matches, score = fuzzy_match(query, field_text)
                    if matches and score > max_score:
                        max_score = score
            except (AttributeError, TypeError):
                # Skip fields that can't be accessed or converted to string
                continue

        if max_score >= min_score:
            results.append((item, max_score))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def highlight_matches(text: str, query: str) -> str:
    """
    Highlight matching parts of text for display.
    
    Returns text with matches wrapped in [bold yellow][/bold yellow] tags.
    """
    if not query or not text:
        return text

    # Simple case-insensitive highlighting
    pattern = re.escape(query.lower())

    # Find matches in lowercase but preserve original case
    matches = list(re.finditer(pattern, text.lower()))
    if not matches:
        return text

    # Process matches in reverse order to avoid index shifting
    result = text
    for match in reversed(matches):
        start, end = match.span()
        original = text[start:end]
        highlighted = f"[bold yellow]{original}[/bold yellow]"
        result = result[:start] + highlighted + result[end:]

    return result
