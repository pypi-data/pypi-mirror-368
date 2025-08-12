"""Custom Markdown renderer with left-aligned headings for Rich."""

from rich import box
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import Markdown, TextElement
from rich.panel import Panel
from rich.text import Text


class LeftAlignedHeading(TextElement):
    """A custom Heading class that left-aligns headers instead of centering them."""

    @classmethod
    def create(cls, markdown, token):
        """Create a heading from a token."""
        return cls(token.tag, token.attrs)

    def __init__(self, tag: str, attrs=None):
        """Initialize the heading."""
        self.tag = tag
        self.attrs = attrs or {}
        super().__init__()
        # Initialize text attribute that the parent class expects
        self.text = Text()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render the heading with left alignment."""
        text = self.text
        text.justify = "left"  # This is the key change - left align instead of center

        # Handle different heading levels
        if self.tag == "h1":
            # For h1, use a panel with left-aligned text
            yield Panel(
                text,
                box=box.HEAVY,
                style="markdown.h1.border",
                padding=(0, 1),
            )
        else:
            # For other headings, add appropriate spacing
            if self.tag == "h2":
                yield Text("")  # Add blank line before h2
            text.stylize("markdown." + self.tag)
            yield text


class LeftAlignedMarkdown(Markdown):
    """A custom Markdown class that uses left-aligned headings."""

    # Override the class variable to use our custom heading
    elements = Markdown.elements.copy()
    elements["heading_open"] = LeftAlignedHeading


def render_markdown_left_aligned(content: str) -> LeftAlignedMarkdown:
    """
    Render markdown content with left-aligned headings.
    
    Args:
        content: The markdown content to render
        
    Returns:
        LeftAlignedMarkdown object with left-aligned headings
    """
    return LeftAlignedMarkdown(content)


# Example usage and comparison
if __name__ == "__main__":
    # Example markdown content
    test_markdown = """# This is an H1 Heading

This is a paragraph under the heading.

## This is an H2 Heading

Another paragraph here.

### This is an H3 Heading

And some more text.

#### H4 Heading

##### H5 Heading

###### H6 Heading

Here's some code:

```python
def hello():
    print("Hello, World!")
```

And a list:
- Item 1
- Item 2
- Item 3
"""

        # Show default centered headings
    console.print("\n[bold yellow]Default Rich Markdown (Centered Headings):[/bold yellow]\n")
    console.print(Markdown(test_markdown))

    console.print("\n" + "="*80 + "\n")

    # Show left-aligned headings
    console.print("[bold yellow]Custom Markdown (Left-Aligned Headings):[/bold yellow]\n")
    console.print(LeftAlignedMarkdown(test_markdown))
