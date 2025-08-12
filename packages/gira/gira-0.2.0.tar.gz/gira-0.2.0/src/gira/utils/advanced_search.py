"""Advanced search utilities with exact match, regex, and case sensitivity support."""

import re
from enum import Enum
from typing import Any, Callable, List, Tuple


class SearchMode(Enum):
    """Search mode options."""
    FUZZY = "fuzzy"
    EXACT = "exact"
    REGEX = "regex"


def exact_match(pattern: str, text: str, case_sensitive: bool = False) -> Tuple[bool, float]:
    """
    Perform exact string matching.
    
    Args:
        pattern: The pattern to search for
        text: The text to search in
        case_sensitive: Whether to perform case-sensitive matching
        
    Returns:
        Tuple of (match_found, relevance_score)
    """
    if not pattern or not text:
        return False, 0.0

    if case_sensitive:
        if pattern == text:
            return True, 1.0
        elif pattern in text:
            # Partial exact match - score based on length ratio
            return True, len(pattern) / len(text)
    else:
        pattern_lower = pattern.lower()
        text_lower = text.lower()
        if pattern_lower == text_lower:
            return True, 1.0
        elif pattern_lower in text_lower:
            # Partial exact match - score based on length ratio
            return True, len(pattern_lower) / len(text_lower)

    return False, 0.0


def regex_match(pattern: str, text: str, case_sensitive: bool = False) -> Tuple[bool, float]:
    """
    Perform regex pattern matching.
    
    Args:
        pattern: The regex pattern to search for
        text: The text to search in
        case_sensitive: Whether to perform case-sensitive matching
        
    Returns:
        Tuple of (match_found, relevance_score)
    """
    if not pattern or not text:
        return False, 0.0

    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        compiled_pattern = re.compile(pattern, flags)

        # Search for the pattern
        match = compiled_pattern.search(text)
        if match:
            # Score based on match length relative to text length
            match_length = match.end() - match.start()
            score = min(1.0, match_length / len(text) + 0.5)
            return True, score
    except re.error:
        # Invalid regex pattern
        return False, 0.0

    return False, 0.0


def advanced_search_and_rank(
    items: List[Any],
    query: str,
    search_fields: List[Callable[[Any], str]],
    search_mode: SearchMode = SearchMode.FUZZY,
    case_sensitive: bool = False,
    min_score: float = 0.1
) -> List[Tuple[Any, float]]:
    """
    Search and rank items based on specified search mode.
    
    Args:
        items: List of items to search
        query: Search query string
        search_fields: List of functions that extract searchable text from items
        search_mode: The search mode to use (fuzzy, exact, regex)
        case_sensitive: Whether to perform case-sensitive matching
        min_score: Minimum relevance score to include in results
    
    Returns:
        List of (item, score) tuples, sorted by relevance score (highest first)
    """
    # Validate query input
    if not query or not query.strip():
        return []

    # Import fuzzy_match here to avoid circular imports
    from gira.utils.search import fuzzy_match

    # Select the appropriate matching function
    if search_mode == SearchMode.EXACT:
        match_func = lambda p, t: exact_match(p, t, case_sensitive)
    elif search_mode == SearchMode.REGEX:
        match_func = lambda p, t: regex_match(p, t, case_sensitive)
    else:  # FUZZY
        if case_sensitive:
            # For case-sensitive fuzzy matching, we need a custom implementation
            def case_sensitive_fuzzy(pattern: str, text: str) -> Tuple[bool, float]:
                # Check for exact match first
                if pattern == text:
                    return True, 1.0

                # Check for substring match
                if pattern in text:
                    position = text.index(pattern)
                    position_score = 1.0 - (position / len(text))
                    length_ratio = len(pattern) / len(text)
                    return True, 0.8 + (0.2 * position_score * length_ratio)

                # Word boundary matches
                words = text.split()
                pattern_words = pattern.split()
                word_matches = 0

                for pattern_word in pattern_words:
                    for word in words:
                        if word == pattern_word or word.startswith(pattern_word):
                            word_matches += 1
                            break

                if word_matches > 0:
                    word_score = word_matches / len(pattern_words)
                    return True, 0.3 + (0.4 * word_score)

                return False, 0.0

            match_func = case_sensitive_fuzzy
        else:
            match_func = fuzzy_match

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
                    matches, score = match_func(query, field_text)
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


def highlight_matches_advanced(
    text: str,
    query: str,
    search_mode: SearchMode = SearchMode.FUZZY,
    case_sensitive: bool = False
) -> str:
    """
    Highlight matching parts of text for display based on search mode.
    
    Returns text with matches wrapped in [bold yellow][/bold yellow] tags.
    """
    if not query or not text:
        return text

    if search_mode == SearchMode.REGEX:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(query, flags)

            # Find all matches
            matches = list(pattern.finditer(text))
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
        except re.error:
            # Invalid regex, return unhighlighted text
            return text

    elif search_mode == SearchMode.EXACT:
        if case_sensitive:
            if query in text:
                # Find all occurrences
                result = text
                start = 0
                replacements = []

                while True:
                    index = result.find(query, start)
                    if index == -1:
                        break
                    replacements.append((index, index + len(query)))
                    start = index + 1

                # Process in reverse order
                for start, end in reversed(replacements):
                    original = text[start:end]
                    highlighted = f"[bold yellow]{original}[/bold yellow]"
                    result = result[:start] + highlighted + result[end:]

                return result
        else:
            # Case-insensitive exact match
            query_lower = query.lower()
            text_lower = text.lower()

            if query_lower in text_lower:
                # Find all occurrences
                result = text
                start = 0
                replacements = []

                while True:
                    index = text_lower.find(query_lower, start)
                    if index == -1:
                        break
                    replacements.append((index, index + len(query_lower)))
                    start = index + 1

                # Process in reverse order
                for start, end in reversed(replacements):
                    original = text[start:end]
                    highlighted = f"[bold yellow]{original}[/bold yellow]"
                    result = result[:start] + highlighted + result[end:]

                return result

    else:  # FUZZY
        # Use the existing highlight_matches for fuzzy mode
        from gira.utils.search import highlight_matches
        return highlight_matches(text, query)

    return text
