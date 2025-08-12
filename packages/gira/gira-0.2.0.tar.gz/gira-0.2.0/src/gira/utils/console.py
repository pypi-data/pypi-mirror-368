"""Console utilities for Gira with proper Unicode handling."""

import os
import sys

from rich.console import Console as RichConsole


def get_console() -> RichConsole:
    """Get a properly configured Rich console that handles Unicode gracefully.
    
    This function creates a Rich console that:
    - Detects terminal capabilities
    - Falls back to ASCII when Unicode is not supported
    - Respects environment variables for encoding
    - Works properly in container environments
    - Disables colors in test environments
    
    Returns:
        A configured Rich Console instance
    """
    # Check if we're in a test environment
    in_test = bool(
        os.environ.get('PYTEST_CURRENT_TEST') or  # Set by pytest
        os.environ.get('CI') or  # Common CI environment variable
        os.environ.get('NO_COLOR') or  # Standard no-color variable
        'pytest' in sys.modules  # pytest is imported
    )

    # Check various environment indicators for Unicode support
    force_unicode = None

    # Check if we're in a known problematic environment
    in_container = bool(os.environ.get("CONTAINER") or
                       os.environ.get("CODEX_ENVIRONMENT") or
                       os.path.exists("/.dockerenv"))

    # Check terminal encoding
    encoding = sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else None
    supports_unicode = encoding and encoding.lower() in ('utf-8', 'utf8')

    # Check TERM environment variable
    term = os.environ.get('TERM', '').lower()
    if term in ('dumb', 'unknown'):
        force_unicode = False

    # Check for explicit environment override
    if os.environ.get('GIRA_ASCII_ONLY', '').lower() in ('1', 'true', 'yes'):
        force_unicode = False
    elif os.environ.get('GIRA_FORCE_UNICODE', '').lower() in ('1', 'true', 'yes'):
        force_unicode = True

    # In containers, be conservative unless explicitly told otherwise
    if in_container and force_unicode is None:
        # Check if locale supports UTF-8
        try:
            import locale
            current_locale = locale.getlocale()
            if current_locale and current_locale[1] and 'UTF-8' in current_locale[1].upper():
                force_unicode = True
            else:
                force_unicode = False
        except:
            force_unicode = False

    # Create console with appropriate settings
    return RichConsole(
        force_terminal=False if in_test else (True if not in_container else None),
        force_jupyter=False,
        legacy_windows=sys.platform == "win32",
        safe_box=not supports_unicode if force_unicode is None else not force_unicode,
        no_color=in_test,  # Disable colors in test environment
        _environ=os.environ
    )


# Create a singleton console instance
console = get_console()
