"""MCP server and CLI for AI-assisted Markdown resume writing and PDF export."""

try:
    from resume_markdown._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

from resume_markdown.__main__ import main
from resume_markdown.server import main as mcp_main

__all__ = ["main", "mcp_main", "__version__"]
