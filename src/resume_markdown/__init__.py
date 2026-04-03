"""MCP server and CLI for AI-assisted Markdown resume writing and PDF export."""

try:
    from resume_markdown._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

from resume_markdown.__main__ import main


def mcp_main():
    """Entry point for the resume-markdown-mcp command.

    Delegates to the CLI when called with init/build subcommands,
    otherwise starts the MCP server.
    """
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("init", "build"):
        return main()
    from resume_markdown.server import main as _server_main
    return _server_main()


__all__ = ["main", "mcp_main", "__version__"]
