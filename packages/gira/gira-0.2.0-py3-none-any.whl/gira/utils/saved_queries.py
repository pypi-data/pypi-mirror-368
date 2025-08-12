"""Utilities for working with saved queries."""

from typing import Optional

from gira.models.saved_query import SavedQuery
from gira.utils.project import get_gira_root


def load_saved_query(name: str) -> Optional[SavedQuery]:
    """Load a saved query by name.
    
    Args:
        name: The name of the saved query (with or without @ prefix)
    
    Returns:
        The SavedQuery if found, None otherwise
    """
    # Remove @ prefix if present
    if name.startswith("@"):
        name = name[1:]

    try:
        project_root = get_gira_root()
        query_file = project_root / ".gira" / "saved-queries" / f"{name}.json"

        if query_file.exists():
            return SavedQuery.from_json_file(str(query_file))
    except Exception:
        pass

    return None


def resolve_query_string(query_string: str, entity_type: str = "ticket") -> str:
    """Resolve a query string, expanding saved query references.
    
    Args:
        query_string: The query string (may be a saved query name like @my-bugs)
        entity_type: The entity type to filter saved queries by
    
    Returns:
        The resolved query string (expanded if it was a saved query)
    
    Raises:
        ValueError: If a saved query reference is not found
    """
    # Check if this is a saved query reference
    if query_string.startswith("@"):
        saved_query = load_saved_query(query_string)
        if not saved_query:
            raise ValueError(f"Saved query '{query_string}' not found")

        # Verify entity type matches
        if saved_query.entity_type != entity_type:
            raise ValueError(
                f"Saved query '{query_string}' is for {saved_query.entity_type} "
                f"entities, not {entity_type}"
            )

        return saved_query.query

    return query_string


def list_saved_query_names(entity_type: Optional[str] = None) -> list[str]:
    """Get a list of all saved query names.
    
    Args:
        entity_type: Optional entity type to filter by
    
    Returns:
        List of saved query names (without @ prefix)
    """
    try:
        project_root = get_gira_root()
        queries_dir = project_root / ".gira" / "saved-queries"

        if not queries_dir.exists():
            return []

        names = []
        for query_file in queries_dir.glob("*.json"):
            try:
                if entity_type:
                    query = SavedQuery.from_json_file(str(query_file))
                    if query.entity_type == entity_type:
                        names.append(query.name)
                else:
                    # Just use the filename without loading
                    names.append(query_file.stem)
            except Exception:
                continue

        return sorted(names)
    except Exception:
        return []
